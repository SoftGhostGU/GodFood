package com.lcf.service.impl;

import com.alibaba.fastjson2.JSONException;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonParseException;
import com.google.gson.JsonObject;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.lcf.service.ServiceBase;
import com.lcf.service.UserService;
import com.lcf.util.JwtUtil;
import io.grpc.StatusRuntimeException;

import java.util.List;

import org.hyperledger.fabric.client.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import com.owlike.genson.Genson;

/**
 * <p>
 * 服务实现类
 * </p>
 *
 * @author lcf
 * @since 2022-12-02
 */
@Service
public class UserServiceImpl extends ServiceBase implements UserService {

    private static String userChaincodeName;
    private static String userChannelName;
    private final Genson genson = new Genson();
    private Gateway gateway;
    private Contract contract;

    public UserServiceImpl() throws Exception {
        userChaincodeName = "user";
        userChannelName = "mychannel";
        gateway = FabricBasic.getGateway();
        contract = fetchContract(gateway, userChannelName, userChaincodeName);
    }

    @Override
    public ResponseDTO createUser(String userName, String email, String password) throws GatewayException {
        BCryptPasswordEncoder bCryptPasswordEncoder = new BCryptPasswordEncoder();
        String encodePwd = bCryptPasswordEncoder.encode(password);
        User user = User.builder()
                .userID(JwtUtil.generateUserId())
                .userName(userName)
                .email(email)
                .passWord(encodePwd)
                .build();
        try {
            byte[] evaluateResult = contract.evaluateTransaction("UserExists", user.getEmail());
            Boolean userExists = genson.deserialize(evaluateResult, Boolean.class);
            if (userExists) {
                // 用户已存在
                System.out.println("*** User already exists: " + user.getEmail());
                return new ResponseDTO<>("用户已存在，不能重复注册");
            }
            System.out.println("\n--> Submit Create Transaction");
            String sortedJson = genson.serialize(user);
            System.out.println("*** Create User JSON: " + sortedJson);
            byte[] submitResult = contract.submitTransaction("CreateUser", user.getEmail(), sortedJson);
            System.out.println("*** Create Result:" + new String(submitResult));
        } catch (Exception e) {
            if (e instanceof JsonParseException || e instanceof JSONException) {
                return new ResponseDTO<>("JSON解析错误，请检查输入格式");
            } else if (e instanceof StatusRuntimeException) {
                return new ResponseDTO<>("网络异常，请稍后再试");
            } else {
                e.printStackTrace();
                return new ResponseDTO<>(e.getMessage());
            }
        }
        return new ResponseDTO<>(200, "注册成功");
    }

    @Override
    public ResponseDTO userLogin(String email, String password) {
        System.out.println("用户登录: " + email);
        JSONObject result = new JSONObject();
        BCryptPasswordEncoder bCryptPasswordEncoder = new BCryptPasswordEncoder();
        try {
            User resultUser = getUserByEmail(email);
            if (resultUser == null) {
                return new ResponseDTO<>("用户不存在");
            }
            if (resultUser.getPassWord() == null || resultUser.getPassWord().isEmpty()) {
                return new ResponseDTO<>("用户密码未设置，请联系管理员");
            }
            if (bCryptPasswordEncoder.matches(password, resultUser.getPassWord())) {
                String token = JwtUtil.generateToken(resultUser.getEmail());
                resultUser.setPassWord(resultUser.getPassWord());
                result.put("userDetail", resultUser);
                result.put("token", token);
                return new ResponseDTO<>(result);
            }
        } catch (Exception e) {
            return new ResponseDTO<>(e.getMessage());
        }
        return new ResponseDTO<>("验证失败,用户不存在或用户类型不符");
    }

    /**
     * 用户信息
     *
     * @param token 令牌
     * @return {@link ResponseDTO}
     */
    @Override
    public ResponseDTO getUserDetail(String token) throws Exception {
        try {
            String email = JwtUtil.validateToken(token);
            User resultUser = getUserByEmail(email);
            return new ResponseDTO<>(resultUser);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseDTO<>(e.getMessage());
        }
    }

    /**
     * 更新用户信息
     *
     * @param token 令牌
     * @param user  新的用户信息
     * @return {@link ResponseDTO}
     */
    @Override
    public ResponseDTO updateUser(String token, User user) throws Exception {
        try {
            String email = JwtUtil.validateToken(token);
            User existingUser = getUserByEmail(email);
            if (existingUser == null) {
                return new ResponseDTO<>("用户不存在");
            }
            // // 只允许更新部分字段（如用户名），邮箱不可更改
            // existingUser.setUserName(user.getUserName());
            // // 如有其他可更新字段，可在此添加

            String sortedJson = genson.serialize(user);
            byte[] submitResult = contract.submitTransaction("UpdateUser", email, sortedJson);
            return new ResponseDTO<>(200, "用户信息更新成功");
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseDTO<>(e.getMessage());
        }
    }

    @Override
    public User getUserByEmail(String email) throws GatewayException {
        try {
            byte[] evaluateResult = contract.evaluateTransaction("getUserByEmail", email);
            User user = genson.deserialize(new String(evaluateResult), User.class);
            return user;
        } catch (Exception e) {
            // TODO: handle exception
            // e.printStackTrace();
            return null; // 如果查询失败，返回null
        }
    }

    @Override
    public ResponseDTO getAllUsers() throws Exception {
        try {
            byte[] evaluateResult = contract.evaluateTransaction("GetAllUsers");
            List<User> resultJson = genson.deserialize(new String(evaluateResult), List.class);
            return new ResponseDTO<>(resultJson);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseDTO<>(e.getMessage());
        }
    }

}
