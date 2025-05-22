# # federated_config.py
# import os

# # Data Source Paths (NEW)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of the current file
# PROCESSED_BUSINESS_FILE = os.path.join(BASE_DIR, "dataset/yelp_business_split_1/yelp_business_with_food_attrs_1_1.json")
# PROCESSED_REVIEW_FILE = os.path.join(BASE_DIR, "dataset/yelp_business_split_1/yelp_review_processed_1_1.json") # Or your split file if testing small scale

# # Data Distribution for Simulation
# NUM_USERS = 3 # Number of clients to simulate
# REVIEWS_PER_USER = 1000 # Number of reviews for each client

# # Define these based on your actual data or preprocessing steps
# CUISINE_TYPES = ['Italian', 'Chinese', 'Mexican', 'Indian', 'FastFood',
#                  'Japanese', 'Thai', 'Mediterranean', 'French', 'American', 'Other']
# GENDERS = ['Male', 'Female']
# ORIGINS = ['North', 'South', 'East', 'West', 'Central', 'International', 'Local']
# FOOD_TEMPERATURE_TYPES = ['Hot', 'Cold', 'RoomTemp']


# # Model
# INPUT_DIM = -1 # Will be set after feature processing
# HIDDEN_DIM = 64
# OUTPUT_DIM = 3  # 3 rating classes (e.g., low, medium, high)

# # Training
# LOCAL_EPOCHS = 3
# LEARNING_RATE = 0.01
# BATCH_SIZE = 32

# # Federated Learning
# NUM_ROUNDS = 5

# # LDP (Local Differential Privacy)
# EPSILON = 1.0
# DELTA = 1e-5
# SENSITIVITY = 1.0 # Assumed sensitivity

# # Server
# SERVER_HOST = '127.0.0.1'
# SERVER_PORT = 5000
# GLOBAL_MODEL_SAVE_PATH = os.path.join(BASE_DIR, "global_yelp_food_model.pth")


# federated_config.py
import os

# Data Source Paths (NEW)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of the current file
PROCESSED_BUSINESS_FILE = os.path.join(BASE_DIR, "dataset/yelp_business_split_1/yelp_business_with_food_attrs_1_1.json")
PROCESSED_REVIEW_FILE = os.path.join(BASE_DIR, "dataset/yelp_business_split_1/yelp_review_processed_1_1.json")

# Data Distribution for Simulation
NUM_USERS = 3 # Number of clients to simulate
REVIEWS_PER_USER = 1000 # Number of reviews for each client

# Define these based on your actual data or preprocessing steps
CUISINE_TYPES = ['Italian', 'Chinese', 'Mexican', 'Indian', 'FastFood',
                 'Japanese', 'Thai', 'Mediterranean', 'French', 'American', 'Other']
GENDERS = ['Male', 'Female', 'Other', 'PreferNotToSay']
ORIGINS = ['North', 'South', 'East', 'West', 'Central', 'International', 'Local']
FOOD_TEMPERATURE_TYPES = ['Hot', 'Cold', 'RoomTemp']


# Model
INPUT_DIM = -1 # Will be set after feature processing
HIDDEN_DIM = 64
OUTPUT_DIM = 3  # 3 rating classes (e.g., low, medium, high)

# Training
LOCAL_EPOCHS = 3
LEARNING_RATE = 0.01
BATCH_SIZE = 32

# Federated Learning
NUM_ROUNDS = 5

# LDP (Local Differential Privacy)
EPSILON = 1.0
DELTA = 1e-5
SENSITIVITY = 1.0 # Assumed sensitivity

# Server
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
GLOBAL_MODEL_SAVE_PATH = os.path.join(BASE_DIR, "global_yelp_food_model.pth")