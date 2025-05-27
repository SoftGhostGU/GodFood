import { View, Input } from '@tarojs/components'
import './RegisterForm.scss'
import Taro from '@tarojs/taro'

export default function RegisterForm() {
  const register = () => {
    console.log('register')
    Taro.navigateTo({
      url: '/pages/index/index'
    })
  }

  return (
    <View className='form-container'>
      <View className='register-input-group'>
        <Input
          className='input'
          type='number'
          placeholder='请输入邮箱'
          placeholderClass='placeholder'
        />
      </View>

      <View className='register-input-group'>
        <Input
          className='input'
          password
          placeholder='请输入密码'
          placeholderClass='placeholder'
        />
        {/* <View className='forgot-password'>忘记密码？</View> */}
      </View>

      <View className='register-input-group'>
        <Input
          className='input'
          password
          placeholder='请再次输入密码'
          placeholderClass='placeholder'
        />
        {/* <View className='forgot-password'>忘记密码？</View> */}
      </View>

      <View
        className='register-button'
        onClick={register}
      >注册</View>
    </View>
  )
}