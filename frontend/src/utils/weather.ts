import Taro from '@tarojs/taro';

// 定义请求接口的 URL
const API_URL = 'http://66mv2622an93.vicp.fun:9090/getWeather';

// 定义请求参数类型
interface GetWeatherParams {
  location: string;
}

// 定义响应数据类型
interface ResponseDTO {
  code: number;
  message: string;
  data?: any; // 天气数据
}

// 获取当前天气接口函数
async function getWeather(params: GetWeatherParams): Promise<ResponseDTO> {
  try {
    const res = await Taro.request({
      url: API_URL,
      method: 'GET',
      data: params
    });

    if (res.statusCode === 200) {
      return res.data as ResponseDTO;
    } else {
      throw new Error(`请求失败，状态码：${res.statusCode}`);
    }
  } catch (error) {
    console.error('获取天气信息请求失败：', error);
    throw error;
  }
}

export default getWeather;