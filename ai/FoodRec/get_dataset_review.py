import csv
import random
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 全局配置 ---
NUM_REVIEWS_PER_USER = 100 # 测试时可以设为100，实际生成数据时设为1000
OUTPUT_DIR = "user_reviews"
USER_DATASET_FILE = "user_dataset_enhanced.csv"
RESTAURANT_DATASET_FILE = "shanghai_restaurants.csv"

# --- 辅助函数 ---
def generate_random_datetime(start_date_str="2023-01-01", end_date_str="2023-12-31"): # 更新了日期范围示例
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates < 0: # Ensure end_date is after start_date
        days_between_dates = 0
    random_number_of_days = random.randrange(days_between_dates + 1) # +1 to include end_date possibility
    random_date = start_date + timedelta(days=random_number_of_days)
    random_hour = random.randint(10, 22)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)

def get_cuisine_from_hometown(hometown_str):
    if not isinstance(hometown_str, str): return None
    hometown_str_lower = hometown_str.lower()
    if "上海" in hometown_str_lower: return "上海本帮菜"
    if "广东" in hometown_str_lower or "广州" in hometown_str_lower or "深圳" in hometown_str_lower: return "粤菜"
    if "四川" in hometown_str_lower or "成都" in hometown_str_lower or "重庆" in hometown_str_lower: return "川菜"
    if "湖南" in hometown_str_lower or "长沙" in hometown_str_lower: return "湘菜"
    if "北京" in hometown_str_lower: return "北京菜"
    if "山东" in hometown_str_lower or "青岛" in hometown_str_lower: return "鲁菜"
    if "江苏" in hometown_str_lower or "南京" in hometown_str_lower or "苏州" in hometown_str_lower : return "苏菜"
    if "浙江" in hometown_str_lower or "杭州" in hometown_str_lower: return "浙菜"
    if "福建" in hometown_str_lower or "厦门" in hometown_str_lower: return "闽菜"
    if "安徽" in hometown_str_lower or "合肥" in hometown_str_lower: return "徽菜"
    if "东北" in hometown_str_lower or "辽宁" in hometown_str_lower or "吉林" in hometown_str_lower or "黑龙江" in hometown_str_lower or \
       "大连" in hometown_str_lower or "长春" in hometown_str_lower or "哈尔滨" in hometown_str_lower:
        return "东北菜"
    if "西北" in hometown_str_lower or "陕西" in hometown_str_lower or "西安" in hometown_str_lower or \
       "甘肃" in hometown_str_lower or "兰州" in hometown_str_lower or "宁夏" in hometown_str_lower or \
       "银川" in hometown_str_lower or "青海" in hometown_str_lower or "西宁" in hometown_str_lower or \
       "新疆" in hometown_str_lower or "乌鲁木齐" in hometown_str_lower:
        return random.choice(["西北菜", "清真菜"]) # 清真菜是西北常见菜系
    if "云南" in hometown_str_lower or "昆明" in hometown_str_lower: return "云南菜"
    if "贵州" in hometown_str_lower or "贵阳" in hometown_str_lower: return "贵州菜"
    if "湖北" in hometown_str_lower or "武汉" in hometown_str_lower: return "湖北菜"
    if "河南" in hometown_str_lower or "郑州" in hometown_str_lower: return "豫菜"
    if "江西" in hometown_str_lower or "nanchang" in hometown_str_lower: return "赣菜"
    if "山西" in hometown_str_lower or "太原" in hometown_str_lower: return "晋菜"
    if "河北" in hometown_str_lower or "石家庄" in hometown_str_lower: return "冀菜"
    if "天津" in hometown_str_lower: return "津菜"
    if "内蒙古" in hometown_str_lower or "呼和浩特" in hometown_str_lower: return random.choice(["蒙餐", "烧烤", "火锅"])
    if "西藏" in hometown_str_lower or "拉萨" in hometown_str_lower: return "藏餐"
    if "海南" in hometown_str_lower or "海口" in hometown_str_lower: return random.choice(["海南菜", "海鲜"])
    return random.choice(["家常菜", "快餐简餐", None, None]) # 增加None的概率

