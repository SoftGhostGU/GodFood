package com.lcf.util;

import com.alibaba.fastjson2.JSONObject;
import io.swagger.models.auth.In;

import java.util.HashMap;
import java.util.Map;

public class SocialRelation {
    private int userId;
    private int friendId;
    private int[][] relationMatrix = new int[15][15];

    public SocialRelation() {
    }

    public void initRelationMatrix() {
        // 初始化关系矩阵，根据实际情况填充数据
        for (int i = 0; i < relationMatrix.length; i++) {
            for (int j = 0; j < relationMatrix[i].length; j++) {
                if(i==j){
                    relationMatrix[i][j] = 0;
                }else{
                    int s = Math.random() < 0.5 ? 0 : 1;
                    relationMatrix[i][j] =s;
                }
            }
        }
    }
    // 获取用户与其他用户的社交权重
    public JSONObject getSocialWeight(int userId) {
        JSONObject weights = new JSONObject();
        for (int i = 0; i < relationMatrix.length; i++) {
            if(i==userId){
                continue;
            }
            int w1 = relationMatrix[userId][i];
            int w2 = relationMatrix[i][userId];

            weights.put(String.valueOf(i),w1+w2);
        }
        return weights;
    }

}
