import { View } from "@tarojs/components";
import './RestaurantCard.scss'
import { useState, useEffect } from 'react';
import { Skeleton, Rate } from 'antd';

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
      <View className="restaurant-card-container">
        <View className="restaurant-card" style={{ backgroundImage: `url(${cardData.image})` }}></View>
        <View className="content-container">
          <View className="restaurant-name">{cardData.name}</View>
          <View className="restaurant-rating">
            <Rate disabled allowHalf defaultValue={cardData.rating} />
            <View className="rating-count">{cardData.rating}</View>
          </View>
          <View className="other-info">
            <View className="restaurant-price">人均: {cardData.pricePerPerson}元</View>
            <View className="restaurant-distance">距离: {cardData.distance}</View>
          </View>
          <View className="restaurant-reasons">
            <View className="restaurant-reason">
              {cardData.reasons[0]}
            </View>
            <View className="restaurant-reason">
              {cardData.reasons[1]}
            </View>
          </View>
        </View>
      </View>
    </Skeleton>
  )
}