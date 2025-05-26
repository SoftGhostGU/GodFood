import pandas as pd
import numpy as np
import os
import json
import time
import random # For generating sample user context for recommendation
import requests # For informing server about NUM_USERS (optional, see notes)

# Import necessary components from your existing FL framework
import federated_config as config
from food_data_generator import get_shanghai_data_for_simulation # To load all data initially
from food_client import Client # The core client logic

# --- Configuration for Single Client Test ---
# Choose which client's data to use (e.g., the first one found)
CLIENT_INDEX_TO_TEST = random.randint(1, 100) # 0 for the first client, 1 for the second, etc.
# If you want to test a specific user_id, you'd need to find its corresponding review file.

# --- Helper: Load stable user profiles (for recommendation demo) ---
USER_PROFILES_DF = None
def load_user_profiles_for_demo():
    global USER_PROFILES_DF
    if os.path.exists(config.USER_ENHANCED_DATASET_FILE):
        USER_PROFILES_DF = pd.read_csv(config.USER_ENHANCED_DATASET_FILE)
        if 'id' in USER_PROFILES_DF.columns:
            USER_PROFILES_DF.set_index('id', inplace=True)
        print(f"INFO (SingleClient): Loaded {len(USER_PROFILES_DF)} user profiles from {config.USER_ENHANCED_DATASET_FILE} for demo.")
    else:
        print(f"WARNING (SingleClient): User profiles {config.USER_ENHANCED_DATASET_FILE} not found. Recommendation demo might be limited.")


