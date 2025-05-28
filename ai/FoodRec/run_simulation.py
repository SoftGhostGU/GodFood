# run_simulation.py
import threading
import time
import pandas as pd
import numpy as np
import os
import federated_config as config
from food_data_generator import get_shanghai_data_for_simulation
from food_client import Client # CATEGORY_COLS, NUMERIC_COLS not directly needed here

client_instances_map = {}
active_clients_count = 0
simulation_lock = threading.Lock()
USER_PROFILES_DF = None

def load_user_profiles_for_demo():
    global USER_PROFILES_DF
    if os.path.exists(config.USER_ENHANCED_DATASET_FILE):
        USER_PROFILES_DF = pd.read_csv(config.USER_ENHANCED_DATASET_FILE)
        if 'id' in USER_PROFILES_DF.columns:
            USER_PROFILES_DF.set_index('id', inplace=True)
        print(f"Loaded {len(USER_PROFILES_DF)} user profiles from {config.USER_ENHANCED_DATASET_FILE} for demo.")
    else:
        print(f"Warning: User profiles {config.USER_ENHANCED_DATASET_FILE} not found. Reco demo limited.")

def run_client_process(client_idx_num, client_review_data, all_restaurants_df, server_url):
    global active_clients_count
    if client_review_data.empty: print(f"INFO: Client {client_idx_num} no review data. Skipping."); return

    if 'user_id' not in client_review_data.columns or client_review_data['user_id'].nunique() != 1:
        print(f"ERROR: Client {client_idx_num}: 'user_id' missing/not unique. Skipping."); return
    client_id_str = client_review_data['user_id'].iloc[0]

    # For Client init, user_enhanced_profile_series can be None if stable features are in review_data
    # It's primarily for constructing the full context during the recommendation demo.
    user_profile_series_for_client = None
    if USER_PROFILES_DF is not None and client_id_str in USER_PROFILES_DF.index:
        user_profile_series_for_client = USER_PROFILES_DF.loc[client_id_str]

    print(f"INFO: Initializing client {client_id_str} (idx {client_idx_num}) with {len(client_review_data)} reviews...")
    try:
        client_instance = Client(client_id=client_id_str,
                                 reviews_df_for_client=client_review_data,
                                 all_restaurants_df=all_restaurants_df,
                                 server_url=server_url,
                                 user_enhanced_profile_series=user_profile_series_for_client)
    except Exception as e_init:
        print(f"ERROR: Client {client_id_str} failed __init__: {e_init}"); import traceback; traceback.print_exc(); return

    if not client_instance.model or client_instance.input_dim <= 0:
        print(f"INFO: Client {client_id_str} model not init or invalid input_dim ({client_instance.input_dim}). Skipping."); return

    client_instances_map[client_id_str] = client_instance
    with simulation_lock: active_clients_count += 1
    print(f"INFO: Client {client_id_str} initialized. Effective INPUT_DIM: {client_instance.input_dim} (Global: {config.INPUT_DIM})")

    for fl_round in range(config.NUM_ROUNDS):
        print(f"\n--- {client_id_str}, FL Round {fl_round + 1}/{config.NUM_ROUNDS} ---")
        client_instance.get_global_model()
        if not client_instance.model:
            print(f"INFO: {client_id_str} no global model for round {fl_round + 1}. Skipping."); time.sleep(1); continue
        if client_instance.train_loader and len(client_instance.train_dataset) > 0:
            client_instance.train_local_model()
            client_instance.send_local_update()
        else: print(f"INFO: {client_id_str} no training data/loader for round {fl_round + 1}.")
        print(f"INFO: {client_id_str} finished round {fl_round + 1}. Waiting..."); time.sleep(np.random.uniform(0.5, 1.0))
    print(f"INFO: {client_id_str} finished all FL rounds.")

