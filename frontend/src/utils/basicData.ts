import Taro from '@tarojs/taro';
import { ResponseDTO } from '../types/basicData';

/**
 * 获取用户预测信息
 * @param token 用户认证token
 * @returns 预测信息数据
 */
export async function getPredictInfo(token: string): Promise<ResponseDTO> {
  try {
    const response = await Taro.request({
      url: 'http://66mv2622an93.vicp.fun:9090/predictInfo',
      method: 'GET',
      header: {
        'Authorization': token,
        'Content-Type': 'application/json'
      }
    });

    // 成功响应处理
    if (response.statusCode === 200) {
      return response.data as ResponseDTO;
    }
    // 处理其他状态码
    throw new Error(`请求失败，状态码: ${response.statusCode}`);
  } catch (error) {
    console.error('获取预测信息失败:', error);
    throw error; // 抛出错误供上层处理
  }
}
