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
from sklearn.impute import SimpleImputer # For handling NaNs
import requests
import time

from food_model import FoodPreferenceModel, weights_to_json_serializable, weights_from_json_serializable
import federated_config as config

# --- IMPORTANT: Define these columns based on your ACTUAL merged Yelp data ---
# These are the columns that will be one-hot encoded or scaled.
# Ensure they exist in the DataFrame created by merging reviews and businesses.

CATEGORY_COLS = [
    'gender', 'origin',  # From review_processed (synthetic)
    'cuisine_type',      # From business_with_food_attrs (synthetic)
    'food_temperature_type' # From business_with_food_attrs (synthetic)
    # Add other *categorical* features like 'state' from business if desired,
    # but be mindful of high cardinality.
]

NUMERIC_COLS = [
    # From review_processed (synthetic user/env features)
    'body_temperature', 'last_night_sleep_duration', 'heart_rate',
    'weather_temperature', 'weather_humidity',
    # From business_with_food_attrs (synthetic restaurant features)
    'avg_sweetness', 'avg_sourness', 'avg_spiciness', 'avg_saltiness',
    # From original business data
    'stars_biz',        # Business's average star rating (renamed to avoid clash with review stars)
    'review_count_biz'  # Business's total review count (renamed)
    # 'latitude', 'longitude' # from business
    # From original review data (related to the review itself, not the user's general state)
    # 'useful', 'funny', 'cool' # Number of votes for the review. Consider if these are features or metadata.
]
# The target for training will be derived from 'stars_rev' (the user's rating in the review).

class ReviewDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

def create_preprocessor():
    categorical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')), # Handle NaNs in categoricals
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    numerical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')), # Handle NaNs in numericals
        ('scaler', StandardScaler())
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_pipeline, CATEGORY_COLS),
            ('num', numerical_pipeline, NUMERIC_COLS)
        ],
        remainder='drop' # Drop any columns not explicitly handled
    )
    return preprocessor

def process_features_for_recommendation(preprocessor, user_features_dict, all_restaurants_df):
    if all_restaurants_df.empty:
        return torch.empty(0), [], 0

    inference_df_list = []
    restaurant_ids_order = []
    user_df = pd.DataFrame([user_features_dict]) # User features as a single-row DataFrame

    for idx, restaurant_row in all_restaurants_df.iterrows():
        combined_features = user_df.copy()
        for col, val in restaurant_row.items(): # Iterate over series items
            # Prefix business columns to avoid clashes, e.g., if 'stars' existed in user_features_dict
            biz_col_name = f"{col}_biz" if col in ['stars', 'review_count'] else col # Example renaming
            if biz_col_name not in combined_features.columns or col == 'restaurant_id':
                 combined_features[biz_col_name if col in ['stars', 'review_count'] else col] = val
            elif col == 'restaurant_id': # Ensure restaurant_id is from restaurant_row
                combined_features['restaurant_id'] = val


        inference_df_list.append(combined_features)
        restaurant_ids_order.append(restaurant_row['restaurant_id'])
    
    if not inference_df_list:
        return torch.empty(0), [], 0

    full_inference_df = pd.concat(inference_df_list, ignore_index=True)
    
    all_expected_feature_cols = CATEGORY_COLS + NUMERIC_COLS
    for col in all_expected_feature_cols:
        if col not in full_inference_df.columns:
            print(f"Warning (Recommend Preproc): Expected feature column '{col}' missing. Adding with NaNs.")
            full_inference_df[col] = np.nan
            
    # Ensure columns are in the exact order the preprocessor expects
    try:
        X_to_process = full_inference_df[all_expected_feature_cols]
    except KeyError as e:
        print(f"KeyError selecting features for recommendation: {e}. Avail: {full_inference_df.columns.tolist()}")
        return torch.empty(0), [], 0
        
    try:
        X_processed = preprocessor.transform(X_to_process)
    except Exception as e:
        print(f"Error during preprocessing transform for recommendation: {e}")
        return torch.empty(0), [], 0

    num_features = X_processed.shape[1]
    return torch.tensor(X_processed, dtype=torch.float32), restaurant_ids_order, num_features


