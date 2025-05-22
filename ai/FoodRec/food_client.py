# food_client.py
import pandas as pd
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import requests
import time

from food_data_generator import generate_review_data_for_user, generate_restaurant_data # For individual client data
from food_model import FoodPreferenceModel, weights_to_json_serializable, weights_from_json_serializable
import federated_config as config

CATEGORY_COLS = ['gender', 'origin', 'cuisine_type', 'food_temperature_type']
NUMERIC_COLS = ['body_temperature', 'last_night_sleep_duration', 'heart_rate',
                'weather_temperature', 'weather_humidity', 'avg_sweetness',
                'avg_sourness', 'avg_spiciness', 'avg_saltiness']

class ReviewDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

def create_preprocessor():
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    numerical_transformer = StandardScaler()
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, CATEGORY_COLS),
            ('num', numerical_transformer, NUMERIC_COLS)
        ], remainder='passthrough'
    )
    return preprocessor

def process_features_for_recommendation(preprocessor, user_features_dict, all_restaurants_df):
    """
    Processes features for all potential user-restaurant pairs for recommendation.
    
    Args:
        preprocessor: The fitted scikit-learn preprocessor.
        user_features_dict: A dictionary containing the current user's features.
                            e.g., {'gender': 'Male', 'origin': 'North', ...}
        all_restaurants_df: DataFrame of all available restaurants.

    Returns:
        A tuple: (processed_features_tensor, list_of_restaurant_ids_in_order)
    """
    if all_restaurants_df.empty:
        return torch.empty(0), [], 0

    # Create a DataFrame for each user-restaurant combination
    inference_df_list = []
    restaurant_ids_order = []

    user_df = pd.DataFrame([user_features_dict]) # DataFrame with one row for user features

    for idx, restaurant_row in all_restaurants_df.iterrows():
        # Create a combined feature set for this user and restaurant
        # User features are constant, restaurant features change
        
        # Start with user features
        combined_features = user_df.copy()

        # Add restaurant features
        for col in all_restaurants_df.columns:
            if col not in combined_features.columns: # Avoid overwriting if user features had same names (unlikely here)
                 combined_features[col] = restaurant_row[col]
            elif col == 'restaurant_id': # ensure restaurant_id is from restaurant_row
                combined_features[col] = restaurant_row[col]


        inference_df_list.append(combined_features)
        restaurant_ids_order.append(restaurant_row['restaurant_id'])
    
    if not inference_df_list:
        return torch.empty(0), [], 0

    full_inference_df = pd.concat(inference_df_list, ignore_index=True)
    
    # Select only the columns the preprocessor expects (excluding IDs, names, target)
    # The columns for `transform` must match those used in `fit`.
    # These are implicitly defined by CATEGORY_COLS and NUMERIC_COLS.
    
    cols_for_preprocessing = [col for col in CATEGORY_COLS + NUMERIC_COLS if col in full_inference_df.columns]
    
    # Ensure all expected columns are present, filling if necessary
    # (This is simplified; robust handling for missing columns is complex)
    for expected_col in CATEGORY_COLS + NUMERIC_COLS:
        if expected_col not in full_inference_df.columns:
            print(f"Warning: Expected column '{expected_col}' not found in combined data for recommendation. Adding with NaN.")
            # Add with NaN or a suitable default. Preprocessor's handle_unknown or imputer should manage.
            full_inference_df[expected_col] = np.nan 


    X_to_process = full_inference_df[CATEGORY_COLS + NUMERIC_COLS] # Order matters for ColumnTransformer
    
    try:
        X_processed = preprocessor.transform(X_to_process)
    except Exception as e:
        print(f"Error during preprocessing for recommendation: {e}")
        print(f"Shape of X_to_process: {X_to_process.shape}")
        print(f"Columns of X_to_process: {X_to_process.columns.tolist()}")
        # You might want to inspect X_to_process further here
        return torch.empty(0), [], 0


    num_features = X_processed.shape[1]
    return torch.tensor(X_processed, dtype=torch.float32), restaurant_ids_order, num_features


