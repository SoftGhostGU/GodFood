# training_api_server.py
import pandas as pd
import numpy as np
import torch
import os
import json
import joblib
import io # For reading CSV string
import time

from flask import Flask, request, jsonify

# Assuming these files are in the same directory or configured in PYTHONPATH
import federated_config as config
from food_model import FoodPreferenceModel # Needed if Client doesn't fully encapsulate model
from food_data_generator import load_csv_to_dataframe, get_shanghai_data_for_simulation # For loading all_restaurants
from food_client import Client

# --- Global Variables for Loaded Resources ---
all_restaurants_df_global = None
# Preprocessor is typically handled by the Client instance itself or loaded from server
# INPUT_DIM is also managed by Client interaction with server or initial fitting

app = Flask(__name__)

# Helper to create a DataFrame from CSV string
def csv_string_to_dataframe(csv_string):
    if not csv_string or not isinstance(csv_string, str):
        return pd.DataFrame()
    try:
        return pd.read_csv(io.StringIO(csv_string))
    except Exception as e:
        print(f"Error converting CSV string to DataFrame: {e}")
        return pd.DataFrame()

def load_global_resources():
    """Loads resources needed by all API calls, primarily restaurant data."""
    global all_restaurants_df_global
    print("--- Loading Global Resources for Training API ---")

    # 1. Load All Restaurant Data (essential for feature processing)
    # We can use a simpler loader if get_shanghai_data_for_simulation is too complex here
    # For now, let's assume a direct load of the restaurant file is sufficient
    
    temp_client_dfs, temp_restaurants_df = get_shanghai_data_for_simulation(
        # Reduce the number of users just to load the restaurant data efficiently
        # Or have a dedicated function in food_data_generator just for restaurants
        # max_users_override=1, 
        # user_reviews_dir_override=None, # Don't load reviews here
        # restaurants_file_override=config.SHANGHAI_RESTAURANTS_FILE
    )
    if temp_restaurants_df.empty:
        print(f"CRITICAL: Could not load restaurant data from {config.SHANGHAI_RESTAURANTS_FILE}. Exiting.")
        exit(1)
    all_restaurants_df_global = temp_restaurants_df
    print(f"Loaded {len(all_restaurants_df_global)} Shanghai restaurants globally.")

    # Ensure config.INPUT_DIM is initialized (e.g. from a saved preprocessor or model if needed)
    # For now, we rely on the Client to negotiate this with the server or fit its own.
    # If a pre-trained global model exists, its input_dim can be used as a default.
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH) and config.INPUT_DIM == -1:
        try:
            model_state_dict = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
            if 'fc1.weight' in model_state_dict:
                config.INPUT_DIM = model_state_dict['fc1.weight'].shape[1]
                print(f"Inferred and set config.INPUT_DIM to {config.INPUT_DIM} from saved global model.")
            else:
                print("Warning: Could not infer INPUT_DIM from saved global model for default.")
        except Exception as e:
            print(f"Warning: Error loading saved global model to infer INPUT_DIM: {e}")
    
    print("--- Global resources loaded ---")


