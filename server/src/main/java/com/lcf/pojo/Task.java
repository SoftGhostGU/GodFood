package com.lcf.pojo;

import com.alibaba.fastjson2.JSONObject;
import lombok.Data;

import java.util.Map;

@Data
public final class Task {

    private String taskID;

    private JSONObject taskDetail;

    private String taskCreatorId;

    private String taskReceiverId;

    private String receiveTime;

    private String taskScore;

    private double latitude;

    private double longitude;

}
