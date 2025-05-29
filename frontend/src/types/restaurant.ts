/**
 * 餐厅信息数据结构
 * 根据实际API返回数据需要调整
 */
export interface Restaurant {
  adcode: string;         // 区域代码
  address: string;        // 地址
  adname: string;         // 区域名称
  biz_type: string;       // 经营业务类型
  business_area: string;  // 商业区域
  cityname: string;       // 城市名称
  cost?: number;          // 成本（可选）
  cuisine?: string;       // 菜系（可选）
  entr_location?: string; // 入口位置经纬度（可选）
  location?: string;      // 地址经纬度（可选）
  meal_ordering?: number; // 预订次数（可选）
  name: string;           // 餐馆名称
  photo_url_first?: string; // 首图 URL（可选）
  pname?: string;         // 省份名称（可选）
  rating_biz?: number;    // 商家评分（可选）
  recommendation_score?: number; // 推荐评分（可选）
  restaurant_id: string;  // 餐馆 ID
  tag?: string;           // 标签（可选）
  tel?: string;           // 电话号码（可选）
  type?: string;          // 类型（可选）
}


/** 接口响应格式 */
export interface ResponseDTO<T = any> {
  code: number;
  message: string;
  data: T;
}

/** 预测参数类型 */
export interface PredictParams {
  // 根据实际需要传递的参数定义
  healthScore?: number;
  dietaryNeeds?: string[];
  location?: {
    lat: number;
    lng: number;
  };
  // 其他预测参数...
}