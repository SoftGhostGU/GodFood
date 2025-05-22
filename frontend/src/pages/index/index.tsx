import { View, Text, Map, Button } from '@tarojs/components'
import { useLoad, getLocation, chooseLocation, showToast } from '@tarojs/taro'
import { useState } from 'react'
import './index.scss'

import RestaurantCard from '../../components/RestaurantCard'
import RestaurantListCard from '../../components/RestaurantListCard'
import LocationMap from '../../components/locationMap'
import {
  StarTwoTone,
  LikeTwoTone,
  EnvironmentTwoTone,
  InfoCircleTwoTone
} from '@ant-design/icons'

import { CardInfo } from '../../types/CardInfo'

const CardInformation: CardInfo[] = [
  {
    name: 'McDonald\'s',
    image: 'https://img.meituan.net/content/df23cf313fb99aeb25ed8d23ce22c035162775.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.8,
    pricePerPerson: 88,
    distance: '500m',
    reasons: ['距离近', '人均消费低', '口味好', '环境好']
  },
  {
    name: 'MIKAKU',
    image: 'https://p0.meituan.net/biztone/1274d5af7a22f2f2e989ebc648713d35621585.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.6,
    pricePerPerson: 128,
    distance: '1.2km',
    reasons: ['价格便宜', '环境好', '服务好', '味道好']
  },
  {
    name: 'BELLOCO',
    image: 'http://p0.meituan.net/biztone/0a0ada83d19dd4fc84aee38bdff02a561008591.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.4,
    pricePerPerson: 78,
    distance: '900m',
    reasons: ['距离近', '人均消费低', '口味好', '环境好']
  },
  {
    name: '帕蓝·暹罗料理',
    image: 'https://img.meituan.net/content/82d497c9464a9def7cfe2f04cca74036201554.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.3,
    pricePerPerson: 95,
    distance: '600m',
    reasons: ['距离近', '人均消费低', '口味好', '环境好']
  },
  {
    name: 'Tomacado花厨',
    image: 'https://img.meituan.net/content/7e8cc9aba20233778a6fa814747de478161608.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.1,
    pricePerPerson: 150,
    distance: '1km',
    reasons: ['环境优雅', '咖啡品质高', '服务态度好', '适合情侣约会']
  },
  {
    name: '点都德',
    image: 'https://img.meituan.net/content/5a8b937259e7d798a4c723af433aba2d46869.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.0,
    pricePerPerson: 105,
    distance: '800m',
    reasons: ['披萨口感好', '有儿童套餐', '位置便利', '价格适中']
  }
]

export default function Index() {
  const [location, setLocation] = useState({
    latitude: 39.90923,
    longitude: 116.397428,
    address: '天安门'
  })
  const [recommendation, setRecommendation] = useState<CardInfo | null>(null)

  useLoad(() => {
    console.log('Page loaded.')
  })

  const handleGetLocation = () => {
    getLocation({
      type: 'gcj02',
      success: (res) => {
        setLocation({
          latitude: res.latitude,
          longitude: res.longitude,
          address: '当前位置'
        })
      }
    })
  }

  const handleChooseLocation = async () => {
    try {
      const res = await chooseLocation({
        latitude: location.latitude,
        longitude: location.longitude
      })
      setLocation({
        latitude: res.latitude,
        longitude: res.longitude,
        address: res.address || res.name || '已选择位置'
      })
    } catch (err) {
      console.error('选择位置失败:', err)
    }
  }

  // 随机推荐一家餐厅
  const handleRandomRecommendation = () => {
    const randomIndex = Math.floor(Math.random() * CardInformation.length)
    const randomRestaurant = CardInformation[randomIndex]
    setRecommendation(randomRestaurant)
    setTimeout(() => {
      showToast({
        title: '已为您推荐餐厅',
        icon: 'success'
      })
    }, 3000)
  }

  return (
    <View className='index'>
      <View className='location-bar' onClick={handleChooseLocation}>
        <EnvironmentTwoTone twoToneColor="#bd574f" />
        <Text className='location-text'>{location.address}</Text>
      </View>

      {/* <View className='ai-bar'>AI推荐</View> */}
      <Text className='title'>今天吃什么？</Text>

      {/* 推荐区域 */}
      <View className='recommendation-bar'>
        <Button
          className='recommend-button'
          onClick={handleRandomRecommendation}
        >
          帮我随机推荐一家餐厅
        </Button>

        <View className='recommendation-result'>
          {recommendation && (
            // <View className='recommendation-result'>
            //   <Text className='recommendation-text'>今日推荐: {recommendation.name}</Text>
            //   <Text className='recommendation-detail'>
            //     评分: {recommendation.rating} | 人均: ¥{recommendation.pricePerPerson} | 距离: {recommendation.distance}
            //   </Text>
            // </View>
            <RestaurantCard
              cardData={recommendation}
            />
          )}
        </View>
      </View>

      <View className='button-bar'>
        <View className='button-item'>
          <View
            className='button-icon'
            onClick={() => {
              console.log('近期热门')
            }}
          >
            <StarTwoTone twoToneColor="#bd574f" />
          </View>
          <Text className='button-text'>近期热门</Text>
        </View>
        <View className='button-item'>
          <View
            className='button-icon'
            onClick={() => {
              console.log('精品推荐')
            }}
          >
            <LikeTwoTone twoToneColor="#bd574f" />
          </View>
          <Text className='button-text'>精品推荐</Text>
        </View>
        <View className='button-item'>
          <View
            className='button-icon'
            onClick={() => {
              console.log('附近美食')
            }}
          >
            <EnvironmentTwoTone twoToneColor="#bd574f" />
          </View>
          <Text className='button-text'>附近美食</Text>
        </View>
        <View className='button-item'>
          <View
            className='button-icon'
            onClick={() => {
              console.log('个人信息')
            }}
          >
            <InfoCircleTwoTone twoToneColor="#bd574f" />
          </View>
          <Text className='button-text'>个人信息</Text>
        </View>

        <View>
          所有推荐的餐厅
        </View>

        <View className='restaurant-list'>
          {CardInformation.map((card, index) => (
            <View className='restaurant-item'>
              <RestaurantListCard key={index} cardData={card} />
            </View>
          ))}
        </View>
      </View>
    </View>
  );
}