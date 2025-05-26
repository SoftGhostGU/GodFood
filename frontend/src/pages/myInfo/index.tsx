import { View, Text } from '@tarojs/components'
import { useLoad } from '@tarojs/taro'
import './index.scss'
import { useState } from 'react'

export default function Index() {
  const [userInfo, setUserInfo] = useState({
    'user-avatar': 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg',
    'user-name': 'GHOST.',
    'user-id': '7238487',
    'user-sign': '热爱生活，享受当下',
    'user-age': '25',
    'user-gender': '男',
    'user-location': '上海市',
    'user-career': '产品设计师',
    'user-phone': '19921539522',
    'user-email': '3089308393@qq.com',
    'user-security': '高'
  })

  useLoad(() => {
    console.log('Page loaded.')
  })

  return (
    <View className='myInfo'>
      <View className='header'>
        <View className='header-prev'></View>
        <View className='header-text'>个人主页</View>
        <View className='header-edit'>编辑</View>
      </View>

      <View className='user-info'>
        <View
          className='user-avatar'
          style={{
            backgroundImage: 'url(' + userInfo['user-avatar'] + ')',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></View>
        <View className='user-name'>{userInfo['user-name']}</View>
        <View className='user-id'>ID: {userInfo['user-id']}</View>
        <View className='user-sign'>{userInfo['user-sign']}</View>
      </View>

      <View className='user-basic-info'>
        <View className='user-age'>
          <View
            className='age-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/birthday.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-age']}岁
        </View>
        <View className='user-gender'>
          <View
            className='gender-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/gender.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-gender']}
        </View>
        <View className='user-location'>
          <View
            className='location-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/location.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-location']}
        </View>
        <View className='user-career'>
          <View
            className='career-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/job.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-career']}
          </View>
      </View>

      <View className='user-other-info'>
        <View className='user-phone'>
          <View
            className='phone-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/phone.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-phone']}
        </View>
        <View className='user-email'>
          <View
            className='email-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/email.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          {userInfo['user-email']}
        </View>
        <View className='user-security'>
          <View
            className='security-icon'
            style={{
              backgroundImage: 'url(../../assets/icon/security.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          ></View>
          账号安全等级：{userInfo['user-security']}
        </View>
      </View>

      <View
        className='edit-btn'
        onClick={() => {
          console.log('Edit button clicked.')
        }}
      >
        编辑资料
      </View>
    </View>
  )
}
