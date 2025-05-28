package com.lcf.service.impl;

import com.alibaba.fastjson2.JSONException;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.gson.JsonObject;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.PredictInfo;
import com.lcf.pojo.User;
import com.lcf.service.PredictInfoService;
import com.lcf.service.ServiceBase;
import com.lcf.service.UserService;
import com.lcf.util.JwtUtil;
import com.lcf.util.Weather;

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
public class PredictInfoServiceImpl extends ServiceBase implements PredictInfoService {

    private final UserService userService;

    public PredictInfoServiceImpl(UserService userService) throws Exception {
        this.userService = userService;
    }

    public ResponseDTO getInfo(String token) throws Exception {
        String email = JwtUtil.validateToken(token);
        User resultUser = userService.getUserByEmail(email);
        if (resultUser == null) {
            return new ResponseDTO<>("用户不存在");
        }
        JsonNode weather = null;
        try {
            if (resultUser.getHometown() != null) {
                weather = Weather.getCurrentWeather(resultUser.getHometown());
            }
        } catch (Exception e) {
            return new ResponseDTO<>("获取天气信息失败，请检查城市名称是否正确");
        }
        // 组装预测信息
        PredictInfo predictInfo = PredictInfo.builder()
                .age(resultUser.getAge())
                .gender(resultUser.getGender())
                .height_cm(resultUser.getHeight_cm())
                .weight_kg(resultUser.getWeight_kg())
                .hometown(resultUser.getHometown())
                .occupation(resultUser.getOccupation())
                .education_level(resultUser.getEducation_level())
                .marital_status(resultUser.getMarital_status())
                .diseases(resultUser.getDiseases())
                .dietary_preferences(resultUser.getDietary_preferences())
                .activity_level(resultUser.getActivity_level())
                .fitness_goals(resultUser.getFitness_goals())
                .food_allergies(resultUser.getFood_allergies())
                .cooking_skills(resultUser.getCooking_skills())
                .heart_rate_bpm(resultUser.getHeart_rate_bpm())
                .blood_sugar_mmol_L(resultUser.getBlood_sugar_mmol_L())
                .sleep_hours_last_night(resultUser.getSleep_hours_last_night())
                .steps_today_before_meal(resultUser.getSteps_today_before_meal())
                .weather_temp_celsius(weather != null ? weather.get("now").get("temp").asDouble() : 0.0)
                .weather_humidity_percent(weather != null ? weather.get("now").get("humidity").asDouble() : 0.0)
                .build();
        return new ResponseDTO<>(predictInfo);
    }

}
