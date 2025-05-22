# run_simulation.py
import threading
import time
import pandas as pd
import numpy as np
import os # For checking file existence

# Assuming food_data_generator.py, food_client.py, federated_config.py are accessible
from food_data_generator import get_yelp_data_for_simulation
from food_client import Client
import federated_config as config

client_instances_map = {}
active_clients_count = 0 # Use a simple counter instead of a global list
simulation_lock = threading.Lock() # For safely modifying active_clients_count

def run_client_process(client_id_num, client_review_data, all_restaurants_df, server_url):
    global active_clients_count
    client_id_str = f"client_{client_id_num}"
    
    if client_review_data.empty:
        print(f"INFO: Client {client_id_str} received no review data. Skipping initialization.")
        return

    print(f"INFO: Initializing {client_id_str} with {len(client_review_data)} reviews...")
    
    try:
        client_instance = Client(client_id=client_id_str, 
                                 reviews_df_for_client=client_review_data, 
                                 all_restaurants_df=all_restaurants_df,
                                 server_url=server_url)
    except Exception as e_init:
        print(f"ERROR: Client {client_id_str} failed during __init__: {e_init}")
        import traceback
        traceback.print_exc()
        return

    if not client_instance.model or client_instance.input_dim <= 0:
        print(f"INFO: Client {client_id_str} model not initialized or invalid input_dim ({client_instance.input_dim}). Skipping participation.")
        return
        
    client_instances_map[client_id_str] = client_instance
    with simulation_lock:
        active_clients_count += 1
    
    # INPUT_DIM should be set by the first client successfully initializing its preprocessor.
    # The Client.__init__ handles setting config.INPUT_DIM.
    # We rely on the first client that processes data successfully to establish this.
    # Subsequent clients will align to this config.INPUT_DIM.
    
    print(f"INFO: Client {client_id_str} successfully initialized. Effective INPUT_DIM: {client_instance.input_dim} (Global config: {config.INPUT_DIM})")

    for fl_round in range(config.NUM_ROUNDS):
        print(f"\n--- {client_id_str}, FL Round {fl_round + 1}/{config.NUM_ROUNDS} ---")
        
        client_instance.get_global_model()
        if not client_instance.model:
            print(f"INFO: {client_id_str} could not obtain/validate global model for round {fl_round + 1}. Skipping training.")
            time.sleep(1) # Avoid busy-looping if server is slow or issue persists
            continue

        if client_instance.train_loader and len(client_instance.train_dataset) > 0:
            client_instance.train_local_model()
            client_instance.send_local_update()
        else:
            print(f"INFO: {client_id_str} has no training data/loader. Skipping local training and update for round {fl_round + 1}.")
            # Client still stays in the loop to potentially receive future global models if data appears.
            # Or, could have logic to make it drop out.

        print(f"INFO: {client_id_str} finished processing for round {fl_round + 1}. Waiting...")
        time.sleep(np.random.uniform(0.5, 2.0)) # Simulate network/computation variance

    print(f"INFO: {client_id_str} finished all FL rounds.")


