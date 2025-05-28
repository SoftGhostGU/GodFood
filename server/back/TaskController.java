package com.lcf.controller;

import cn.hutool.core.date.DateUnit;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.IdUtil;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.*;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/api/task")
@Tag(name = "任务管理", description = "任务相关操作")
public class TaskController {

    @Autowired
    TaskService taskService;

    @Operation(summary = "获取所有任务")
    @GetMapping("/getTaskAll")
    public ResponseDTO getTaskAll() {
        return new ResponseDTO(taskService.getTaskAll());
    }

    @Operation(summary = "获取已完成任务")
    @GetMapping("/getTaskFinished")
    public ResponseDTO getTaskFinished() {
        return taskService.getTaskFinished();
    }

    @Operation(summary = "提交任务")
    @PostMapping("/submitTask")
    @ApiResponse(responseCode = "200", description = "任务提交成功", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"提交成功\"}")))
    public ResponseDTO createTask(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "任务对象", required = true, content = @Content(mediaType = "application/json", schema = @Schema(implementation = Task.class), examples = @ExampleObject(value = "{\"taskCreatorId\":\"boss\", \"taskDetail\":{\"area\":\"上海宝山\", \"content\":\"去超市买东西\"}}"))) @RequestBody Task task) {

        Date start = new Date();
        ResponseDTO result = taskService.createTask(task);
        Date end = new Date();
        long tests = DateUtil.between(start, end, DateUnit.SECOND);
        System.out.println(tests);
        return result;
    }

    @Operation(summary = "任务抢单")
    @PostMapping("/obtainTask")
    public ResponseDTO obtainTask(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "任务对象", required = true, content = @Content(schema = @Schema(implementation = Task.class))) @RequestBody Task task) {
        task.setReceiveTime(DateUtil.now());
        return taskService.updateTask(task);
    }

    @Operation(summary = "更新任务")
    @PostMapping("/updateTask")
    public ResponseDTO updateTask(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "任务对象", required = true, content = @Content(schema = @Schema(implementation = Task.class))) @RequestBody Task task) {
        return taskService.updateTask(task);
    }

    @Operation(summary = "批量提交测试任务")
    @GetMapping("/submitTaskTest")
    public ResponseDTO createTaskTest(
            @Parameter(description = "生成任务数", example = "5") @RequestParam("num") int num) {

        Date start = new Date();
        long startTime = System.currentTimeMillis();
        long timeLimit = 300000; // 5分钟
        AtomicInteger loopCount = new AtomicInteger(0);

        List<Task> test = generateTestTaskList(num);
        for (int i = 0; i < num; i++) {
            if ((System.currentTimeMillis() - startTime) >= timeLimit) {
                System.out.println("在规定的 " + timeLimit + " 毫秒内，共进行了 " + loopCount + " 次循环");
                break;
            }
            Task t = test.get(i);
            taskService.createTask(t);
            loopCount.incrementAndGet();
        }
        Date end = new Date();
        long tests = DateUtil.between(start, end, DateUnit.SECOND);
        System.out.println(tests);
        return new ResponseDTO("事务花费时间为：" + tests);
    }

    public static List<Task> generateTestTaskList(int size) {
        List<Task> taskList = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            JSONObject taskDetail = new JSONObject();
            taskDetail.put("area", "上海宝山");
            taskDetail.put("mode", "线下交付");
            taskDetail.put("money", "100");
            taskDetail.put("deadline", "2024-08-14 07:27:05");
            taskDetail.put("content", "去汉堡王，买个大号的披萨");
            taskDetail.put("type", "跑腿");
            taskDetail.put("dateEnd1", "2024-08-14");
            taskDetail.put("dateEnd2", "07:27:05");
            taskDetail.put("specialRequirement", "多加辣椒");

            Task task = new Task();
            task.setTaskID(IdUtil.simpleUUID());
            task.setTaskDetail(taskDetail);
            task.setTaskCreatorId("boss");
            task.setTaskReceiverId("");
            task.setReceiveTime("");
            task.setTaskScore("");

            taskList.add(task);
        }
        return taskList;
    }
}