class Client:
    def __init__(self, client_id, reviews_df, restaurants_df, server_url):
        self.client_id = client_id
        self.server_url = server_url
        self.restaurants_df_ref = restaurants_df.copy() # Keep a reference to all restaurant data

        self.preprocessor = create_preprocessor()
        
        self.X_train, self.y_train, self.input_dim = self._preprocess_training_data(reviews_df, self.restaurants_df_ref, client_id)
        
        if config.INPUT_DIM == -1:
            print(f"Client {client_id} setting global INPUT_DIM to {self.input_dim}")
            config.INPUT_DIM = self.input_dim
        elif config.INPUT_DIM != self.input_dim:
            print(f"WARNING: Client {self.client_id} input_dim {self.input_dim} "
                  f"differs from global config.INPUT_DIM {config.INPUT_DIM}. ")
            # Attempt to align if possible, or error if features fundamentally mismatch
            # This suggests the preprocessor might not be generating consistent feature sets
            # For now, try to proceed, but this is a point of potential failure.
            self.input_dim = config.INPUT_DIM # Align with global config

        self.model = FoodPreferenceModel(input_dim=self.input_dim)
        self.train_dataset = ReviewDataset(self.X_train, self.y_train)
        self.train_loader = DataLoader(self.train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)

    def _preprocess_training_data(self, reviews_df, restaurants_df, client_id="temp"):
        # Merge review and restaurant data for training
        data = pd.merge(reviews_df, restaurants_df, on='restaurant_id')
        # Define target: Bin ratings into classes
        bins = [0, 2.5, 3.5, 6]
        labels = [0, 1, 2]
        data['rating_class'] = pd.cut(data['rating'], bins=bins, labels=labels, right=True, include_lowest=True).astype(int)
        y = data['rating_class'].values
        
        # Features for training are from the merged data
        X = data.drop(['user_id', 'restaurant_id', 'restaurant_name', 'rating', 'rating_class'], axis=1, errors='ignore')
        
        # Fit the preprocessor on this client's training data
        X_processed = self.preprocessor.fit_transform(X)
        
        return X_processed, y, X_processed.shape[1]

    def get_global_model(self):
        # (This method remains the same as before)
        try:
            response = requests.get(f"{self.server_url}/get_global_model")
            response.raise_for_status()
            global_weights_serializable = response.json().get('model_weights') 
            if global_weights_serializable:
                global_weights = weights_from_json_serializable(global_weights_serializable)
                current_keys = set(self.model.state_dict().keys())
                received_keys = set(global_weights.keys())

                if current_keys != received_keys:
                    print(f"Client {self.client_id}: Mismatch in model keys with global model!")
                    if config.INPUT_DIM != self.model.fc1.in_features:
                        print(f"Client {self.client_id}: INPUT_DIM seems to have changed. Attempting to re-initialize model.")
                        try:
                            self.model = FoodPreferenceModel(input_dim=config.INPUT_DIM)
                            self.input_dim = config.INPUT_DIM 
                            self.model.load_state_dict(global_weights)
                            print(f"Client {self.client_id}: Loaded global model after re-initialization.")
                        except Exception as e_reinit:
                            print(f"Client {self.client_id}: Failed to re-initialize or load model: {e_reinit}")
                    else:
                         print(f"Client {self.client_id}: Key mismatch persists. Cannot load global model.")
                else:
                    self.model.load_state_dict(global_weights)
                    print(f"Client {self.client_id}: Loaded global model.")
            else:
                print(f"Client {self.client_id}: No global model available from server.")
        except requests.exceptions.RequestException as e:
            print(f"Client {self.client_id}: Error getting global model: {e}")
        except Exception as e_load: 
            print(f"Client {self.client_id}: Error processing or loading global model: {e_load}")


    def train_local_model(self):
        # (This method remains the same as before)
        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=config.LEARNING_RATE)
        criterion = nn.CrossEntropyLoss()
        for epoch in range(config.LOCAL_EPOCHS):
            epoch_loss = 0
            for features, labels in self.train_loader:
                optimizer.zero_grad()
                outputs = self.model(features)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            avg_epoch_loss = epoch_loss / len(self.train_loader)
            print(f"Client {self.client_id}, Epoch {epoch+1}/{config.LOCAL_EPOCHS}, Loss: {avg_epoch_loss:.4f}")

    def send_local_update(self):
        # (This method remains the same as before)
        local_weights = self.model.state_dict()
        noisy_weights = add_local_differential_privacy(
            local_weights, config.EPSILON, config.DELTA, config.SENSITIVITY
        )
        serializable_weights = weights_to_json_serializable(noisy_weights)
        try:
            payload = {'client_id': self.client_id, 'model_weights': serializable_weights, 'data_size': len(self.train_dataset)}
            response = requests.post(f"{self.server_url}/submit_update", json=payload)
            response.raise_for_status()
            print(f"Client {self.client_id}: Sent model update to server. Status: {response.json().get('status')}")
        except requests.exceptions.RequestException as e:
            print(f"Client {self.client_id}: Error sending update: {e}")

    def recommend_restaurant(self, user_features_dict):
        """
        Recommends the best restaurant for a user based on their current features.
        User features required: gender, origin, body_temperature, last_night_sleep_duration, 
                                 heart_rate, weather_temperature, weather_humidity.
        """
        if not self.restaurants_df_ref.empty:
            # Preprocess features for all user-restaurant combinations
            features_tensor, restaurant_ids_order, num_features = process_features_for_recommendation(
                self.preprocessor,
                user_features_dict,
                self.restaurants_df_ref
            )

            if features_tensor.nelement() == 0: # Check if tensor is empty
                print(f"Client {self.client_id}: No features processed for recommendation.")
                return None, None

            if num_features != self.input_dim:
                print(f"Client {self.client_id}: FATAL! Feature mismatch for recommendation. "
                      f"Expected {self.input_dim}, got {num_features}. Cannot proceed with reliable recommendation.")
                # This is a critical error. The preprocessor output dimension must match model input.
                # Could be due to new categories in OneHotEncoder not handled consistently by 'ignore'
                # or fundamental mismatch in expected columns.
                return None, None # Indicate failure

            self.model.eval() # Set model to evaluation mode
            with torch.no_grad(): # Disable gradient calculations
                # Get model outputs (logits for rating classes) for all restaurant combinations
                all_predictions_logits = self.model(features_tensor)
                
                # We want to pick the restaurant most likely to get a "High Preference" (class 2)
                # Or, we can use a weighted score from the logits/probabilities.
                # Option 1: Probability of being class 2 (High Preference)
                probabilities = torch.softmax(all_predictions_logits, dim=1)
                score_for_high_preference = probabilities[:, 2] # Class 2 is 'High Preference'

                # Option 2: Expected rating (if classes are 0, 1, 2, treat as ordinal)
                # expected_score = probabilities[:, 0]*0 + probabilities[:, 1]*1 + probabilities[:, 2]*2
                # For simplicity, let's use the probability of "High Preference"

                best_restaurant_idx = torch.argmax(score_for_high_preference).item()
                recommended_restaurant_id = restaurant_ids_order[best_restaurant_idx]
                recommendation_score = score_for_high_preference[best_restaurant_idx].item()

            recommended_restaurant_details = self.restaurants_df_ref[
                self.restaurants_df_ref['restaurant_id'] == recommended_restaurant_id
            ].iloc[0]

            print(f"Client {self.client_id}: Recommendation complete.")
            return recommended_restaurant_details, recommendation_score
        else:
            print(f"Client {self.client_id}: No restaurants available for recommendation.")
            return None, None


