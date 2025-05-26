import csv
import random
import string
from faker import Faker # 需要安装: pip install Faker

# 初始化 Faker 以生成中文名
fake = Faker('zh_CN')

# 定义可能的选项
genders = ["男", "女"]
hometowns = [
    "北京", "上海", "广东广州", "广东深圳", "四川成都", "浙江杭州", "江苏南京",
    "湖北武汉", "陕西西安", "重庆", "天津", "山东青岛", "湖南长沙", "福建厦门",
    "辽宁大连", "河南郑州", "安徽合肥", "江西南昌", "山西太原", "云南昆明",
    "贵州贵阳", "甘肃兰州", "海南海口", "河北石家庄", "吉林长春", "黑龙江哈尔滨",
    "内蒙古呼和浩特", "宁夏银川", "青海西宁", "西藏拉萨", "新疆乌鲁木齐"
]
possible_diseases = ["高血糖", "高血压", "高血脂", "糖尿病", "痛风", "脂肪肝", "冠心病", "颈椎病", "胃病", "失眠"]
possible_dietary_preferences = [
    "减脂", "增肌", "少油", "少盐", "清淡", "辛辣", "素食", "生酮饮食",
    "高蛋白", "低碳水", "地中海饮食", "无麸质", "高纤维", "抗炎饮食"
]
occupations = [
    "软件工程师", "教师", "医生", "护士", "设计师", "市场营销", "销售", "公务员",
    "自由职业者", "学生", "退休", "建筑师", "律师", "会计", "研究员", "项目经理"
]
education_levels = ["高中及以下", "大专", "本科", "硕士", "博士"]
marital_statuses = ["未婚", "已婚", "离异", "丧偶"]
hobbies_list = [
    "阅读", "电影", "音乐", "旅游", "运动", "烹饪", "园艺", "摄影", "绘画", "写作",
    "舞蹈", "瑜伽", "冥想", "编程", "游戏", "手工", "登山", "钓鱼", "乐器"
]
activity_levels = ["几乎不运动", "每周1-2次", "每周3-5次", "几乎每天"]
fitness_goals_list = ["减重", "增肌", "保持健康", "提高耐力", "塑形", "无特定目标"]
food_allergies_list = ["海鲜", "花生", "坚果", "乳制品", "鸡蛋", "大豆", "谷蛋白(小麦)", "芒果"]
cooking_skills_levels = ["厨房新手", "偶尔下厨", "家常菜水平", "烹饪达人"]


def generate_random_id(length=10):
    """生成指定长度的随机字母数字ID"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_user_data():
    """生成单个用户的随机数据"""
    user_id = generate_random_id()
    gender = random.choice(genders)
    name = fake.name_male() if gender == "男" else fake.name_female()
    age = random.randint(18, 75)

    if gender == "男":
        height = random.randint(160, 195) # cm
        weight = round(random.uniform(max(50, height * 0.3 + 10), min(120, height * 0.6)), 1) # kg, 稍微调整了体重逻辑
    else: # 女
        height = random.randint(150, 180) # cm
        weight = round(random.uniform(max(40, height * 0.25 + 5), min(100, height * 0.55)), 1) # kg

    hometown = random.choice(hometowns)
    occupation = random.choice(occupations)
    education_level = random.choice(education_levels)
    marital_status = random.choice(marital_statuses)
    has_children = random.choice([True, False]) if marital_status == "已婚" or age > 30 else False


    # 兴趣爱好 (0到3种)
    num_hobbies = random.randint(0, 3)
    if num_hobbies == 0 or random.random() < 0.1: # 10%概率没有特别爱好
        hobbies = "None"
    else:
        hobbies = "; ".join(random.sample(hobbies_list, k=min(num_hobbies, len(hobbies_list))))
        if not hobbies: hobbies = "None"


    # 随机生成疾病 (0到2种疾病，或者没有)
    num_diseases = random.randint(0, 2)
    if num_diseases == 0 or random.random() < 0.5: # 50%概率没有疾病
        diseases = "None"
    else:
        # 根据年龄稍微增加患病概率
        disease_chance_modifier = (age - 18) / 100 # 年龄越大，基础概率越高一点点
        if random.random() < (0.3 + disease_chance_modifier): # 基础30% + 年龄调整
             diseases = "; ".join(random.sample(possible_diseases, k=min(num_diseases, len(possible_diseases))))
        else:
            diseases = "None"
        if not diseases: diseases = "None"


    # 随机生成饮食偏好 (0到3种偏好，或者没有)
    num_preferences = random.randint(0, 3)
    if num_preferences == 0 or random.random() < 0.15: # 15%概率没有明确偏好
        dietary_preferences = "None"
    else:
        dietary_preferences = "; ".join(random.sample(possible_dietary_preferences, k=min(num_preferences, len(possible_dietary_preferences))))
        if not dietary_preferences: dietary_preferences = "None"

    activity_level = random.choice(activity_levels)

    # 健身目标
    if activity_level == "几乎不运动" and random.random() < 0.6:
        fitness_goals = "无特定目标"
    else:
        num_fitness_goals = random.randint(0, 2)
        if num_fitness_goals == 0 or random.random() < 0.3:
            fitness_goals = "无特定目标"
        else:
            fitness_goals = "; ".join(random.sample(fitness_goals_list, k=min(num_fitness_goals, len(fitness_goals_list)-1))) # -1 避免选到“无特定目标”
            if not fitness_goals: fitness_goals = "无特定目标"


    # 食物过敏 (0到2种)
    num_allergies = random.randint(0, 2)
    if num_allergies == 0 or random.random() < 0.85: # 85%概率没有食物过敏
        food_allergies = "None"
    else:
        food_allergies = "; ".join(random.sample(food_allergies_list, k=min(num_allergies, len(food_allergies_list))))
        if not food_allergies: food_allergies = "None"

    cooking_skills = random.choice(cooking_skills_levels)
    daily_food_budget_cny = random.randint(30, 200) # 每日伙食费30-200元


    return {
        "id": user_id,
        "name": name,
        "age": age,
        "gender": gender,
        "height_cm": height,
        "weight_kg": weight,
        "hometown": hometown,
        "occupation": occupation,
        "education_level": education_level,
        "marital_status": marital_status,
        "has_children": has_children,
        "hobbies": hobbies,
        "diseases": diseases,
        "dietary_preferences": dietary_preferences,
        "activity_level": activity_level,
        "fitness_goals": fitness_goals,
        "food_allergies": food_allergies,
        "cooking_skills": cooking_skills,
        "daily_food_budget_cny": daily_food_budget_cny
    }

def main():
    num_users = 100
    filename = "user_dataset_enhanced.csv"
    fieldnames = [
        "id", "name", "age", "gender", "height_cm", "weight_kg", "hometown",
        "occupation", "education_level", "marital_status", "has_children", "hobbies",
        "diseases", "dietary_preferences", "activity_level", "fitness_goals",
        "food_allergies", "cooking_skills", "daily_food_budget_cny"
    ]

    users_data = []
    for i in range(num_users):
        print(f"Generating user {i+1}/{num_users}...")
        users_data.append(generate_user_data())

    try:
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in users_data:
                writer.writerow(user)
        print(f"\n成功生成 {num_users} 条用户数据到文件: {filename}")
    except IOError:
        print(f"错误: 无法写入文件 {filename}")

if __name__ == "__main__":
    main()