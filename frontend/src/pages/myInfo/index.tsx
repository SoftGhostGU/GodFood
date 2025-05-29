import { View } from '@tarojs/components'
import { useLoad, showToast } from '@tarojs/taro'
import './index.scss'
import { useEffect, useState } from 'react'
import { getStorage, navigateTo } from '@tarojs/taro'

// import UploadAvatar from './components/uploadAvatar'
import EditModal from './components/editModal'

import { getInfo, updateUserInfo } from '../../utils/user'

interface EditForm {
  avatar: string;
  name: string;
  sign: string;
  age: string;
  gender: string;
  location: string;
  career: string;
  phone: string;
  email: string;
}

export default function Index() {
  const [_, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState('');

  const [userInfo, setUserInfo] = useState({
    // 'user-avatar': 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg',
    // 'user-name': 'GHOST.',
    // 'user-id': '7238487',
    // 'user-sign': '热爱生活，享受当下',
    // 'user-age': '25',
    // 'user-gender': '男',
    // 'user-location': '上海市',
    // 'user-career': '产品设计师',
    // 'user-phone': '19921539522',
    // 'user-email': '3089308393@qq.com',
    // 'user-security': '高'
    'user-avatar': "https://s21.ax1x.com/2025/05/29/pVpDCpn.png",
    'user-name': 'username',
    'user-id': '未登录',
    'user-sign': '热爱生活，享受当下',
    'user-age': '0',
    'user-gender': '男',
    'user-location': '上海市',
    'user-career': '产品设计师',
    'user-phone': '未填写',
    'user-email': '未填写',
    'user-security': '低'
  })
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    avatar: userInfo['user-avatar'],
    name: userInfo['user-name'],
    sign: userInfo['user-sign'],
    age: userInfo['user-age'],
    gender: userInfo['user-gender'],
    location: userInfo['user-location'],
    career: userInfo['user-career'],
    phone: userInfo['user-phone'],
    email: userInfo['user-email']
  })

  useEffect(() => {
    const checkLoginAndFetchUser = async () => {
      // 1. 获取 accessToken
      const storageRes = await getStorage({ key: 'accessToken' })
        .then(res => {
          console.log('Storage API Response:', res.data);
          return res.data;
        })
        .catch(() => '');

      setToken(storageRes); // 更新 token 状态

      if (!storageRes) {
        // 未登录：跳转到登录页
        showToast({
          title: '请先登录',
          icon: 'none',
          duration: 2000,
        });
        setTimeout(() => {
          navigateTo({ url: '/pages/login/index' });
        }, 2000);
        return; // 终止后续逻辑
      }

      // 2. 已登录：获取用户信息
      try {
        const userInformation = await getInfo(storageRes); // 使用 storageRes（确保 token 最新）
        console.log('User Info:', userInformation);
        // 更新用户信息状态（假设有 setUserInfo）
        setUserInfo({
          'user-avatar': userInformation.data.avatarUrl,
          'user-name': userInformation.data.userName || '未填写',
          'user-id': userInformation.data.userID || '未登录',
          'user-sign': '热爱生活，享受当下',
          'user-age': userInformation.data.age || '未填写',
          'user-gender': userInformation.data.gender == '未知' ? '男' : userInformation.data.gender,
          'user-location': userInformation.data.hometown || '上海市',
          'user-career': userInformation.data.occupation || '产品设计师',
          'user-phone': userInformation.data.phone == 0 ? '未填写' : userInformation.data.phone,
          'user-email': userInformation.data.email,
          'user-security': '高'
        });
        console.log('User Info After Login:', userInfo);
        setIsLoggedIn(true);
      } catch (error) {
        console.error('获取用户信息失败:', error);
        showToast({
          title: '获取用户信息失败',
          icon: 'none',
        });
      }
    };

    checkLoginAndFetchUser();
  }, []);

  useEffect(() => {
    setEditForm({
      avatar: userInfo['user-avatar'],
      name: userInfo['user-name'],
      sign: userInfo['user-sign'],
      age: userInfo['user-age'],
      gender: userInfo['user-gender'],
      location: userInfo['user-location'],
      career: userInfo['user-career'],
      phone: userInfo['user-phone'],
      email: userInfo['user-email']
    });
  }, [userInfo]);

  const userInformation = getInfo(token)
  console.log(userInformation)

  const showModal = () => {
    // 打开弹窗时初始化表单数据
    setEditForm({
      avatar: userInfo['user-avatar'],
      name: userInfo['user-name'],
      sign: userInfo['user-sign'],
      age: userInfo['user-age'],
      gender: userInfo['user-gender'],
      location: userInfo['user-location'],
      career: userInfo['user-career'],
      phone: userInfo['user-phone'],
      email: userInfo['user-email']
    })
    setIsModalOpen(true)
  };

  const handleOk = () => {
    // 保存修改
    setUserInfo({
      ...userInfo,
      'user-avatar': editForm.avatar,
      'user-name': editForm.name,
      'user-sign': editForm.sign,
      'user-age': editForm.age,
      'user-gender': editForm.gender,
      'user-location': editForm.location,
      'user-career': editForm.career,
      'user-phone': editForm.phone,
      'user-email': editForm.email
    })
    setIsModalOpen(false)
    showToast({
      title: '修改完成',
      icon: 'success',
      duration: 2000
    })
  };

  const handleSave = async (formData: EditForm) => {
  try {
    // 从userInfo映射到API字段
    const currentData = {
      avatarUrl: userInfo['user-avatar'],
      userName: userInfo['user-name'],
      age: Number(userInfo['user-age']) || 0,
      gender: userInfo['user-gender'],
      hometown: userInfo['user-location'],
      occupation: userInfo['user-career'],
      phone: userInfo['user-phone'],
      email: userInfo['user-email'],
      userID: userInfo['user-id'],
      // 其他字段保持原值...
    };

    // console.log('userInformation', userInformation);
    const previousData = await getInfo(token).then(res => {
      console.log('getInfo:', res.data);
      return res.data;
    });
    console.log('previousData:', previousData);

    // 只覆盖editForm中修改的字段
    const payload = {
      ...previousData,
      ...(formData.avatar && { avatarUrl: formData.avatar }),
      ...(formData.name && { userName: formData.name }),
      ...(formData.age && { age: Number(formData.age) }),
      ...(formData.gender && { gender: formData.gender }),
      ...(formData.location && { hometown: formData.location }),
      ...(formData.career && { occupation: formData.career }),
      ...(formData.phone && { phone: formData.phone }),
      ...(formData.email && { email: formData.email }),
    };

    console.log('最终提交数据:', payload);

    const res = await updateUserInfo(payload, token);
    
    if (res.code === 200) {
      setUserInfo(prev => ({
        ...prev,
        'user-avatar': payload.avatarUrl,
        'user-name': payload.userName,
        'user-age': payload.age.toString(),
        'user-gender': payload.gender,
        'user-location': payload.hometown,
        'user-career': payload.occupation,
        'user-phone': payload.phone,
        'user-email': payload.email
      }));
      
      setIsModalOpen(false);
      showToast({ title: '更新成功', icon: 'success' });
      return true;
    }
    throw new Error(res.message || '更新失败');
  } catch (error: any) {
    console.error('更新失败:', error);
    showToast({ 
      title: error.message || '更新用户信息失败',
      icon: 'none'
    });
    return false;
  }
};

  const handleCancel = () => {
    setIsModalOpen(false);
  };

  useLoad(() => {
    console.log('Page loaded.')
  })

  const editInfo = () => {
    console.log('Edit button clicked.')
    showModal()
  }

  return (
    <View className='myInfo'>
      <View className='header'>
        <View className='header-prev'></View>
        <View className='header-text'>个人主页</View>
        <View
          className='header-edit'
          onClick={editInfo}
        >编辑</View>
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
        onClick={editInfo}
      >
        编辑资料
      </View>

      <EditModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSave}
        formData={editForm}
        onFormChange={setEditForm}
      />
    </View>
  )
}
