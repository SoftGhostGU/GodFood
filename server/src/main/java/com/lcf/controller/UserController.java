package com.lcf.controller;



import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.lcf.service.UserService;
import com.lcf.util.JwtUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import org.hyperledger.fabric.client.GatewayException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;

import static org.springframework.web.bind.annotation.RequestMethod.GET;
import static org.springframework.web.bind.annotation.RequestMethod.POST;


/**
 * 用户控制器
 *
 * @author lcfsm
 * @date 2023/08/16
 */
@Api(tags = {"用户接口"})
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
            @ApiImplicitParam(paramType = "body", dataType = "User", name = "user", value = "用户", required = true)
    })
    @ApiOperation(value = "登录", notes = "登录", httpMethod = "POST")
    @RequestMapping(value = "/login", method = POST)
    public ResponseDTO<JSONObject> login(@RequestBody User user) {
        return userService.userLogin(user);
    }


    /**
     * 获取所有用户
     *
     * @return {@link ResponseDTO}<{@link JSONObject}>
     * @throws GatewayException 网关异常
     */
    @ApiOperation(value = "获取所有用户", notes = "获取所有用户", httpMethod = "GET")
    @RequestMapping(value = "/getUserAll", method = GET)
    public ResponseDTO<JSONObject> getUserAll() throws GatewayException {
        return userService.getUserAll();
    }

//    @RequestMapping(value = "/getUserDetail", method = GET)
//    public ResponseDTO<JSONObject> getUserAll(@RequestHeader("Authorization") String token) {
//        return userService.getUserDetail(token);
//    }


    /**
     * 用户注册
     *
     * @param user 用户
     * @return {@link ResponseDTO}<{@link Object}>
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "body", dataType = "User", name = "user", value = "用户", required = true)
    })
    @ApiOperation(value = "用户注册", notes = "用户注册", httpMethod = "POST")
    @RequestMapping(value = "/register", method = POST)
    public ResponseDTO<Object> register(@RequestBody User user) {
        return userService.createUser(user);
    }


    /**
     * 获取用户详细信息
     *
     * @return {@link ResponseDTO}<{@link JSONObject}>
     */
    @ApiImplicitParams({
            @ApiImplicitParam(paramType = "header", dataType = "string", name = "token", value = "", required = true)
    })
    @ApiOperation(value = "获取用户详细信息", notes = "获取用户详细信息", httpMethod = "GET")
    @RequestMapping(value = "info",method = GET)
    public ResponseDTO<JSONObject>getInfo(@RequestHeader("Authorization") String token){
       return userService.userInfo(token);
    }


    /**
     * 注销登录
     *
     * @return {@link ResponseDTO}<{@link Object}>
     */
    @ApiOperation(value = "注销登录", notes = "注销登录", httpMethod = "GET")
    @RequestMapping(value = "/sign_out",method = GET)
    public ResponseDTO<Object> loginOut(){
        return new ResponseDTO<>();
    }

}

