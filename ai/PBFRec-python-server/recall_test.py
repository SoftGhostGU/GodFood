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
model.load_state_dict(torch.load('dataset/local_model/6768_1_local_model.pth'))

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
def target_class(data):
    # 计算分位数来定义类别边界
    quantiles = torch.quantile(data.y, torch.tensor([0.5, 0.75]))

    # 根据分位数将连续值离散化为四个类别
    # 注意：这里我们简单地使用分位数作为阈值，但在实践中可能需要更精细的处理
    # （例如，处理边界值或使用更复杂的离散化方法）
    target = torch.zeros_like(data.y, dtype=torch.long)
    target[(data.y >= quantiles[0]) & (data.y < quantiles[1])] = 1
    target[(data.y >= quantiles[1])] = 2
    return target

# 更精确的敏感度计算函数示例
def calculate_sensitivity(model, data):
    # 这里简单假设敏感度为模型参数的最大绝对值
    all_params = torch.cat([param.view(-1) for param in model.parameters()])
    return torch.max(torch.abs(all_params)).item()
# 扰动差分隐私方法-概率p
def calculate_probability(li, li_prime, n, epsilon):
    """
    根据给定的公式计算概率
    :param li: 当前标签
    :param li_prime: 预测标签
    :param n: 类别总数
    :param epsilon: 噪声参数
    :return: 概率值
    """
    if li == li_prime:
        return np.exp(epsilon) / (n - 1 + np.exp(epsilon))
    else:
        return 1 / (n - 1 + np.exp(epsilon))
# 本地差分隐私加噪函数（使用高斯机制）
def add_local_differential_privacy(model, epsilon, delta, data):
    """
    :param model: 加载好的模型
    :param epsilon: 隐私预算，值越小，隐私保护程度越高
    :param delta: 松弛参数，通常是一个非常小的正数
    :param data: 用于计算敏感度的数据
    """
    n = len(model.parameters().data)  # 总数
    sensitivity = calculate_sensitivity(model, data)
    # 高斯机制的标准差计算
    std_dev = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon
    for param in model.parameters():
        noise = torch.normal(0, std_dev, param.shape)
        li = param.data
        li_prime = param.data + noise
        probability = calculate_probability(li, li_prime, n, epsilon)
        # 生成0到1之间的随机数
        random_number = np.random.rand()
        # 如果随机数小于概率，则添加噪声
        if random_number < probability:
            param.data = li_prime

if __name__ == '__main__':
    # 设置隐私预算
    epsilon = 1.0
    delta = 1e-5

    # 假设这里有一些数据用于计算敏感度
    # 实际使用时，需要替换为真实的训练数据
    dummy_data = torch.randn(10, 133)
    # 给模型参数加噪
    add_local_differential_privacy(model, epsilon, delta, dummy_data)
    k_list =[]
    for i in range(50):
        predk, targetk = test_recall_k(i)
        k = recall_score(targetk, predk, average='weighted')
        np.append(k_list,k)
        k_list.append(k)
    print(k_list)