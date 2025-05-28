# api_server.py
import pandas as pd
import numpy as np
import torch
import os
import json
import joblib
import random # For default values if needed, though user provides context

from flask import Flask, request, jsonify

# Assuming these files are in the same directory or configured in PYTHONPATH
import federated_config as config
from food_model import FoodPreferenceModel
from food_data_generator import load_csv_to_dataframe # Use adapted loader
from food_client import process_features_for_recommendation

# --- Global Variables for Loaded Resources ---
all_restaurants_df_global = None
inference_model_global = None
preprocessor_global = None
input_dim_global = -1

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False # Explicitly set this globally if needed

def infer_input_dim_from_model(state_dict):
    if 'fc1.weight' in state_dict: return state_dict['fc1.weight'].shape[1]
    print("Warning: Could not infer input_dim from model state_dict."); return -1

def load_resources():
    """Loads all necessary resources once at server startup."""
    global all_restaurants_df_global, inference_model_global, preprocessor_global, input_dim_global

    print("--- Loading Resources for Inference API ---")

    # 1. Load Restaurant Data
    all_restaurants_df_global = load_csv_to_dataframe(config.SHANGHAI_RESTAURANTS_FILE)
    if all_restaurants_df_global.empty:
        print("CRITICAL: No Shanghai restaurant data. Exiting.")
        exit(1) # Critical failure
    if 'id' in all_restaurants_df_global.columns:
        all_restaurants_df_global.rename(columns={'id': 'restaurant_id'}, inplace=True)
    if 'rating' in all_restaurants_df_global.columns:
        all_restaurants_df_global.rename(columns={'rating': 'rating_biz'}, inplace=True)
    print(f"Loaded {len(all_restaurants_df_global)} Shanghai restaurants.")

    # 2. Load Model
    if not os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        print(f"CRITICAL: Model {config.GLOBAL_MODEL_SAVE_PATH} not found. Train first. Exiting.")
        exit(1)
    try:
        model_state_dict = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
        print("Global model state_dict loaded.")
    except Exception as e:
        print(f"CRITICAL: Error loading model: {e}. Exiting.")
        exit(1)

    input_dim_global = config.INPUT_DIM
    if input_dim_global == -1:
        input_dim_global = infer_input_dim_from_model(model_state_dict)
    if input_dim_global <= 0:
        print(f"CRITICAL: Invalid INPUT_DIM ({input_dim_global}). Exiting.")
        exit(1)
    print(f"Using INPUT_DIM: {input_dim_global} for model.")
    config.INPUT_DIM = input_dim_global # Ensure config is updated if inferred

    try:
        inference_model_global = FoodPreferenceModel(input_dim=input_dim_global)
        inference_model_global.load_state_dict(model_state_dict)
        inference_model_global.eval() # Set to evaluation mode
        print("Global model weights loaded into inference instance.")
    except Exception as e:
        print(f"CRITICAL: Error initializing/loading model: {e}. Exiting.")
        exit(1)

    # 3. Load Preprocessor
    if not os.path.exists(config.PREPROCESSOR_SAVE_PATH):
        print(f"CRITICAL: Preprocessor {config.PREPROCESSOR_SAVE_PATH} not found. Train first. Exiting.")
        exit(1)
    try:
        preprocessor_global = joblib.load(config.PREPROCESSOR_SAVE_PATH)
        print("Loaded saved preprocessor.")
    except Exception as e:
        print(f"CRITICAL: Error loading preprocessor: {e}. Exiting.")
        exit(1)
    
    print("--- All resources loaded successfully ---")


