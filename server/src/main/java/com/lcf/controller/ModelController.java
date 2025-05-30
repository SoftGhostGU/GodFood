package com.lcf.controller;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import com.github.xiaoymin.knife4j.annotations.Ignore;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.pojo.UserReview;
import com.lcf.service.ModelService;
import com.lcf.service.TaskService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import springfox.documentation.annotations.ApiIgnore;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import static org.springframework.web.bind.annotation.RequestMethod.POST;

import java.util.List;

@Api(tags = { "模型接口" })
@RestController
@CrossOrigin(origins = "*")
public class ModelController {

    @Autowired
    ModelService modelService;

    // 上传本地模型
    @ApiIgnore
    @GetMapping("loadModel")
    public ResponseDTO loadModel() {
        try {
            modelService.loadModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("加载本地模型成功");
    }

    // 下载通道模型
    @ApiIgnore
    @GetMapping("updateModel")
    public ResponseDTO updateModel() {
        try {
            modelService.updateModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("更新本地模型成功");
    }

    // 基于社交关系模型初始化
    @ApiIgnore
    @GetMapping("initModel")
    public ResponseDTO initModel() {
        try {
            modelService.initModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new ResponseDTO("基于社交关系模型初始化成功");
    }

    // 模型预测
    @ApiIgnore
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

    @ApiOperation(value = "训练模型（餐厅打卡）", notes = "触发模型的训练以及聚合过程（餐厅打卡）", httpMethod = "POST")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "token", value = "用户令牌", required = true, dataType = "String", paramType = "header")
    })
    @RequestMapping(value = "/train", method = POST)
    public ResponseDTO<String> trainPredictModel(@RequestHeader String token, @RequestBody UserReview info)
            throws Exception {
        return new ResponseDTO<>(200, modelService.train(info, token));
    }
}
