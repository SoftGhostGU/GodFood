package com.lcf.service;

import com.lcf.pojo.Task;

import java.util.List;

public interface ModelService {
    //加载本地模型
    void loadModel() throws Exception;
    //更新本地模型
    void updateModel() throws Exception;
    //数据预处理和模型训练
    void preprocessAndTrain() throws Exception;
    //基于社交关系模型初始化
    void initModel();
    //模型预测
    String predict() throws Exception;
    //条件感知
    List<Task> conditionAware(List<Task> pre_results);
}