class Client:
    def __init__(self, client_id, reviews_df_for_client, all_restaurants_df, server_url):
        self.client_id = client_id
        self.server_url = server_url
        self.restaurants_df_ref = all_restaurants_df.copy() # All business data
        self.preprocessor = create_preprocessor()
        self.model = None # Initialize model later
        self.input_dim = 0

        self.X_train, self.y_train, self.input_dim = self._preprocess_training_data(
            reviews_df_for_client, self.restaurants_df_ref
        )
        
        if self.X_train.shape[0] == 0 or self.input_dim <= 0:
            print(f"CRITICAL: Client {self.client_id} has no training data or 0 features after preprocessing. input_dim: {self.input_dim}")
            self.train_dataset = None
            self.train_loader = None
            # Do not set global INPUT_DIM if this client failed
        else:
            if config.INPUT_DIM == -1:
                print(f"Client {client_id} setting global INPUT_DIM to {self.input_dim}")
                config.INPUT_DIM = self.input_dim
            elif config.INPUT_DIM != self.input_dim:
                print(f"WARNING: Client {self.client_id} local input_dim {self.input_dim} "
                      f"differs from global config.INPUT_DIM {config.INPUT_DIM}. Aligning to global.")
                self.input_dim = config.INPUT_DIM # Align
            
            self.model = FoodPreferenceModel(input_dim=self.input_dim)
            self.train_dataset = ReviewDataset(self.X_train, self.y_train)
            self.train_loader = DataLoader(self.train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)

    def _preprocess_training_data(self, reviews_df, restaurants_df):
        if reviews_df.empty:
            print(f"Client {self.client_id}: Received empty reviews_df for training.")
            return np.array([]), np.array([]), 0

        print(f"Client {self.client_id}: Columns in reviews_df BEFORE MERGE: {reviews_df.columns.tolist()}")
        if 'stars' not in reviews_df.columns: # Assuming 'stars' is the review rating
             print(f"CRITICAL (Client {self.client_id}): 'stars' column (review rating) NOT in reviews_df BEFORE MERGE.")
             return np.array([]), np.array([]), 0

        # Perform the merge, adding suffixes to avoid column name collisions
        # Especially for 'stars' and 'review_count' which can exist in both business and review data
        data = pd.merge(reviews_df, restaurants_df, on='restaurant_id', how='inner', suffixes=('_rev', '_biz'))
        
        print(f"Client {self.client_id}: Columns in data AFTER MERGE: {data.columns.tolist()}")
        if data.empty:
            print(f"Client {self.client_id}: Merged training data is EMPTY. Check 'restaurant_id' matches between reviews and businesses.")
            # Print some non-matching IDs for diagnosis if possible
            review_ids = set(reviews_df['restaurant_id'].unique())
            biz_ids = set(restaurants_df['restaurant_id'].unique())
            print(f"  Unique restaurant_ids in client's reviews: {len(review_ids)}. Sample: {list(review_ids)[:5]}")
            print(f"  Unique restaurant_ids in all businesses: {len(biz_ids)}. Sample: {list(biz_ids)[:5]}")
            print(f"  Intersection size: {len(review_ids.intersection(biz_ids))}")
            return np.array([]), np.array([]), 0

        # Target variable is based on the review's star rating
        rating_column_name = 'stars_rev' # Due to suffix from merge
        if rating_column_name not in data.columns:
            print(f"Client {self.client_id}: Rating column '{rating_column_name}' missing in merged data. Cannot create target.")
            return np.array([]), np.array([]), 0
        
        data[rating_column_name] = pd.to_numeric(data[rating_column_name], errors='coerce')
        data.dropna(subset=[rating_column_name], inplace=True) # Remove rows where rating is not a number
        if data.empty:
            print(f"Client {self.client_id}: No valid '{rating_column_name}' data after conversion/dropna.")
            return np.array([]), np.array([]), 0

        bins = [0, 2.5, 3.5, 6] # ratings 1,2 -> 0; 3 -> 1; 4,5 -> 2
        labels = [0, 1, 2]
        data['rating_class'] = pd.cut(data[rating_column_name], bins=bins, labels=labels, right=True, include_lowest=True)
        data.dropna(subset=['rating_class'], inplace=True) # Remove rows if rating_class is NaN
        if data.empty:
            print(f"Client {self.client_id}: No data left after creating 'rating_class'. Check '{rating_column_name}' values and binning.")
            return np.array([]), np.array([]), 0
        y = data['rating_class'].astype(int).values
        
        # Prepare features for the preprocessor
        all_feature_cols_for_preprocessor = CATEGORY_COLS + NUMERIC_COLS
        
        # Ensure all feature columns are present in 'data', adding NaNs if not
        for col in all_feature_cols_for_preprocessor:
            if col not in data.columns:
                print(f"Warning (Train Preproc): Feature column '{col}' not found in merged data. Adding with NaNs.")
                data[col] = np.nan
        
        try:
            X_for_fitting = data[all_feature_cols_for_preprocessor] # Select in defined order
        except KeyError as e:
            print(f"KeyError selecting features for fitting: {e}. Available: {data.columns.tolist()}. Expected: {all_feature_cols_for_preprocessor}")
            return np.array([]), np.array([]), 0

        try:
            X_processed = self.preprocessor.fit_transform(X_for_fitting)
        except Exception as e:
            print(f"Error during preprocessor fit_transform for client {self.client_id}: {e}")
            print(f"  Shape of X_for_fitting: {X_for_fitting.shape}")
            print(f"  NaN counts in X_for_fitting:\n{X_for_fitting.isnull().sum().to_string()}")
            return np.array([]), np.array([]), 0 # Return empty and 0 dim on error
        
        print(f"Client {self.client_id}: Preprocessed training data. X_shape: {X_processed.shape}, y_shape: {y.shape}")
        return X_processed, y, X_processed.shape[1] if X_processed.shape[0] > 0 else 0


    def get_global_model(self):
        if not self.model: # Check if model was initialized
            # Try to initialize if global INPUT_DIM is now available
            if config.INPUT_DIM > 0 :
                print(f"Client {self.client_id}: Model was not initialized. Attempting now with global INPUT_DIM: {config.INPUT_DIM}")
                try:
                    self.input_dim = config.INPUT_DIM
                    self.model = FoodPreferenceModel(input_dim=self.input_dim)
                except ValueError as ve:
                    print(f"Client {self.client_id}: Failed to initialize model even with global INPUT_DIM. Error: {ve}")
                    return # Cannot proceed
            else:
                print(f"Client {self.client_id}: Model not initialized and global INPUT_DIM not set. Cannot get global model.")
                return

        try:
            response = requests.get(f"{self.server_url}/get_global_model")
            response.raise_for_status()
            content = response.json()
            global_weights_serializable = content.get('model_weights')
            
            if global_weights_serializable:
                global_weights = weights_from_json_serializable(global_weights_serializable)
                
                # Crucial: Ensure model's input layer matches config.INPUT_DIM if it changed
                if self.model.fc1.in_features != config.INPUT_DIM and config.INPUT_DIM > 0:
                    print(f"Client {self.client_id}: Global INPUT_DIM ({config.INPUT_DIM}) differs from current model "
                          f"({self.model.fc1.in_features}). Re-initializing model.")
                    try:
                        self.model = FoodPreferenceModel(input_dim=config.INPUT_DIM)
                        self.input_dim = config.INPUT_DIM # Update client's dim
                    except ValueError as ve:
                        print(f"Client {self.client_id}: Failed to re-initialize model with new INPUT_DIM. Error: {ve}")
                        return # Cannot load weights if model cannot be re-initialized

                # Check keys after potential re-initialization
                current_keys = set(self.model.state_dict().keys())
                received_keys = set(global_weights.keys())

                if current_keys != received_keys:
                    print(f"Client {self.client_id}: Mismatch in model keys with global model AFTER potential re-init! Cannot load.")
                    print(f"  Model expects keys like: {list(current_keys)[:3]}... ({len(current_keys)} total)")
                    print(f"  Received keys like: {list(received_keys)[:3]}... ({len(received_keys)} total)")
                else:
                    self.model.load_state_dict(global_weights)
                    print(f"Client {self.client_id}: Loaded global model state into current model (input features: {self.model.fc1.in_features}).")
            else:
                print(f"Client {self.client_id}: No global model weights available from server (or 'model_weights' key missing). Message: {content.get('message')}")
        except requests.exceptions.RequestException as e:
            print(f"Client {self.client_id}: Error getting global model: {e}")
        except Exception as e_load: 
            print(f"Client {self.client_id}: Error processing or loading global model: {e_load}")


    def train_local_model(self):
        if not self.model or not self.train_loader:
            state = "no model" if not self.model else "no dataloader"
            print(f"Client {self.client_id}: Cannot train due to {state}.")
            return

        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=config.LEARNING_RATE)
        criterion = nn.CrossEntropyLoss()
        
        print(f"Client {self.client_id}: Starting local training for {config.LOCAL_EPOCHS} epochs on {len(self.train_dataset)} samples.")
        for epoch in range(config.LOCAL_EPOCHS):
            epoch_loss = 0
            num_batches = 0
            for features, labels in self.train_loader:
                if features.ndim == 1: features = features.unsqueeze(0) # Ensure batch dim
                if features.shape[0] == 0: continue
                
                optimizer.zero_grad()
                outputs = self.model(features)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                num_batches += 1
            
            if num_batches > 0:
                 avg_epoch_loss = epoch_loss / num_batches
                 print(f"Client {self.client_id}, Epoch {epoch+1}/{config.LOCAL_EPOCHS}, Loss: {avg_epoch_loss:.4f}")
            else:
                 print(f"Client {self.client_id}, Epoch {epoch+1}/{config.LOCAL_EPOCHS}, No batches processed in this epoch.")


    def send_local_update(self):
        if not self.model or not self.train_dataset or len(self.train_dataset) == 0:
            print(f"Client {self.client_id}: Cannot send update. Model not trained or no training data.")
            return
        
        local_weights = self.model.state_dict()
        noisy_weights = add_local_differential_privacy(
            local_weights, config.EPSILON, config.DELTA, config.SENSITIVITY
        )
        serializable_weights = weights_to_json_serializable(noisy_weights)
        try:
            payload = {'client_id': self.client_id, 
                       'model_weights': serializable_weights, 
                       'data_size': len(self.train_dataset)}
            response = requests.post(f"{self.server_url}/submit_update", json=payload)
            response.raise_for_status()
            print(f"Client {self.client_id}: Sent model update to server. Status: {response.json().get('status')}")
        except requests.exceptions.RequestException as e:
            print(f"Client {self.client_id}: Error sending update: {e}")
        except Exception as e_ser:
            print(f"Client {self.client_id}: Error during update serialization or sending: {e_ser}")


    def recommend_restaurant(self, user_features_dict):
        if not self.model:
            print(f"Client {self.client_id}: Model not available for recommendation.")
            return None, None
        if self.restaurants_df_ref.empty:
            print(f"Client {self.client_id}: No restaurants available for recommendation.")
            return None, None

        # Ensure user_features_dict has all keys expected by CATEGORY_COLS + NUMERIC_COLS that are user-specific
        # For those that are restaurant-specific, they will come from all_restaurants_df
        user_specific_cols = [
            'gender', 'origin', 'body_temperature', 'last_night_sleep_duration',
            'heart_rate', 'weather_temperature', 'weather_humidity'
        ]
        for col in user_specific_cols:
            if col not in user_features_dict:
                print(f"Warning (Recommend): User feature '{col}' missing. Setting to NaN/Default for recommendation.")
                user_features_dict[col] = np.nan # Or a sensible default

        features_tensor, restaurant_ids_order, num_features = process_features_for_recommendation(
            self.preprocessor, user_features_dict, self.restaurants_df_ref
        )

        if features_tensor.nelement() == 0:
            print(f"Client {self.client_id}: No features processed for recommendation.")
            return None, None

        # Critical check: num_features from preprocessor must match current model's input_dim
        current_model_input_dim = self.model.fc1.in_features
        if num_features != current_model_input_dim:
            print(f"Client {self.client_id}: FATAL! Feature mismatch for recommendation. "
                  f"Model expected {current_model_input_dim}, preprocessor output {num_features}. Cannot recommend.")
            return None, None

        self.model.eval()
        with torch.no_grad():
            all_predictions_logits = self.model(features_tensor)
            probabilities = torch.softmax(all_predictions_logits, dim=1)
            score_for_high_preference = probabilities[:, 2] 

            if score_for_high_preference.numel() == 0:
                print(f"Client {self.client_id}: No scores generated by model for recommendation.")
                return None, None

            best_restaurant_idx = torch.argmax(score_for_high_preference).item()
            recommended_restaurant_id = restaurant_ids_order[best_restaurant_idx]
            recommendation_score = score_for_high_preference[best_restaurant_idx].item()

        recommended_restaurant_details = self.restaurants_df_ref[
            self.restaurants_df_ref['restaurant_id'] == recommended_restaurant_id
        ].iloc[0] # Get as Series

        print(f"Client {self.client_id}: Recommendation complete.")
        return recommended_restaurant_details, recommendation_score

