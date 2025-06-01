/**
 * 定义接口返回的基本响应结构
 * 根据文档中的 ResponseDTO«string» 推断
 */
interface ResponseDTO<T> {
  code: number;
  message: string;
  data?: T;
  success: boolean;
}

/**
 * 定义用户评价数据结构
 * 由于文档中没有提供 UserReview 的具体结构，这里使用通用类型
 * 实际使用时应根据具体业务需求定义
 */
interface UserReview {
  "activity_level": string,
  "age": number,
  "blood_pressure_mm_hg": string,
  "blood_sugar_mmol_l": number,
  "cooking_skills": string,
  "daily_food_budget_cny": number,
  "dietary_preferences": string,
  "diseases": string,
  "education_level": string,
  "fitness_goals": string,
  "food_allergies": string,
  "gender": string,
  "has_children": boolean,
  "heart_rate_bpm": number,
  "height_cm": number,
  "hobbies": string,
  "hometown": string,
  "id": string,
  "marital_status": string,
  "name": string,
  "occupation": string,
  "restaurant_id": string,
  "restaurant_name": string,
  "review_datetime": string,
  "review_text_placeholder": string,
  "sleep_hours_last_night": number,
  "steps_today_before_meal": number,
  "user_id": string,
  "user_rating": number,
  "was_hungry_before_meal": boolean,
  "weather_humidity_percent": number,
  "weather_temp_celsius": number,
  "weight_kg": number
}

/**
 * 训练模型（餐厅打卡）
 * @param token 用户令牌
 * @param userReview 用户评价数据
 * @returns 包含响应数据的Promise
 * @throws 当请求失败或响应不成功时抛出错误
 */
export const trainModel = async (
  token: string,
  userReview: UserReview,
): Promise<ResponseDTO<string>> => {
  const url = `http://66mv2622an93.vicp.fun:9090/train`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': token
      },
      body: JSON.stringify(userReview)
    });

    if (!response.ok) {
      // 根据文档中的响应状态码处理不同错误
      switch (response.status) {
        case 401:
          throw new Error('未授权: 请检查token是否正确');
        case 403:
          throw new Error('禁止访问: 无权限执行此操作');
        case 404:
          throw new Error('资源未找到');
        default:
          throw new Error(`请求失败，状态码: ${response.status}`);
      }
    }

    const data: ResponseDTO<string> = await response.json();
    
    // 检查业务逻辑是否成功
    if (!data.success) {
      throw new Error(data.message || '训练模型失败');
    }

    return data;
  } catch (error) {
    console.error('训练模型请求出错:', error);
    return Promise.reject(error);
    // throw error;
  }
}

// 使用示例
/*
const token = 'your_token_here';
const userReview: UserReview = {
  restaurantId: '123',
  rating: 5,
  reviewText: '很好吃'
};

trainModel(token, userReview)
  .then(data => console.log('训练结果:', data))
  .catch(err => console.error('错误:', err));
*/