import { View, Input } from '@tarojs/components'
import './LoginForm.scss'

export default function LoginForm() {
  const login = () => {
    console.log('login')
  }
  
  return (
    <View className='form-container'>
      <View className='input-group'>
        <Input
          className='input'
          type='number'
          placeholder='请输入邮箱'
          placeholderClass='placeholder'
        />
      </View>

      <View className='input-group'>
        <Input
          className='input'
          password
          placeholder='请输入密码'
          placeholderClass='placeholder'
        />
        <View className='forgot-password'>忘记密码？</View>
      </View>

      <View
        className='login-button'
        onClick={login}
      >登录</View>
    </View>
  )
}