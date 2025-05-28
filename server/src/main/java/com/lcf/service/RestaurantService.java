package com.lcf.service;

import com.alibaba.fastjson2.JSONObject;
import com.lcf.dto.ResponseDTO;
import com.lcf.pojo.Restaurant;
import com.lcf.pojo.User;

import java.util.List;

public interface RestaurantService {
    Restaurant getRestaurantById(String restaurantID);

    JSONObject getAllRestaurants();

    ResponseDTO getRestaurantsByPredict(String token) throws Exception;
}