// types/predict.ts

/**
 * 预测信息接口响应数据类型
 * 注意：根据实际返回的JSONObject结构可能需要调整
 */
export interface PredictInfo {
  // 示例字段，根据实际API返回数据补充
  predictionResult?: any;
  healthScore?: number;
  dietarySuggestions?: string[];
  lastUpdated?: string;
  // 其他可能的字段...
}

/** 标准响应格式 */
export interface ResponseDTO<T = any> {
  code: number;
  message: string;
  data?: T;
}