if __name__ == '__main__':
    print("--- Starting Federated Learning Simulation with Yelp Data ---")
    print("IMPORTANT: Ensure the food_server.py is running in a separate terminal!")
    print(f"Business data: {config.PROCESSED_BUSINESS_FILE}")
    print(f"Review data: {config.PROCESSED_REVIEW_FILE}")
    
    if not os.path.exists(config.PROCESSED_BUSINESS_FILE) or \
       not os.path.exists(config.PROCESSED_REVIEW_FILE):
        print("ERROR: One or both processed Yelp data files not found. Please check paths in federated_config.py and run preprocessing scripts.")
        exit()
    
    time.sleep(3) 

    server_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"

    client_review_datasets, all_restaurants_df = get_yelp_data_for_simulation()

    if all_restaurants_df.empty:
        print("CRITICAL ERROR: No business data loaded. Simulation cannot proceed.")
        exit()
    if not client_review_datasets or all(df.empty for df in client_review_datasets):
        print("CRITICAL ERROR: No review data distributed to any client. Simulation cannot proceed.")
        exit()
    
    # Determine the actual number of clients for whom data was prepared
    num_clients_with_data = sum(1 for df in client_review_datasets if not df.empty)
    
    # IMPORTANT: The server expects config.NUM_USERS. If we start fewer clients,
    # the server might wait indefinitely for aggregation unless config.NUM_USERS is
    # dynamically communicated or the server has a timeout/flexible threshold.
    # For this simulation, we'll adjust config.NUM_USERS if fewer clients have data.
    # This is a simplification; real FL systems have more dynamic client management.
    if num_clients_with_data < config.NUM_USERS:
        print(f"WARNING: Data prepared for only {num_clients_with_data} clients, "
              f"but config.NUM_USERS is {config.NUM_USERS}. ")
        if num_clients_with_data > 0 :
            print(f"Adjusting simulated NUM_USERS to {num_clients_with_data} for this run.")
            config.NUM_USERS = num_clients_with_data # Server will now expect this many
        else:
            print("CRITICAL: No clients have data. Exiting.")
            exit()
            
    client_threads = []
    for i in range(config.NUM_USERS): # Iterate up to the (potentially adjusted) NUM_USERS
        if i < len(client_review_datasets) and not client_review_datasets[i].empty:
            thread = threading.Thread(target=run_client_process, 
                                      args=(i, client_review_datasets[i], all_restaurants_df, server_url))
            client_threads.append(thread)
        else:
            # This case should be less frequent now due to adjustment of config.NUM_USERS
            print(f"INFO: Skipping thread creation for client index {i} - no data was assigned or index out of bounds.")

    if not client_threads:
        print("CRITICAL ERROR: No client threads were prepared to start. Check data loading and distribution. Exiting.")
        exit()
        
    print(f"INFO: Starting {len(client_threads)} client threads for simulation...")
    for i, thread in enumerate(client_threads):
        thread.start()
        if i == 0: time.sleep(2) # Give first client a bit more time to set INPUT_DIM
        else: time.sleep(0.5) 

    for thread in client_threads:
        thread.join()

    print(f"\n--- Simulation Summary ---")
    print(f"All {len(client_threads)} client threads have completed.")
    print(f"Total clients that actively participated (initialized model): {active_clients_count}")
    print(f"Final Global INPUT_DIM recorded in config: {config.INPUT_DIM}")

    if client_instances_map and active_clients_count > 0:
        # Try to pick an active client for demo
        active_client_ids = [cid for cid, client in client_instances_map.items() if client.model and client.input_dim > 0]
        if active_client_ids:
            example_client_id = active_client_ids[0]
            example_client = client_instances_map[example_client_id]
            print(f"\n--- Demonstrating Recommendation on Active Client: {example_client_id} ---")
            
            current_user_features = {
                'gender': np.random.choice(config.GENDERS),
                'origin': np.random.choice(config.ORIGINS),
                'body_temperature': round(np.random.normal(37.0, 0.3),1),
                'last_night_sleep_duration': round(np.random.uniform(6, 9),1),
                'heart_rate': int(np.random.normal(75, 8)),
                'weather_temperature': round(np.random.uniform(15, 28),1),
                'weather_humidity': round(np.random.uniform(40, 60),1)
            }
            print(f"\nUser context for recommendation ({example_client_id}):")
            for key, val in current_user_features.items(): print(f"  {key}: {val}")
            
            recommended_restaurant, score = example_client.recommend_restaurant(current_user_features)
            
            if recommended_restaurant is not None:
                print("\nRecommended Restaurant Details:")
                print(f"  Name: {recommended_restaurant.get('name', 'N/A')}")
                print(f"  ID: {recommended_restaurant.get('restaurant_id', 'N/A')}")
                print(f"  Original Stars: {recommended_restaurant.get('stars_biz', 'N/A')}") # Note: stars_biz from merge
                print(f"  Categories: {recommended_restaurant.get('categories', 'N/A')}")
                print(f"  Synthetic Cuisine: {recommended_restaurant.get('cuisine_type', 'N/A')}")
                print(f"  Predicted Score (Prob of High Pref): {score:.4f}")
            else:
                print(f"Could not make a recommendation for {example_client_id}. (Model might not be trained or data issue).")
        else:
            print("No active clients with valid models found for recommendation demo.")
    else:
        print("No active client instances available for recommendation demo (or active_clients_count is 0).")

    print("\n--- Federated Learning Simulation with Yelp Data Complete ---")