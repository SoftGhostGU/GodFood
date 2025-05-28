# food_client.py
import pandas as pd
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import requests
import time
import joblib
import os
import threading

from food_model import FoodPreferenceModel, weights_to_json_serializable, weights_from_json_serializable
import federated_config as config

# --- CRITICAL: Define CATEGORY_COLS and NUMERIC_COLS based on your MERGED data ---
# These columns come from:
# 1. Stable user profile (e.g., gender, age, hometown, diseases - assumed in each review row)
# 2. Contextual review data (e.g., heart_rate, weather - in each review row)
# 3. Restaurant data (e.g., cuisine, cost - merged from shanghai_restaurants.csv)

CATEGORY_COLS = [
    # User Stable Profile
    'gender', 'hometown', 'occupation', 'education_level', 'marital_status',
    'activity_level', 'cooking_skills', 'diseases', 'dietary_preferences', 'food_allergies',
    # Restaurant Features
    'cuisine', 'type', 'adname', 'pname', 'business_area',
    # 'was_hungry_before_meal', # If boolean, treat as category or map to 0/1 numeric
]

NUMERIC_COLS = [
    # User Stable Profile
    'age', 'height_cm', 'weight_kg', 'daily_food_budget_cny',
    # User Contextual Review Data
    'heart_rate_bpm', 'blood_sugar_mmol_L', 'sleep_hours_last_night',
    'weather_temp_celsius', 'weather_humidity_percent', 'steps_today_before_meal',
    # Restaurant Features
    'cost', 'rating_biz', # 'rating_biz' is the original restaurant rating
]
# Note: 'blood_pressure_mmHg' was excluded due to format. If used, preprocess it into numeric columns.
# Note: 'location' (lat/lon) was excluded. If used, split and add to NUMERIC_COLS.


class ReviewDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
    def __len__(self):
        return len(self.features)
    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

def create_preprocessor():
    # For OneHotEncoder, categories can be learned from data (handle_unknown='ignore' is key)
    # Or, provide specific categories from config if they are comprehensive for better control
    categorical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')), # Handles NaNs
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    numerical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')), # Handles NaNs
        ('scaler', StandardScaler())
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_pipeline, CATEGORY_COLS),
            ('num', numerical_pipeline, NUMERIC_COLS)
        ],
        remainder='drop',
        n_jobs=-1
    )
    return preprocessor

def process_features_for_recommendation(preprocessor, user_context_dict, all_restaurants_df_orig):
    if all_restaurants_df_orig.empty: return torch.empty(0), [], 0
    all_restaurants_df = all_restaurants_df_orig.copy()

    inference_df_list = []
    restaurant_ids_order = []
    user_base_df = pd.DataFrame([user_context_dict])

    for _, restaurant_row_series in all_restaurants_df.iterrows():
        restaurant_row = restaurant_row_series.to_dict()
        combined_features_df = user_base_df.copy()
        for col, val in restaurant_row.items():
            if col in CATEGORY_COLS or col in NUMERIC_COLS : # If it's a direct feature used by model
                 combined_features_df[col] = val
            # No need to add restaurant_id to features, it's for tracking
        inference_df_list.append(combined_features_df)
        restaurant_ids_order.append(restaurant_row['restaurant_id'])

    if not inference_df_list: return torch.empty(0), [], 0
    full_inference_df = pd.concat(inference_df_list, ignore_index=True)

    all_expected_feature_cols = CATEGORY_COLS + NUMERIC_COLS
    for col in all_expected_feature_cols:
        if col not in full_inference_df.columns:
            full_inference_df[col] = np.nan

    try:
        X_to_process = full_inference_df[all_expected_feature_cols]
        X_processed = preprocessor.transform(X_to_process)
    except Exception as e:
        print(f"Error during preproc transform for recommendation: {e}")
        return torch.empty(0), [], 0

    return torch.tensor(X_processed, dtype=torch.float32), restaurant_ids_order, X_processed.shape[1]