@app.route('/train_user_model', methods=['POST'])
def train_user_model_api():
    global all_restaurants_df_global

    if all_restaurants_df_global is None or all_restaurants_df_global.empty:
        return jsonify({"error": "Server resources (restaurant data) not loaded properly."}), 500

    content_type = request.headers.get('Content-Type')
    if 'application/json' in content_type:
        data = request.get_json()
        if 'user_reviews_csv' not in data:
            return jsonify({"error": "Missing 'user_reviews_csv' in JSON payload."}), 400
        user_reviews_csv_string = data['user_reviews_csv']
    elif 'text/csv' in content_type or 'text/plain' in content_type: # Allow direct CSV upload
        user_reviews_csv_string = request.data.decode('utf-8')
    else:
        return jsonify({"error": "Unsupported Content-Type. Please send 'application/json' with a 'user_reviews_csv' field or 'text/csv'."}), 415

    client_review_data = csv_string_to_dataframe(user_reviews_csv_string)

    if client_review_data.empty:
        return jsonify({"error": "Provided user review data is empty or could not be parsed."}), 400

    if 'user_id' not in client_review_data.columns or client_review_data['user_id'].nunique() == 0:
        return jsonify({"error": "'user_id' column missing or empty in the provided review data."}), 400
    
    if client_review_data['user_id'].nunique() > 1:
        return jsonify({"error": "Review data contains multiple 'user_id's. API handles one user at a time."}), 400
        
    client_id_str = str(client_review_data['user_id'].iloc[0])
    print(f"\n--- Received training request for user_id: {client_id_str} with {len(client_review_data)} reviews ---")

    # Extract stable user profile features from the first row if they are consistent
    # The Client class expects user_enhanced_profile_series for stable features.
    # If all features are in each row of review_data, Client's process_features needs to handle it.
    # For simplicity, let's assume the first row can provide the 'stable' profile parts.
    # Your CSV structure suggests user profile info is repeated, so this is reasonable.
    
    # Define which columns are considered "stable" user profile vs. "contextual/review-specific"
    # This needs to align with how Client expects its `user_enhanced_profile_series`
    # and how it distinguishes them from features in `reviews_df_for_client`.
    # For now, let's take all non-review-specific columns from the first row.
    
    # A more robust way: define profile columns in config.
    profile_cols = [col for col in config.USER_PROFILE_COLS if col in client_review_data.columns] # USER_PROFILE_COLS should be defined in config
    
    user_profile_series_for_client = None
    if profile_cols:
        user_profile_series_for_client = client_review_data.iloc[0][profile_cols]
        print(f"Extracted user profile for {client_id_str}: {user_profile_series_for_client.to_dict()}")
    else:
        print(f"Warning: No user profile columns ({config.USER_PROFILE_COLS}) found in input for {client_id_str}. Client might rely on defaults or error out.")


    server_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"

    try:
        # Initialize Client
        # The Client's __init__ is expected to:
        # 1. Process features (potentially fitting preprocessor if first time / needed)
        # 2. Set its self.input_dim
        # 3. Initialize its self.model structure (e.g., FoodPreferenceModel(input_dim))
        client_instance = Client(client_id=client_id_str,
                                 reviews_df_for_client=client_review_data.copy(), # Pass a copy
                                 all_restaurants_df=all_restaurants_df_global,
                                 server_url=server_url,
                                 user_enhanced_profile_series=user_profile_series_for_client)
    except Exception as e_init:
        print(f"ERROR: Client {client_id_str} failed __init__: {e_init}")
        import traceback; traceback.print_exc()
        return jsonify({"error": f"Client initialization failed: {str(e_init)}"}), 500

    print(f"===================Client {client_id_str} initialized for training. Effective INPUT_DIM: {client_instance.input_dim}===================")

    if not client_instance.model or client_instance.input_dim <= 0:
        msg = f"Client {client_id_str} model not initialized or invalid input_dim ({client_instance.input_dim}). Cannot train."
        print(f"INFO: {msg}")
        return jsonify({"error": msg}), 500
    
    print(f"INFO: Client {client_id_str} initialized for training. Effective INPUT_DIM: {client_instance.input_dim}")

    # --- Perform Training ---
    # This mimics one round of FL for this client
    print(f"--- {client_id_str}, Local Training (API Call) ---")
    
    # 1. Get Global Model (optional, if client doesn't have one or wants fresh one)
    #    The Client constructor might already do this if its logic includes fetching on init.
    #    Or, explicitly call it:
    global_model_processed_successfully = client_instance.get_global_model()
    if not global_model_processed_successfully: # Check the return value
        msg = f"Client {client_id_str}: Failed to get, apply, or server provided no weights for global model from {server_url}. Cannot train effectively."
        print(f"WARNING: {msg}")
        return jsonify({"warning": msg, "message": "Training not performed due to issues with obtaining/applying global model weights."}), 202 # Accepted, but not fully processed


    # 2. Train Local Model
    training_loss = None
    if client_instance.train_loader and len(client_instance.train_dataset) > 0:
        print(f"Client {client_id_str}: Starting local training with {len(client_instance.train_dataset)} samples.")
        # The train_local_model in Client might run for config.LOCAL_EPOCHS
        # You might want to override this for the API (e.g., fewer epochs for quicker response)
        training_loss = client_instance.train_local_model() # Add API_TRAIN_EPOCHS to config
        print(f"Client {client_id_str}: Local training completed. Last epoch avg loss: {training_loss}")
    else:
        msg = f"Client {client_id_str}: No training data/loader prepared. Cannot train."
        print(f"INFO: {msg}")
        return jsonify({"message": msg, "status": "No training performed."}), 200

    # 3. Send Local Update to Server (Optional)
    #   This depends heavily on whether your food_server.py is set up to receive
    #   and incorporate individual, ad-hoc updates outside of formal FL rounds.
    update_sent_successfully = False
    if config.API_SEND_UPDATE_TO_SERVER: # Add this to config
        print(f"Client {client_id_str}: Attempting to send model update to server.")
        update_sent_successfully = client_instance.send_local_update()
        if update_sent_successfully:
            print(f"Client {client_id_str}: Model update successfully sent to server.")
        else:
            print(f"Client {client_id_str}: Failed to send model update to server or server did not confirm.")
    else:
        print(f"Client {client_id_str}: Skipping sending update to server as per configuration.")


    # What to return?
    # - Status of training
    # - Maybe some metrics like loss
    # - Confirmation if update was sent
    response_data = {
        "user_id": client_id_str,
        "status": "Training process completed.",
        "training_samples_processed": len(client_instance.train_dataset) if client_instance.train_dataset else 0,
        "average_loss_last_epoch": training_loss if training_loss is not None else "N/A",
        "input_dim_used": client_instance.input_dim,
        "update_sent_to_server": update_sent_successfully if config.API_SEND_UPDATE_TO_SERVER else "NotAttempted"
    }
    
    print(f"INFO: User {client_id_str} training API call finished.")
    return jsonify(response_data), 200


