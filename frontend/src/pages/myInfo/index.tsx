import { View, Text, Input } from '@tarojs/components'
import { useLoad, showToast } from '@tarojs/taro'
import './index.scss'
import { useEffect, useState } from 'react'
import { Modal } from 'antd';
import { getStorage, navigateTo } from '@tarojs/taro'

// import UploadAvatar from './components/uploadAvatar'
import EditModal from './components/editModal'

import { getInfo } from '../../utils/user'

export default function Index() {
  const [_, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState('');

  const [userInfo, setUserInfo] = useState({
    'user-avatar': 'https://s21.ax1x.com/2025/05/26/pVSDcIH.jpg',
    'user-name': 'GHOST.',
    'user-id': '7238487',
    'user-sign': '热爱生活，享受当下',
    'user-age': '25',
    'user-gender': '男',
    'user-location': '上海市',
    'user-career': '产品设计师',
    'user-phone': '19921539522',
    'user-email': '3089308393@qq.com',
    'user-security': '高'
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
          'user-name': userInformation.data.userName,
          'user-id': userInformation.data.userID,
          'user-sign': '热爱生活，享受当下',
          'user-age': userInformation.data.age,
          'user-gender': userInformation.data.gender == '未知'? '男' : userInformation.data.gender,
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

      {/* <Modal
        title="编辑资料"
        closable={{ 'aria-label': 'Custom Close Button' }}
        open={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
        style={{
          top: '23px', // 控制距离顶部的距离
          margin: '0 auto' // 水平居中
        }}
      // className="centered-modal"
      >
        <View className="edit-form">
          <View className="form-item">
            <Text className="label">头像:</Text>
            <UploadAvatar imgUrl={editForm.avatar} />
          </View>

          <View className="form-item">
            <Text className="label">昵称:</Text>
            <Input
              value={editForm.name}
              onInput={(e) => setEditForm({ ...editForm, name: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">个性签名:</Text>
            <Input
              value={editForm.sign}
              onInput={(e) => setEditForm({ ...editForm, sign: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">年龄:</Text>
            <Input
              type="number"
              value={editForm.age}
              onInput={(e) => setEditForm({ ...editForm, age: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">性别:</Text>
            <Input
              value={editForm.gender}
              onInput={(e) => setEditForm({ ...editForm, gender: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">所在地:</Text>
            <Input
              value={editForm.location}
              onInput={(e) => setEditForm({ ...editForm, location: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">职业:</Text>
            <Input
              value={editForm.career}
              onInput={(e) => setEditForm({ ...editForm, career: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">手机号:</Text>
            <Input
              type="number"
              value={editForm.phone}
              onInput={(e) => setEditForm({ ...editForm, phone: e.detail.value })}
            />
          </View>

          <View className="form-item">
            <Text className="label">邮箱:</Text>
            <Input
              value={editForm.email}
              onInput={(e) => setEditForm({ ...editForm, email: e.detail.value })}
            />
          </View>
        </View>
      </Modal> */}
      <EditModal
        isOpen={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
        editForm={editForm}
        setEditForm={setEditForm}
      />
    </View>
  )
}