class Client:
    _preprocessor_fitted_and_saved = False
    _shared_preprocessor = None
    _preprocessor_lock = threading.Lock() # For thread-safe first fit/save

    def __init__(self, client_id, reviews_df_for_client, all_restaurants_df, server_url, user_enhanced_profile_series=None):
        self.client_id = client_id
        self.server_url = server_url
        self.restaurants_df_ref = all_restaurants_df.copy() # Has 'rating_biz'
        self.model = None
        self.input_dim = 0
        self.user_profile_stable_features = user_enhanced_profile_series # Store for recommendation context

        with Client._preprocessor_lock:
            if not Client._preprocessor_fitted_and_saved:
                if os.path.exists(config.PREPROCESSOR_SAVE_PATH): # Try loading first
                    try:
                        Client._shared_preprocessor = joblib.load(config.PREPROCESSOR_SAVE_PATH)
                        Client._preprocessor_fitted_and_saved = True
                        print(f"Client {self.client_id}: Loaded shared preprocessor from {config.PREPROCESSOR_SAVE_PATH}")
                    except Exception as e_load_p:
                        print(f"Client {self.client_id}: Found preprocessor file but FAILED to load: {e_load_p}. Will attempt to refit.")
                        Client._preprocessor_fitted_and_saved = False # Force refit attempt

                if not Client._preprocessor_fitted_and_saved: # Still not loaded/saved, this client will fit
                    print(f"Client {self.client_id}: No preprocessor found or load failed. Attempting to fit and save.")
                    temp_preprocessor_for_fitting = create_preprocessor()
                    self.X_train, self.y_train, self.input_dim = self._preprocess_training_data(
                        reviews_df_for_client, self.restaurants_df_ref, temp_preprocessor_for_fitting, fit_mode=True
                    )
                    if self.input_dim > 0:
                        Client._shared_preprocessor = temp_preprocessor_for_fitting
                        Client._preprocessor_fitted_and_saved = True
                        try:
                            joblib.dump(Client._shared_preprocessor, config.PREPROCESSOR_SAVE_PATH)
                            print(f"Client {self.client_id} SAVED shared preprocessor to {config.PREPROCESSOR_SAVE_PATH}")
                        except Exception as e_save_prep:
                            print(f"Client {self.client_id} FAILED to save shared preprocessor: {e_save_prep}")
                            Client._preprocessor_fitted_and_saved = False
                    else:
                         print(f"Client {self.client_id}: Failed to fit the preprocessor. Input_dim is 0.")
            else: # Preprocessor already fitted/loaded by another thread/instance
                 pass # Will use Client._shared_preprocessor in _preprocess_training_data

        # All clients (including the first one after fitting) use the shared preprocessor for transform
        if Client._shared_preprocessor:
            self.X_train, self.y_train, self.input_dim = self._preprocess_training_data(
                reviews_df_for_client, self.restaurants_df_ref, Client._shared_preprocessor, fit_mode=False
            )
        else: # Should not happen if logic above is correct and first client succeeds
            print(f"Client {self.client_id}: CRITICAL - Shared preprocessor is not available. Cannot process data.")
            self.X_train, self.y_train, self.input_dim = np.array([]), np.array([]), 0


        if self.X_train.shape[0] == 0 or self.input_dim <= 0:
            print(f"CRITICAL: Client {self.client_id} training data empty or input_dim is 0. Actual input_dim: {self.input_dim}")
            self.train_dataset, self.train_loader = None, None
        else:
            if config.INPUT_DIM == -1 and self.input_dim > 0:
                print(f"Client {self.client_id} setting global config.INPUT_DIM to {self.input_dim}")
                config.INPUT_DIM = self.input_dim
            elif config.INPUT_DIM > 0 and self.input_dim > 0 and config.INPUT_DIM != self.input_dim:
                print(f"WARNING: Client {self.client_id} local input_dim {self.input_dim} "
                      f"differs from global config.INPUT_DIM {config.INPUT_DIM}. Aligning to global.")
                self.input_dim = config.INPUT_DIM

            try:
                self.model = FoodPreferenceModel(input_dim=self.input_dim)
                self.train_dataset = ReviewDataset(self.X_train, self.y_train)
                self.train_loader = DataLoader(self.train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
                print(f"Client {self.client_id} model initialized (input_dim: {self.input_dim}).")
            except ValueError as ve:
                 print(f"Client {self.client_id} ERROR initializing model (input_dim {self.input_dim}): {ve}")
                 self.model, self.train_loader, self.train_dataset = None, None, None

    def _preprocess_training_data(self, reviews_df_client, restaurants_df_all, preprocessor_to_use, fit_mode=False):
        if reviews_df_client.empty: return np.array([]), np.array([]), 0

        # **ASSUMPTION**: reviews_df_client CONTAINS ALL STABLE USER FEATURES (gender, age, etc.)
        # AND ALL CONTEXTUAL REVIEW FEATURES (heart_rate, etc.)
        required_cols_in_reviews = [
            'user_rating', 'restaurant_id', # Core for merging and target
            *CATEGORY_COLS, *NUMERIC_COLS # All features model expects
        ]
        # Filter out columns that are expected to come from restaurant_df_all after merge
        review_specific_expected_cols = [
            col for col in required_cols_in_reviews
            if col not in restaurants_df_all.columns or col == 'restaurant_id' # restaurant_id is merge key
        ]
        missing_from_reviews = [col for col in review_specific_expected_cols if col not in reviews_df_client.columns]
        if missing_from_reviews:
            print(f"Client {self.client_id}: ERROR - Review data is missing expected feature columns: {missing_from_reviews}. Check data generation.")
            return np.array([]), np.array([]), 0

        merged_data = pd.merge(reviews_df_client, restaurants_df_all, on='restaurant_id', how='inner', suffixes=('_rev', '_biz'))
        if merged_data.empty:
            print(f"Client {self.client_id}: Merged data is empty. No common restaurant_ids or other issue.")
            return np.array([]), np.array([]), 0

        rating_col = 'user_rating'
        merged_data[rating_col] = pd.to_numeric(merged_data[rating_col], errors='coerce')
        merged_data.dropna(subset=[rating_col], inplace=True)
        if merged_data.empty: return np.array([]), np.array([]), 0

        bins = [0, 2.51, 3.91, 5.1]; labels = [0, 1, 2] # Adjusted bins slightly: <=2.5, 2.6-3.9, >=4.0
        merged_data['rating_class'] = pd.cut(merged_data[rating_col], bins=bins, labels=labels, right=False, include_lowest=True)
        merged_data.dropna(subset=['rating_class'], inplace=True)
        if merged_data.empty: return np.array([]), np.array([]), 0
        y = merged_data['rating_class'].astype(int).values

        all_feature_cols = CATEGORY_COLS + NUMERIC_COLS
        # Ensure all listed feature columns exist in merged_data, adding NaNs if not (imputer will handle)
        for col in all_feature_cols:
            if col not in merged_data.columns:
                # This indicates a mismatch between defined features and actual data content.
                # print(f"Client {self.client_id}: Warning - Feature '{col}' not in merged_data. Adding NaNs.")
                merged_data[col] = np.nan
        try:
            X_for_processing = merged_data[all_feature_cols]
        except KeyError as e:
            print(f"KeyError selecting features for preproc from merged_data: {e}. Avail: {merged_data.columns.tolist()}.")
            return np.array([]), np.array([]), 0

        try:
            if fit_mode:
                X_processed = preprocessor_to_use.fit_transform(X_for_processing)
                # print(f"Client {self.client_id}: Preprocessor fitted. Output dim: {X_processed.shape[1]}")
            else:
                X_processed = preprocessor_to_use.transform(X_for_processing)
                # print(f"Client {self.client_id}: Data transformed. Output dim: {X_processed.shape[1]}")
            current_dim = X_processed.shape[1]
        except Exception as e:
            print(f"Error during preprocessor {'fit_transform' if fit_mode else 'transform'} for {self.client_id}: {e}")
            # print(f"  Data head:\n{X_for_processing.head().to_string()}")
            # print(f"  NaNs:\n{X_for_processing.isnull().sum()[X_for_processing.isnull().sum() > 0].to_string()}")
            return np.array([]), np.array([]), 0
        return X_processed, y, current_dim if X_processed.shape[0] > 0 else 0

    def get_global_model(self):
        if not self.model: # Attempt to initialize if not done
            if config.INPUT_DIM > 0: self.model = FoodPreferenceModel(config.INPUT_DIM); self.input_dim = config.INPUT_DIM
            else: print(f"Client {self.client_id}: Cannot get global model, local model not init (INPUT_DIM unknown)."); return
        try:
            response = requests.get(f"{self.server_url}/get_global_model")
            response.raise_for_status()
            content = response.json()
            global_weights_serializable = content.get('model_weights')
            server_input_dim = content.get('input_dim', -1)

            if server_input_dim > 0 and config.INPUT_DIM == -1: # Server has dim, config doesn't
                config.INPUT_DIM = server_input_dim
                print(f"Client {self.client_id}: Updated global config.INPUT_DIM from server to {server_input_dim}")
            if server_input_dim > 0 and self.input_dim != server_input_dim:
                print(f"Client {self.client_id}: Aligning model to server's INPUT_DIM {server_input_dim} (was {self.input_dim})")
                self.input_dim = server_input_dim
                self.model = FoodPreferenceModel(input_dim=self.input_dim) # Re-initialize

            if global_weights_serializable:
                global_weights = weights_from_json_serializable(global_weights_serializable)
                if self.model.fc1.in_features != self.input_dim: # Final check after potential re-init
                    print(f"Client {self.client_id}: Model re-init for dim {self.input_dim} before loading weights.")
                    self.model = FoodPreferenceModel(input_dim=self.input_dim)
                self.model.load_state_dict(global_weights, strict=False)
                print(f"Client {self.client_id}: Loaded global model (input_dim: {self.model.fc1.in_features}).")
            else:
                print(f"Client {self.client_id}: No global model weights from server ({content.get('message')}).")
        except Exception as e: print(f"Client {self.client_id}: Error getting/loading global model: {e}")

    def train_local_model(self):
        if not self.model or not self.train_loader: print(f"Client {self.client_id}: Cannot train (no model/loader)."); return
        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=config.LEARNING_RATE)
        criterion = nn.CrossEntropyLoss()
        print(f"Client {self.client_id}: Training for {config.LOCAL_EPOCHS} epochs on {len(self.train_dataset)} samples.")
        for epoch in range(config.LOCAL_EPOCHS):
            e_loss, batches = 0,0
            for features, labels in self.train_loader:
                optimizer.zero_grad(); outputs = self.model(features); loss = criterion(outputs, labels)
                loss.backward(); optimizer.step(); e_loss += loss.item(); batches += 1
            if batches > 0: print(f"  Epoch {epoch+1}, Avg Loss: {e_loss/batches:.4f}")

    def send_local_update(self):
        if not self.model or not self.train_dataset or len(self.train_dataset)==0: print(f"Client {self.client_id}: Cannot send update."); return
        serializable_weights = weights_to_json_serializable(self.model.state_dict()) # No LDP for now
        payload = {'client_id': self.client_id, 'model_weights': serializable_weights,
                   'data_size': len(self.train_dataset), 'input_dim': self.input_dim}
        try:
            response = requests.post(f"{self.server_url}/submit_update", json=payload)
            response.raise_for_status()
            print(f"Client {self.client_id}: Sent update. Status: {response.json().get('status')}")
        except Exception as e: print(f"Client {self.client_id}: Error sending update: {e}")

    def recommend_top_restaurants(self, user_context_dict_full, top_n=20):
        if not self.model: print(f"Client {self.client_id}: Model not available."); return pd.DataFrame(), []
        if Client._shared_preprocessor is None:
            print(f"Client {self.client_id}: Shared preprocessor is None! Cannot recommend."); return pd.DataFrame(), []

        features_tensor, restaurant_ids_order, num_feat = process_features_for_recommendation(
            Client._shared_preprocessor, user_context_dict_full, self.restaurants_df_ref
        )
        if features_tensor.nelement() == 0: return pd.DataFrame(), []
        if num_feat != self.model.fc1.in_features:
            print(f"FATAL (Recommend): Feature mismatch! Model: {self.model.fc1.in_features}, Preproc: {num_feat}"); return pd.DataFrame(), []

        self.model.eval()
        with torch.no_grad():
            logits = self.model(features_tensor); probs = torch.softmax(logits, dim=1)
            high_pref_scores = probs[:, 2] # Index 2 for 'high' rating class
            if high_pref_scores.numel() == 0: return pd.DataFrame(), []
            k = min(top_n, len(restaurant_ids_order))
            top_scores, top_indices = torch.topk(high_pref_scores, k=k)
            rec_ids = [restaurant_ids_order[i] for i in top_indices]

        rec_df = self.restaurants_df_ref[self.restaurants_df_ref['restaurant_id'].isin(rec_ids)].copy()
        id_score_map = dict(zip(rec_ids, top_scores.tolist()))
        rec_df['recommendation_score'] = rec_df['restaurant_id'].map(id_score_map)
        rec_df = rec_df.sort_values(by='recommendation_score', ascending=False).reset_index(drop=True)
        print(f"Client {self.client_id}: Top {len(rec_df)} recommendations generated.")
        return rec_df, top_scores.tolist()

# Standalone test (food_client.py)
if __name__ == '__main__':
    # ... (you can adapt the standalone test from previous version if needed, ensuring Shanghai data is loaded) ...
    print("food_client.py standalone execution is primarily for syntax checking.")
    print("Run run_simulation.py for a full test.")