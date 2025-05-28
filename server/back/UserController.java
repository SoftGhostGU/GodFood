package com.lcf.controller;

import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.lcf.service.UserService;
import com.lcf.util.Weather;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.*;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;

import org.hyperledger.fabric.client.GatewayException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@Tag(name = "用户管理", description = "用户相关接口")
public class UserController {

    @Autowired
    UserService userService;

    @Operation(summary = "登录")
    @ApiResponse(responseCode = "200", description = "登录成功", content = @Content(mediaType = "application/json", examples = @ExampleObject(value = "{\"code\": 0, \"msg\": \"OK\"}")))
    @PostMapping("/login")
    public ResponseDTO<JSONObject> login(
            @Parameter(description = "用户邮箱", required = true, example = "test@example.com") @RequestParam String email,
            @Parameter(description = "用户密码", required = true, example = "123456") @RequestParam String password) {
        return userService.userLogin(email, password);
    }

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public ResponseDTO<Object> register(
            @Parameter(description = "用户名", required = true, example = "Tom") @RequestParam String userName,
            @Parameter(description = "邮箱", required = true, example = "tom@example.com") @RequestParam String email,
            @Parameter(description = "密码", required = true, example = "pass123") @RequestParam String password)
            throws GatewayException {
        return userService.createUser(userName, email, password);
    }

    @Operation(summary = "获取用户自己的详细信息")
    @GetMapping("/info")
    public ResponseDTO<User> getInfo(
            @Parameter(description = "Token", example = "Bearer {token}", required = true) @RequestHeader("Authorization") String token)
            throws Exception {
        return userService.getUserDetail(token);
    }

    @Operation(summary = "注销登录")
    @GetMapping("/sign_out")
    public ResponseDTO<Object> loginOut() {
        return new ResponseDTO<>();
    }

    @Operation(summary = "获取当前天气")
    @GetMapping("/getWeather")
    public ResponseDTO<JSONObject> getWeather(
            @Parameter(description = "位置", example = "310000") @RequestParam int location) {
        return new ResponseDTO<>(Weather.getCurrentWeather(location));
    }

    @Operation(summary = "更新用户信息")
    @PostMapping("/updateUser")
    public ResponseDTO<Object> updateUser(
            @Parameter(description = "用户Token", example = "Bearer {token}", required = true) @RequestHeader("Authorization") String token,

            @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "用户信息", required = true, content = @Content(mediaType = "application/json", schema = @Schema(implementation = User.class), examples = @ExampleObject(value = "{\"name\":\"Alice\", \"email\":\"alice@example.com\"}"))) @RequestBody User user)
            throws Exception {
        return userService.updateUser(token, user);
    }
}
