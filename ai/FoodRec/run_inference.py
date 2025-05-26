# run_inference.py
import pandas as pd
import numpy as np
import torch
import os
import json
import joblib
import random # For generating sample user context

import federated_config as config
from food_model import FoodPreferenceModel
from food_data_generator import load_csv_to_dataframe # Use adapted loader
from food_client import process_features_for_recommendation

def infer_input_dim_from_model(state_dict):
    if 'fc1.weight' in state_dict: return state_dict['fc1.weight'].shape[1]
    print("Warning: Could not infer input_dim from model state_dict."); return -1

def main():
    print("--- Running Standalone Inference for Shanghai Data ---")

    all_restaurants_df = load_csv_to_dataframe(config.SHANGHAI_RESTAURANTS_FILE)
    if all_restaurants_df.empty: print("CRITICAL: No Shanghai restaurant data. Exiting."); return
    if 'id' in all_restaurants_df.columns: all_restaurants_df.rename(columns={'id': 'restaurant_id'}, inplace=True)
    if 'rating' in all_restaurants_df.columns: all_restaurants_df.rename(columns={'rating': 'rating_biz'}, inplace=True)
    print(f"Loaded {len(all_restaurants_df)} Shanghai restaurants.")

    if not os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        print(f"CRITICAL: Model {config.GLOBAL_MODEL_SAVE_PATH} not found. Train first. Exiting."); return
    try:
        model_state_dict = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
        print("Global model state_dict loaded.")
    except Exception as e: print(f"CRITICAL: Error loading model: {e}. Exiting."); return

    input_dim = config.INPUT_DIM
    if input_dim == -1: input_dim = infer_input_dim_from_model(model_state_dict)
    if input_dim <= 0: print(f"CRITICAL: Invalid INPUT_DIM ({input_dim}). Exiting."); return
    print(f"Using INPUT_DIM: {input_dim} for model.")
    config.INPUT_DIM = input_dim # Ensure config is updated if inferred

    try:
        inference_model = FoodPreferenceModel(input_dim=input_dim)
        inference_model.load_state_dict(model_state_dict)
        inference_model.eval()
        print("Global model weights loaded into inference instance.")
    except Exception as e: print(f"CRITICAL: Error initializing/loading model: {e}. Exiting."); return

    if not os.path.exists(config.PREPROCESSOR_SAVE_PATH):
        print(f"CRITICAL: Preprocessor {config.PREPROCESSOR_SAVE_PATH} not found. Train first. Exiting."); return
    try:
        preprocessor = joblib.load(config.PREPROCESSOR_SAVE_PATH)
        print("Loaded saved preprocessor.")
        # Optional: Test preprocessor output dim here if desired, like in food_client.py
    except Exception as e: print(f"CRITICAL: Error loading preprocessor: {e}. Exiting."); return

    # --- Define a Sample User Context for Inference ---
    # This MUST include all user-specific features from CATEGORY_COLS and NUMERIC_COLS
    user_context = {
        'gender': np.random.choice(config.GENDERS if config.GENDERS and config.GENDERS[0] is not None else ['男', '女']),
        'age': random.randint(25, 55),
        'hometown': np.random.choice([
    "北京", "上海", "广东广州", "广东深圳", "四川成都", "浙江杭州", "江苏南京",
    "湖北武汉", "陕西西安", "重庆", "天津", "山东青岛", "湖南长沙", "福建厦门",
    "辽宁大连", "河南郑州", "安徽合肥", "江西南昌", "山西太原", "云南昆明",
    "贵州贵阳", "甘肃兰州", "海南海口", "河北石家庄", "吉林长春", "黑龙江哈尔滨",
    "内蒙古呼和浩特", "宁夏银川", "青海西宁", "西藏拉萨", "新疆乌鲁木齐"
]),
        'occupation': random.choice([
    "软件工程师", "教师", "医生", "护士", "设计师", "市场营销", "销售", "公务员",
    "自由职业者", "学生", "退休", "建筑师", "律师", "会计", "研究员", "项目经理"
]),
        'education_level': random.choice(["高中及以下", "大专", "本科", "硕士", "博士"]),
        'marital_status': random.choice(["未婚", "已婚", "离异"]),
        'activity_level': np.random.choice(config.ACTIVITY_LEVELS if config.ACTIVITY_LEVELS and config.ACTIVITY_LEVELS[0] is not None else ["每周1-2次"]),
        'cooking_skills': np.random.choice(config.COOKING_SKILLS_LEVELS if config.COOKING_SKILLS_LEVELS and config.COOKING_SKILLS_LEVELS[0] is not None else ["家常菜水平"]),
        'diseases': random.choice(["高血糖", "高血压", "高血脂", "糖尿病", "痛风", "脂肪肝", "冠心病", "颈椎病", "胃病", "失眠", "None"]),
        'dietary_preferences': random.choice([
    "减脂", "增肌", "少油", "少盐", "清淡", "辛辣", "素食", "生酮饮食",
    "高蛋白", "低碳水", "地中海饮食", "无麸质", "高纤维", "抗炎饮食", "None"
]),
        'food_allergies': random.choice(["海鲜", "花生", "坚果", "乳制品", "鸡蛋", "大豆", "谷蛋白(小麦)", "芒果", "None"]),
        'height_cm': random.randint(155, 185),
        'weight_kg': round(random.uniform(50.0, 85.0), 1),
        'daily_food_budget_cny': random.randint(40, 180),
        'heart_rate_bpm': int(np.random.normal(72, 7)),
        'blood_sugar_mmol_L': round(np.random.uniform(4.2, 6.8), 1),
        'sleep_hours_last_night': round(np.random.uniform(6.0, 8.0), 1),
        'weather_temp_celsius': round(np.random.uniform(0, 1), 1),
        'weather_humidity_percent': round(np.random.uniform(45, 75), 1),
        'steps_today_before_meal': int(np.random.uniform(1500, 9000)),
        # 'was_hungry_before_meal': random.choice([True, False]) # If it's a feature
    }
    # Ensure all expected user-side columns are present
    all_user_side_features_expected = [
        col for col in config.CATEGORY_COLS + config.NUMERIC_COLS if col not in all_restaurants_df.columns
    ]
    for col in all_user_side_features_expected:
        if col not in user_context: # If any user-side feature defined in COLS is missing from context
            print(f"Warning (Inference Context): User feature '{col}' missing. Adding default placeholder.")
            # Add a very basic placeholder; ideally, context should be complete
            user_context[col] = "Unknown" if col in config.CATEGORY_COLS else 0.0
            
    print(f"\n--- User context: ----------------")
    
    print(json.dumps(user_context, ensure_ascii=False, indent=4))

    print(f"\n--- Making Top 10 Recommendation for User Context ---")
    # print(f"User Context: {user_context}") # Can be very verbose

    features_tensor, restaurant_ids_order, num_feat_proc = process_features_for_recommendation(
        preprocessor, user_context, all_restaurants_df
    )
    top_recs_df = pd.DataFrame()
    if features_tensor.nelement() == 0: print("No features processed for recommendation.")
    elif num_feat_proc != input_dim: print(f"FATAL: Feature mismatch! Model expects {input_dim}, Preproc: {num_feat_proc}.")
    else:
        inference_model.eval()
        with torch.no_grad():
            logits = inference_model(features_tensor); probs = torch.softmax(logits, dim=1)
            high_pref_scores = probs[:, 2]
            if high_pref_scores.numel() > 0:
                k = min(10, len(restaurant_ids_order))
                top_scores_t, top_indices_t = torch.topk(high_pref_scores, k=k)
                rec_ids = [restaurant_ids_order[i] for i in top_indices_t]
                top_recs_df = all_restaurants_df[all_restaurants_df['restaurant_id'].isin(rec_ids)].copy()
                id_score_map_inf = dict(zip(rec_ids, top_scores_t.tolist()))
                top_recs_df['recommendation_score'] = top_recs_df['restaurant_id'].map(id_score_map_inf)
                top_recs_df = top_recs_df.sort_values(by='recommendation_score', ascending=False).reset_index(drop=True)

    if not top_recs_df.empty:
        print("\n--- Top 10 Recommended Restaurants ---")
        for i, row in top_recs_df.iterrows():
            print(f"  {i+1}. {row.get('name','N/A')} (ID: {row.get('restaurant_id')}) "
                  f"Cuisine: {row.get('cuisine','N/A')} Score: {row.get('recommendation_score'):.4f}")
    else: print("\nNo recommendations could be made.")
    print("\n--- Inference Script Finished ---")

if __name__ == "__main__":
    main()