# run_simulation.py
import threading
import time
import pandas as pd
import numpy as np

from food_data_generator import generate_restaurant_data, generate_review_data_for_user, GENDERS, ORIGINS
from food_client import Client
import federated_config as config

client_instances_map = {}

def run_client_process(client_id_num, client_data, restaurants_df, server_url):
    client_id_str = f"client_{client_id_num}"
    print(f"Starting {client_id_str}...")
    
    client_instance = Client(client_id=client_id_str, 
                             reviews_df=client_data, 
                             restaurants_df=restaurants_df,
                             server_url=server_url)
    client_instances_map[client_id_str] = client_instance
    
    if client_id_num > 0: 
        while config.INPUT_DIM == -1 and not getattr(config, '_INPUT_DIM_SET_BY_CLIENT_0', False):
            print(f"{client_id_str} waiting for INPUT_DIM to be set...")
            time.sleep(0.5)
    elif client_id_num == 0:
        if config.INPUT_DIM != -1:
            setattr(config, '_INPUT_DIM_SET_BY_CLIENT_0', True)

    print(f"{client_id_str} proceeding with INPUT_DIM: {client_instance.input_dim} (Global: {config.INPUT_DIM})")

    for fl_round in range(config.NUM_ROUNDS):
        print(f"\n--- {client_id_str}, FL Round {fl_round + 1}/{config.NUM_ROUNDS} ---")
        client_instance.get_global_model()
        client_instance.train_local_model()
        client_instance.send_local_update()
        print(f"{client_id_str} finished round {fl_round + 1}. Waiting...")
        time.sleep(1)

    print(f"{client_id_str} finished all FL rounds.")


if __name__ == '__main__':
    print("Starting Federated Learning Simulation (Restaurant Recommendation Focus)...")
    print("IMPORTANT: Ensure the food_server.py is running in a separate terminal!")
    time.sleep(2) 

    server_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
    restaurants_df_global = generate_restaurant_data(config.NUM_RESTAURANTS)

    client_datasets = []
    for i in range(config.NUM_USERS):
        user_reviews = generate_review_data_for_user(i, config.REVIEWS_PER_USER, restaurants_df_global['restaurant_id'].tolist())
        client_datasets.append(user_reviews)

    client_threads = []
    for i in range(config.NUM_USERS):
        thread = threading.Thread(target=run_client_process, 
                                  args=(i, client_datasets[i], restaurants_df_global, server_url))
        client_threads.append(thread)
        thread.start()
        if i == 0: 
            time.sleep(2) 
        else:
            time.sleep(0.5)

    for thread in client_threads:
        thread.join()

    print("\nFederated Learning Simulation Complete.")
    print(f"Final INPUT_DIM used by configuration: {config.INPUT_DIM}")

    # --- Demonstrate Restaurant Recommendation on one client ---
    if client_instances_map:
        example_client_id = f"client_0"
        example_client = client_instances_map.get(example_client_id)

        if example_client:
            print(f"\n--- Demonstrating Recommendation on {example_client_id} ---")
            
            # Define a sample user's current state for recommendation
            current_user_features_for_recommendation = {
                'gender': np.random.choice(GENDERS),
                'origin': np.random.choice(ORIGINS),
                'body_temperature': np.random.normal(37.0, 0.3),
                'last_night_sleep_duration': np.random.uniform(6, 9),
                'heart_rate': np.random.normal(75, 8),
                'weather_temperature': np.random.uniform(15, 28), # Pleasant weather
                'weather_humidity': np.random.uniform(40, 60)
            }
            print(f"\nUser context for recommendation ({example_client_id}):")
            for key, val in current_user_features_for_recommendation.items():
                print(f"  {key}: {val:.2f}" if isinstance(val, float) else f"  {key}: {val}")
            
            recommended_restaurant, score = example_client.recommend_restaurant(current_user_features_for_recommendation)
            
            if recommended_restaurant is not None:
                print("\nRecommended Restaurant Details:")
                print(f"  Name: {recommended_restaurant['restaurant_name']}")
                print(f"  ID: {recommended_restaurant['restaurant_id']}")
                print(f"  Cuisine: {recommended_restaurant['cuisine_type']}")
                print(f"  Avg Spiciness: {recommended_restaurant['avg_spiciness']:.2f}")
                print(f"  Food Temp Type: {recommended_restaurant['food_temperature_type']}")
                print(f"  Predicted Score (Prob of High Pref): {score:.4f}")
            else:
                print(f"Could not make a recommendation for {example_client_id}.")
        else:
            print("Could not find an example client instance for recommendation demo.")
    else:
        print("No client instances available for recommendation demo.")