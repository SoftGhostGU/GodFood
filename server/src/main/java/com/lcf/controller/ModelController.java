package com.lcf.controller;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.ModelService;
import com.lcf.service.TaskService;
import io.swagger.annotations.Api;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Api(tags = {"模型接口"})
@RestController
public class ModelController {

    @Autowired
    ModelService modelService;

    //上传本地模型
    @GetMapping("loadModel")
    public ResponseDTO loadModel() {
        try {
            modelService.loadModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("加载本地模型成功");
    }

    //下载通道模型
    @GetMapping("updateModel")
    public ResponseDTO updateModel() {
        try {
            modelService.updateModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("更新本地模型成功");
    }

    //基于社交关系模型初始化
    @GetMapping("initModel")
    public ResponseDTO initModel() {
        try {
            modelService.initModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("基于社交关系模型初始化成功");
    }

    //模型预测
    @GetMapping("predict")
    public ResponseDTO predict() {
        try {
            String tasks = modelService.predict();
            JSONObject json = JSONObject.parseObject(tasks);

            List<Task> taskList = JSON.parseArray(json.toJSONString(), Task.class);
            return new ResponseDTO(modelService.conditionAware(taskList));
        } catch (Exception e) {
            e.printStackTrace();

        }
        return new ResponseDTO("模型预测失败");
    }
}
