import { View } from "@tarojs/components";
import './RestaurantListCard.scss';

export default function RestaurantListCard({ cardData }) {
  console.log(cardData);

  return (
    <View className="restaurant-list-card">
      {/* 显示餐厅图片 */}
      <View
        style={{
          backgroundImage: `url(${cardData.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
        className="restaurant-list-card__image"
      ></View>

      <View className="text-container">
        {/* 显示餐厅名称 */}
        <View className="restaurant-list-card__name">{cardData.name}</View>

        <View className="mini-text-container">
          {/* 显示人均消费 */}
          <View className="restaurant-list-card__price">
            人均 {cardData.pricePerPerson} 元
          </View>

          {/* 显示评分 */}
          <View className="restaurant-list-card__rating">
            评分: {cardData.rating}
          </View>

          {/* 显示距离 */}
          <View className="restaurant-list-card__distance">
            评分: {cardData.distance}
          </View>
        </View>

        {/* 显示推荐理由，以列表形式展示 */}
        <View className="restaurant-list-card__reasons">
          <View className="restaurant-list-card__reason-list">
            {cardData.reasons.map((reason: string, index: number) => (
              <View key={index} className="restaurant-list-card__reason">
                {index > 0 && "  /  "} {/* 只在非第一个理由前加 / */}
                {reason}
              </View>
            ))}
          </View>
        </View>
      </View>
    </View>
  );
}
