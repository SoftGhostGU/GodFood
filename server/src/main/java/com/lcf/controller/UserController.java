package com.lcf.controller;

import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.databind.JsonNode;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
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
@Api(tags = { "用户接口" })
@RestController
public class UserController {

    @Autowired
    UserService userService;

    /**
     * 登录
     *
     * @param user 用户
     * @return {@link ResponseDTO}<{@link JSONObject}>
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "query", name = "email", value = "用户邮箱", required = true, dataType = "string"),
            @ApiImplicitParam(paramType = "query", name = "password", value = "用户密码", required = true, dataType = "string")
    })
    @ApiOperation(value = "登录", notes = "登录", httpMethod = "POST", response = JSONObject.class)
    @RequestMapping(value = "/login", method = POST)
    public ResponseDTO<JSONObject> login(@RequestParam String email, @RequestParam String password) {
        return userService.userLogin(email, password);
    }

    /**
     * 用户注册
     *
     * @param user 用户
     * @return {@link ResponseDTO}<{@link Object}>
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "query", dataType = "string", name = "userName", value = "用户名", required = true),
            @ApiImplicitParam(paramType = "query", dataType = "string", name = "email", value = "邮箱", required = true),
            @ApiImplicitParam(paramType = "query", dataType = "string", name = "password", value = "密码", required = true)
    })
    @ApiOperation(value = "用户注册", notes = "用户注册", httpMethod = "POST")
    @RequestMapping(value = "/register", method = POST)
    public ResponseDTO<Object> register(@RequestParam String userName, @RequestParam String email,
            @RequestParam String password) throws GatewayException {
        return userService.createUser(userName, email, password);
    }

    /**
     * 获取用户详细信息
     *
     * @return {@link ResponseDTO}<{@link JSONObject}>
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "header", dataType = "string", name = "Authorization", value = "Token", required = true, defaultValue = "Bearer {token}")
    })
    @ApiOperation(value = "获取用户自己的详细信息", notes = "获取用户详细信息", httpMethod = "GET")
    @RequestMapping(value = "info", method = GET)
    public ResponseDTO<JSONObject> getInfo(@RequestHeader("Authorization") String token) throws Exception {
        return userService.getUserDetail(token);
    }

    @ApiOperation(value = "获取当前天气", notes = "获取当前天气", httpMethod = "GET")
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "query", name = "location", value = "位置", required = true, dataType = "string")
    })
    @RequestMapping(value = "/getWeather", method = GET)
    public ResponseDTO<JsonNode> getWeather(@RequestParam String location) {
        return new ResponseDTO<JsonNode>(Weather.getCurrentWeather(location));
    }

    @ApiOperation(value = "更新用户信息", notes = "更新用户信息", httpMethod = "POST")
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "header", name = "Authorization", value = "用户token", required = true, dataType = "string")
    })
    @RequestMapping(value = "/updateUser", method = POST)
    public ResponseDTO<Object> updateUser(
            @RequestHeader("Authorization") String token,
            @ApiParam(value = "用户信息", required = true) @RequestBody User user) throws Exception {
        return userService.updateUser(token, user);
    }

    @ApiOperation(value = "获取所有用户", notes = "获取所有用户列表", httpMethod = "GET")
    @RequestMapping(value = "/users", method = GET)
    public ResponseDTO<JSONObject> getAllUsers() throws Exception {
        return userService.getAllUsers();
    }

}
