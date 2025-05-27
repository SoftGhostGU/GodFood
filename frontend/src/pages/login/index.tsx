import { View, Text } from '@tarojs/components'
import './index.scss'
import { useState } from 'react'

import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'

export default function Login() {
  // 使用useState来管理当前激活的选项卡
  const [activeTab, setActiveTab] = useState('login')

  const toLogin = () => {
    setActiveTab('login')
    console.log('login')
  }

  const toRegister = () => {
    setActiveTab('register')
    console.log('register')
  }

  return (
    <View className='login-container'>
      <View className='login-header'>
        <View
          className='logo'
          style={{
            backgroundImage: 'url(../../assets/images/logo.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></View>
        <View className='title'>欢迎回来</View>
      </View>

      <View className='tab-container'>
        <Text
          className={`tab ${activeTab === 'login' ? 'active' : ''}`}
          onClick={toLogin}
        >登录</Text>
        <Text
          className={`tab ${activeTab === 'register' ? 'active' : ''}`}
          onClick={toRegister}
        >注册</Text>
      </View>

      {activeTab === 'login' ?
        <LoginForm /> :
        <RegisterForm />
      }

      <View className='divider'>
        <View className='divider-line'></View>
        <Text className='divider-text'>其他登录方式</Text>
        <View className='divider-line'></View>
      </View>

      <View className='other-login-methods'>
        <View
          className='login-icon'
          style={{
            backgroundImage: 'url(../../assets/images/wechat.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></View>
        <View
          className='login-icon'
          style={{
            backgroundImage: 'url(../../assets/images/weibo.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></View>
        <View
          className='login-icon'
          style={{
            backgroundImage: 'url(../../assets/images/google.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></View>
      </View>

      <View className='footer'>
        <Text className='footer-text'>登录即代表同意</Text>
        <Text className='footer-text footer-link'>《用户协议》</Text>
        <Text className='footer-text'>和</Text>
        <Text className='footer-text footer-link'>《隐私政策》</Text>
      </View>
    </View>
  )
}