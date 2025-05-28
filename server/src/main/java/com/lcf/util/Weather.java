package com.lcf.util;

import java.net.URI;
import java.net.http.HttpClient;

import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lcf.dto.ResponseDTO;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpUtil;

public class Weather {

    private static final RestTemplate restTemplate = new RestTemplate();
    private static final String API_KEY = "4b8d46de948640a28c10c99f098db445";
    // 101021500 putuo
    private static final String WEATHER_API_URL = "https://mk3qqpv493.re.qweatherapi.com/v7/weather/now?location=101021500&key="
            + API_KEY;

    public static JsonNode getCurrentWeather(String location) {
        String res = HttpUtil.get(WEATHER_API_URL);
        ObjectMapper objectMapper = new ObjectMapper();
        JsonNode jsonNode;
        try {
            jsonNode = objectMapper.readTree(res);
            System.out.println(jsonNode.get("now"));
            return jsonNode; // 返回 JSON 字符串
        } catch (JsonMappingException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (JsonProcessingException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return null;
    }
}
