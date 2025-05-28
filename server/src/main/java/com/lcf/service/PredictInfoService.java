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
public interface PredictInfoService {

    public ResponseDTO getInfo(String token) throws Exception;

}
