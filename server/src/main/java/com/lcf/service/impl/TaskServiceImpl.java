package com.lcf.service.impl;

import cn.hutool.json.JSONUtil;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.ServiceBase;
import com.lcf.service.TaskService;

import io.grpc.StatusRuntimeException;
import org.hyperledger.fabric.client.Contract;
import org.hyperledger.fabric.client.Gateway;
import org.hyperledger.fabric.client.GatewayException;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class TaskServiceImpl extends ServiceBase implements TaskService {

    private static String taskChaincodeName;
    private static String taskChannelName;
    private Gateway gateway;
    private Contract contract;

    public TaskServiceImpl() throws Exception {
        taskChaincodeName="task";
        taskChannelName="mychannel";
        gateway = FabricBasic.getGateway();
        contract=fetchContract(gateway,taskChannelName,taskChaincodeName);
    }

    @Override
    public JSONObject getTaskAll() {
        try {
            byte[] result = contract.evaluateTransaction("GetAllAssets");
            JSONObject resultJson = prettyJson(result);
            JSONArray allAssert = resultJson.getJSONArray("allAssert");
            JSONArray resultAssert = new JSONArray();
            if(allAssert!=null){
                allAssert.forEach(a->{
                    JSONObject jsonObject = JSONObject.parseObject(a.toString());
                    jsonObject.put("taskDetail", JSONUtil.parseObj((jsonObject.get("taskDetail").toString())));
                    resultAssert.add(jsonObject);
                });
            }
            resultJson.put("allAssert",resultAssert);
            resultJson.put("total", resultAssert.size());
            System.out.println("*** Result: " + resultJson);
            return resultJson;
        }catch (Exception e){
            e.printStackTrace();
            return null;
        }
    }

    @Override
    public ResponseDTO getTaskFinished() {
        JSONObject resultJson = getTaskAll();
        JSONArray allAssert = resultJson.getJSONArray("allAssert");
        JSONArray resultAssert=new JSONArray();;
        allAssert.forEach(a-> {
            JSONObject jsonObject = JSONObject.parseObject(a.toString());
            if(!jsonObject.get("taskReceiverId").equals("")) {
                resultAssert.add(jsonObject);
            }
        });
        resultJson.put("allAssert",resultAssert);
        return new ResponseDTO<>(resultJson);
    }



    @Override
    public ResponseDTO createTask(Task task) {
        try{
            byte[] submitResult=contract.submitTransaction(
                    "CreateAsset",task.getTaskDetail().toString(),task.getTaskCreatorId(),task.getTaskReceiverId(),task.getReceiveTime(),task.getTaskScore());
            System.out.println("*** Transaction committed successfully"+ prettyJson(submitResult));
        }catch (Exception e){
            return new ResponseDTO<>(e.getMessage());
        }
        return new ResponseDTO<>(200,"创建任务成功");
    }

    @Override
    public ResponseDTO updateTask(Task task) {
        try{
            byte[] submitResult=contract.submitTransaction("UpdateAsset", task.getTaskID(),task.getTaskDetail().toString(),task.getTaskCreatorId(),task.getTaskReceiverId(),task.getReceiveTime(),task.getTaskScore());
            System.out.println("*** Transaction update successfully"+ prettyJson(submitResult));
        }catch (Exception e){
            return new ResponseDTO<>(e.getMessage());
        }
        return new ResponseDTO<>(200,"更新任务成功");
    }

    @Override
    public void setTaskChaincodeName(String taskChaincodeName) {
        TaskServiceImpl.taskChaincodeName = taskChaincodeName;
    }

    @Override
    public void setTaskChannelName(String taskChannelName) {
        TaskServiceImpl.taskChannelName = taskChannelName;
    }


}
