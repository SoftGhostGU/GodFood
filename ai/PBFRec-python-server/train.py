import numpy as np
import torch.optim.adam
import model1
import torch_geometric.data
from sklearn.metrics import recall_score
import matplotlib.pyplot as plt

#训练轮数
epochs = 4500
#使用gpu加速训练
device = "cuda"

# 导入pt数据集
data,silce = torch.load('dataset\\checkin_data\\6768.pt')


#创建神经网络模型
model = model1.gcn_model(in_channels=133,hidden_channel=512,out_channels=3)
# model = model.to(device)

model.load_state_dict(torch.load('dataset/local_model/6768_1_local_model.pth'))

# 定义损失函数和优化器
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.008)
def train(data):
    out = model(data.x, data.edge_index)
    optimizer.zero_grad()
    # target = torch.where(data.y < data.y.mean(), torch.zeros_like(data.y), torch.ones_like(data.y))
    target = target_class(data)
    target = target.long()
    loss = criterion(out, target)
    loss.backward()
    # 更新模型参数
    optimizer.step()
    return loss,out


def test(data):
    # 设置模型为评估模式
    model.eval()
    # 使用模型对输入数据进行前向传播
    out = model(data.x, data.edge_index)
    # 对输出进行argmax操作，在行的方向，取最大值所在的索引作为预测结果
    pred = out.argmax(dim=1)
    # 判断预测结果是否与测试集的真实标签相等，得到一个布尔类型的张量
    # target = torch.where(data.y < data.y.mean(), torch.zeros_like(data.y), torch.ones_like(data.y))
    target = target_class(data)
    test_correct = pred == target
    # 计算预测正确的样本数量，并转换为整数类型
    acc = int(test_correct.sum()) / int(len(data.y))
    recall = recall_score(target, pred, average='weighted')  # 使用加权平均
    # 返回准确率
    return acc,recall

def target_class(data):
    # 计算分位数来定义类别边界
    quantiles = torch.quantile(data.y, torch.tensor([0.5, 0.75]))
    # 根据分位数将连续值离散化为四个类别
    target = torch.zeros_like(data.y, dtype=torch.long)
    target[(data.y >= quantiles[0]) & (data.y < quantiles[1])] = 1
    target[(data.y >= quantiles[1])] = 2
    return target
def test_recall_k(k):
    predk = []
    targetk = []
    # 设置模型为评估模式
    model.eval()
    # 使用模型对输入数据进行前向传播
    out = model(data.x, data.edge_index)
    # 对输出进行argmax操作，在行的方向，取最大值所在的索引作为预测结果
    pred = out.argmax(dim=1)
    target = target_class(data)
    # 返回前k个预测为1的结果
    for i in range(len(pred)):
        if(k == 0):
            return predk , targetk
        if(pred[i] == 2):
            k=k-1
            predk = np.append(predk, pred[i])
            targetk = np.append(targetk, target[i])
# 平滑曲线
def moving_average(data, window_size):
    smoothed_data = []
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        end = i + 1
        smoothed_data.append(sum(data[start:end]) / len(data[start:end]))
    return smoothed_data

if __name__ == '__main__':
    # predk, targetk = test_recall_k(50)
    # print(predk)
    # print(targetk)
    # print('Recall@k: {:.4f}'.format(recall_score(targetk, predk, average='weighted')))
    k_list =[]
    for i in range(2):
        predk, targetk = test_recall_k(i)
        k = recall_score(targetk, predk, average='weighted')
        np.append(k_list,k)
        k_list.append(k)
    print(k_list)
    # k_list = k_list[18:40]
    # print(k_list[1])
    # print(k_list[10])
    # epochs = np.arange(1, len(k_list) + 1)
    # # 绘制折线图
    # plt.plot(epochs, k_list, c='green', label='recall@k')
    # # 为x轴和y轴添加标签
    # plt.xlabel('K')  # x轴标签
    # plt.ylabel('Recall@K')  # y轴标签
    # plt.show()
    # plt.savefig('dataset/local_img/6768_1_local_loss.png')
    val_losses = []
    val_accuracies = []
    ahead_loss = 100
    for epoch in range(epochs):
        loss, out = train(data)
        acc,recall = test(data)
        if(loss.item()<=1):
            val_losses.append(loss.item())
            val_accuracies.append(acc)
            ahead_loss = loss.item()
        # print('Epoch: {:03d}, accuray : {}, recall: {}'.format(epoch,acc, recall))
        print('Epoch: {:03d}, Loss: {:.4f}, accuray : {}, recall: {}'.format(epoch, loss.item(), acc,recall))
        if(acc >= 0.8):
            torch.save(model.state_dict(), 'dataset/local_model/6768_1_local_model.pth')
        # if(epoch == epochs-1):
        #     val_accuracies = moving_average(val_accuracies, 15)
        #     epochs = np.arange(1, len(val_accuracies) + 1)
        #     plt.plot(epochs, val_accuracies, c='green', label='Accuracies')
        #     plt.xlabel('Epoch')  # x轴标签
        #     plt.ylabel('Accuracies')  # y轴标签
        #     plt.savefig('dataset/local_img/6768_1_local_accuracies.png')
        #     plt.show()
        if(loss.item()>ahead_loss):
            epochs = np.arange(1, len(val_losses) + 1)
            plt.plot(epochs, val_losses, c='red', label='Validation Loss')
            plt.xlabel('Epoch')  # x轴标签
            plt.ylabel('Validation Loss')  # y轴标签
            plt.savefig('dataset/local_img/6768_1_local_loss.png')


    # epochs = np.arange(1, len(val_accuracies) + 1)
    # plt.plot(epochs, val_accuracies, c='green', label='Accuracies')
    # plt.xlabel('Epoch')  # x轴标签
    # plt.ylabel('Accuracies')  # y轴标签
    # plt.savefig('dataset/local_img/6768_1_local_accuracies.png')
    # plt.show()







