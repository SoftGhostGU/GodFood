# federated_config.py
import os

# Data Generation
NUM_USERS = 3
REVIEWS_PER_USER = 100
NUM_RESTAURANTS = 20
CUISINE_TYPES = ['Italian', 'Chinese', 'Mexican', 'Indian', 'FastFood']
GENDERS = ['Male', 'Female', 'Other']
ORIGINS = ['North', 'South', 'East', 'West', 'Central'] # Example origins

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
EPSILON = 1.0  # Privacy budget
DELTA = 1e-5   # Relaxation parameter
SENSITIVITY = 1.0 # Assumed sensitivity for model parameter updates (this is a simplification)

# Server
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
GLOBAL_MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "global_food_model.pth") # Save in the same directory