@app.route('/recommend', methods=['POST'])
def recommend():
    global all_restaurants_df_global, inference_model_global, preprocessor_global, input_dim_global

    if not all_restaurants_df_global.size or not inference_model_global or not preprocessor_global:
        return jsonify({"error": "Server resources not loaded properly."}), 500

    user_context = request.get_json()
    if not user_context:
        return jsonify({"error": "Invalid input: No JSON payload received."}), 400

    print(f"\n--- Received recommendation request for user context: ---")
    print(json.dumps(user_context, ensure_ascii=False, indent=2))

    # Ensure all expected user-side columns are present in the received context
    # This mirrors the placeholder logic from the original script for robustness
    all_user_side_features_expected = [
        col for col in config.CATEGORY_COLS + config.NUMERIC_COLS 
        if col not in all_restaurants_df_global.columns # Only consider user-side features
    ]
    
    missing_features = []
    for col in all_user_side_features_expected:
        if col not in user_context:
            missing_features.append(col)
            # Add a very basic placeholder; ideally, client sends complete context
            # For this API, we might prefer to return an error if critical features are missing
            # For now, maintaining behavior of original script:
            print(f"Warning (API Request): User feature '{col}' missing. Adding default placeholder.")
            user_context[col] = "Unknown" if col in config.CATEGORY_COLS else 0.0
    
    if missing_features:
        print(f"API Warning: The following user features were missing and defaulted: {missing_features}")


    try:
        features_tensor, restaurant_ids_order, num_feat_proc = process_features_for_recommendation(
            preprocessor_global, user_context, all_restaurants_df_global
        )
    except Exception as e:
        print(f"Error during feature processing: {e}")
        return jsonify({"error": f"Error during feature processing: {str(e)}"}), 500

    recommendations_output = []
    
    if features_tensor.nelement() == 0:
        print("No features processed for recommendation.")
        return jsonify({"message": "No features could be processed for recommendation.", "recommendations": []})
    elif num_feat_proc != input_dim_global:
        error_msg = f"FATAL: Feature mismatch! Model expects {input_dim_global}, Preprocessor generated: {num_feat_proc}."
        print(error_msg)
        return jsonify({"error": error_msg}), 500
    else:
        inference_model_global.eval() # Ensure it's in eval mode
        with torch.no_grad():
            logits = inference_model_global(features_tensor)
            probs = torch.softmax(logits, dim=1) # Probabilities for [low, medium, high]
            high_pref_scores = probs[:, 2]       # Assuming index 2 is 'high preference'

            if high_pref_scores.numel() > 0:
                k = min(20, len(restaurant_ids_order)) # Get top 20 or fewer if not enough options
                
                # Ensure k is not greater than the number of scores available
                if high_pref_scores.numel() < k:
                    k = high_pref_scores.numel()
                
                if k == 0: # No scores to pick from
                    return jsonify({"message": "No recommendations could be generated based on scores.", "recommendations": []})

                top_scores_t, top_indices_t = torch.topk(high_pref_scores, k=k)
                
                rec_ids = [restaurant_ids_order[i] for i in top_indices_t.tolist()] # .tolist() for safety
                
                # Filter all_restaurants_df for these IDs and add score
                top_recs_df = all_restaurants_df_global[all_restaurants_df_global['restaurant_id'].isin(rec_ids)].copy()
                
                id_score_map_inf = dict(zip(rec_ids, top_scores_t.tolist()))
                top_recs_df['recommendation_score'] = top_recs_df['restaurant_id'].map(id_score_map_inf)
                
                # Sort by score and prepare for JSON output
                top_recs_df = top_recs_df.sort_values(by='recommendation_score', ascending=False).reset_index(drop=True)
                
                # Convert DataFrame to list of dicts for JSON response
                # Fill NaN values for robustness, e.g., if some restaurant details are missing
                recommendations_output = top_recs_df.fillna('N/A').to_dict(orient='records')
            else:
                 print("No high preference scores generated.")
                 return jsonify({"message": "No high preference scores generated.", "recommendations": []})


    if recommendations_output:
        print(f"\n--- Sending Top {len(recommendations_output)} Recommended Restaurants ---")
        # for rec in recommendations_output:
        #     print(f"  - {rec.get('name','N/A')} (ID: {rec.get('restaurant_id')}) Score: {rec.get('recommendation_score'):.4f}")
    else:
        print("\nNo recommendations could be made for the given context.")
        return jsonify({"message": "No recommendations could be made for the given context.", "recommendations": []})

    return jsonify({"recommendations": recommendations_output})

if __name__ == "__main__":
    load_resources() # Load all models, data, preprocessors
    print("--- Starting Flask Development Server ---")
    # Make sure your federated_config.py, food_model.py, etc. are accessible
    app.run(host='0.0.0.0', port=5001, debug=True) # Using port 5001 to avoid common conflicts