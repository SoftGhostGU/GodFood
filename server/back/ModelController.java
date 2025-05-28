package com.lcf.controller;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.ModelService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Tag(name = "模型接口", description = "模型相关操作")
@RestController
@RequestMapping("/api/model")
public class ModelController {

    @Autowired
    ModelService modelService;

    @Operation(summary = "加载本地模型")
    @ApiResponse(responseCode = "200", description = "加载成功", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"加载本地模型成功\"}")))
    @GetMapping("/load")
    public ResponseDTO loadModel() {
        try {
            modelService.loadModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("加载本地模型成功");
    }

    @Operation(summary = "更新本地模型")
    @ApiResponse(responseCode = "200", description = "更新成功", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"更新本地模型成功\"}")))
    @GetMapping("/update")
    public ResponseDTO updateModel() {
        try {
            modelService.updateModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("更新本地模型成功");
    }

    @Operation(summary = "模型初始化（基于社交关系）")
    @ApiResponse(responseCode = "200", description = "初始化成功", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"初始化成功\"}")))
    @GetMapping("/init")
    public ResponseDTO initModel() {
        try {
            modelService.initModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("基于社交关系模型初始化成功");
    }

    @Operation(summary = "模型预测")
    @ApiResponse(responseCode = "200", description = "返回预测任务列表", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"预测成功\", \"data\": [{...}]}")))
    @GetMapping("/predict")
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
