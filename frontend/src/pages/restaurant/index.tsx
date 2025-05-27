import { View, Text } from "@tarojs/components";
import Taro from '@tarojs/taro';
import "./index.scss";
import { ShareAltOutlined } from "@ant-design/icons";
import { Rate } from 'antd';
import { EnvironmentTwoTone, PhoneTwoTone } from '@ant-design/icons';

import MySwiper from './swiper/swiper'

export default function RestaurantPage() {
  const restaurantTags = [
    { id: 1, name: "特色美食" },
    { id: 2, name: "低卡健康" },
    { id: 3, name: "快速服务" },
    { id: 4, name: "a" },
    { id: 5, name: "bb" },
    { id: 6, name: "ccc" },
    { id: 7, name: "dddd" },
    { id: 8, name: "eeeee" },
    { id: 9, name: "ffffff" },
    { id: 10, name: "ggggggg" },
    // 可以添加更多标签
  ];

  const backToIndex = () => {
    console.log('back to index')
    Taro.navigateTo({
      url: '/pages/index/index'
    })
  }

  const clockIn = () => {
    console.log('clock in')
  }

  return (
    <View className="container">
      <View className='header'>
        <View
          className='back-icon'
          onClick={backToIndex}
        >{`<`}</View>
        <View className='title'>餐厅详情</View>
        <ShareAltOutlined
          className='setting-icon'
        />
      </View>

      <View className="image-container">
        <MySwiper />
      </View>

      <View className="info-container">
        <View className="restaurants-name">
          江南小馆
        </View>
        <View className="star-and-price">
          <View className="star">
            <Rate
              disabled
              allowHalf
              defaultValue={4.8}
            />
            <View className="rating-count">{4.8}</View>
          </View>
          <View className="vertical-line"></View> {/* 竖线分割 */}
          <View className="price">¥100/人</View>
        </View>

        <View className="time">
          <Text className="time-content">营业时间：09:00-23:00</Text>
        </View>

        <View className="types">
          <Text className="type">#中餐</Text>
          <Text className="type">#江浙菜</Text>
          <Text className="type">#家常菜</Text>
        </View>

        <View className="horizontal-line"></View> {/* 横线分割 */}

        <View className="location">
          <EnvironmentTwoTone twoToneColor="#4a79f7" />
          <Text className="location-content">上海市黄浦区南京东路123号</Text>
        </View>

        <View className="phone">
          <PhoneTwoTone twoToneColor="#4a79f7" />
          <Text className="phone-content">021-12345678</Text>
        </View>

        <View className="horizontal-line"></View> {/* 横线分割 */}
      </View>

      <View className="tag-container">
        <View className="tag-title">餐厅特色</View>
        <View className="tag-list">
          {restaurantTags.map(tag => (
            <View key={tag.id} className="tag-item">
              {tag.name}
            </View>
          ))}
        </View>
      </View>

      <View className="clock-in-container">
        <View
          className="clock-in"
          onClick={clockIn}
        >
          打卡签到
        </View>
      </View>
    </View>
  )
}