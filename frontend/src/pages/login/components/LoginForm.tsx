import { View, Input, Text } from '@tarojs/components'
import './LoginForm.scss'
import Taro, { hideLoading, showLoading, showToast, setStorageSync } from '@tarojs/taro'
import { useState } from 'react'

import { login } from '../../../utils/user'

export default function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const [errors, setErrors] = useState({
    email: '',
    password: ''
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData({
      ...formData,
      [field]: value
    })
    // 输入时清除错误提示
    if (errors[field as keyof typeof errors]) {
      setErrors({
        ...errors,
        [field]: ''
      })
    }
  }

  const validateForm = () => {
    let isValid = true
    const newErrors = {
      email: '',
      password: ''
    }

    // 邮箱校验
    if (!formData.email) {
      newErrors.email = '请输入邮箱'
      isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址'
      isValid = false
    }

    // 密码校验
    if (!formData.password) {
      newErrors.password = '请输入密码'
      isValid = false
    } else if (formData.password.length < 6) {
      newErrors.password = '密码长度不能少于6位'
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const userLogin = async () => {
    // 表单验证
    if (!validateForm()) {
      return;
    }

    try {
      console.log('登录信息:', formData);

      // 显示加载中状态
      showLoading({
        title: '登录中...',
        mask: true
      });

      // 调用封装好的login函数
      const result = await login({
        email: formData.email,
        password: formData.password
      });

      // 隐藏加载状态
      hideLoading();

      // 根据返回结果处理
      if (result.code === 200) {
        showToast({
          title: '登录成功',
          icon: 'success',
          duration: 2000
        });

        // 存储token等用户信息（根据实际返回数据结构调整）
        if (result.data?.token) {
          setStorageSync('accessToken', result.data.token);
        }

        // 跳转到首页
        Taro.navigateTo({
          url: '/pages/myInfo/index'
        });
      } else {
        // 业务逻辑错误
        showToast({
          title: result.message || '登录失败',
          icon: 'none',
          duration: 2000
        });
      }
    } catch (error) {
      // 隐藏加载状态
      hideLoading();

      console.error('登录请求失败:', error);

      // 网络错误或系统错误
      showToast({
        title: error.message.includes('Failed to fetch')
          ? '网络连接失败，请检查网络'
          : (error.message || '登录失败'),
        icon: 'none',
        duration: 2000
      });
    }
  };

  return (
    <View className='form-container'>
      <View className='input-group'>
        <Input
          className='input'
          type='text'
          placeholder='请输入邮箱'
          placeholderClass='placeholder'
          value={formData.email}
          onInput={(e) => handleInputChange('email', e.detail.value)}
        />
        {errors.email && (
          <Text className='error-message' style={{ top: '100%' }}>
            {errors.email}
          </Text>
        )}
      </View>

      <View className='input-group' style={{ position: 'relative', marginBottom: errors.password ? '30px' : '20px' }}>
        <Input
          className='input'
          password
          placeholder='请输入密码'
          placeholderClass='placeholder'
          value={formData.password}
          onInput={(e) => handleInputChange('password', e.detail.value)}
        />
        {errors.password && (
          <Text className='error-message' style={{ top: '100%' }}>
            {errors.password}
          </Text>
        )}
        <View className='forgot-password'>忘记密码？</View>
      </View>

      <View
        className='login-button'
        onClick={userLogin}
      >登录</View>
    </View>
  )
}