def add_local_differential_privacy(model_state_dict, epsilon, delta, sensitivity):
    noisy_state_dict = {}
    for name, param_tensor in model_state_dict.items():
        if param_tensor.is_floating_point():
            std_dev = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon
            noise = torch.normal(0, std_dev, param_tensor.shape).to(param_tensor.device)
            noisy_state_dict[name] = param_tensor + noise
        else:
            noisy_state_dict[name] = param_tensor # Keep non-float params as is
    return noisy_state_dict

if __name__ == '__main__':
    print("Standalone test of food_client.py (requires processed Yelp files as per config)")
    # This test is more meaningful if federated_config.py points to small sample files
    # or if the full dataset is available and PROCESSED_REVIEW_FILE is small enough.
    from food_data_generator import get_yelp_data_for_simulation # For loading
    
    # Modify config for a small, quick test
    original_num_users = config.NUM_USERS
    original_reviews_per_user = config.REVIEWS_PER_USER
    config.NUM_USERS = 1 
    config.REVIEWS_PER_USER = 50 # Use a small number of reviews for the test client
    
    try:
        print(f"Attempting to load data for standalone client test using paths from config:")
        print(f"  Reviews: {config.PROCESSED_REVIEW_FILE}")
        print(f"  Business: {config.PROCESSED_BUSINESS_FILE}")
        client_review_dfs, restaurants_df_global = get_yelp_data_for_simulation()
        
        if not client_review_dfs or client_review_dfs[0].empty or restaurants_df_global.empty:
            print("Standalone test: Failed to load or distribute sufficient Yelp data. Ensure files exist and paths are correct in config.")
        else:
            client0_reviews_train = client_review_dfs[0]
            print(f"Standalone test: Client 0 will use {len(client0_reviews_train)} reviews for training.")
            
            client0 = Client(client_id="client_0_yelp_standalone_test", 
                             reviews_df_for_client=client0_reviews_train, 
                             all_restaurants_df=restaurants_df_global, 
                             server_url=f"http://{config.SERVER_HOST}:{config.SERVER_PORT}")
            
            if client0.model and client0.input_dim > 0:
                print(f"Client 0 initialized with input_dim: {client0.input_dim}")
                client0.get_global_model() # Attempt to get (likely no model from server in standalone)
                print("--- Starting standalone local training ---")
                client0.train_local_model()
                
                print("\n--- Client 0 Test Recommendation (Yelp Data) ---")
                current_user_features = {
                    'gender': np.random.choice(config.GENDERS),
                    'origin': np.random.choice(config.ORIGINS),
                    'body_temperature': 36.8,
                    'last_night_sleep_duration': 7.5,
                    'heart_rate': 65,
                    'weather_temperature': 22.0,
                    'weather_humidity': 55.0
                    # Restaurant-specific features are added during process_features_for_recommendation
                }
                print(f"Recommending for user features: {current_user_features}")

                recommended_restaurant, score = client0.recommend_restaurant(current_user_features)

                if recommended_restaurant is not None:
                    print("\nRecommended Restaurant:")
                    print(f"  Name: {recommended_restaurant.get('name', 'N/A')}")
                    print(f"  ID: {recommended_restaurant.get('restaurant_id', 'N/A')}")
                    print(f"  Cuisine (Synthetic): {recommended_restaurant.get('cuisine_type', 'N/A')}")
                    print(f"  Predicted Score (Prob of High Pref): {score:.4f}")
                else:
                    print("Could not make a recommendation with the test data/model.")
            else:
                print(f"Client 0 model not initialized or input_dim is 0 ({client0.input_dim}). Cannot run full standalone test.")

    except Exception as e:
        print(f"Error during standalone client test setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        config.NUM_USERS = original_num_users
        config.REVIEWS_PER_USER = original_reviews_per_user