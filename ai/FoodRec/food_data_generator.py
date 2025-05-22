# food_data_generator.py
import pandas as pd
import numpy as np
import json
import os # Added for os.path.exists
from federated_config import (
    PROCESSED_BUSINESS_FILE, PROCESSED_REVIEW_FILE,
    NUM_USERS, REVIEWS_PER_USER
)

def load_json_lines_to_dataframe(file_path):
    """Loads a JSON Lines file into a Pandas DataFrame."""
    records = []
    if not os.path.exists(file_path):
        print(f"ERROR: Data file not found: {file_path}")
        return pd.DataFrame()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON line {line_number} in {file_path}: {line.strip()}")
        return pd.DataFrame(records)
    except Exception as e:
        print(f"ERROR: Could not read file {file_path}. Error: {e}")
        return pd.DataFrame()

def get_yelp_data_for_simulation():
    """
    Loads the preprocessed Yelp business and review data.
    Distributes review data among clients.
    """
    print(f"Loading business data from: {PROCESSED_BUSINESS_FILE}")
    restaurants_df = load_json_lines_to_dataframe(PROCESSED_BUSINESS_FILE)
    if restaurants_df.empty:
        print("CRITICAL: Business data could not be loaded or is empty. Exiting.")
        exit()

    if 'business_id' in restaurants_df.columns and 'restaurant_id' not in restaurants_df.columns:
        restaurants_df.rename(columns={'business_id': 'restaurant_id'}, inplace=True)
    elif 'restaurant_id' not in restaurants_df.columns:
        print("CRITICAL: 'business_id' or 'restaurant_id' not found in business data. Exiting.")
        exit()

    print(f"Loading review data from: {PROCESSED_REVIEW_FILE}")
    all_reviews_df = load_json_lines_to_dataframe(PROCESSED_REVIEW_FILE)
    if all_reviews_df.empty:
        print("CRITICAL: Review data could not be loaded or is empty. Exiting.")
        exit()

    if 'business_id' in all_reviews_df.columns and 'restaurant_id' not in all_reviews_df.columns:
        all_reviews_df.rename(columns={'business_id': 'restaurant_id'}, inplace=True)
    elif 'restaurant_id' not in all_reviews_df.columns:
        print("CRITICAL: 'business_id' or 'restaurant_id' not found in review data. Exiting.")
        exit()

    # Ensure essential columns for training exist in reviews
    if 'user_id' not in all_reviews_df.columns:
        print("CRITICAL: 'user_id' column missing in review data. Exiting.")
        exit()
    if 'stars' not in all_reviews_df.columns: # Assuming 'stars' is the rating column
        print("CRITICAL: 'stars' (rating) column missing in review data. Exiting.")
        exit()


    client_review_datasets = []
    num_total_reviews = len(all_reviews_df)

    if num_total_reviews == 0:
        print("CRITICAL: No reviews available in the loaded review data. Exiting.")
        exit()

    actual_reviews_per_user = REVIEWS_PER_USER
    if NUM_USERS * REVIEWS_PER_USER > num_total_reviews :
        print(f"Warning: Requested {NUM_USERS * REVIEWS_PER_USER} reviews across {NUM_USERS} users, "
              f"but only {num_total_reviews} total reviews available.")
        actual_reviews_per_user = num_total_reviews // NUM_USERS
        if actual_reviews_per_user == 0:
            actual_reviews_per_user = 1 # Assign at least one if possible
        print(f"Adjusting REVIEWS_PER_USER for simulation to approximately {actual_reviews_per_user}")


    if actual_reviews_per_user == 0:
        print("CRITICAL: Calculated reviews per user is 0. Cannot distribute. Exiting.")
        exit()
        
    # Shuffle all reviews once
    shuffled_reviews = all_reviews_df.sample(frac=1, random_state=42).reset_index(drop=True)

    start_idx = 0
    for i in range(NUM_USERS):
        end_idx = start_idx + actual_reviews_per_user
        
        if start_idx >= num_total_reviews: # No more reviews left to assign
            print(f"Warning: Ran out of reviews. Client {i} and subsequent will not get data.")
            break 
            
        client_subset = shuffled_reviews.iloc[start_idx:min(end_idx, num_total_reviews)]
        
        if client_subset.empty:
            print(f"Warning: Client {i} would receive an empty dataset (start_idx: {start_idx}). This might indicate all reviews are used.")
            # This case should be rare if actual_reviews_per_user > 0 and start_idx < num_total_reviews
            continue # Skip adding an empty dataset for a client if logic allows

        client_review_datasets.append(client_subset)
        start_idx = end_idx
            
    if not client_review_datasets or all(df.empty for df in client_review_datasets):
        print("CRITICAL: Failed to distribute any review data to clients. Exiting.")
        exit()
        
    print(f"Distributed review data to {len(client_review_datasets)} clients for simulation.")
    for i, df in enumerate(client_review_datasets):
        print(f"  Client {i} received {len(df)} reviews.")

    return client_review_datasets, restaurants_df

if __name__ == '__main__':
    print("Testing Yelp data loading and distribution (food_data_generator.py)...")
    
    # This standalone test relies on the config paths being correct
    # and the files existing.
    if not os.path.exists(PROCESSED_REVIEW_FILE) or not os.path.exists(PROCESSED_BUSINESS_FILE):
        print(f"Warning: One or both data files not found: "
              f"{PROCESSED_REVIEW_FILE}, {PROCESSED_BUSINESS_FILE}")
        print("Skipping standalone test of food_data_generator.py. "
              "Ensure files are present for the main simulation.")
    else:
        client_dfs, restaurant_df_global = get_yelp_data_for_simulation()

        if restaurant_df_global is not None and not restaurant_df_global.empty:
            print("\nSample of Global Restaurant Data:")
            print(restaurant_df_global.head())
            print(f"Total restaurants loaded: {len(restaurant_df_global)}")
            print(f"Restaurant columns: {restaurant_df_global.columns.tolist()}")

        if client_dfs:
            print("\nSample of Review Data for Client 0 (if available):")
            if client_dfs[0] is not None and not client_dfs[0].empty:
                print(client_dfs[0].head())
                print(f"Review columns for Client 0: {client_dfs[0].columns.tolist()}")
            else:
                print("Client 0 received an empty or no review dataset.")
        else:
            print("No client review datasets were generated in the test.")