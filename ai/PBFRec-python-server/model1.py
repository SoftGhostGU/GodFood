import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, BatchNorm
from torch_geometric.nn import ChebConv
class gcn_model(nn.Module):
    def __init__(self, in_channels, out_channels,hidden_channel,K = 8):
        super().__init__()
        self.cond1 = ChebConv(in_channels, hidden_channel, K)
        self.bn1 = BatchNorm(hidden_channel)
        self.cond2 = ChebConv(hidden_channel, hidden_channel, K)
        self.bn2 = BatchNorm(hidden_channel)
        self.cond3 = ChebConv(hidden_channel, hidden_channel, K)
        self.bn3 = BatchNorm(hidden_channel)
        self.cond4 = ChebConv(hidden_channel, out_channels, K)

    def forward(self, x, edge_index):
        x = x.float()
        # 第一个GCN层
        x = self.cond1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        # 第二个GCN层
        x = self.cond2(x, edge_index)
        x = self.bn2(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        # 第三个GCN层
        x = self.cond3(x, edge_index)
        x = self.bn3(x)
        x = F.relu(x)
        # x = F.dropout(x, p=0.5, training=self.training)
        # 最后一个GCN层，不进行激活和Dropout
        x = self.cond4(x, edge_index)

        return x