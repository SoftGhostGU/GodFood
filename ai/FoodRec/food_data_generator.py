# food_data_generator.py (adapted for Shanghai data)
import pandas as pd
import os
import glob
import federated_config as config # Import to modify config.NUM_USERS

def load_csv_to_dataframe(file_path, required_cols=None):
    if not os.path.exists(file_path):
        print(f"ERROR: Data file not found: {file_path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        if required_cols:
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"ERROR: File {file_path} missing required cols: {missing_cols}. Found: {df.columns.tolist()}")
                return pd.DataFrame()
        return df
    except Exception as e:
        print(f"ERROR: Could not read CSV {file_path}. Error: {e}")
        return pd.DataFrame()

def get_shanghai_data_for_simulation():
    print(f"Loading Shanghai restaurant data from: {config.SHANGHAI_RESTAURANTS_FILE}")
    restaurants_df = load_csv_to_dataframe(config.SHANGHAI_RESTAURANTS_FILE,
                                           required_cols=['id', 'name', 'cuisine', 'rating', 'cost']) # Add other essentials
    if restaurants_df.empty:
        print("CRITICAL: Shanghai restaurant data failed to load. Exiting.")
        exit()

    if 'id' in restaurants_df.columns and 'restaurant_id' not in restaurants_df.columns:
        restaurants_df.rename(columns={'id': 'restaurant_id'}, inplace=True)
    elif 'restaurant_id' not in restaurants_df.columns:
        print("CRITICAL: 'restaurant_id' (or 'id') not in restaurant data. Exiting.")
        exit()
    # Rename restaurant 'rating' to 'rating_biz' for consistency in client
    if 'rating' in restaurants_df.columns and 'rating_biz' not in restaurants_df.columns:
        restaurants_df.rename(columns={'rating': 'rating_biz'}, inplace=True)


    print(f"Searching for user review files in: {config.USER_REVIEWS_DIR}")
    user_review_files = glob.glob(os.path.join(config.USER_REVIEWS_DIR, "*_reviews.csv"))

    if not user_review_files:
        print(f"CRITICAL: No user review files found in {config.USER_REVIEWS_DIR}. Exiting.")
        exit()

    config.NUM_USERS = len(user_review_files) # Update global config
    print(f"Found {config.NUM_USERS} user review files. config.NUM_USERS set.")

    client_review_datasets = []
    required_review_cols = ['user_id', 'restaurant_id', 'user_rating',
                            # --- ADD ALL STABLE USER PROFILE COLS EXPECTED BY THE CLIENT ---
                            'gender', 'age', 'hometown', 'occupation', 'education_level',
                            'marital_status', 'activity_level', 'cooking_skills',
                            'height_cm', 'weight_kg', 'daily_food_budget_cny',
                            'diseases', 'dietary_preferences', 'food_allergies',
                            # --- ADD ALL CONTEXTUAL REVIEW COLS EXPECTED ---
                            'heart_rate_bpm', 'blood_sugar_mmol_L', # 'blood_pressure_mmHg' if preprocessed
                            'sleep_hours_last_night', 'weather_temp_celsius',
                            'weather_humidity_percent', 'steps_today_before_meal'
                           ]

    for review_file_path in user_review_files:
        # print(f"  Loading reviews from: {os.path.basename(review_file_path)}")
        review_df = load_csv_to_dataframe(review_file_path, required_cols=required_review_cols)
        if not review_df.empty:
            client_review_datasets.append(review_df)
        else:
            print(f"    Warning: Review file {os.path.basename(review_file_path)} empty or failed. Skipping.")

    # Filter out clients who ended up with no data and update NUM_USERS again if needed
    client_review_datasets = [df for df in client_review_datasets if not df.empty]
    if len(client_review_datasets) < config.NUM_USERS:
        print(f"Warning: After loading, only {len(client_review_datasets)} clients have review data. Updating config.NUM_USERS.")
        config.NUM_USERS = len(client_review_datasets)

    if config.NUM_USERS == 0:
        print("CRITICAL: No clients have data after final check. Exiting.")
        exit()

    print(f"Prepared review data for {config.NUM_USERS} clients.")
    return client_review_datasets, restaurants_df

if __name__ == '__main__':
    # ... (standalone test code - can be kept or removed) ...
    print("Testing Shanghai data loading (food_data_generator.py)...")
    client_dfs, restaurant_df_global = get_shanghai_data_for_simulation()
    if restaurant_df_global is not None and not restaurant_df_global.empty:
        print("\nSample of Global Shanghai Restaurant Data:")
        print(restaurant_df_global.head())
    if client_dfs:
        print(f"\nSample of Review Data for Client 0 (Total clients: {len(client_dfs)}):")
        if client_dfs[0] is not None and not client_dfs[0].empty:
            print(client_dfs[0].head())