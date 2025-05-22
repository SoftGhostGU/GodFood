import { View } from "@tarojs/components";
import './RestaurantCard.scss'
import React, { useState, useEffect } from 'react';
import { Button, Skeleton, Space } from 'antd';

export default function RestaurantCard({ cardData }) {
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (cardData) {
      showSkeleton();
    }
  }, [cardData]);

  const showSkeleton = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  };

  return (
    <Skeleton loading={loading} active={true} className="restaurant-card-skeleton">
      <View className="restaurant-card" style={{ backgroundImage: `url(${cardData.image})` }}>
        <View className="content-container">
          <View className="restaurant-name">{cardData.name}</View>
          <View className="other-info">
            <View className="restaurant-rating">评分: {cardData.rating}</View>
            <View className="restaurant-price">人均: {cardData.pricePerPerson}元</View>
            <View className="restaurant-distance">距离: {cardData.distance}</View>
          </View>
          <View className="restaurant-reasons">
            {cardData.reasons[0]}
          </View>
        </View>
      </View>
    </Skeleton>
  )
}