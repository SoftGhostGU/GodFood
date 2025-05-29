import { request } from '@tarojs/taro'

// 定义请求接口的 URL
const REGISTER_API_URL = 'http://66mv2622an93.vicp.fun:9090/register';
const LOGIN_API_URL = 'http://66mv2622an93.vicp.fun:9090/login';
const INFO_API_URL = 'http://66mv2622an93.vicp.fun:9090/info';

// 定义请求参数类型
interface RegisterParams {
  email: string;
  password: string;
  userName: string;
}

interface LoginParams {
  email: string;
  password: string;
}

interface UserInfo {
  activity_level?: string;
  age?: number;
  avatarUrl?: string;
  blood_sugar_mmol_L?: number;
  cooking_skills?: string;
  daily_food_budget_cny?: number;
  dietary_preferences?: string;
  diseases?: string;
  education_level?: string;
  email?: string;
  fitness_goals?: string;
  food_allergies?: string;
  gender?: string;
  has_children?: string;
  heart_rate_bpm?: number;
  height_cm?: number;
  hobbies?: string;
  hometown?: string;
  marital_status?: string;
  occupation?: string;
  passWord?: string; // 注意：密码字段通常不应通过普通更新接口传输
  phone?: string;
  sleep_hours_last_night?: number;
  steps_today_before_meal?: number;
  userID?: string;
  userName?: string;
  weight_kg?: number;
}

// 定义响应数据类型
interface ResponseDTO {
  code: number;
  message: string;
  data?: any;
}

// 用户注册接口函数
export const register = async (params: RegisterParams): Promise<ResponseDTO> => {
  try {
    const res = await request({
      url: REGISTER_API_URL,
      method: 'POST',
      data: params,
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      }
    });

    if (res.statusCode === 200) {
      console.log('注册请求成功：', res.data);
      return res.data as ResponseDTO;
    } else {
      throw new Error(`请求失败，状态码：${res.statusCode}`);
    }
  } catch (error) {
    console.error('注册请求失败：', error);
    throw error;
  }
}

// 用户登录接口函数
export const login = async (params: LoginParams): Promise<ResponseDTO> => {
  try {
    const res = await request({
      url: LOGIN_API_URL,
      method: 'POST',
      data: params,
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      }
    });

    if (res.statusCode === 200) {
      console.log('登录请求成功：', res.data);
      return res.data as ResponseDTO;
    } else {
      throw new Error(`请求失败，状态码：${res.statusCode}`);
    }
  } catch (error) {
    console.error('登录请求失败：', error);
    throw error;
  }
}

// 获取用户详细信息接口函数
export const getInfo = async (token: string): Promise<ResponseDTO> => {
  try {
    const res = await request({
      url: INFO_API_URL,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (res.statusCode === 200) {
      console.log('获取用户信息请求成功：', res.data);
      return res.data as ResponseDTO;
    } else {
      throw new Error(`请求失败，状态码：${res.statusCode}`);
    }
  } catch (error) {
    console.error('获取用户信息请求失败：', error);
    throw error;
  }
}

/**
 * 更新用户信息
 * @param userData 更新的用户数据（Partial<UserInfo> 表示可选部分字段）
 * @param token 用户认证 token
 */
export const updateUserInfo = async (
  userData: Partial<UserInfo>,
  token: string
): Promise<ResponseDTO> => {
  try {
    const safeData = { ...userData };
    // delete safeData.passWord;

    const response = await request({
      url: 'http://66mv2622an93.vicp.fun:9090/updateUser',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token,
      },
      data: safeData,
    });

    // 处理 HTTP 状态码
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.data as ResponseDTO;
    } else {
      throw new Error(`请求失败: ${response.statusCode}`);
    }
  } catch (error) {
    console.error('更新用户信息失败:', error);
    throw error;
  }
}