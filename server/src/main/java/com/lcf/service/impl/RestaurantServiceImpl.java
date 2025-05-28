package com.lcf.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONUtil;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.databind.JsonNode;
import com.lcf.blockchain.FabricBasic;
import com.lcf.dto.ResponseDTO;
import com.lcf.service.ServiceBase;
import com.lcf.service.UserService;
import com.lcf.util.JwtUtil;
import com.lcf.util.Weather;
import com.lcf.pojo.PredictInfo;
import com.lcf.pojo.Restaurant;
import com.lcf.pojo.User;
import com.lcf.service.RestaurantService;

import io.grpc.StatusRuntimeException;
import lombok.extern.slf4j.Slf4j;

import org.hyperledger.fabric.client.Contract;
import org.hyperledger.fabric.client.Gateway;
import org.hyperledger.fabric.client.GatewayException;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class RestaurantServiceImpl extends ServiceBase implements RestaurantService {
    private static String restaurantChaincodeName;
    private static String restaurantChannelName;
    private Gateway gateway;
    private Contract contract;
    private final UserService userService;

    public RestaurantServiceImpl(UserService userService) throws Exception {
        this.userService = userService;
        restaurantChaincodeName = "task";
        restaurantChannelName = "mychannel";
        gateway = FabricBasic.getGateway();
        contract = fetchContract(gateway, restaurantChannelName, restaurantChaincodeName);
    }

    @Override
    public JSONObject getAllRestaurants() {
        try {
            byte[] result = contract.evaluateTransaction("GetAllAssets");
            System.out.println("*** Result: " + new String(result));
            if (result == null || result.length == 0) {
                return new JSONObject().fluentPut("message", "No restaurants found");
            }
            JSONObject resultJson = prettyJson(result);
            JSONArray all = resultJson.getJSONArray("allAssert");
            JSONArray resultRestaurants = new JSONArray();
            if (all != null) {
                all.forEach(a -> {
                    JSONObject jsonObject = JSONObject.parseObject(a.toString());
                    jsonObject.put("taskDetail", JSONUtil.parseObj((jsonObject.get("taskDetail").toString())));
                    resultRestaurants.add(jsonObject);
                });
            }
            resultJson.put("allRestaurants", resultRestaurants);
            resultJson.put("total", resultRestaurants.size());
            System.out.println("*** Result: " + resultJson);
            return resultJson;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    @Override
    public Restaurant getRestaurantById(String restaurantID) {
        try {
            byte[] result = contract.evaluateTransaction("GetAssetByID", restaurantID);
            JSONObject resultJson = prettyJson(result);
            if (resultJson != null) {
                Restaurant restaurant = new Restaurant();
                restaurant.setRestaurantID(restaurantID);
                restaurant.setRestaurantDetail(resultJson.getJSONObject("restaurantDetail"));
                return restaurant;
            } else {
                return null;
            }
        } catch (StatusRuntimeException e) {
            e.printStackTrace();
            return null;
        } catch (GatewayException e) {
            e.printStackTrace();
            return null;
        }
    }

    @Override
    public ResponseDTO getRestaurantsByPredict(String token) throws Exception {
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
        try {
            String predictResults = postRequest("http://127.0.0.1:5001/recommend",
                    JSONObject.toJSONString(predictInfo));

            return new ResponseDTO<>(JSONObject.parseObject(predictResults));
        } catch (StatusRuntimeException e) {
            e.printStackTrace();
            return null;
        } catch (GatewayException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 发送POST请求
     *
     * @param url  请求地址
     * @param json 请求体
     * @return 请求结果，处理成json的形式
     * @throws Exception
     */
    public String postRequest(String url, String json) throws Exception {
        HttpResponse response = HttpRequest.post(url)
                .body(json)
                .execute();
        if (!response.isOk()) {
            log.error("POST request failed with status code: {}", response.getStatus());
            throw new Exception("Unexpected code " + response.getStatus());
        }
        log.info("Received response with status code: {}", response.getStatus());

        return response.body();
    }

}