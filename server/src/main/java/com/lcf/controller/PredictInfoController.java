package com.lcf.controller;

import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.databind.JsonNode;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.lcf.service.PredictInfoService;
import com.lcf.service.UserService;
import com.lcf.util.Weather;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.media.*;

import org.hyperledger.fabric.client.GatewayException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import static org.springframework.web.bind.annotation.RequestMethod.GET;
import static org.springframework.web.bind.annotation.RequestMethod.POST;

import java.util.List;

/**
 * 用户控制器
 *
 * @author lcfsm
 * @date 2023/08/16
 */
@Api(tags = { "预测信息页面" })
@RestController
@CrossOrigin(origins = "*")
public class PredictInfoController {

    @Autowired
    PredictInfoService predictInfoService;

    @ApiOperation(value = "预测信息展示", notes = "获取用户信息", httpMethod = "GET")
    @RequestMapping(value = "/predictInfo", method = GET)
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "header", name = "Authorization", value = "用户身份令牌", required = true, dataType = "string")
    })
    public ResponseDTO<JSONObject> getAllPredictInfo(@RequestHeader("Authorization") String token) throws Exception {
        return predictInfoService.getInfo(token);
    }

}
