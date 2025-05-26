# federated_config.py
import os

# --- Data Source Paths for Shanghai Data ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHANGHAI_RESTAURANTS_FILE = os.path.join(BASE_DIR, "shanghai_restaurants.csv")
USER_REVIEWS_DIR = os.path.join(BASE_DIR, "user_reviews")
USER_ENHANCED_DATASET_FILE = os.path.join(BASE_DIR, "user_dataset_enhanced.csv")

# --- Data Distribution & Simulation ---
NUM_USERS = 100

# --- Feature Definitions (CRITICAL: DEFINE THESE ACCURATELY) ---
# These lists are now the single source of truth for feature columns.
CATEGORY_COLS = [
    # User Stable Profile Features (expected in each review row after data prep)
    'gender', 'hometown', 'occupation', 'education_level', 'marital_status',
    'activity_level', 'cooking_skills', 'diseases', 'dietary_preferences', 'food_allergies',
    # Restaurant Features (from shanghai_restaurants.csv)
    'cuisine',  # e.g., '粤菜', '川菜'
    'type',     # Restaurant type from shanghai_restaurants
    'adname',   # District name from shanghai_restaurants
    'pname',    # Province/City part (e.g., "上海市") from shanghai_restaurants
    'business_area', # e.g., "淮海路" from shanghai_restaurants
    # 'was_hungry_before_meal', # If you have this and it's categorical (e.g., True/False mapped to strings or kept as bool then handled)
]

NUMERIC_COLS = [
    # User Stable Profile Features
    'age', 'height_cm', 'weight_kg', 'daily_food_budget_cny',
    # User Contextual Review Data Features (from [user_id]_reviews.csv)
    'heart_rate_bpm', 'blood_sugar_mmol_L', 'sleep_hours_last_night',
    'weather_temp_celsius', 'weather_humidity_percent', 'steps_today_before_meal',
    # Restaurant Features (from shanghai_restaurants.csv)
    'cost',         # Restaurant's average cost
    'rating_biz',   # Restaurant's original average rating (ensure this column name exists after loading/renaming)
    # 'latitude', 'longitude', # If you decide to use them, ensure they are split from 'location'
]
# Note: 'blood_pressure_mmHg' would need preprocessing (e.g., split into systolic/diastolic)
# and then those two new columns added to NUMERIC_COLS.

# --- Category Value Lists (for OneHotEncoder if you want explicit categories, or for data validation/generation) ---
CUISINE_TYPES = ["粤菜", "川菜", "湘菜", "鲁菜", "苏菜", "浙菜", "闽菜", "徽菜",
    "上海本帮菜", "北京菜", "东北菜", "西北菜", "云南菜", "贵州菜",
    "日本料理", "韩国料理", "泰国菜", "越南菜", "印度菜", "西餐",
    "意大利菜", "法国菜", "墨西哥菜", "地中海菜", "土耳其菜",
    "火锅", "烧烤", "海鲜", "素食", "清真", "茶餐厅", "快餐简餐",
    "面包甜点", "咖啡厅", "酒吧", "小吃夜宵"]
GENDERS = ['男', '女']
ORIGINS = ['北京', '上海', '广东', '四川', '浙江', '江苏', '湖南', '湖北', '山东', '东北地区', '其他地区'] # Simplified
ACTIVITY_LEVELS = ["几乎不运动", "每周1-2次", "每周3-5次", "几乎每天"]
COOKING_SKILLS_LEVELS = ["厨房新手", "偶尔下厨", "家常菜水平", "烹饪达人"]
# ... other lists like OCCUPATIONS, EDUCATION_LEVELS etc. can also be here if needed for generation/validation


# --- Model ---
INPUT_DIM = -1
HIDDEN_DIM = 128
OUTPUT_DIM = 3

# --- Training ---
LOCAL_EPOCHS = 3
LEARNING_RATE = 0.005
BATCH_SIZE = 32

# --- Federated Learning ---
NUM_ROUNDS = 10

# --- LDP (Local Differential Privacy) ---
EPSILON = 1.0
DELTA = 1e-5
SENSITIVITY = 1.0

# --- Server ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001
GLOBAL_MODEL_SAVE_PATH = os.path.join(BASE_DIR, "global_shanghai_food_model.pth")
PREPROCESSOR_SAVE_PATH = os.path.join(BASE_DIR, "global_shanghai_preprocessor.joblib")