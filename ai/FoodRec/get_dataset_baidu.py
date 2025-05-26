import requests
import json  # 导入 json 模块

# 接口地址
url = "https://api.map.baidu.com/place/v2/search"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
ak = "QdXmk1OLCT2dZR03ye9J8jhogPThi8TP"

params = {
    "query": "粤菜",
    "tag": "餐厅",
    "region": "上海",
    "output": "json",
    "ak": ak,
    "scope": 2,
    "page_size": 100,
    "page_num": 0
}

response = requests.get(url=url, params=params)
if response:
    # 使用 json.dumps 格式化输出
    formatted_json = json.dumps(response.json(), indent=4, ensure_ascii=False)
    print(formatted_json)