if __name__ == '__main__':
    print("--- Starting FL Simulation with Shanghai Data ---")
    print("IMPORTANT: Ensure food_server.py (Shanghai) is RUNNING!")
    if not os.path.exists(config.SHANGHAI_RESTAURANTS_FILE) or not os.path.isdir(config.USER_REVIEWS_DIR):
        print("ERROR: Restaurant file or user reviews dir not found. Check config paths."); exit()

    load_user_profiles_for_demo()
    time.sleep(2) # Give server a moment if just started

    server_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
    all_client_review_dfs, all_restaurants_df_global = get_shanghai_data_for_simulation()

    if all_restaurants_df_global.empty: print("CRITICAL: No restaurant data. Exiting."); exit()
    if not all_client_review_dfs: print("CRITICAL: No client review data. Exiting."); exit()
    # config.NUM_USERS is updated by get_shanghai_data_for_simulation
    print(f"INFO: Simulating with {config.NUM_USERS} clients based on review files found.")

    client_threads = []
    # Iterate up to the potentially adjusted config.NUM_USERS
    for i in range(config.NUM_USERS):
        if i < len(all_client_review_dfs) and not all_client_review_dfs[i].empty:
            thread = threading.Thread(target=run_client_process,
                                      args=(i, all_client_review_dfs[i], all_restaurants_df_global, server_url))
            client_threads.append(thread)
    if not client_threads: print("CRITICAL: No client threads prepared. Exiting."); exit()

    print(f"INFO: Starting {len(client_threads)} client threads...")
    for i, thread in enumerate(client_threads):
        thread.start()
        if i == 0: time.sleep(5) # More time for first client to fit preprocessor & set INPUT_DIM
        else: time.sleep(0.8)

    for thread in client_threads: thread.join()

    print(f"\n--- Simulation Summary ---")
    print(f"All {len(client_threads)} client threads completed. Active clients: {active_clients_count}")
    print(f"Final Global INPUT_DIM in config: {config.INPUT_DIM}")

    if client_instances_map and active_clients_count > 0 and USER_PROFILES_DF is not None:
        example_client_id = next(iter(client_instances_map)) # First active client
        example_client = client_instances_map[example_client_id]
        print(f"\n--- Demo: Top 10 Recommendation from Active Client: {example_client_id} ---")
        if example_client_id not in USER_PROFILES_DF.index:
            print(f"ERROR: User {example_client_id} not in USER_PROFILES_DF for demo context.")
        else:
            user_stable_profile_dict = USER_PROFILES_DF.loc[example_client_id].to_dict()
            # Simulate current contextual features for this user
            full_user_context = user_stable_profile_dict.copy()
            full_user_context.update({
                'heart_rate_bpm': int(np.random.normal(70, 5)),
                'blood_sugar_mmol_L': round(np.random.uniform(5.0, 7.5), 1),
                'sleep_hours_last_night': round(np.random.uniform(7, 8), 1),
                'weather_temp_celsius': round(np.random.uniform(20, 28), 1),
                'weather_humidity_percent': round(np.random.uniform(55, 75), 1),
                'steps_today_before_meal': int(np.random.uniform(3000, 7000)),
            })
            # Ensure all CATEGORY_COLS and NUMERIC_COLS that are user-side are present
            # This is a bit manual; ideally Client's preprocessor would define expected features
            # For now, we rely on CATEGORY_COLS and NUMERIC_COLS being comprehensive
            for col in config.CATEGORY_COLS + config.NUMERIC_COLS: # Use config lists
                if col not in full_user_context and col not in all_restaurants_df_global.columns: # If it's a user-side col
                    print(f"Warning (Demo Reco): User feature '{col}' missing from context. Adding default.")
                    full_user_context[col] = np.random.choice(config.GENDERS) if col == 'gender' else \
                                             np.random.choice(config.ORIGINS) if col == 'hometown' else \
                                             0 # Or other sensible default / NaN for imputer

            print(f"\nUser context for {example_client_id}: (sample features)")
            print(f"  Age: {full_user_context.get('age')}, Gender: {full_user_context.get('gender')}, Cuisine Pref (from profile): {full_user_context.get('dietary_preferences')}")
            print(f"  Current Heart Rate: {full_user_context.get('heart_rate_bpm')}, Weather Temp: {full_user_context.get('weather_temp_celsius')}")

            top_recs_df, _ = example_client.recommend_top_restaurants(full_user_context, top_n=20)
            if not top_recs_df.empty:
                print("\nTop 20 Recommended Restaurants:")
                for i, row in top_recs_df.iterrows():
                    print(f"  {i+1}. {row.get('name','N/A')} (ID: {row.get('restaurant_id')}) "
                        #   f"Cuisine: {row.get('cuisine','N/A')} Score: {row.get('recommendation_score'):.4f}")
                        f"Cuisine: {row.get('cuisine','N/A')}")
            else: print(f"Could not make recommendations for {example_client_id}.")
    else: print("No active clients or user profiles for recommendation demo.")
    print("\n--- FL Simulation (Shanghai Data) Complete ---")