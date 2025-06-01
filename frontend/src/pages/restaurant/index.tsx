import { View, Text } from "@tarojs/components";
import React from 'react';
import Taro, { showToast, navigateTo, getStorage } from '@tarojs/taro';
import "./index.scss";
import { ShareAltOutlined } from "@ant-design/icons";
import { Rate } from 'antd';
import { EnvironmentTwoTone, PhoneTwoTone } from '@ant-design/icons';

import { fetchRecommendedRestaurants } from '../../utils/restaurant';
import { getInfo } from '../../utils/user'
import { trainModel } from '../../utils/model'

import MySwiper from './swiper/swiper'

export default function RestaurantPage(cardData: any) {
  const [id, setId] = React.useState(0);
  const [recommendedRestaurants, setRecommendedRestaurants] = React.useState();

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const [restaurantImg, setRestaurantImg] = React.useState([]);
  const [restaurantName, setRestaurantName] = React.useState('');
  const [restaurantStar, setRestaurantStar] = React.useState(0.0);
  const [restaurantPrice, setRestaurantPrice] = React.useState(0);
  const [restaurantTypes, setRestaurantTypes] = React.useState([]);
  const [restaurantAddress, setRestaurantAddress] = React.useState('');
  const [restaurantPhone, setRestaurantPhone] = React.useState('');
  const [restaurantTags, setRestaurantTags] = React.useState([]);

  // 获取推荐餐厅的完整实现
  const getAllRecommendedRestaurants = async (id: number) => {
    try {
      setLoading(true);
      const response = await fetchRecommendedRestaurants();

      if (response?.data?.data?.recommendations?.[id-1]) {
        return response.data.data.recommendations[id-1];
      }
      throw new Error('未找到对应餐厅数据');
    } catch (err) {
      console.error('获取推荐餐厅失败:', err);
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // 处理路由参数
  React.useEffect(() => {
    const query = Taro.getCurrentInstance().router?.params;
    if (query?.id) {
      const newId = parseInt(query.id, 10);
      if (!isNaN(newId)) {
        setId(newId);
      }
    }
  }, []);

  // 根据id获取数据
  React.useEffect(() => {
    const fetchData = async () => {
      if (id) {
        const data = await getAllRecommendedRestaurants(id);
        if (data) {
          console.log('推荐餐厅数据 - before:', data);
          // setRecommendedRestaurants(data);
          setRestaurantImg(data.photo_url_first);
          setRestaurantName(data.name);
          setRestaurantStar(data.rating_biz);
          setRestaurantPrice(data.cost || 100);
          setRestaurantTypes(data.type?.split(';'));
          setRestaurantAddress(data.address);
          setRestaurantPhone(data.tel);
          setRestaurantTags(data.tag.split(','));
        }
      }
    };

    fetchData();
  }, [id]); // id变化时重新获取

  // const restaurantTags = [
  //   { id: 1, name: "特色美食" },
  //   { id: 2, name: "低卡健康" },
  //   { id: 3, name: "快速服务" },
  //   { id: 4, name: "a" },
  //   { id: 5, name: "bb" },
  //   { id: 6, name: "ccc" },
  //   { id: 7, name: "dddd" },
  //   { id: 8, name: "eeeee" },
  //   { id: 9, name: "ffffff" },
  //   { id: 10, name: "ggggggg" },
  //   // 可以添加更多标签
  // ];

  const backToIndex = () => {
    console.log('back to index')
    Taro.navigateTo({
      url: '/pages/index/index'
    })
  }

  const clockIn = async () => {
    console.log('clock in')
    const token = await getStorage({ key: 'accessToken' })
        .then(res => res.data)
        .catch(() => {
          showToast({ title: '请先登录', icon: 'none' });
          setTimeout(() => navigateTo({ url: '/pages/login/index' }), 2000);
          throw new Error('未获取到用户token');
        });
    const userInfo = await getInfo(token).then(res => res.data);
    console.log('userInfo:', userInfo);

    showToast({
      title: '打卡成功，已经加入训练集',
      icon: 'success',
      duration: 2000
    })

    userInfo.has_children = userInfo.has_children == "未知" ? false : true;
    await trainModel(token, userInfo)

    setTimeout(() => {
      navigateTo({
        url: '/pages/index/index'
      })
    }, 2000)
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
        <MySwiper images={restaurantImg} />
      </View>

      <View className="info-container">
        <View className="restaurants-name">
          {restaurantName}
        </View>
        <View className="star-and-price">
          <View className="star">
            <Rate
              disabled
              allowHalf
              count={5}
              value={restaurantStar}
            />
            <View className="rating-count">{restaurantStar}</View>
          </View>
          <View className="vertical-line"></View> {/* 竖线分割 */}
          <View className="price">¥{restaurantPrice}/人</View>
        </View>

        <View className="time">
          <Text className="time-content">营业时间：09:00-23:00</Text>
        </View>

        <View className="types">
          {restaurantTypes.map(type => (
            <Text key={type} className="type">#{type}</Text>
          ))}
        </View>

        <View className="horizontal-line"></View> {/* 横线分割 */}

        <View className="location">
          <EnvironmentTwoTone twoToneColor="#4a79f7" />
          <Text className="location-content">{restaurantAddress}</Text>
        </View>

        <View className="phone">
          <PhoneTwoTone twoToneColor="#4a79f7" />
          <Text className="phone-content">{restaurantPhone}</Text>
        </View>

        <View className="horizontal-line"></View> {/* 横线分割 */}
      </View>

      <View className="tag-container">
        <View className="tag-title">餐厅特色</View>
        <View className="tag-list">
          {restaurantTags.map((tag, index) => (
            <View key={index} className="tag-item">
              {tag}
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