def simulate_review_context_dynamic(user_stable_profile):
    heart_rate = random.randint(60, 100)
    if "高血压" in str(user_stable_profile.get("diseases", "")) or "冠心病" in str(user_stable_profile.get("diseases", "")):
        heart_rate = random.randint(75, 115)
    blood_sugar = round(random.uniform(4.5, 9.0), 1)
    if "糖尿病" in str(user_stable_profile.get("diseases", "")) or "高血糖" in str(user_stable_profile.get("diseases", "")):
        blood_sugar = round(random.uniform(7.0, 16.0), 1)
    systolic_bp = random.randint(100, 135); diastolic_bp = random.randint(65, 85)
    if "高血压" in str(user_stable_profile.get("diseases", "")):
        systolic_bp = random.randint(130, 170); diastolic_bp = random.randint(80, 105)
    blood_pressure_val = f"{systolic_bp}/{diastolic_bp}"
    sleep_hours = round(random.uniform(6.0, 8.5), 1)
    if "失眠" in str(user_stable_profile.get("diseases", "")): sleep_hours = round(random.uniform(4.0, 7.0), 1)
    temperature_celsius = random.randint(0, 38) # 上海的温度范围可以更广一些
    humidity_percent = random.randint(30, 95)   # 上海的湿度范围也可以更广
    steps_today = random.randint(1500, 18000)
    if str(user_stable_profile.get("activity_level", "")).strip() == "几乎不运动":
        steps_today = random.randint(500, 5000)
    is_hungry = random.choice([True, False, None]) # Adding None as an option

    return {
        "review_datetime": generate_random_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        "heart_rate_bpm": heart_rate,
        "blood_sugar_mmol_L": blood_sugar,
        "blood_pressure_mmHg": blood_pressure_val,
        "sleep_hours_last_night": sleep_hours,
        "weather_temp_celsius": temperature_celsius,
        "weather_humidity_percent": humidity_percent,
        "steps_today_before_meal": steps_today,
        "was_hungry_before_meal": is_hungry
    }

def generate_review_text_placeholder(user_profile, restaurant, rating):
    r_cuisine = restaurant.get('cuisine', '餐厅')
    r_name = restaurant.get('name', '这家店')
    if rating >= 4.5: return f"强烈推荐{r_name}！这家{r_cuisine}味道正宗，服务周到，环境也很棒，下次一定还来！"
    elif rating >= 4.0: return f"{r_name}的{r_cuisine}做得相当不错，整体体验很好，值得一试。"
    elif rating >= 3.0: return f"这家{r_cuisine}餐厅{r_name}还可以，口味和服务都还行，属于不会出错的选择。"
    elif rating >= 2.0: return f"对{r_name}的印象一般，{r_cuisine}的口味或者服务方面有提升空间。"
    else: return f"不太推荐{r_name}，这次的{r_cuisine}体验不佳，希望店家能改进。"