def main():
    print("--- Starting Single Client FL Simulation Script ---")
    print("INFO (SingleClient): This script simulates a single client's lifecycle.")
    print("IMPORTANT: Ensure food_server.py (Shanghai version) is running if you want to test server interaction!")

    # 1. Load all necessary data (restaurants and all client review data initially)
    # get_shanghai_data_for_simulation also updates config.NUM_USERS based on found files.
    # For a single client test, we'll still let it run to correctly set up config,
    # but then we'll only use data for the specified CLIENT_INDEX_TO_TEST.
    print("INFO (SingleClient): Loading all datasets to correctly initialize configurations...")
    all_client_review_dfs, all_restaurants_df_global = get_shanghai_data_for_simulation()

    if all_restaurants_df_global.empty:
        print("CRITICAL (SingleClient): No restaurant data loaded. Exiting.")
        return
    if not all_client_review_dfs:
        print("CRITICAL (SingleClient): No client review data prepared. Exiting.")
        return

    if CLIENT_INDEX_TO_TEST >= len(all_client_review_dfs):
        print(f"CRITICAL (SingleClient): CLIENT_INDEX_TO_TEST ({CLIENT_INDEX_TO_TEST}) is out of bounds. "
              f"Only {len(all_client_review_dfs)} clients' data available. Exiting.")
        return

    # Select data for the single client we want to test
    single_client_review_data = all_client_review_dfs[CLIENT_INDEX_TO_TEST]
    if single_client_review_data.empty:
        print(f"CRITICAL (SingleClient): Review data for client at index {CLIENT_INDEX_TO_TEST} is empty. Exiting.")
        return

    # Extract user_id for this client
    if 'user_id' not in single_client_review_data.columns or single_client_review_data['user_id'].nunique() != 1:
        print(f"ERROR (SingleClient): 'user_id' missing or not unique for client at index {CLIENT_INDEX_TO_TEST}. Exiting."); return
    client_id_str = single_client_review_data['user_id'].iloc[0]
    print(f"INFO (SingleClient): Will simulate for client ID: {client_id_str} (from index {CLIENT_INDEX_TO_TEST})")


    # Load stable user profiles for the recommendation demo part
    load_user_profiles_for_demo()
    user_profile_series_for_this_client = None
    if USER_PROFILES_DF is not None and client_id_str in USER_PROFILES_DF.index:
        user_profile_series_for_this_client = USER_PROFILES_DF.loc[client_id_str]


    # Server URL
    server_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"

    # --- Optional: Inform server this is a 1-client run (if server supports it) ---
    # This helps the server aggregate immediately if it's designed for flexible NUM_USERS
    try:
        print(f"INFO (SingleClient): Informing server to expect 1 client for this test run...")
        response = requests.post(f"{server_url}/set_expected_clients", json={'num_clients': 1})
        if response.status_code == 200:
            print(f"INFO (SingleClient): Server acknowledged. Response: {response.json().get('message', 'OK')}")
        else:
            print(f"WARNING (SingleClient): Server responded with {response.status_code} to /set_expected_clients. "
                  "It might not support this, or an error occurred. Proceeding...")
    except requests.exceptions.RequestException as e:
        print(f"WARNING (SingleClient): Could not inform server about expected clients (server might be down or endpoint not exist): {e}")
        print("INFO (SingleClient): Proceeding with simulation. Server might wait for more clients if not configured for single updates.")

    # 2. Initialize the Single Client
    print(f"\nINFO (SingleClient): Initializing client instance for {client_id_str}...")
    try:
        client_instance = Client(client_id=client_id_str,
                                 reviews_df_for_client=single_client_review_data,
                                 all_restaurants_df=all_restaurants_df_global,
                                 server_url=server_url,
                                 user_enhanced_profile_series=user_profile_series_for_this_client) # Pass profile for reco demo later
    except Exception as e_init:
        print(f"ERROR (SingleClient): Client {client_id_str} failed during __init__: {e_init}")
        import traceback; traceback.print_exc()
        return

    if not client_instance.model or client_instance.input_dim <= 0:
        print(f"ERROR (SingleClient): Client {client_id_str} model not initialized or invalid input_dim "
              f"({client_instance.input_dim}). Cannot proceed with FL rounds.")
        return
    print(f"INFO (SingleClient): Client {client_id_str} initialized. INPUT_DIM: {client_instance.input_dim}")


    # 3. Simulate Federated Learning Rounds for the Single Client
    for fl_round in range(config.NUM_ROUNDS):
        print(f"\n--- Single Client: {client_id_str}, FL Round {fl_round + 1}/{config.NUM_ROUNDS} ---")

        # Get global model (might be initial or from its own previous update if server is running)
        client_instance.get_global_model()
        if not client_instance.model:
            print(f"INFO (SingleClient - {client_id_str}): No global model available for round {fl_round + 1}. "
                  "If this is the first round, it's normal. Otherwise, check server.")
            # If it's just for local testing without a server, we might want to proceed with the current local model.
            # However, for a true FL simulation, we'd ideally always sync.
            # For a single client test, if get_global_model fails and it's not the first round,
            # it implies a server issue or that the server isn't updating the global model with one client.
            # Let's assume the client trains on whatever model it has.
            if fl_round > 0 : # If not first round and still no global model, could be an issue.
                 print(f"WARNING (SingleClient - {client_id_str}): Still no global model from server after round 1.")


        # Train local model
        if client_instance.train_loader and len(client_instance.train_dataset) > 0:
            client_instance.train_local_model()
        else:
            print(f"INFO (SingleClient - {client_id_str}): No training data/loader. Skipping local training.")
            # If no training data, no point in sending update usually.
            print(f"INFO (SingleClient - {client_id_str}): Finished round {fl_round + 1} (no training/update).")
            time.sleep(1)
            continue # Skip sending update if no training

        # Send update to server
        client_instance.send_local_update()

        print(f"INFO (SingleClient - {client_id_str}): Finished processing for round {fl_round + 1}. Short pause...")
        time.sleep(1) # Short delay

    print(f"\nINFO (SingleClient - {client_id_str}): Finished all {config.NUM_ROUNDS} FL rounds.")

    # 4. Demonstrate Recommendation (using the client's final local model)
    print(f"\n--- Single Client: {client_id_str} - Demonstrating Top 10 Recommendation ---")
    if user_profile_series_for_this_client is None and USER_PROFILES_DF is not None and client_id_str in USER_PROFILES_DF.index:
        # Fallback if it wasn't passed to Client init but is available now
        user_profile_series_for_this_client = USER_PROFILES_DF.loc[client_id_str]
    
    if user_profile_series_for_this_client is None:
        print("WARNING (SingleClient - Reco Demo): Stable user profile not available. Using very generic context.")
        # Create a very generic context if full profile is missing
        user_stable_profile_dict = {
            'gender': np.random.choice(config.GENDERS if hasattr(config, 'GENDERS') and config.GENDERS else ['男']),
            'age': 30,
            'hometown': np.random.choice(config.ORIGINS if hasattr(config, 'ORIGINS') and config.ORIGINS else ['上海']),
            # Add defaults for ALL user-side CATEGORY_COLS and NUMERIC_COLS
        }
        for col_name in config.CATEGORY_COLS:
            if col_name not in user_stable_profile_dict and col_name not in all_restaurants_df_global.columns:
                user_stable_profile_dict[col_name] = "Unknown" # Generic default
        for col_name in config.NUMERIC_COLS:
            if col_name not in user_stable_profile_dict and col_name not in all_restaurants_df_global.columns:
                user_stable_profile_dict[col_name] = 0.0 # Generic default
    else:
        user_stable_profile_dict = user_profile_series_for_this_client.to_dict()

    # Simulate current contextual features for this user
    full_user_context_for_recommendation = user_stable_profile_dict.copy()
    full_user_context_for_recommendation.update({
        'heart_rate_bpm': int(np.random.normal(70, 5)),
        'blood_sugar_mmol_L': round(np.random.uniform(5.0, 7.5), 1),
        'sleep_hours_last_night': round(np.random.uniform(7, 8), 1),
        'weather_temp_celsius': round(np.random.uniform(20, 28), 1),
        'weather_humidity_percent': round(np.random.uniform(55, 75), 1),
        'steps_today_before_meal': int(np.random.uniform(3000, 7000)),
    })
    # Ensure all *user-side* features expected by the model are present in the context
    all_user_side_features_expected = [
        col for col in config.CATEGORY_COLS + config.NUMERIC_COLS
        if col not in all_restaurants_df_global.columns # Heuristic: if not in restaurants, it's user-side
    ]
    for col in all_user_side_features_expected:
        if col not in full_user_context_for_recommendation:
            print(f"Warning (SingleClient - Reco Context): User feature '{col}' missing. Adding default.")
            # Add appropriate default based on type (more robust than generic 0)
            if col in config.CATEGORY_COLS:
                full_user_context_for_recommendation[col] = "DefaultCategory"
            elif col in config.NUMERIC_COLS:
                full_user_context_for_recommendation[col] = 0.0 # Or np.nan if imputer handles it better


    print(f"\nUser context for recommendation ({client_id_str}): (sample features)")
    print(json.dumps(full_user_context_for_recommendation, ensure_ascii=False, indent=4))
    # print(f"  Age: {full_user_context_for_recommendation.get('age')}, Gender: {full_user_context_for_recommendation.get('gender')}, "
    #       f"Dietary Pref: {full_user_context_for_recommendation.get('dietary_preferences')}")
    # print(f"  Current Heart Rate: {full_user_context_for_recommendation.get('heart_rate_bpm')}, "
    #       f"Weather Temp: {full_user_context_for_recommendation.get('weather_temp_celsius')}")

    top_recs_df, _ = client_instance.recommend_top_restaurants(full_user_context_for_recommendation, top_n=10)

    if not top_recs_df.empty:
        print("\nTop 10 Recommended Restaurants (based on client's model):")
        for i, row in top_recs_df.iterrows():
            print(f"  {i+1}. {row.get('name','N/A')} (ID: {row.get('restaurant_id')}) "
                  f"Cuisine: {row.get('cuisine','N/A')} Score: {row.get('recommendation_score'):.4f}")
    else:
        print(f"Could not make recommendations for {client_id_str}. "
              "(Model might not be trained, preprocessor issue, or no suitable restaurants).")

    print("\n--- Single Client FL Simulation Script Finished ---")

if __name__ == "__main__":
    main()