# (add_local_differential_privacy function remains the same)
def add_local_differential_privacy(model_state_dict, epsilon, delta, sensitivity):
    noisy_state_dict = {}
    for name, param_tensor in model_state_dict.items():
        if param_tensor.is_floating_point():
            std_dev = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon
            noise = torch.normal(0, std_dev, param_tensor.shape).to(param_tensor.device)
            noisy_state_dict[name] = param_tensor + noise
        else:
            noisy_state_dict[name] = param_tensor
    return noisy_state_dict


if __name__ == '__main__':
    # Standalone test
    print("Testing Client standalone (recommendation focus)...")
    
    restaurants_df_global = generate_restaurant_data(config.NUM_RESTAURANTS)
    client0_reviews_train = generate_review_data_for_user(0, config.REVIEWS_PER_USER, restaurants_df_global['restaurant_id'].tolist())
    
    client0 = Client(client_id="client_0_reco_test", 
                     reviews_df=client0_reviews_train, 
                     restaurants_df=restaurants_df_global, 
                     server_url=f"http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    
    # Simulate getting a model and training
    client0.get_global_model() # Will likely be empty if server not running, or load from disk
    client0.train_local_model() # Train on its local data
    
    print("\n--- Client 0 Test Recommendation ---")
    # Define user's current state for recommendation
    current_user_features = {
        'gender': 'Female',
        'origin': 'South',
        'body_temperature': 36.8,
        'last_night_sleep_duration': 7.5,
        'heart_rate': 65,
        'weather_temperature': 22.0,
        'weather_humidity': 55.0
        # Restaurant-specific features like 'cuisine_type', 'avg_sweetness' etc.
        # will be picked from each restaurant in `restaurants_df_ref` during `process_features_for_recommendation`
    }
    print(f"Recommending for user features: {current_user_features}")

    recommended_restaurant, score = client0.recommend_restaurant(current_user_features)

    if recommended_restaurant is not None:
        print("\nRecommended Restaurant:")
        print(f"  Name: {recommended_restaurant['restaurant_name']}")
        print(f"  ID: {recommended_restaurant['restaurant_id']}")
        print(f"  Cuisine: {recommended_restaurant['cuisine_type']}")
        print(f"  Predicted Score (Prob of High Pref): {score:.4f}")
    else:
        print("Could not make a recommendation.")

    print(f"Client 0 test finished. Input dim: {client0.input_dim}")