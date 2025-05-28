package com.lcf.service;

import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.baomidou.mybatisplus.extension.service.IService;
import org.hyperledger.fabric.client.*;

/**
 * <p>
 * 服务类
 * </p>
 *
 * @author lcf
 * @since 2022-12-02
 */
public interface UserService {

    public ResponseDTO userLogin(String email, String password);

    public User getUserByEmail(String email) throws GatewayException;

    /**
     * 更新用户信息，允许只更新部分字段
     * 
     * @param token 用户身份令牌
     * @param user  用户对象，包含需要更新的字段（可为null）
     * @return 响应结果
     * @throws Exception 异常
     */
    public ResponseDTO updateUser(String token, User user) throws Exception;

    public ResponseDTO createUser(String userName, String email, String password) throws GatewayException;

    public ResponseDTO getUserDetail(String token) throws Exception;

    public ResponseDTO getAllUsers() throws Exception;

}
