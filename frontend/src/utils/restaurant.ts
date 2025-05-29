// api/restaurant.ts
import Taro from '@tarojs/taro';
import { ResponseDTO, Restaurant } from '../types/restaurant';
import { getStorage, showToast, request } from '@tarojs/taro';

/**
 * 根据预测信息获取推荐餐厅
 * @param token 用户认证token
 */
export async function getRestaurantsByPredict(
  token: string
): Promise<ResponseDTO<Restaurant[]>> {
  try {
    const response = await request({
      url: 'http://66mv2622an93.vicp.fun:9090/getRestaurantsByPredict',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'token': token
      }
    });

    if (response.statusCode === 200) {
      return response.data as ResponseDTO<Restaurant[]>;
    }
    throw new Error(`请求失败: ${response.statusCode}`);
  } catch (error) {
    console.error('获取餐厅失败:', error);
    throw error;
  }
}

/**
 * 高阶封装 - 自动处理token的餐厅请求
 */
export async function fetchRecommendedRestaurants(): Promise<Restaurant[]> {
  // 获取token
  const token = await getStorage({ key: 'accessToken' })
    .then(res => res.data)
    .catch(() => {
      showToast({ title: '请先登录', icon: 'none' });
      throw new Error('未登录');
    });

  // 调用接口
  const result = await getRestaurantsByPredict(token);
  
  // 处理业务错误
  if (result.code !== 200) {
    showToast({ title: result.message || '获取推荐失败', icon: 'none' });
    throw new Error(result.message);
  }

  return result.data || [];
}