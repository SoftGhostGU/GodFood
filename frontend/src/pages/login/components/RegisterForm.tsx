import { View, Input } from '@tarojs/components'
import './RegisterForm.scss'

export default function RegisterForm() {
  const login = () => {
    console.log('login')
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
        className='login-button'
        onClick={login}
      >注册</View>
    </View>
  )
}