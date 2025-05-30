package com.lcf.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.http.HttpUtil;
import cn.hutool.http.body.RequestBody;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.pojo.User;
import com.owlike.genson.Genson;
import com.lcf.pojo.UserReview;
import com.lcf.service.ModelService;
import com.lcf.service.ServiceBase;
import com.lcf.service.TaskService;
import com.lcf.util.DijkstraAlgorithm;
import com.lcf.util.DistanceCalculator;
import com.lcf.util.JwtUtil;

import lombok.extern.slf4j.Slf4j;
import org.hyperledger.fabric.client.Contract;
import org.hyperledger.fabric.client.Gateway;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class ModelServiceImpl extends ServiceBase implements ModelService {
    private static String modelChaincodeName;
    private static String modelChannelName;
    private Gateway gateway;
    private Contract contract;
    private final Genson genson = new Genson();

    @Autowired
    private TaskService taskService;

    public ModelServiceImpl() throws Exception {
        modelChaincodeName = "model";
        modelChannelName = "mychannel";
        gateway = FabricBasic.getGateway();
        contract = fetchContract(gateway, modelChannelName, modelChaincodeName);
    }

    /**
     * 用于加载模型，并上传至区块链
     */
    @Override
    public void loadModel() throws Exception {
        // 调用本地模型加载接口，获取本地模型数据
        String model = postRequest("http://localhost:5000/loadModel", "");
        // 调用数据集特征大小接口，获取用户特征大小
        String featureSize = postRequest("http://localhost:5000/get_dataset_feature_size", "");
        // 上链
        try {
            byte[] submitResult = contract.submitTransaction(
                    "CreateModel", model, featureSize);
            System.out.println("*** Transaction committed successfully" + prettyJson(submitResult));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * 更新模型
     *
     * 重写此方法以在需要时更新模型。
     */
    @Override
    public void updateModel() throws Exception {
        // 下载通道模型
        byte[] result = contract.evaluateTransaction("GetAllAssets");
        JSONObject resultJson = prettyJson(result);
        JSONArray allAssert = resultJson.getJSONArray("allAssert");
        // 更新本地模型
        String model = postRequest("http://localhost:5000/updateModel", allAssert.toString());
    }

    @Override
    public String train(UserReview info, String token) throws Exception {
        // 解析token，获取用户email
        String email = JwtUtil.validateToken(token);
        // 将info存储在本地文件中，当文件中有两条记录时，触发本地模型训练
        String filePath = "user_reviews.json";
        List<UserReview> reviews = new ArrayList<>();
        java.io.File file = new java.io.File(filePath);
        if (file.exists()) {
            try (java.io.FileReader reader = new java.io.FileReader(file);
                    java.io.BufferedReader br = new java.io.BufferedReader(reader)) {
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }
                if (!sb.toString().isEmpty()) {
                    reviews = com.alibaba.fastjson2.JSON.parseArray(sb.toString(), UserReview.class);
                }
            }
        }
        reviews.add(info);
        try (java.io.FileWriter writer = new java.io.FileWriter(filePath, false)) {
            writer.write(JSONArray.toJSONString(reviews));
        }
        if (reviews.size() >= 2) {
            System.out.println(UserReview.toCsvJson(reviews));
            // 触发本地模型训练
            postRequest("http://localhost:5000/train_user_model",
                    UserReview.toCsvJson(reviews));
            // 清空文件
            try (java.io.FileWriter writer = new java.io.FileWriter(filePath, false)) {
                writer.write("");
            }

            // 获取本地模型数据
            String res = HttpUtil.get("http://localhost:5000/get_global_model");
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode modelData = objectMapper.readTree(res);
            // System.out.println(modelData);
            // 将本地模型推到区块链上
            String modelDataStr = objectMapper.writeValueAsString(modelData.get("model_weights"));
            byte[] submitResult = contract.submitTransaction("CreateModel", modelDataStr,
                    modelData.get("input_dim").toString(), email);
            // fetch the aggregated model on the blockchain
            // 链上聚合模型并获取聚合后的模型
            byte[] aggResult = contract.evaluateTransaction("aggregateModels");
            // 更新本地模型...

            return new String("Successfully trained model and updated blockchain with new aggregated model");

        }
        return "Model training not triggered, need at least 2 records";
    }

    /**
     * 初始化模型的方法。
     *
     * 这是一个重写的方法，用于初始化模型。
     *
     * @return 无返回值
     */
    @Override
    public void initModel() {
        // 调用智能合约初始化模型
        try {
            // 初始化
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * 进行预测
     *
     * <p>
     * 该方法是重写方法，用于执行预测操作。
     * </p>
     *
     * @return 无返回值
     */
    @Override
    public String predict() throws Exception {
        JSONObject result = taskService.getTaskAll();
        return postRequest("http://localhost:5000/predict", result.toString());
    }

    /**
     * 重写conditionAware方法
     *
     */
    @Override
    public List<Task> conditionAware(List<Task> tasks) {
        ArrayList<Task> pre_tasks = new ArrayList<>();
        // 以最近的一次任务记录作为当前位置
        JSONObject first_task = taskService.getTaskAll().getJSONArray("allAssert").getJSONObject(0);
        // 将task_h转化为List<Task>
        first_task.get("latitude");
        first_task.get("longitude");
        Task task_one = new Task();
        task_one.setLatitude(Double.parseDouble(first_task.get("latitude").toString()));
        task_one.setLongitude(Double.parseDouble(first_task.get("longitude").toString()));
        pre_tasks.add(task_one);
        pre_tasks.addAll(tasks);

        // 构建图
        int n = tasks.size();
        int[][] graph = new int[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double distance = DistanceCalculator.calculateDistance(tasks.get(i), tasks.get(j));
                graph[i][j] = (int) distance;
                graph[j][i] = (int) distance;
            }
        }

        // 使用迪杰斯特拉算法找到最短路径
        List<Integer> shortestPath = DijkstraAlgorithm.dijkstra(graph, 0);

        // 根据最短路径顺序返回任务列表
        List<Task> shortestTaskList = new ArrayList<>();
        for (int index : shortestPath) {
            shortestTaskList.add(tasks.get(index));
        }
        return shortestTaskList;
    }

    /**
     * 发送POST请求
     *
     * @param url  请求地址
     * @param json 请求体
     * @return 请求结果，处理成json的形式
     * @throws Exception
     */
    public String postRequest(String url, String json) throws Exception {
        HttpResponse response = HttpRequest.post(url)
                .body(json)
                .execute();
        if (!response.isOk()) {
            log.error("POST request failed with status code: {}", response.getStatus());
            throw new Exception("Unexpected code " + response.getStatus());
        }
        log.info("Received response with status code: {}", response.getStatus());

        return response.body();
    }

    /**
     * 发送GET请求
     *
     * @param url 请求地址
     * @return 请求结果，处理成json的形式
     * @throws Exception
     */
    public String getRequest(String url) throws Exception {
        HttpResponse response = HttpRequest.get(url)
                .execute();
        if (!response.isOk()) {
            log.error("GET request failed with status code: {}", response.getStatus());
            throw new Exception("Unexpected code " + response.getStatus());
        }
        log.info("Received response with status code: {}", response.getStatus());
        return response.body();
    }
}
