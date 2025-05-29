import { View, Input, Text } from '@tarojs/components'
import './RegisterForm.scss'
import Taro from '@tarojs/taro'
import { useState } from 'react'

import { register } from '../../../utils/user'

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    userName: '',
    email: '',
    password: ''
  })
  
  const [errors, setErrors] = useState({
    userName: '',
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
      userName: '',
      email: '',
      password: ''
    }

    // 用户名校验
    if (!formData.userName.trim()) {
      newErrors.userName = '请输入用户名'
      isValid = false
    } else if (formData.userName.length < 2 || formData.userName.length > 16) {
      newErrors.userName = '用户名长度需为2-16个字符'
      isValid = false
    } else if (!/^[\u4e00-\u9fa5a-zA-Z0-9_]+$/.test(formData.userName)) {
      newErrors.userName = '用户名只能包含中文、字母、数字和下划线'
      isValid = false
    }

    // 邮箱校验
    if (!formData.email.trim()) {
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
    } else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{6,}$/.test(formData.password)) {
      newErrors.password = '需包含大小写字母和数字'
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const userRegister = () => {
    if (!validateForm()) {
      return
    }
    
    console.log('注册信息:', formData)

    register(formData)

    Taro.navigateTo({
      url: '/pages/login/index'
    })
  }

  return (
    <View className='form-container'>
      <View className={`register-input-group ${errors.userName ? 'has-error' : ''}`}>
        <Input
          className='input'
          type='text'
          placeholder='请输入用户名（2-16位字符）'
          placeholderClass='placeholder'
          value={formData.userName}
          onInput={(e) => handleInputChange('userName', e.detail.value)}
        />
        {errors.userName && <Text className='error-message'>{errors.userName}</Text>}
      </View>

      <View className={`register-input-group ${errors.email ? 'has-error' : ''}`}>
        <Input
          className='input'
          type='text'
          placeholder='请输入邮箱'
          placeholderClass='placeholder'
          value={formData.email}
          onInput={(e) => handleInputChange('email', e.detail.value)}
        />
        {errors.email && <Text className='error-message'>{errors.email}</Text>}
      </View>

      <View className={`register-input-group ${errors.password ? 'has-error' : ''}`}>
        <Input
          className='input'
          password
          placeholder='请输入密码（至少6位，含大小写字母和数字）'
          placeholderClass='placeholder'
          value={formData.password}
          onInput={(e) => handleInputChange('password', e.detail.value)}
        />
        {errors.password && <Text className='error-message'>{errors.password}</Text>}
      </View>

      <View
        className='register-button'
        onClick={userRegister}
      >注册</View>
    </View>
  )
}