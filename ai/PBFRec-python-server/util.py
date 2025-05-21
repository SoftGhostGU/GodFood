import time

from sklearn.manifold import TSNE
from matplotlib import pyplot as plt
from torch_geometric.utils import to_networkx
import networkx as nx
import numpy as np
import seaborn as sns
import datetime

def drop_tensor_draw_scatter(data,color):
    # 使用t-SNE算法对数据进行降维处理，得到二维数据z
    z = TSNE(n_components=2).fit_transform(data.detach().cpu().numpy())

    # 创建一个大小为10x10的图形窗口
    fig = plt.figure(figsize=(10, 10))

    # 在图形窗口中绘制散点图，其中x轴为z的第一列，y轴为z的第二列，点的颜色由参数color指定
    plt.scatter(z[:, 0], z[:, 1],c=color)

    # 显示图形
    plt.show()


def drop_tensor_draw_scatter_list(data_list,num_subplots):
    # 如果num_subplots为None，则将其设置为data_list的长度
    if(num_subplots==None):
        num_subplots = len(data_list)

    # 计算行数r和列数c
    r=int(num_subplots/2)+1
    c=int(num_subplots/2)

    # 创建一个r行c列的图形窗口
    fig, axes = plt.subplots(r,c, figsize=(20, 10))

    the_r = 0
    the_c = 0

    for i, data in enumerate(data_list):
        # 将data.x从tensor中取出，转换为numpy数组
        data_transform_numpy = data.x.detach().cpu().numpy()

        # 使用t-SNE进行降维处理
        z = TSNE(n_components=2).fit_transform(data_transform_numpy)

        # 在指定的坐标轴上进行散点图的绘制（原始代码中被注释掉的行已被删除，并使用下一行的代码替代）
        # sns.scatterplot(x=z[:, 0], y=z[:, 1], ax= axes[the_r][the_c])
        # 在指定的坐标轴上进行散点图的绘制
        axes[the_r][the_c].scatter(z[:, 0], z[:, 1])

        the_c = the_c+1

        # 如果列数已经超过了设定的列数c，则将列数重置为0，行数加1
        if(the_c>=c):
            the_c=0
            the_r=the_r+1

        # 如果行数超过了设定的行数r，则显示图形并返回
        if(the_r>r):
            plt.show()
            return

    # 显示图形
    plt.show()



# 数据可视化
def draw_tensor_network(data,color):
    name = str(time.time())+'.png'
    #网络化
    G = to_networkx(data)
    G = G.to_undirected()
    #创建绘图窗口
    fig = plt.figure(figsize=(12, 12))
    #使用spring_layout算法计算节点位置
    pos = nx.spring_layout(G,k=0.5)
    #使用计算出的节点位置绘制网络图，并设置节点颜色
    nx.draw_networkx(G,pos,node_color ="#F4A460",node_size =400,edge_color='blue', with_labels=True)
    plt.savefig(name, dpi=300)
    plt.show()



if __name__ == '__main__':
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos,edge_color='red')
    plt.show()