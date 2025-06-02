import { Swiper, SwiperItem, Image, View } from '@tarojs/components'
import React from 'react';
import './swiper.scss'

export default function MySwiper(images: any) {
  console.log(images)

  const slides = [
    // { id: 1, url: 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg', title: '标题1' },
    // { id: 2, url: 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg', title: '标题2' },
    // { id: 3, url: 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg', title: '标题3' },
    // { id: 4, url: 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg', title: '标题4' }
    { id: 1, url: images, title: '餐厅详情' }
  ]

  console.log(slides)

  return (
    <Swiper
      className="swiper-container"
      indicatorDots
      autoplay
      circular
    >
      {slides.map(item => (
        <SwiperItem key={item.id}>
          <Image className="slide-image" src={item.url.images} mode="aspectFill" />
          <View className="slide-title">{item.title}</View>
        </SwiperItem>
      ))}
    </Swiper>
  )
}