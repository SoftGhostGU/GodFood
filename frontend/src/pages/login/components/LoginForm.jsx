import { View, Input, Button, Text } from '@tarojs/components';
import { useState } from 'react';
// import { login } from '../../../utils/auth';
import Taro from '@tarojs/taro';
import '../index.scss';
// import { formErrorToaster } from '../../../utils/error';
import { EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const LoginForm = ({ onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!agreed) {
      Taro.showToast({
        title: '请先同意服务协议',
        icon: 'none'
      });
      return;
    }
    
    setLoading(true);
    // login(username, password)
    //   .then(() => {
    //     Taro.showToast({
    //       title: '登录成功',
    //       icon: 'success'
    //     });
    //     Taro.navigateTo({
    //       url: 'pages/index/index'
    //     })
    //   })
    //   .catch(formErrorToaster)
    //   .finally(() => {
    //     setLoading(false);
    //   });
  };

  const [passwordVisible, setPasswordVisible] = useState(false);

  const togglePasswordVisible = () => {
    setPasswordVisible(!passwordVisible);
  }

  return (
    <View className="login-form">
      

      <View className="footer">
        <Text className="register-link" onClick={onSwitchToRegister}>
          还没有账号？立即注册
        </Text>
      </View>
    </View>
  );
};

export default LoginForm; 