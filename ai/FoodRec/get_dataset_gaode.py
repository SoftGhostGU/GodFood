import requests
import json
import pandas as pd
import time
import argparse
import os

# 高德地图Web服务API的Key
AMAP_KEY = "c60e4ddd909153c5feca43869c9d1020" # 强烈建议将Key存储在环境变量或配置文件中

# 定义要查询的菜系关键词列表
# 你可以根据需要扩展这个列表
CUISINE_KEYWORDS = [
    "粤菜", "川菜", "湘菜", "鲁菜", "苏菜", "浙菜", "闽菜", "徽菜",
    "上海本帮菜", "北京菜", "东北菜", "西北菜", "云南菜", "贵州菜",
    "日本料理", "韩国料理", "泰国菜", "越南菜", "印度菜", "西餐",
    "意大利菜", "法国菜", "墨西哥菜", "地中海菜", "土耳其菜",
    "火锅", "烧烤", "海鲜", "素食", "清真", "茶餐厅", "快餐简餐",
    "面包甜点", "咖啡厅", "酒吧", "小吃夜宵"
]

# CUISINE_KEYWORDS = [
#     "土耳其菜",
#     "火锅", "烧烤", "海鲜", "素食", "清真", "茶餐厅", "快餐简餐",
#     "面包甜点", "咖啡厅"
# ]

# 定义要提取的CSV列名
CSV_COLUMNS = [
    'id', 'name', 'cuisine', 'type', 'tel', 'tag', 'entr_location', 'address',
    'adcode', 'adname', 'pname', 'biz_type', 'cityname', 'business_area',
    'location', 'cost', 'rating', 'meal_ordering', 'photo_url_first'
]

