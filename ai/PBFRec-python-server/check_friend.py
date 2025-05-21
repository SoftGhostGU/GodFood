import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder
import  matplotlib.pyplot as plt
import numpy as np
import matplotlib
import torch
import util
import torch.nn.functional as F
import pytz
import datetime
from torch_geometric.data import InMemoryDataset, Data
import torch.nn as nn
from util import draw_tensor_network
matplotlib.use('TkAgg')

# 设置列不限制数量
pd.set_option('display.max_columns', None)
# 设置 value 的显示长度为 100，默认为 50
pd.set_option('max_colwidth', 100)

def dataload():
    checkins = pd.read_csv('E:\\datasets\\dataset_WWW2019\\dataset_WWW_Checkins_anonymized.txt', sep='\t')
    friendship = pd.read_csv('E:\\datasets\\dataset_WWW2019\\dataset_WWW_friendship_new.txt', sep='\t')
    poi = pd.read_csv('E:\\datasets\\dataset_WWW2019\\raw_POIs.txt', sep='\t')

    checkins.columns = ['user_id', 'venue_id', 'utc_time', 'timezone_offset']
    poi.columns = ['venue_id', 'latitude', 'longitude', 'category_name', 'country_code']
    friendship.columns = ['user1_id', 'user2_id']
    return checkins,friendship,poi
# 画出某用户下的签到概况
def draw_venues_check_in_count(venues_check,venues_check_in_count_list):
    venues_check = np.array(venues_check).reshape(1, -1).flatten()
    venues_check_in_count_list = np.array(venues_check_in_count_list).reshape(1, -1).flatten()
    plt.bar(venues_check, venues_check_in_count_list)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.title('user check in count')
    plt.xlabel('task')
    plt.ylabel('check in count')
    plt.show()
#分析分组的具体数据
def group_data_by_user_id(user_groups):
    user_check = []
    user_check_in_count_list = []
    for user_id, group in tqdm(user_groups):
        # group.venue_id = LabelEncoder().fit_transform(group.venue_id)
        venus_groups = group.groupby(group.venue_id)
        user_check.append(user_id)
        # 各个用户所签到的地点数量
        user_check_in_count_list.append(len(venus_groups))
        # if (user_id == 0):
        #     for venue_id, venus_group in tqdm(venus_groups):
        #         venues_check.append(venue_id)
        #         venues_check_in_count_list.append(len(venus_group))
        #         print("用户{}众包记录中，任务{}，签到的次数为{},".format(user_id, venue_id, len(venus_group)))

        #     break
        print("用户{}众包记录中，签到的次数为{},".format(user_id, len(group)))
    plt.scatter(user_check, user_check_in_count_list)
    plt.xlabel("user")
    plt.ylabel("check in count")


    return user_check,user_check_in_count_list
# 获取超过阈值的用户
def get_group_len_over_threshold(user_groups, threshold=90):
    return [user_id for user_id, group in tqdm(user_groups) if len(group.groupby(group.venue_id)) >= threshold]
# 获取超过阈值的用户和其对应的签到次数
def get_group_len_over_threshold_1(user_groups):
    results = []
    # 遍历user_groups，应用条件过滤
    for user_id, group in tqdm(user_groups):
        group_len = len(group.groupby(group.venue_id))
        if (is_close_to(group_len, 92)):
            results.append((user_id, group_len))
        if (is_close_to(group_len, 92) or
                is_slightly_below(group_len, 145.22) or
                is_slightly_above(group_len, 145.22) or
                is_close_to(group_len, 1500)):
            results.append((user_id, group_len))

    # 输出结果
    for user_id, group_len in results:
        print(f"User ID: {user_id}, Groupby Length: {group_len}")
# 判断是否接近目标值
def is_close_to(value, target, epsilon=5):
     return abs(value - target) <= epsilon
# 判断是否略低于目标值
def is_slightly_below(value, target):
    return value < target and value >= target - 5
# 判断是否略高于目标值
def is_slightly_above(value, target):
    return value > target and value <= target + 5

# 将经纬度映射到向量
def position_encoding(latitude = torch.tensor(37.7749), longitude = torch.tensor(-122.4194), d = 128):
    # 我们可以将经纬度转换为弧度，因为PyTorch的三角函数默认使用弧度
    longitudes_rad = torch.mul(longitude, torch.tensor(torch.pi / 180.0))
    latitudes_rad = torch.mul(latitude, torch.tensor(torch.pi / 180.0))

    # 对经纬度使用sin和cos函数进行编码
    encoded_longitudes_sin = torch.sin(longitudes_rad)
    encoded_longitudes_cos = torch.cos(longitudes_rad)
    encoded_latitudes_sin = torch.sin(latitudes_rad)
    encoded_latitudes_cos = torch.cos(latitudes_rad)

    # 将编码后的经纬度合并为一个张量
    encoded_data = torch.stack((encoded_longitudes_sin, encoded_longitudes_cos,
                                encoded_latitudes_sin, encoded_latitudes_cos))
    return encoded_data.numpy().reshape(-1)

