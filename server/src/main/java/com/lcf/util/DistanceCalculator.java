package com.lcf.util;

import com.lcf.pojo.Task;

public class DistanceCalculator {
    private static final double R = 6371; // 地球半径，单位：公里

    public static double calculateDistance(Task task1, Task task2) {
        double lat1 = Math.toRadians(task1.getLatitude());
        double lon1 = Math.toRadians(task1.getLongitude());
        double lat2 = Math.toRadians(task2.getLatitude());
        double lon2 = Math.toRadians(task2.getLongitude());

        double dlon = lon2 - lon1;
        double dlat = lat2 - lat1;

        double a = Math.pow(Math.sin(dlat / 2), 2) +
                Math.cos(lat1) * Math.cos(lat2) *
                        Math.pow(Math.sin(dlon / 2), 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }
}
