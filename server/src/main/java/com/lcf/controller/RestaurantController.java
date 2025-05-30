package com.lcf.controller;

import cn.hutool.core.date.DateUnit;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.IdUtil;
import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Task;
import com.lcf.service.RestaurantService;
import com.lcf.service.TaskService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import springfox.documentation.annotations.ApiIgnore;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

@Api(tags = { "餐厅接口" })
@RestController
@CrossOrigin(origins = "*")
public class RestaurantController {

    @Autowired
    RestaurantService restaurantService;

    /**
     * 获取所有餐厅
     *
     * @return {@link ResponseDTO}
     */
    @ApiOperation(value = "获取所有餐厅", notes = "获取所有餐厅", httpMethod = "GET")
    @GetMapping("getAllRestaurants")
    @ApiIgnore
    public ResponseDTO getAllRestaurants() {
        return new ResponseDTO(restaurantService.getAllRestaurants());
    }

    @ApiOperation(value = "根据预测信息获取餐厅", notes = "根据预测信息获取餐厅", httpMethod = "POST")
    @ApiImplicitParam(name = "token", value = "用户身份令牌", required = true, dataType = "String", paramType = "header")
    @PostMapping("getRestaurantsByPredict")
    public ResponseDTO getRestaurantsByPredict(@RequestHeader String token) throws Exception {
        return new ResponseDTO(restaurantService.getRestaurantsByPredict(token));
    }

    @ApiOperation(value = "根据餐厅ID获取餐厅信息", notes = "根据餐厅ID获取餐厅信息", httpMethod = "GET")
    @ApiImplicitParam(name = "restaurantID", value = "餐厅ID", required = true, dataType = "String", paramType = "query")
    @GetMapping("getRestaurantById")
    @ApiIgnore
    public ResponseDTO getRestaurantById(@RequestParam String restaurantID) {
        return new ResponseDTO(restaurantService.getRestaurantById(restaurantID));
    }

}