def calculate_restaurant_suitability_score(user_stable_profile, restaurant_info):
    score = 50
    user_diseases = str(user_stable_profile.get("diseases", "none")).lower()
    user_allergies = str(user_stable_profile.get("food_allergies", "none")).lower()
    user_preferences = str(user_stable_profile.get("dietary_preferences", "none")).lower()
    user_fitness_goals = str(user_stable_profile.get("fitness_goals", "none")).lower()
    user_hometown_val = user_stable_profile.get("hometown", "") # Get hometown string
    user_hometown_cuisine = get_cuisine_from_hometown(user_hometown_val) # Pass string

    r_cuisine = str(restaurant_info.get("cuisine", "")).lower()
    r_tags = str(restaurant_info.get("tag", "")).lower()

    if user_hometown_cuisine and user_hometown_cuisine.lower() in r_cuisine: score += random.randint(20, 35)
    if ("糖尿病" in user_diseases or "高血糖" in user_diseases) and \
       ("甜" in r_tags or "饮品" in r_cuisine or "面包" in r_cuisine or "蛋糕" in r_cuisine ): score -= random.randint(65, 85) #更强的负面
    if ("高血压" in user_diseases or "高血脂" in user_diseases) and \
       ("油炸" in r_tags or "肥" in r_tags or "咸" in r_tags or "重口味" in r_cuisine or ("川菜" in r_cuisine and "清淡" not in user_preferences)): score -= random.randint(35, 55)
    if "痛风" in user_diseases and ("海鲜" in r_cuisine or "啤酒" in r_tags or "动物内脏" in r_tags or "火锅" in r_cuisine): score -= random.randint(55, 75)
    if "胃病" in user_diseases and ("辛辣" in r_cuisine or "刺激" in r_tags or "油腻" in r_cuisine or "生冷" in r_tags): score -= random.randint(30,50)

    if "none" not in user_allergies:
        if "海鲜" in user_allergies and ("海鲜" in r_cuisine or "鱼" in r_tags or "虾" in r_tags or "蟹" in r_tags): score -= 150 #绝对避免
        if "花生" in user_allergies and ("花生" in r_tags or "坚果" in r_tags): score -= 150
        if "乳制品" in user_allergies and ("奶" in r_tags or "芝士" in r_tags or "奶油" in r_tags): score -= 120
        if "谷蛋白(小麦)" in user_allergies and ("面" in r_tags or "面包" in r_cuisine or "披萨" in r_cuisine or "饺" in r_tags): score -= 120

    if ("减脂" in user_preferences or "减重" in user_fitness_goals):
        if ("沙拉" in r_cuisine or "轻食" in r_cuisine or "健康" in r_tags or "低卡" in r_tags or "蒸" in r_tags): score += random.randint(25,40)
        elif ("油炸" in r_tags or "甜点" in r_cuisine or "高热量" in r_tags or "奶油" in r_tags): score -= random.randint(20,35)
    if ("增肌" in user_preferences or "高蛋白" in user_preferences or "增肌" in user_fitness_goals):
        if ("牛肉" in r_tags or "鸡胸" in r_tags or "鱼" in r_tags or "健身餐" in r_cuisine or "蛋" in r_tags): score += random.randint(25,40)
    if "清淡" in user_preferences:
        if ("清淡" in r_cuisine or "蒸" in r_tags or "粥" in r_cuisine or "粤菜" in r_cuisine): score += random.randint(20,35)
        elif ("辛辣" in r_cuisine or "重口味" in r_tags or "油腻" in r_cuisine): score -= random.randint(15,30)
    if "辛辣" in user_preferences:
        if ("川菜" in r_cuisine or "湘菜" in r_cuisine or "辣" in r_tags or "火锅" in r_cuisine): score += random.randint(20,35)
        elif ("清淡" in r_cuisine or "粤菜" in r_cuisine): score -= random.randint(10,20) #喜欢辣的可能觉得清淡的不过瘾
    if "素食" in user_preferences and ("素食" in r_cuisine or "斋" in r_tags or "蔬菜" in r_tags) : score += random.randint(30,50)
    elif "素食" in user_preferences and ("肉" in r_tags or "海鲜" in r_cuisine or "牛" in r_tags or "鸡" in r_tags or "猪" in r_tags): score -= random.randint(60, 90)

    return max(1, int(score))

def select_restaurant_based_on_suitability(user_stable_profile, restaurants_df):
    if restaurants_df.empty: return None
    suitability_scores = restaurants_df.apply(
        lambda r_row: calculate_restaurant_suitability_score(user_stable_profile, r_row.to_dict()), axis=1
    )
    # Add a small constant to all scores to handle cases where all calculated scores are 0 or very low
    # This ensures that sample can still pick even if all suitability is low (but picks randomly then)
    suitability_scores = suitability_scores + 1e-6

    if suitability_scores.sum() == 0:
        return restaurants_df.sample(1).iloc[0].to_dict()
    try:
        # Normalize scores to be probabilities for sampling if they are not already
        # If any score is negative after calculation (though max(1,...) should prevent this), handle it.
        if (suitability_scores < 0).any(): # Should not happen due to max(1, int(score))
            suitability_scores = suitability_scores.clip(lower=1e-6) # Clip negative to small positive
        
        # Check again if sum is zero after potential clipping (highly unlikely now)
        if suitability_scores.sum() == 0:
             return restaurants_df.sample(1).iloc[0].to_dict()

        return restaurants_df.sample(1, weights=suitability_scores).iloc[0].to_dict()
    except ValueError as e: # Handles cases like all weights are zero
        # print(f"Debug: ValueError in sample: {e}. Scores sum: {suitability_scores.sum()}. Scores sample: {suitability_scores.head().tolist()}")
        return restaurants_df.sample(1).iloc[0].to_dict()
    except Exception as e_gen:
        print(f"General error in select_restaurant_based_on_suitability: {e_gen}")
        return restaurants_df.sample(1).iloc[0].to_dict()


