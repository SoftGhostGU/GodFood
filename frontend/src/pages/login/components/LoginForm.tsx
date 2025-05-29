import { View, Input, Text } from '@tarojs/components'
import './LoginForm.scss'
import Taro from '@tarojs/taro'
import { useState } from 'react'

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

  const login = () => {
    if (!validateForm()) {
      return
    }
    
    console.log('登录信息:', formData)
    Taro.navigateTo({
      url: '/pages/index/index'
    })
  }
  
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
        onClick={login}
      >登录</View>
    </View>
  )
}