if __name__ == "__main__":
    # Add these to your federated_config.py:
    # USER_PROFILE_COLS = ['age', 'gender', 'height_cm', 'weight_kg', 'hometown', 'occupation', 
    #                        'education_level', 'marital_status', 'has_children', 'hobbies', 
    #                        'diseases', 'dietary_preferences', 'activity_level', 
    #                        'fitness_goals', 'food_allergies', 'cooking_skills', 
    #                        'daily_food_budget_cny'] # List all stable user profile columns from your CSV
    # API_TRAIN_EPOCHS = 1 # Number of epochs for training via API, can be less than full FL
    # API_SEND_UPDATE_TO_SERVER = True # Or False, depending on server capability

    if not hasattr(config, 'USER_PROFILE_COLS'):
        print("CRITICAL: 'USER_PROFILE_COLS' not defined in federated_config.py. Please define it.")
        print("Example: USER_PROFILE_COLS = ['age', 'gender', ...etc... ]")
        exit(1)
    if not hasattr(config, 'API_TRAIN_EPOCHS'): config.API_TRAIN_EPOCHS = 1 # Default
    if not hasattr(config, 'API_SEND_UPDATE_TO_SERVER'): config.API_SEND_UPDATE_TO_SERVER = False # Default cautious

    load_global_resources() # Load restaurants data etc.
    print("--- Starting Flask Development Server for Training API ---")
    app.run(host='0.0.0.0', port=5002, debug=True) # Use a different port, e.g., 5002