package com.lcf.controller;

import com.lcf.dto.ResponseDTO;
import com.lcf.service.RestaurantService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.*;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/restaurant")
@Tag(name = "餐厅接口", description = "餐厅相关操作")
public class RestaurantController {

    @Autowired
    RestaurantService restaurantService;

    @Operation(summary = "获取所有餐厅")
    @GetMapping("/getAll")
    public ResponseDTO getAllRestaurants() {
        return new ResponseDTO(restaurantService.getAllRestaurants());
    }

    @Operation(summary = "根据预测信息获取餐厅")
    @ApiResponse(responseCode = "200", description = "返回匹配的餐厅列表", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"OK\", \"data\": [\"餐厅A\", \"餐厅B\"]}")))
    @PostMapping("/predict")
    public ResponseDTO getRestaurantsByPredict(
            @Parameter(description = "预测输入信息", required = true, example = "适合情侣晚餐") @RequestParam String info)
            throws Exception {
        return new ResponseDTO(restaurantService.getRestaurantsByPredict(info));
    }

    @Operation(summary = "根据餐厅ID获取餐厅信息")
    @ApiResponse(responseCode = "200", description = "返回指定餐厅信息", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"message\": \"OK\", \"data\": {\"name\": \"小南国\", \"location\": \"浦东新区\"}}")))
    @GetMapping("/getById")
    public ResponseDTO getRestaurantById(
            @Parameter(description = "餐厅ID", required = true, example = "rest_1001") @RequestParam String restaurantID) {
        return new ResponseDTO(restaurantService.getRestaurantById(restaurantID));
    }
}
