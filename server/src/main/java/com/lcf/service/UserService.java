package com.lcf.service;

import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.baomidou.mybatisplus.extension.service.IService;
import org.hyperledger.fabric.client.*;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author lcf
 * @since 2022-12-02
 */
public interface UserService {

    public ResponseDTO userLogin(User user);

    public ResponseDTO userInfo(String token);

    public User getUserById(String userId) throws GatewayException;

    public ResponseDTO createUser(User user) ;

    public ResponseDTO getUserAll() throws GatewayException;

    public JSONObject getUserDetail(String userId) throws Exception;

    public void setUserChaincodeName(String userChaincodeName);

    public void setUserChannelName(String userChannelName);


}
