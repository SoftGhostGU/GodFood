import { View, Text } from '@tarojs/components'
import { useLoad } from '@tarojs/taro'
import './index.scss'

import RestaurantCard from '../../components/RestaurantCard'

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
  useLoad(() => {
    console.log('Page loaded.')
  })

  return (
    <View className='index'>
      <View className='loaction-bar'>aaa</View>
      <View className='search-bar'>aaa</View>
      <Text className='title'>今天吃什么？</Text>
      <View className='restaurant-list'>
        {CardInformation.map((card, index) => (
          <RestaurantCard key={index} cardData={card} />
        ))}
      </View>
      <View className='button-bar'>aaa</View>
      <View className='recommendation-bar'>aaa</View>
    </View>
  );
}
