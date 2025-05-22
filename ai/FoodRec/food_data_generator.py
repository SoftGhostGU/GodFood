# food_data_generator.py
import pandas as pd
import numpy as np
from federated_config import NUM_USERS, REVIEWS_PER_USER, NUM_RESTAURANTS, CUISINE_TYPES, GENDERS, ORIGINS

def generate_restaurant_data(num_restaurants):
    restaurants = []
    for i in range(num_restaurants):
        restaurants.append({
            'restaurant_id': f'r_{i}',
            'cuisine_type': np.random.choice(CUISINE_TYPES),
            'avg_sweetness': np.random.uniform(0, 5),
            'avg_sourness': np.random.uniform(0, 5),
            'avg_spiciness': np.random.uniform(0, 5),
            'avg_saltiness': np.random.uniform(0, 5),
            'food_temperature_type': np.random.choice(['Hot', 'Cold', 'RoomTemp']),
            'restaurant_name': f'Restaurant {i}'
        })
    return pd.DataFrame(restaurants)

def generate_review_data_for_user(user_id, num_reviews, restaurant_ids):
    reviews = []
    for i in range(num_reviews):
        reviews.append({
            'user_id': f'u_{user_id}',
            'gender': np.random.choice(GENDERS),
            'origin': np.random.choice(ORIGINS),
            'body_temperature': np.random.normal(37.0, 0.5),
            'last_night_sleep_duration': np.random.uniform(4, 10),
            'heart_rate': np.random.normal(70, 10),
            'weather_temperature': np.random.uniform(-5, 35),
            'weather_humidity': np.random.uniform(20, 90),
            'restaurant_id': np.random.choice(restaurant_ids),
            'rating': np.random.randint(1, 6) # 1 to 5 stars
        })
    return pd.DataFrame(reviews)

def get_all_data():
    restaurants_df = generate_restaurant_data(NUM_RESTAURANTS)
    all_reviews = []
    for i in range(NUM_USERS):
        user_reviews_df = generate_review_data_for_user(i, REVIEWS_PER_USER, restaurants_df['restaurant_id'].tolist())
        all_reviews.append(user_reviews_df)
    
    reviews_df = pd.concat(all_reviews, ignore_index=True)
    return reviews_df, restaurants_df

if __name__ == '__main__':
    reviews, restaurants = get_all_data()
    print("Sample Reviews:")
    print(reviews.head())
    print("\nSample Restaurants:")
    print(restaurants.head())
    print(f"\nTotal reviews: {len(reviews)}, Total restaurants: {len(restaurants)}")