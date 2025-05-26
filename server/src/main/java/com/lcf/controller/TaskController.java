package com.lcf.controller;

import cn.hutool.core.date.DateUnit;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.IdUtil;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.TaskService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

@Api(tags = {"任务接口"})
@RestController
public class TaskController {

    @Autowired
    TaskService taskService;

    /**
     * 获取所有任务
     *
     * @return {@link ResponseDTO}
     */
    @ApiOperation(value = "获取所有任务", notes = "获取所有任务", httpMethod = "GET")
    @GetMapping("getTaskAll")
    public ResponseDTO getTaskAll(){
        return new ResponseDTO(taskService.getTaskAll());
    }

    /**
     * 获取已完成任务
     *
     * @return {@link ResponseDTO}
     */
    @ApiOperation(value = "获取已完成任务", notes = "获取已完成任务", httpMethod = "GET")
    @GetMapping("getTaskFinished")
    public ResponseDTO getTaskFinished(){
        return taskService.getTaskFinished();
    }

    /**
     * 提交任务
     *
     * @param task 任务
     * @return {@link ResponseDTO}
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "body", dataType = "com.lcf.pojo.Task", name = "task", value = "任务", required = true)
    })
    @ApiOperation(value = "提交任务", notes = "提交任务", httpMethod = "POST")
    @PostMapping("submitTask")
    public ResponseDTO createTask(@RequestBody Task task){
        // 记录程序开始时间
        Date start = new Date();
        ResponseDTO result = taskService.createTask(task);
        Date end = new Date();
        long tests = DateUtil.between(start,end, DateUnit.SECOND);
        System.out.println(tests);
        return result;
    }

    /**
     * 任务抢单
     *
     * @param task 任务
     * @return {@link ResponseDTO}
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "body", dataType = "com.lcf.pojo.Task", name = "task", value = "任务", required = true)
    })
    @ApiOperation(value = "任务抢单", notes = "抢单", httpMethod = "POST")
    @PostMapping("obtainTask")
    public ResponseDTO obtainTask(@RequestBody Task task){
        task.setReceiveTime(DateUtil.now());
        return taskService.updateTask(task);
    }

    /**
     * 更新任务
     *
     * @param task 任务
     * @return {@link ResponseDTO}
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "body", dataType = "com.lcf.pojo.Task", name = "task", value = "任务", required = true)
    })
    @ApiOperation(value = "更新任务", notes = "更新任务", httpMethod = "POST")
    @PostMapping("updateTask")
    public ResponseDTO updateTask(@RequestBody Task task){
        return taskService.updateTask(task);
    }


    @GetMapping("submitTask")
    public ResponseDTO createTaskTest(@RequestParam("num")int num){
        // 记录程序开始时间
        Date start = new Date();
        long startTime = System.currentTimeMillis();
        long timeLimit = 300000; // 规定时间 5 秒（以毫秒为单位）
        AtomicInteger loopCount = new AtomicInteger(0);
        List<Task>test = generateTestTaskList(num);
        for(int i =0 ;i<num;i++){
            if((System.currentTimeMillis() - startTime) >= timeLimit){
                System.out.println("在规定的 " + timeLimit + " 毫秒内，共进行了 " + loopCount + " 次循环");
                break;
            }
            Task t = test.get(i);
            ResponseDTO result = taskService.createTask(t);
            loopCount.incrementAndGet();
        }
        Date end = new Date();
        long tests = DateUtil.between(start,end, DateUnit.SECOND);
        System.out.println(tests);
        return new ResponseDTO("事务花费时间为："+tests);
    }



    public static List<Task> generateTestTaskList(int size) {
        List<Task> taskList = new ArrayList<>();
        for(int i = 0; i<size; i++){
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
