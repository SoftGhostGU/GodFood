import { View, Text, Button } from '@tarojs/components'
import { useLoad, chooseLocation, showToast } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import './index.scss'

import RestaurantCard from '../../components/RestaurantCard'
import RestaurantListCard from '../../components/RestaurantListCard'
// import LocationMap from '../../components/locationMap'
import {
  StarTwoTone,
  LikeTwoTone,
  EnvironmentTwoTone,
  InfoCircleTwoTone
} from '@ant-design/icons'

import { CardInfo } from '../../types/CardInfo'

const CardInformation: CardInfo[] = [
  {
    id: 1,
    name: 'McDonald\'s',
    image: 'https://img.meituan.net/content/df23cf313fb99aeb25ed8d23ce22c035162775.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.8,
    pricePerPerson: 88,
    distance: '500m',
    reasons: ['距离近', '人均消费低', '口味好']
  },
  {
    id: 2,
    name: 'MIKAKU',
    image: 'https://p0.meituan.net/biztone/1274d5af7a22f2f2e989ebc648713d35621585.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.6,
    pricePerPerson: 128,
    distance: '1.2km',
    reasons: ['价格便宜', '环境好', '服务好']
  },
  {
    id: 3,
    name: 'BELLOCO',
    image: 'http://p0.meituan.net/biztone/0a0ada83d19dd4fc84aee38bdff02a561008591.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.4,
    pricePerPerson: 78,
    distance: '900m',
    reasons: ['距离近', '人均消费低', '口味好']
  },
  {
    id: 4,
    name: '帕蓝·暹罗料理',
    image: 'https://img.meituan.net/content/82d497c9464a9def7cfe2f04cca74036201554.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.3,
    pricePerPerson: 95,
    distance: '600m',
    reasons: ['距离近', '人均消费低', '口味好']
  },
  {
    id: 5,
    name: 'Tomacado花厨',
    image: 'https://img.meituan.net/content/7e8cc9aba20233778a6fa814747de478161608.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.1,
    pricePerPerson: 150,
    distance: '1km',
    reasons: ['环境优雅', '咖啡品质高', '服务态度好']
  },
  {
    id: 6,
    name: '点都德',
    image: 'https://img.meituan.net/content/5a8b937259e7d798a4c723af433aba2d46869.jpg%40340w_255h_1e_1c_1l%7Cwatermark%3D0',
    rating: 4.0,
    pricePerPerson: 105,
    distance: '800m',
    reasons: ['披萨口感好', '有儿童套餐', '位置便利']
  }
]

export default function Index() {
  const [location, setLocation] = useState({
    latitude: 39.90923,      // 默认纬度（天安门）
    longitude: 116.397428,   // 默认经度
    address: '正在获取位置...' // 初始提示
  });
  const [recommendation, setRecommendation] = useState<CardInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false);
  const [cardData, setCardData] = useState(CardInformation);

  useLoad(() => {
    console.log('Page loaded.')
  })

  // 加载cardData数据
  // useEffect(() => {
  //   const fetchData = async () => {
  //     setIsLoading(true);
  //     try {
  //       const response = await fetch('你的API地址');
  //       const data = await response.json();
  //       setCardData(data);
  //     } catch (error) {
  //       console.error('加载失败:', error);
  //     } finally {
  //       setIsLoading(false); // 无论成功失败都关闭加载状态
  //     }
  //   };

  //   fetchData();
  // }, []);

  useEffect(() => {
    // 检查浏览器是否支持Geolocation
    if (!navigator.geolocation) {
      setLocation(prev => ({ ...prev, address: '浏览器不支持定位功能' }));
      return;
    }

    // 高精度定位配置
    const options = {
      enableHighAccuracy: true,  // 高精度模式（可能耗时长）
      timeout: 10000,            // 超时时间（10秒）
      maximumAge: 0              // 禁用缓存，强制获取最新位置
    };

    // 获取当前位置
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        // 处理 calculateCity 的异步结果
        try {
          const city = (await calculateCity()) as string; // 等待 calculateCity 返回值
          console.log('calculateCity result:', city);
          setLocation({
            latitude,
            longitude,
            address: city
          });
        } catch (error) {
          setLocation(prev => ({ ...prev, address: `获取城市信息失败: ${error.message}` }));
        }
      },
      (error) => {
        let errorMessage = '定位失败: ';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += '用户拒绝了定位请求';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage += '位置信息不可用';
            break;
          case error.TIMEOUT:
            errorMessage += '请求超时';
            break;
          default:
            errorMessage += '未知错误';
        }
        setLocation(prev => ({ ...prev, address: errorMessage }));
      },
      options
    );

    // const fetchData = async () => {
    //   setIsLoading(true);
    //   try {
    //     const response = await fetch('你的API地址');
    //     const data = await response.json();
    //     setCardData(data);
    //   } catch (error) {
    //     console.error('加载失败:', error);
    //   } finally {
    //     setIsLoading(false); // 无论成功失败都关闭加载状态
    //   }
    // };

    // fetchData();
  }, []);

  const getCityFromCoords = async (lat: number, lng: number) => {
    return new Promise((resolve) => {
      const geocoder = new Intl.DisplayNames(['zh'], { type: 'region' });
      // 通过时区猜测城市（粗略）
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const city = timezone.split('/')[1] || '未知城市';
      resolve(city);
    });
  };

  const calculateCity = async () => {
    const city = await getCityFromCoords(location.latitude, location.longitude)
    return city;
  }

  // 随机推荐一家餐厅
  const handleRandomRecommendation = () => {
    const randomIndex = Math.floor(Math.random() * cardData.length)
    const randomRestaurant = cardData[randomIndex]
    setRecommendation(randomRestaurant)
    setIsLoading(true)
    setTimeout(() => {
      showToast({
        title: '已为您推荐餐厅',
        icon: 'success'
      })
      setIsLoading(false)
    }, 2000)
  }

  return (
    <View className='index'>
      <View className='location-bar'>
        <EnvironmentTwoTone
          className='location-icon'
          twoToneColor="#bd574f"
        />
        <Text className='location-text'>{location.address}</Text>
      </View>

      {/* <View className='ai-bar'>AI推荐</View> */}
      <Text className='title'>今天吃什么？</Text>

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
      </View>

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
            <RestaurantCard
              cardData={recommendation || {}}
              isLoading={isLoading}
            />
          )}
        </View>
      </View>

      <View className='all-title'>
        所有推荐的餐厅 {`>`}
      </View>

      <View className='restaurant-list'>
        {cardData.map((card, _) => (
          <View key={card.id} className='restaurant-item'>
            <RestaurantListCard
              cardData={card}
              isLoading={isLoading}
            />
          </View>
        ))}
      </View>
    </View>
  );
}