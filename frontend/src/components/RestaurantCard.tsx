import { View } from "@tarojs/components";
import './RestaurantCard.scss'
import { useState, useEffect } from 'react';
import { Skeleton, Rate } from 'antd';

export default function RestaurantCard({ cardData, isLoading }) {

  return (
    <View className="restaurant-card-container">
      {/* 图片区域 - 单独控制骨架屏 */}
      {isLoading ? (
        <Skeleton.Image
          active
          className="restaurant-card-skeleton-image"
        />
      ) : (
        <View
          className="restaurant-card"
          style={{ backgroundImage: `url(${cardData.image})` }}
        />
      )}

      {/* 内容区域 - 统一用一个Skeleton控制 */}
      <Skeleton
        loading={isLoading}
        active
        className="restaurant-card-skeleton"
        title={false} // 不显示标题占位
        paragraph={{ rows: 3 }} // 根据内容区域高度调整行数
      >
        <View className="content-container">
          <View className="restaurant-name">{cardData.name}</View>
          <View className="restaurant-rating">
            <Rate disabled allowHalf defaultValue={cardData.rating} />
            <View className="rating-count">{cardData.rating}</View>
          </View>
          <View className="other-info">
            <View className="restaurant-price">人均: {cardData.pricePerPerson}元</View>
            {/* <View className="restaurant-distance">距离: {cardData.distance}</View> */}
          </View>
          <View className="restaurant-reasons">
            {cardData.reasons.slice(0, 2).map((reason, index) => (
              <View key={index} className="restaurant-reason">
                {reason}
              </View>
            ))}
          </View>
        </View>
      </Skeleton>
    </View>
  );
}