def generate_rating_for_user(user_stable_profile, restaurant_info, base_restaurant_rating_str, dynamic_context_dict):
    try: base_rating = float(base_restaurant_rating_str)
    except (ValueError, TypeError): base_rating = random.uniform(2.8, 3.8) # More realistic default

    rating_modifier = 0
    user_diseases = str(user_stable_profile.get("diseases", "none")).lower()
    user_allergies = str(user_stable_profile.get("food_allergies", "none")).lower()
    user_preferences = str(user_stable_profile.get("dietary_preferences", "none")).lower()
    r_cuisine = str(restaurant_info.get("cuisine", "")).lower()
    r_tags = str(restaurant_info.get("tag", "")).lower()

    if ("糖尿病" in user_diseases or "高血糖" in user_diseases) and ("甜" in r_tags or "饮品" in r_cuisine or "蛋糕" in r_tags): rating_modifier -= random.uniform(1.2, 2.8)
    if ("海鲜" in user_allergies) and ("海鲜" in r_cuisine or "鱼" in r_tags or "虾" in r_tags): return round(random.uniform(0.5, 1.8), 1) # Immediate low score
    if ("花生" in user_allergies) and ("花生" in r_tags or "坚果" in r_tags): return round(random.uniform(0.5, 1.8), 1)

    if "清淡" in user_preferences:
        if ("清淡" in r_cuisine or "蒸" in r_tags or "粤菜" in r_cuisine): rating_modifier += random.uniform(0.3, 0.9)
        elif ("辛辣" in r_cuisine or "油腻" in r_tags or "重口味" in r_cuisine): rating_modifier -= random.uniform(0.4, 1.5)
    if "辛辣" in user_preferences:
        if ("川菜" in r_cuisine or "湘菜" in r_cuisine or "辣" in r_tags): rating_modifier += random.uniform(0.3,0.9)
        elif ("清淡" in r_cuisine and "粤菜" in r_cuisine): rating_modifier -= random.uniform(0.2,0.6)

    temp = dynamic_context_dict.get("weather_temp_celsius", 22)
    if temp > 32: # Hot
        rating_modifier -= random.uniform(0.1, 0.3)
        if "火锅" in r_cuisine or "烧烤" in r_cuisine or "辛辣" in r_cuisine : rating_modifier -= random.uniform(0.2, 0.5)
        elif "冷饮" in r_tags or "凉菜" in r_tags or "冰" in r_tags : rating_modifier += random.uniform(0.1, 0.4)
    elif temp < 8: # Cold
        rating_modifier -= random.uniform(0.1, 0.3)
        if "冷饮" in r_tags or "凉菜" in r_tags : rating_modifier -= random.uniform(0.2, 0.5)
        elif "火锅" in r_cuisine or "热汤" in r_tags or "炖菜" in r_cuisine : rating_modifier += random.uniform(0.2, 0.6)

    pickiness_factor = random.uniform(-0.6, 0.6) # Increased range for more variance
    rating_modifier += pickiness_factor
    
    final_rating = base_rating + rating_modifier
    return round(max(0.5, min(5.0, final_rating)), 1)

