/*
 * SPDX-License-Identifier: Apache-2.0
 */

package com.lcf.pojo;

import javax.validation.constraints.NotBlank;

import org.springframework.boot.context.properties.ConstructorBinding;

import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModelProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {

    private String userID;
    private String userName;
    @ApiModelProperty(value = "用户邮箱", required = true)
    @NotBlank(message = "用户邮箱不能为空")
    private String email;
    private String passWord;
    @Builder.Default
    private String avatarUrl = "https://s21.ax1x.com/2025/05/29/pVpDCpn.png"; // 默认头像URL
    @Builder.Default
    private Integer age = 0;
    @Builder.Default
    private String phone = "0";
    @Builder.Default
    private String gender = "未知"; // 未知, 男, 女
    @Builder.Default
    private Integer height_cm = 0;
    @Builder.Default
    private Integer weight_kg = 0;
    @Builder.Default
    private String hometown = "";
    @Builder.Default
    private String occupation = "";
    @Builder.Default
    private String education_level = "";
    @Builder.Default
    private String marital_status = "未知"; // 未知, 未婚, 已婚
    @Builder.Default
    private String has_children = "未知"; // 未知, 无, 有
    @Builder.Default
    private String hobbies = "";
    @Builder.Default
    private String diseases = "";
    @Builder.Default
    private String dietary_preferences = "";
    @Builder.Default
    private String activity_level = "0"; // 0:未知, 1:几乎不运动, 2:每周1-2次, 3:每周3-5次
    @Builder.Default
    private String fitness_goals = ""; // 例如: 减脂, 增肌, 提高耐力等
    @Builder.Default
    private String food_allergies = ""; // 忌口： 花生, 海鲜等
    @Builder.Default
    private String cooking_skills = "0"; // 0:未知, 1:不会, 2:一般, 3:熟练
    @Builder.Default
    private Integer daily_food_budget_cny = 0;
    @Builder.Default
    private double heart_rate_bpm = 0.0; // 心率
    @Builder.Default
    private double blood_sugar_mmol_L = 0.0; // 血糖
    @Builder.Default
    private double sleep_hours_last_night = 0.0; // 昨晚睡眠时长
    @Builder.Default
    private Integer steps_today_before_meal = 0; // 今日步数

}
