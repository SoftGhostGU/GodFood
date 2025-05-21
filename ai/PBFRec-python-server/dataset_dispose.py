import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder
import  matplotlib.pyplot as plt
import numpy as np
import matplotlib
import torch
import time
import util
import torch.nn.functional as F
import pytz
import datetime
from torch_geometric.data import InMemoryDataset, Data
import torch.nn as nn
from check_friend import dataload, encode_timestamp,get_group_len_over_threshold, get_group_len_over_threshold_1,get_category_dict, get_node_feature, add_checkin_count_todata, position_encoding, embadding_category, convert_utc_with_offset_to_timestamp

matplotlib.use('TkAgg')

class DisposeCheckinDataset(InMemoryDataset):
    def __init__(self, root,transform=None, pre_transform=None, pre_filter=None):
        super().__init__(root, transform, pre_transform, pre_filter)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self):
        return ['']

    @property
    def processed_file_names(self):
        return ['checkin.dataset']

    def download(self):
        pass

    def process(self):
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



        # 随机选择部分user_id数据进行处理
        simple_user_id = np.random.choice(checkins.user_id.unique(), 100, replace=False)

        # 筛选出user_id在simple_user_id中的数据
        checkins = checkins.loc[checkins.user_id.isin(simple_user_id)]

        # 将经纬度映射到向量
        checkins['local_encoding'] = checkins.apply(
            lambda row: position_encoding(torch.tensor(row['latitude']), torch.tensor(row['longitude'])), axis=1)

        # 将类别embedding编码
        checkins['category_encoding'] = checkins.apply(
            lambda row: embadding_category(unique_category_with_index,
                                           unique_category_with_index[row['category_name']]), axis=1)

        # 将时间转换为
        checkins['timestamp'] = checkins.apply(
            lambda row: convert_utc_with_offset_to_timestamp(row['utc_time'], row['timezone_offset']), axis=1)
        # 将时间戳编码为向量，用24*7个向量表示小时数，再用6位向量表示第几周
        checkins['timestamp_encoding'] = checkins.apply(lambda row: encode_timestamp(row['timestamp']), axis=1)

        checkins = checkins.drop(
            ['country_code', 'latitude', 'longitude', 'timezone_offset', 'utc_time', 'category_name'], axis=1)

        # 按照用户分组
        user_groups = checkins.groupby(checkins.user_id)

        for user_id, group in tqdm(user_groups):
            # 记录开始时间
            start_time = time.time()

            data_list = []
            # 将timestamp重新编码
            group['sess_timestamp'] = LabelEncoder().fit_transform(group.timestamp)
            # 按照时间戳排序
            group_sorted = group.sort_values(by='sess_timestamp')
            # 将时间戳转为数组
            group_sorted['timestamp'] = np.array(group_sorted['timestamp'].values).reshape(len(group_sorted), -1)
            # 重置索引编号
            group_sorted = group_sorted.reset_index(drop=True)
            node_features = get_node_feature(group_sorted)
            source_nodes = group_sorted['sess_timestamp'].values[:-1]
            target_nodes = group_sorted['sess_timestamp'].values[1:]
            edge_index = torch.tensor([source_nodes, target_nodes])
            y = torch.tensor(group_sorted.checkin_count.values, dtype=torch.float32)
            data = Data(x=torch.tensor(node_features).to(torch.double), edge_index=edge_index, y=y)
            data_list.append(data)
            # 将数据合并
            data, slice = self.collate(data_list)

            end_time = time.time()
            # 计算持续时间
            duration = end_time - start_time
            print(f"User ID: {user_id}, duration: {duration}s, len:{len(group.groupby(group.venue_id))},len1:{len(group)}")
            # 将数据保存到指定位置
            # torch.save((data, slice), 'dataset/checkin_data/{}.pt'.format(user_id))

if __name__ == '__main__':
    DisposeCheckinDataset(root='dataset/')

