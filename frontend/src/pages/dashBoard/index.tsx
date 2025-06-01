import { View, Text } from '@tarojs/components';
import './index.scss';
import { ConsoleSqlOutlined, SettingTwoTone } from '@ant-design/icons';
import { Progress } from 'antd';
import { useEffect, useState } from 'react';
import { getStorage, showToast, navigateTo } from '@tarojs/taro';
import HealthEditModal from './components/editForm';
import { getPredictInfo } from '../../utils/basicData';

import { getInfo, updateUserInfo } from '../../utils/user'

const HealthData = () => {
  // 状态管理
  const [currentBmi, setCurrentBmi] = useState(22.4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // 健康数据状态（统一管理）
  const [healthData, setHealthData] = useState({
    height_cm: 0,
    weight_kg: 0,
    blood_sugar: 0,
    cooking_skill: "0",
    dietary_preference: "",
    disease: "",
    education_level: "",
    fitness_goal: "",
    foodAllergy: "",
    heart_rate_bpm: 0,
    sleep_hours_last_night: 0,
    steps_today_before_meal: 0,
    weather_humidity_percent: 0,
    weather_temp_celsius: 0
  });

  // 获取健康数据
  useEffect(() => {
    const fetchPredictData = async () => {
      try {
        setLoading(true);
        // 1. 获取token
        const token = await getStorage({ key: 'accessToken' })
          .then(res => res.data)
          .catch(() => {
            showToast({ title: '请先登录', icon: 'none', duration: 2000 });
            setTimeout(() => navigateTo({ url: '/pages/login/index' }), 2000);
            throw new Error('未获取到用户token');
          });

        // 2. 调用接口获取数据
        const result = await getPredictInfo(token);
        console.log('result:', result);

        // 3. 更新健康数据状态
        setHealthData({
          height_cm: result.data.height_cm || 0,
          weight_kg: result.data.weight_kg || 0,
          blood_sugar: result.data.blood_sugar || 0,
          cooking_skill: result.data.cooking_skill || "0",
          dietary_preference: result.data.dietary_preference || "",
          disease: result.data.disease || "",
          education_level: result.data.education_level || "",
          fitness_goal: result.data.fitness_goal || "",
          foodAllergy: result.data.foodAllergy || "",
          heart_rate_bpm: result.data.heart_rate_bpm || 0,
          sleep_hours_last_night: result.data.sleep_hours_last_night || 0,
          steps_today_before_meal: result.data.steps_today_before_meal || 0,
          weather_humidity_percent: result.data.weather_humidity_percent || 0,
          weather_temp_celsius: result.data.weather_temp_celsius || 0
        });

        // 计算BMI
        if (result.data.height_cm && result.data.weight_kg) {
          const heightInM = result.data.height_cm / 100;
          const bmi = result.data.weight_kg / (heightInM * heightInM);
          setCurrentBmi(parseFloat(bmi.toFixed(1)));
        }

      } catch (err) {
        setError(err.message);
        showToast({ title: err.message || '获取预测信息失败', icon: 'none' });
      } finally {
        setLoading(false);
      }
    };

    fetchPredictData();
  }, []);

  // BMI建议
  const getAdvice = (bmi) => {
    if (bmi < 18.5) return '您的体重过轻，建议增加营养摄入并进行适量运动。';
    if (bmi >= 18.5 && bmi < 24) return '您的BMI指数处于健康范围，建议保持当前的饮食和运动习惯。';
    if (bmi >= 24 && bmi < 28) return '您的体重超重，建议控制饮食并增加运动量。';
    if (bmi >= 28) return '您的体重肥胖，建议尽快咨询医生并制定减重计划。';
    return '未知的BMI范围';
  };

  // 编辑模态框控制
  const showEditModal = () => setIsEditModalOpen(true);
  const handleCloseModal = () => setIsEditModalOpen(false);

  const handleSave_ = async (formData: typeof healthData) => {
    try {
      // 1. 获取token
      const token = await getStorage({ key: 'accessToken' })
        .then(res => res.data)
        .catch(() => {
          showToast({ title: '请先登录', icon: 'none' });
          setTimeout(() => navigateTo({ url: '/pages/login/index' }), 2000);
          throw new Error('未获取到用户token');
        });

      // 2. 获取当前健康数据
      const previousData = await getInfo(token).then(res => res.data);
      console.log('当前健康数据:', previousData);
      console.log('提交的健康数据:', formData);

      // 3. 构建提交数据（只包含修改的字段）
      const payload = {
        ...previousData,
        ...(formData.height_cm && { height_cm: formData.height_cm }),
        ...(formData.weight_kg && { weight_kg: formData.weight_kg }),
        ...(formData.blood_sugar && { blood_sugar: formData.blood_sugar }),
        ...(formData.cooking_skill && { cooking_skill: formData.cooking_skill }),
        ...(formData.dietary_preference && { dietary_preference: formData.dietary_preference }),
        ...(formData.disease && { disease: formData.disease }),
        ...(formData.education_level && { education_level: formData.education_level }),
        ...(formData.fitness_goal && { fitness_goal: formData.fitness_goal }),
        ...(formData.foodAllergy && { foodAllergy: formData.foodAllergy }),
        ...(formData.heart_rate_bpm && { heart_rate_bpm: formData.heart_rate_bpm }),
        ...(formData.sleep_hours_last_night && { sleep_hours_last_night: formData.sleep_hours_last_night }),
        ...(formData.steps_today_before_meal && { steps_today_before_meal: formData.steps_today_before_meal }),
        ...(formData.weather_humidity_percent && { weather_humidity_percent: formData.weather_humidity_percent }),
        ...(formData.weather_temp_celsius && { weather_temp_celsius: formData.weather_temp_celsius }),
      };

      console.log('提交的健康数据:', payload);

      // 4. 调用更新接口（假设存在 updateHealthInfo 接口）
      const res = await updateUserInfo(payload, token);

      if (res.code === 200) {
        // 5. 更新本地状态
        setHealthData(formData);

        // 重新计算BMI
        if (formData.height_cm && formData.weight_kg) {
          const heightInM = formData.height_cm / 100;
          const bmi = formData.weight_kg / (heightInM * heightInM);
          setCurrentBmi(parseFloat(bmi.toFixed(1)));
        }

        // 6. 关闭模态框并提示
        setIsEditModalOpen(false);
        showToast({ title: '健康数据更新成功', icon: 'success' });
        return true;
      }

      throw new Error(res.message || '更新健康数据失败');
    } catch (error) {
      console.error('更新健康数据失败:', error);
      showToast({
        title: error.message || '更新健康数据失败',
        icon: 'none'
      });
      return false;
    }
  };

  // 保存健康数据
  const handleSave = async (formData) => {
    try {
      // 这里添加保存到API的逻辑
      // const response = await updateHealthData(formData);

      // 更新本地状态
      setHealthData(formData);
      handleSave_(formData);
      showToast({ title: '保存成功', icon: 'success' });
      return true;
    } catch (error) {
      showToast({ title: '保存失败', icon: 'none' });
      return false;
    } finally {
      setIsEditModalOpen(false);
    }
  };

  // 计算BMI进度条百分比
  const getBmiProgressPercent = () => {
    if (currentBmi < 18.5) return 10;
    if (currentBmi >= 18.5 && currentBmi < 24) return 50;
    if (currentBmi >= 24 && currentBmi < 28) return 75;
    return 90;
  };

  return (
    <View className='container'>
      {/* 头部 */}
      <View className='header'>
        <Text className='title'>健康数据</Text>
        <SettingTwoTone
          twoToneColor="#4a79f7"
          className='setting-icon'
          onClick={showEditModal}
        />
      </View>

      {/* BMI展示 */}
      <View className='bmi-section'>
        <View className='bmi-title'>BMI指数</View>
        <View className='bmi-value'>{currentBmi}</View>
        <View className='bmi-description'>
          {currentBmi < 18.5 ? '体重过轻' :
            currentBmi < 24 ? '健康体重' :
              currentBmi < 28 ? '体重超重' : '体重肥胖'}
        </View>
        <Progress
          percent={getBmiProgressPercent()}
          status="active"
          strokeColor="#4a79f7"
          showInfo={false}
        />
        <View className='bmi-data'>
          <View className='bmi-low'>18.5</View>
          <View className='bmi-high'>24.9</View>
        </View>
      </View>

      {/* 健康数据展示 */}
      <View className='info-section'>
        {[
          { label: '身高', value: healthData.height_cm, unit: 'cm', icon: 'height' },
          { label: '体重', value: healthData.weight_kg, unit: 'kg', icon: 'weight' },
          { label: '血糖', value: healthData.blood_sugar, icon: 'blood_sugar' },
          { label: '饮食偏好', value: healthData.dietary_preference, icon: 'dietary_preference' },
          { label: '疾病', value: healthData.disease, icon: 'disease' },
          { label: '学历水平', value: healthData.education_level, icon: 'education' },
          { label: '目标健康', value: healthData.fitness_goal, icon: 'fitness_goal' },
          { label: '过敏食品', value: healthData.foodAllergy, icon: 'foodAllergy' },
          { label: '心跳速率', value: healthData.heart_rate_bpm, unit: 'bpm', icon: 'heart_rate_bpm' },
          { label: '睡眠时长', value: healthData.sleep_hours_last_night, unit: '小时', icon: 'sleep' },
          { label: '运动量', value: healthData.steps_today_before_meal, unit: '步', icon: 'step' },
          { label: '湿度', value: healthData.weather_humidity_percent, unit: '%', icon: 'weather_humidity' },
          { label: '温度', value: healthData.weather_temp_celsius, unit: '℃', icon: 'weather_temp' },
        ].map((item, index) => (
          <View className='info-item' key={index}>
            <View className='info-title'>
              <View
                className='info-icon'
                style={{
                  backgroundImage: `url(../../assets/icon/${item.icon}.png)`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat',
                }}
              ></View>
              <View className='label'>{item.label}</View>
            </View>
            <View className='value'>
              {item.value} {item.unit || ''}
            </View>
          </View>
        ))}
      </View>

      {/* 健康建议 */}
      <View className='advice-section'>
        <View className='advice-title'>健康建议</View>
        <View className='advice-content'>{getAdvice(currentBmi)}</View>
      </View>

      {/* 编辑模态框 */}
      <HealthEditModal
        isOpen={isEditModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSave}
        formData={healthData}
        onFormChange={setHealthData}
      />
    </View>
  );
};

export default HealthData;  