# --- 主逻辑 ---
def main():
    print("开始生成用户评价数据 (包含稳定用户画像特征)...")
    try:
        user_profiles_df = pd.read_csv(USER_DATASET_FILE)
        restaurants_df_orig = pd.read_csv(RESTAURANT_DATASET_FILE)
    except FileNotFoundError as e: print(f"错误: 数据文件未找到: {e}"); return
    except Exception as e: print(f"加载CSV时出错: {e}"); return

    if 'id' not in user_profiles_df.columns: print(f"错误: 用户画像文件 {USER_DATASET_FILE} 缺少 'id' 列。"); return
    if 'id' not in restaurants_df_orig.columns: print(f"错误: 餐厅文件 {RESTAURANT_DATASET_FILE} 缺少 'id' 列。"); return

    restaurants_df = restaurants_df_orig.copy() # Work with a copy
    restaurants_df.rename(columns={'id': 'restaurant_id'}, inplace=True)
    restaurants_df['cost'] = pd.to_numeric(restaurants_df['cost'], errors='coerce').fillna(restaurants_df['cost'].median())

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR); print(f"已创建输出目录: {OUTPUT_DIR}")

    total_users_to_process = len(user_profiles_df)
    print(f"共找到 {total_users_to_process} 个用户画像, {len(restaurants_df)} 家餐厅。")

    for index, user_profile_row in user_profiles_df.iterrows():
        user_id_from_profile = user_profile_row["id"] # This is the correct user_id
        user_stable_profile_dict = user_profile_row.to_dict()

        print(f"\n--- 用户 {index + 1}/{total_users_to_process} (ID: {user_id_from_profile}) 生成 {NUM_REVIEWS_PER_USER} 条评价 ---")
        user_reviews_list = []
        output_filename = os.path.join(OUTPUT_DIR, f"{user_id_from_profile}_reviews.csv")

        for i in range(NUM_REVIEWS_PER_USER):
            if (i + 1) % (NUM_REVIEWS_PER_USER // 5 or 1) == 0: # Print progress more frequently
                 print(f"  生成评价 {i + 1}/{NUM_REVIEWS_PER_USER} for user {user_id_from_profile}...")

            selected_restaurant_dict = select_restaurant_based_on_suitability(user_stable_profile_dict, restaurants_df)
            if selected_restaurant_dict is None: continue

            restaurant_id_val = selected_restaurant_dict["restaurant_id"]
            dynamic_context_dict = simulate_review_context_dynamic(user_stable_profile_dict)
            base_r_rating_val = selected_restaurant_dict.get("rating")
            user_rating_val = generate_rating_for_user(
                user_stable_profile_dict, selected_restaurant_dict, base_r_rating_val, dynamic_context_dict
            )
            # review_text_val = generate_review_text_placeholder(user_stable_profile_dict, selected_restaurant_dict, user_rating_val)

            single_review_data = {}
            single_review_data.update(user_stable_profile_dict)
            single_review_data.update(dynamic_context_dict)
            
            # Ensure 'user_id' is correct and 'id' from profile is used as 'user_id'
            single_review_data['user_id'] = user_id_from_profile # Explicitly set from the loop's user_id
            if 'id' in single_review_data and single_review_data['id'] == user_id_from_profile :
                pass # 'id' from user_stable_profile_dict is already the user_id
            elif 'id' in single_review_data: # If 'id' somehow got a different value, remove it to avoid confusion
                del single_review_data['id']


            single_review_data['restaurant_id'] = restaurant_id_val
            single_review_data['restaurant_name'] = selected_restaurant_dict.get("name", "N/A")
            single_review_data['user_rating'] = user_rating_val
            # single_review_data['review_text_placeholder'] = review_text_val
            
            user_reviews_list.append(single_review_data)

        if user_reviews_list:
            reviews_output_df = pd.DataFrame(user_reviews_list)
            try:
                reviews_output_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
                print(f"  成功为用户 {user_id_from_profile} 生成评价数据到: {output_filename}")
            except IOError as e_io:
                print(f"  错误: 无法写入文件 {output_filename} for user {user_id_from_profile}: {e_io}")
        else:
            print(f"  用户 {user_id_from_profile} 没有生成任何评价。")

    print("\n所有用户评价数据生成完毕！")

if __name__ == "__main__":
    main()