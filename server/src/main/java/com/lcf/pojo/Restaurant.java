package com.lcf.pojo;

import com.alibaba.fastjson2.JSONObject;
import lombok.Data;

import java.util.Map;

@Data
public final class Restaurant {

    private String restaurantID;

    private JSONObject restaurantDetail;

}
