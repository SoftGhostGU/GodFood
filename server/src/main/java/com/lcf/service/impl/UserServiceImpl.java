package com.lcf.service.impl;

import com.alibaba.fastjson2.JSONException;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonParseException;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.User;
import com.lcf.service.ServiceBase;
import com.lcf.service.UserService;
import com.lcf.util.JwtUtil;
import io.grpc.StatusRuntimeException;
import org.hyperledger.fabric.client.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author lcf
 * @since 2022-12-02
 */
@Service
public class UserServiceImpl extends ServiceBase implements UserService{

    private static String userChaincodeName;
    private static String userChannelName;
    private Gateway gateway;
    private Contract contract;

    public UserServiceImpl() throws Exception {
        userChaincodeName="user";
        userChannelName="mychannel";
        gateway = FabricBasic.getGateway();
        contract=fetchContract(gateway,userChannelName,userChaincodeName);
    }


    @Override
    public ResponseDTO userLogin(User user) {
        JSONObject result=new JSONObject();
        BCryptPasswordEncoder bCryptPasswordEncoder = new BCryptPasswordEncoder();
        try{
            User resultUser=getUserById(user.getUserID());
            if(bCryptPasswordEncoder.matches(user.getPassWord(),resultUser.getPassWord()) && user.getUserType().equals(resultUser.getUserType())){
                String token=JwtUtil.generateToken(user.getUserID());
                resultUser.setPassWord(user.getPassWord());
                result.put("userDetail",resultUser);
                result.put("token",token);
                return new ResponseDTO<>(result);
            }
        }catch (Exception e){
            return  new ResponseDTO<>(e.getMessage());
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
    public ResponseDTO userInfo(String token) {
        JSONObject result=new JSONObject();
        try{
            String userId=JwtUtil.validateToken(token);
            User resultUser=getUserById(userId);

            JSONObject userInfo = getUserDetail(userId);
            resultUser.setChannelId(userInfo.get("channelId").toString());
            resultUser.setTxId(userInfo.get("txId").toString());
            result.put("userDetail",resultUser);
            result.put("avatar","https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif");
            return new ResponseDTO<>(result);
        }catch (Exception e){
            e.printStackTrace();
            return  new ResponseDTO<>(e.getMessage());
        }
    }

    /**
     * 通过id查询用户，同一个用户名不能同时是工作者或者请求者
     *
     * @return {@link ResponseDTO}
     */
    @Override
    public User getUserById(String userId) throws GatewayException{
            byte[] evaluateResult = contract.evaluateTransaction("ReadAsset", userId);
            System.out.println("*** 验证成功--Result:" + prettyJson(evaluateResult));
            User resultUser = new User(prettyJson(evaluateResult));
            return resultUser;
    }

    @Override
    public ResponseDTO createUser(User user){
        BCryptPasswordEncoder bCryptPasswordEncoder = new BCryptPasswordEncoder();
        String encodePwd = bCryptPasswordEncoder.encode(user.getPassWord());
        user.setPassWord(encodePwd);
        try{
            byte[] evaluateResult = contract.evaluateTransaction("CreateAsset", user.getUserID());
            if(evaluateResult.length>0){
                System.out.println("*** Result:" + prettyJson(evaluateResult));
                return new ResponseDTO<>("用户已存在，不能重复注册");
            }
        }catch (StatusRuntimeException | GatewayException e){
            try{
                System.out.println("\n--> Submit Transaction");
                byte[] submitResult=contract.submitTransaction("CreateAsset",user.getUserID(), user.getPassWord(), user.getUserType(), user.getPhoneNumber(), user.getCreditScore(), user.getMarginBalance());
                System.out.println("*** Result:" + prettyJson(submitResult));
            }catch(Exception x){
                return new ResponseDTO<>(x.getMessage());
            }
        }
        return new ResponseDTO<>(200,"注册成功");
    }

    /**
     * 查询所有用户
     *
     * @return {@link ResponseDTO}
     * @throws GatewayException 网关异常
     */
    @Override
    public ResponseDTO getUserAll() {
        try {
            byte[] result = contract.evaluateTransaction("GetAllAssets");
            System.out.println("*** Result: " + prettyJson(result));
            return new ResponseDTO<>(prettyJson(result));
        }catch (Exception e){
            e.printStackTrace();
            return new ResponseDTO<>(e.getMessage());
        }

    }

    @Override
    public JSONObject getUserDetail(String userId) throws Exception {
        try{
            byte[] result = contract.evaluateTransaction("ReadAssetDetail",userId);
            System.out.println("*** Result: " + prettyJson(result));
            return prettyJson(result);
        }catch(Exception e){
            throw new Exception(e.getMessage());
        }
    }


    @Override
    public void setUserChaincodeName(String userChaincodeName) {
        UserServiceImpl.userChaincodeName = userChaincodeName;
    }

    @Override
    public void setUserChannelName(String userChannelName) {
        UserServiceImpl.userChannelName = userChannelName;
    }


}
