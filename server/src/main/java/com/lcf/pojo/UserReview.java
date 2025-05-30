package com.lcf.pojo;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;

import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.JsonObject;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserReview {
    @Builder.Default
    private String id = "123";
    private String name;
    private int age;
    private String gender;
    private double height_cm;
    private double weight_kg;
    private String hometown;
    private String occupation;
    private String education_level;
    private String marital_status;
    private boolean has_children;
    private String hobbies;
    private String diseases;
    private String dietary_preferences;
    private String activity_level;
    private String fitness_goals;
    private String food_allergies;
    private String cooking_skills;
    private double daily_food_budget_cny;
    @Builder.Default
    private String review_datetime = "2023-09-29 12:51:29";
    private int heart_rate_bpm;
    private double blood_sugar_mmol_l;
    private String blood_pressure_mm_hg;
    private double sleep_hours_last_night;
    private double weather_temp_celsius;
    private double weather_humidity_percent;
    private int steps_today_before_meal;
    private boolean was_hungry_before_meal;
    private String user_id;
    private String restaurant_id;
    private String restaurant_name;
    private double user_rating;
    private String review_text_placeholder;

    private static final String HEADER = "id,name,age,gender,height_cm,weight_kg,hometown,occupation,education_level,marital_status,has_children,hobbies,diseases,dietary_preferences,activity_level,fitness_goals,food_allergies,cooking_skills,daily_food_budget_cny,review_datetime,heart_rate_bpm,blood_sugar_mmol_L,blood_pressure_mmHg,sleep_hours_last_night,weather_temp_celsius,weather_humidity_percent,steps_today_before_meal,was_hungry_before_meal,user_id,restaurant_id,restaurant_name,user_rating,review_text_placeholder";

    public static String toCsvJson(List<UserReview> reviews) throws Exception {
        StringBuilder sb = new StringBuilder();
        sb.append(HEADER).append("\n");

        for (UserReview r : reviews) {
            StringJoiner line = new StringJoiner(",");
            line.add(r.getId());
            line.add(r.getName());
            line.add(String.valueOf(r.getAge()));
            line.add(r.getGender());
            line.add(String.valueOf(r.getHeight_cm()));
            line.add(String.valueOf(r.getWeight_kg()));
            line.add(r.getHometown());
            line.add(r.getOccupation());
            line.add(r.getEducation_level());
            line.add(r.getMarital_status());
            line.add(String.valueOf(r.isHas_children()));
            line.add(escapeCsv(r.getHobbies()));
            line.add(escapeCsv(r.getDiseases()));
            line.add(r.getDietary_preferences());
            line.add(r.getActivity_level());
            line.add(r.getFitness_goals());
            line.add(escapeCsv(r.getFood_allergies()));
            line.add(r.getCooking_skills());
            line.add(String.valueOf(r.getDaily_food_budget_cny()));
            line.add(r.getReview_datetime());
            line.add(String.valueOf(r.getHeart_rate_bpm()));
            line.add(String.valueOf(r.getBlood_sugar_mmol_l()));
            line.add(r.getBlood_pressure_mm_hg());
            line.add(String.valueOf(r.getSleep_hours_last_night()));
            line.add(String.valueOf(r.getWeather_temp_celsius()));
            line.add(String.valueOf(r.getWeather_humidity_percent()));
            line.add(String.valueOf(r.getSteps_today_before_meal()));
            line.add(String.valueOf(r.isWas_hungry_before_meal()));
            line.add(r.getUser_id());
            line.add(r.getRestaurant_id());
            line.add(r.getRestaurant_name());
            line.add(String.valueOf(r.getUser_rating()));
            line.add(r.getReview_text_placeholder());
            sb.append(line.toString()).append("\n");
            // sb.append(line.toString());

        }
        // 删除sb末尾的换行符
        if (sb.length() > 0 && sb.charAt(sb.length() - 1) == '\n') {
            sb.deleteCharAt(sb.length() - 1);
        }
        Map<String, String> result = new HashMap<>();
        result.put("user_reviews_csv", sb.toString());

        return JSONObject.toJSONString(result);
    }

    // 转义CSV字段中可能出现的逗号、引号、分号等
    private static String escapeCsv(String value) {
        if (value == null)
            return "";
        if (value.contains(",") || value.contains(";") || value.contains("\"")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

}