def fetch_restaurants_by_keyword(keyword, city="上海", offset=1000, max_pages=500):
    all_pois = []
    base_url = "https://restapi.amap.com/v3/place/text"

    actual_offset = 20

    print(f"\nFetching restaurants for keyword: '{keyword}' in city: '{city}'...")

    for page_num in range(1, max_pages + 1):
        params = {
            "key": AMAP_KEY,
            "keywords": keyword,
            "types": "050000",  # 050000 是餐饮服务的分类代码
            "city": city,
            "children": "1",     # 尝试获取子POI，意义不大，但保留
            "offset": actual_offset,   # 每页记录数
            "page": page_num,
            "extensions": "all" # 获取详细信息
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # 如果请求失败则抛出HTTPError
            data = response.json()

            if data.get("status") == "1" and data.get("infocode") == "10000":
                pois = data.get("pois", [])
                if not pois:
                    print(f"  Page {page_num}: No more results found for '{keyword}'.")
                    break  # 没有更多数据了，停止翻页
                
                all_pois.extend(pois)
                print(f"  Page {page_num}: Fetched {len(pois)} POIs. Total so far for '{keyword}': {len(all_pois)}")

                # 检查是否已经达到或超过了API声称的总数，或者API不再返回新数据
                # 高德API的count字段有时不准确，或者有隐藏的上限
                current_count_api = int(data.get("count", 0))
                if len(all_pois) >= current_count_api and current_count_api > 0 :
                    print(f"  Reached API reported count ({current_count_api}) for '{keyword}'.")
                    break
                if len(pois) < actual_offset: # 如果返回的记录数少于请求的offset，说明是最后一页
                    print(f"  Last page for '{keyword}' (received {len(pois)} < requested {actual_offset}).")
                    break

            elif data.get("infocode") == "10001": # KEY不正确或过期
                 print(f"ERROR: Invalid API Key. Infocode: {data.get('infocode')}, Info: {data.get('info')}")
                 return [] # 返回空列表，停止后续操作
            elif data.get("infocode") == "10003": # 访问已超出日访问量限制
                 print(f"ERROR: Daily query limit exceeded. Infocode: {data.get('infocode')}, Info: {data.get('info')}")
                 return all_pois # 返回已获取的数据
            else:
                print(f"  Page {page_num}: API request failed for '{keyword}'. Status: {data.get('status')}, Infocode: {data.get('infocode')}, Info: {data.get('info')}")
                break # 如果API返回错误状态，则停止翻页

        except requests.exceptions.RequestException as e:
            print(f"  Page {page_num}: Request Exception for '{keyword}': {e}")
            break # 网络或请求错误，停止翻页
        except json.JSONDecodeError as e:
            print(f"  Page {page_num}: JSON Decode Error for '{keyword}': {e}. Response text: {response.text[:200]}")
            break

        time.sleep(1)  # 遵守API调用频率限制，稍微延迟一下

    print(f"Finished fetching for keyword '{keyword}'. Total POIs collected: {len(all_pois)}")
    return all_pois


def parse_poi_data(poi, cuisine):
    """
    从单个POI JSON对象中提取所需字段。
    """
    # 从 biz_ext 中安全地获取 'cost', 'rating', 'meal_ordering'
    biz_ext = poi.get("biz_ext", {})
    cost = biz_ext.get("cost", None) # 可能为空或"[]"
    rating = biz_ext.get("rating", None) # 可能为空或"[]"
    meal_ordering = biz_ext.get("meal_ordering", "0") # 默认为"0"

    # 处理空cost和rating，高德有时返回 "[]" 作为空值
    if cost == "[]" or not cost : cost = None
    if rating == "[]" or not rating: rating = None


    # 获取第一张照片的URL
    photos = poi.get("photos", [])
    photo_url_first = photos[0].get("url", None) if photos and isinstance(photos, list) and photos[0] else None

    return {
        'id': poi.get("id"),
        'name': poi.get("name"),
        'cuisine': cuisine,
        'type': poi.get("type"),
        'tel': poi.get("tel") if poi.get("tel") and poi.get("tel") != "[]" else None,
        'tag': poi.get("tag") if poi.get("tag") and poi.get("tag") != "[]" else None,
        'entr_location': poi.get("entr_location") if poi.get("entr_location") and poi.get("entr_location") != "[]" else None,
        'address': poi.get("address"),
        'adcode': poi.get("adcode"),
        'adname': poi.get("adname"),
        'pname': poi.get("pname"),
        'biz_type': poi.get("biz_type") if poi.get("biz_type") and poi.get("biz_type") != "[]" else None,
        'cityname': poi.get("cityname"),
        'business_area': poi.get("business_area") if poi.get("business_area") and poi.get("business_area") != "[]" else None,
        'location': poi.get("location"),
        'cost': cost,
        'rating': rating,
        'meal_ordering': meal_ordering,
        'photo_url_first': photo_url_first
    }

def main(output_csv_file, city, max_pages_per_keyword):
    all_restaurant_data = []
    collected_poi_ids = set() # 用于去重

    for keyword in CUISINE_KEYWORDS:
        pois_for_keyword = fetch_restaurants_by_keyword(keyword, city=city, max_pages=max_pages_per_keyword)
        
        for poi in pois_for_keyword:
            poi_id = poi.get("id")
            if poi_id and poi_id not in collected_poi_ids: # 避免重复添加同一个POI
                parsed_data = parse_poi_data(poi, keyword)
                all_restaurant_data.append(parsed_data)
                collected_poi_ids.add(poi_id)
        
        # 可选：如果API有严格的QPS限制，可以在每个关键词后增加更长的延时
        # time.sleep(1) 

    if not all_restaurant_data:
        print("No restaurant data collected. CSV file will not be created.")
        return

    # 创建DataFrame并保存到CSV
    df = pd.DataFrame(all_restaurant_data, columns=CSV_COLUMNS)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_csv_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        df.to_csv(output_csv_file, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility
        print(f"\nSuccessfully saved {len(df)} unique restaurants to {output_csv_file}")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch restaurant data from Gaode Maps API and save to CSV.")
    parser.add_argument(
        "--output_file", 
        type=str, 
        default="restaurants_gaode.csv",
        help="Path to save the output CSV file."
    )
    parser.add_argument(
        "--city",
        type=str,
        default="上海",
        help="City to search for restaurants in (e.g., 上海, 北京)."
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=1000, # 默认每个关键词最多爬取10页，每页20条，大概200条。高德一般限制总数在1000条左右。
        help="Maximum number of pages to fetch for each keyword. Each page typically has 20 results."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=AMAP_KEY, # Default to the one defined in script
        help="Your Gaode Maps Web Service API Key."
    )

    args = parser.parse_args()
    
    # Update AMAP_KEY if provided via command line
    if args.api_key and args.api_key != AMAP_KEY:
        AMAP_KEY = args.api_key
        print(f"Using API Key provided from command line.")
    elif not AMAP_KEY:
        print("ERROR: Gaode API Key is not set. Please provide it via --api_key or set it in the script.")
        exit()


    main(args.output_file, args.city, args.max_pages)

    # 示例：检查生成的CSV文件的前几行
    if os.path.exists(args.output_file):
        print(f"\n--- First 5 rows of {args.output_file} ---")
        try:
            df_check = pd.read_csv(args.output_file)
            print(df_check.head().to_string())
        except Exception as e:
            print(f"Could not read or display CSV for verification: {e}")