# 将UTC时间加上时区偏移量转换为时间戳
def convert_utc_with_offset_to_timestamp(utc_time_str, offset_hours):
    utc_tz = pytz.utc
    utc_time = datetime.datetime.strptime(utc_time_str, '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=utc_tz)
    offset = datetime.timedelta(hours=offset_hours)
    local_time = utc_time + offset
    return local_time.timestamp()
# 添加签到次数
def add_checkin_count_todata(checkins):
    checkin_counts = checkins.groupby(['user_id', 'venue_id']).size().reset_index(name='checkin_count')
    merged_df = pd.merge(checkins, checkin_counts, on=['user_id', 'venue_id'], how='left')
    return merged_df
# 获取类别字典
def get_category_dict(categories):
    unique_strings = list(set(categories))
    # 创建一个空字典来存储唯一值和它们的索引
    unique_category_with_index = {}
    # 遍历原始列表并分配索引
    for i, s in enumerate(unique_strings):
        if s not in unique_category_with_index:
            unique_category_with_index[s] = i
    return unique_category_with_index
# 将类别编码为向量
def embadding_category(category_dict,category_index):

    # 假设我们有4个类别，并且将每个类别嵌入到5维的向量中
    num_embeddings = len(category_dict.keys())  # 类别数量
    embedding_dim = 128  # 嵌入向量的维度

    # 创建一个嵌入层
    embedding_layer = nn.Embedding(num_embeddings, embedding_dim)

    indices = torch.tensor([category_index], dtype=torch.long)  # 类别索引，必须是long类型

    # 使用嵌入层对类别索引进行编码
    embedded = embedding_layer(indices)
    embedded = embedded.detach().numpy().reshape(-1)
    return embedded

# 将签到时间编码为向量
def encode_timestamp(timestamp):
    # 计算一周内的小时偏移量
    hour_offset = timestamp % (24 * 7)
    # 计算所在的周数
    week_number = timestamp // (24 * 7)

    # 创建小时向量
    hour_vector = np.zeros(24 * 7)
    hour_vector[hour_offset] = 1

    # 创建周数向量
    week_vector = np.zeros(6)
    week_vector[week_number] = 1

    # 合并两个向量
    encoded_vector = np.concatenate((hour_vector, week_vector))

    return encoded_vector

def get_node_feature(group_sorted):
    node_features = []
    for i in range(len(group_sorted)):
        node_features_merge =np.concatenate(
            [group_sorted.local_encoding.values[i],
             group_sorted.category_encoding.values[i],
             [group_sorted.timestamp.values[i]]])
        node_features.append(node_features_merge)
    return node_features
# 获取数据集特征大小
def get_dataset_feature_size():
    # 加载数据
    checkins, friendship, poi = dataload()

    ###数据预处理
    # 签到记录和场所信息合并
    checkins = pd.merge(checkins, poi, on='venue_id')
    # id重新编码
    # checkins.venue_id = LabelEncoder().fit_transform(checkins.venue_id)
    # checkins.user_id = LabelEncoder().fit_transform(checkins.user_id)

    # 按照用户分组
    user_groups = checkins.groupby(checkins.user_id)

    # 移除签到次数少于90次的用户
    filter_userids = get_group_len_over_threshold(user_groups)
    checkins = checkins.loc[checkins.user_id.isin(filter_userids)]

    # 获取地点类别元组
    unique_category_with_index = get_category_dict(checkins['category_name'])

    # 将用户对于每个任务id的签到次数作为标签
    checkins = add_checkin_count_todata(checkins)

    check_num = checkins["checkin_count"]
    task_id = checkins["venue_id"]
    user_id = checkins["user_id"]

    # checkins = checkins.sample(n = 100000)

    # 随机选择部分user_id数据进行处理
    simple_user_id = np.random.choice(checkins.user_id.unique(), 1000, replace=False)

    # 筛选出user_id在simple_user_id中的数据
    checkins = checkins.loc[checkins.user_id.isin(simple_user_id)]

    # 建立类别字典
    category_dict = dict(zip(checkins['category_name'].unique(), range(len(checkins['category_name'].unique()))))

    # 将经纬度映射到向量
    checkins['local_encoding'] = checkins.apply(
        lambda row: position_encoding(torch.tensor(row['latitude']), torch.tensor(row['longitude'])), axis=1)

    # 将类别embedding编码
    checkins['category_encoding'] = checkins.apply(
        lambda row: embadding_category(unique_category_with_index, unique_category_with_index[row['category_name']]),
        axis=1)

    # 将时间转换为时间戳
    checkins['timestamp'] = checkins.apply(
        lambda row: convert_utc_with_offset_to_timestamp(row['utc_time'], row['timezone_offset']), axis=1)
    # 将时间戳编码为向量，用24*7个向量表示小时数，再用6位向量表示第几周
    checkins['timestamp_encoding'] = checkins.apply(lambda row: encode_timestamp(row['timestamp']), axis=1)

    checkins = checkins.drop(
        ['country_code', 'latitude', 'longitude', 'timezone_offset', 'utc_time', 'category_name'], axis=1)

    # 按照用户分组
    user_groups = checkins.groupby(checkins.user_id)

    data_list = []

    for user_id, group in tqdm(user_groups):
        if(user_id==6768):
            return [
                len(group_sorted['timestamp']),
                len(group_sorted['local_encoding']),
                len(group_sorted['category_encoding'])]


if __name__ == '__main__':
    # 加载数据
    checkins, friendship, poi = dataload()

    ###数据预处理
    # 签到记录和场所信息合并
    checkins = pd.merge(checkins, poi, on='venue_id')
    # id重新编码
    # checkins.venue_id = LabelEncoder().fit_transform(checkins.venue_id)
    # checkins.user_id = LabelEncoder().fit_transform(checkins.user_id)

    # 按照用户分组
    user_groups = checkins.groupby(checkins.user_id)

    # 移除签到次数少于90次的用户
    filter_userids = get_group_len_over_threshold(user_groups)
    checkins = checkins.loc[checkins.user_id.isin(filter_userids)]

    # 获取地点类别元组
    unique_category_with_index = get_category_dict(checkins['category_name'])

    # 将用户对于每个任务id的签到次数作为标签
    checkins = add_checkin_count_todata(checkins)

    check_num = checkins["checkin_count"]
    task_id = checkins["venue_id"]
    user_id = checkins["user_id"]


    # checkins = checkins.sample(n = 100000)

    # 随机选择部分user_id数据进行处理
    simple_user_id = np.random.choice(checkins.user_id.unique(), 1000, replace=False)

    # 筛选出user_id在simple_user_id中的数据
    checkins = checkins.loc[checkins.user_id.isin(simple_user_id)]

    # 建立类别字典
    category_dict = dict(zip(checkins['category_name'].unique(), range(len(checkins['category_name'].unique()))))

    # 将经纬度映射到向量
    checkins['local_encoding'] = checkins.apply(
        lambda row: position_encoding(torch.tensor(row['latitude']), torch.tensor(row['longitude'])), axis=1)

    # 将类别embedding编码
    checkins['category_encoding'] = checkins.apply(
        lambda row: embadding_category(unique_category_with_index,unique_category_with_index[row['category_name']]), axis=1)

    # 将时间转换为时间戳
    checkins['timestamp'] = checkins.apply(
        lambda row: convert_utc_with_offset_to_timestamp(row['utc_time'],row['timezone_offset']), axis=1)
    # 将时间戳编码为向量，用24*7个向量表示小时数，再用6位向量表示第几周
    checkins['timestamp_encoding'] = checkins.apply(lambda row: encode_timestamp(row['timestamp']), axis=1)

    checkins = checkins.drop(
        ['country_code', 'latitude', 'longitude','timezone_offset','utc_time','category_name'], axis=1)

    # 按照用户分组
    user_groups = checkins.groupby(checkins.user_id)

    data_list = []

    for user_id,group in tqdm(user_groups):
        # 将timestamp重新编码
        group['sess_timestamp'] = LabelEncoder().fit_transform(group.timestamp)
        # 按照时间戳排序
        group_sorted = group.sort_values(by='sess_timestamp')
        # 将时间戳转为数组
        group_sorted['timestamp'] = np.array(group_sorted['timestamp'].values).reshape(len(group_sorted),-1)
        # 重置索引编号
        group_sorted = group_sorted.reset_index(drop=True)
        node_features = get_node_feature(group_sorted)
        source_nodes = group_sorted['sess_timestamp'].values[:-1]
        target_nodes = group_sorted['sess_timestamp'].values[1:]
        edge_index = torch.tensor([source_nodes, target_nodes])
        y = torch.tensor(group_sorted.checkin_count.values, dtype=torch.float32)
        data = Data(x=torch.tensor(node_features).to(torch.double), edge_index=edge_index, y=y)
        if (data.x.size()[0] < 150):
            draw_tensor_network(data, 'green')
        # draw_tensor_network(data,'green')
        data_list.append(data)
