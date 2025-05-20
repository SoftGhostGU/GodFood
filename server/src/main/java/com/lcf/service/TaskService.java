package com.lcf.service;

import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import org.hyperledger.fabric.client.GatewayException;


public interface TaskService {

    public JSONObject getTaskAll() ;

    public ResponseDTO createTask(Task task) ;

    public ResponseDTO updateTask(Task task) ;

    public ResponseDTO getTaskFinished();

    public void setTaskChaincodeName(String taskChaincodeName);

    public void setTaskChannelName(String taskChannelName);

}
