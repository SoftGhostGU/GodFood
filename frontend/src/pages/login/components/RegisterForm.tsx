import { View, Input, Text } from '@tarojs/components'
import './RegisterForm.scss'
import Taro from '@tarojs/taro'
import { useState } from 'react'

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  })
  
  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmPassword: ''
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
      password: '',
      confirmPassword: ''
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

    // 确认密码校验
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请再次输入密码'
      isValid = false
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致'
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const register = () => {
    if (!validateForm()) {
      return
    }
    
    console.log('注册信息:', formData)
    Taro.navigateTo({
      url: '/pages/index/index'
    })
  }

  return (
    <View className='form-container'>
      <View className={`register-input-group ${errors.email ? 'has-error' : ''}`}>
        <Input
          className='input'
          type='text'  // 改为text类型，number类型不适合邮箱输入
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
          placeholder='请输入密码'
          placeholderClass='placeholder'
          value={formData.password}
          onInput={(e) => handleInputChange('password', e.detail.value)}
        />
        {errors.password && <Text className='error-message'>{errors.password}</Text>}
      </View>

      <View className={`register-input-group ${errors.confirmPassword ? 'has-error' : ''}`}>
        <Input
          className='input'
          password
          placeholder='请再次输入密码'
          placeholderClass='placeholder'
          value={formData.confirmPassword}
          onInput={(e) => handleInputChange('confirmPassword', e.detail.value)}
        />
        {errors.confirmPassword && <Text className='error-message'>{errors.confirmPassword}</Text>}
      </View>

      <View
        className='register-button'
        onClick={register}
      >注册</View>
    </View>
  )
}