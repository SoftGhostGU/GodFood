import numpy as np
import torch.optim.adam
import model1
import train
from flask import Flask, request, jsonify
import recall_test
import dataset_dispose
import check_friend
import torch_geometric.data
from sklearn.metrics import recall_score
import matplotlib.pyplot as plt
app = Flask(__name__)

#加载模型网络结构
model = model1.gcn_model(in_channels=133,hidden_channel=512,out_channels=3)

#加载模型参数
model.load_state_dict(torch.load('dataset/local_model/6768_1_local_model.pth'))

#设置为评估模式
model.eval()

#使用flask框架搭建web服务，实现数据的接收和处理
@app.route('/predict', methods=['POST'])
def predict():
    #接收前端发送的数据
    data = request.get_json()
    pass



#数据预处理和模型训练
@app.route('/preprocessAndTrain', methods=['POST'])
def preprocess():
    dataset_dispose.DisposeCheckinDataset(root='dataset/')
    data, silce = torch.load('dataset\\checkin_data\\6768.pt')
    train.train(data)




#发送本地模型参数
@app.route('/loadModel', methods=['POST'])
def send_model():
    # 设置隐私预算
    epsilon = 1.0
    delta = 1e-5
    # 计算敏感度
    dummy_data = torch.randn(10, 133)
    # 给模型参数加噪
    recall_test.add_local_differential_privacy(model, epsilon, delta, dummy_data)
    # 将模型参数转换为可以JSON序列化的格式
    model_state_dict = {k: v.detach().cpu().numpy().tolist() for k, v in model.state_dict().items()}

    # 返回JSON响应
    return jsonify({'model': model_state_dict})



#接收通道模型参数，更新本地模型
@app.route('/update_model', methods=['POST'])
def upload_model():
    model.load_state_dict(request.get_json())
    torch.save(model.state_dict(), 'dataset/local_model/6768_1_local_model.pth')
    return "Model uploaded successfully!"



#查询用户数据集特征大小
@app.route('/get_dataset_feature_size', methods=['POST'])
def get_dataset_feature_size():
    return check_friend.get_dataset_feature_size()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)