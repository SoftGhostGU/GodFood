import { View, Text, Image } from '@tarojs/components';
import './index.scss';
import { SettingTwoTone } from '@ant-design/icons';
import { Progress } from 'antd';
import { useState } from 'react';

const HealthData = () => {
  const [currentBmi, setCurrentBmi] = useState(22.4);

  // 根据BMI值提供建议的函数
  const getAdvice = (bmi) => {
    if (bmi < 18.5) {
      return '您的体重过轻，建议增加营养摄入并进行适量运动。';
    } else if (bmi >= 18.5 && bmi < 24) {
      return '您的BMI指数处于健康范围，建议保持当前的饮食和运动习惯。';
    } else if (bmi >= 24 && bmi < 28) {
      return '您的体重超重，建议控制饮食并增加运动量。';
    } else if (bmi >= 28) {
      return '您的体重肥胖，建议尽快咨询医生并制定减重计划。';
    } else {
      return '未知的BMI范围';
    }
  };

  return (
    <View className='container'>
      <View className='header'>
        <Text className='title'>健康数据</Text>
        <SettingTwoTone
          twoToneColor="#aa5c53"
          className='setting-icon'
        />
      </View>
      <View className='bmi-section'>
        <View className='bmi-title'>BMI指数</View>
        <View className='bmi-value'>22.4</View>
        <View className='bmi-description'>健康体重</View>
        <Progress
          percent={50}
          status="active"
          strokeColor="#4a79f7"
          showInfo={false}
        />
        <View className='bmi-data'>
          <View className='bmi-low'>18.5</View>
          <View className='bmi-high'>24.9</View>
        </View>
      </View>
      <View className='info-section'>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/height.png)` }}
            ></View>
            <View className='label'>身高</View>
          </View>
          <View className='value'>175cm</View>
          <View className='status'>↑ 保持不变</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/weight.png)` }}
            ></View>
            <View className='label'>体重</View>
          </View>
          <View className='value'>68kg</View>
          <View className='status'>↑ +0.5kg</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/fatness.png)` }}
            ></View>
            <View className='label'>体脂率</View>
          </View>
          <View className='value'>22.5%</View>
          <View className='status'>保持</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/muscle.png)` }}
            ></View>
            <View className='label'>肌肉量</View>
          </View>
          <View className='value'>35.2kg</View>
          <View className='status'>+0.8kg</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/metabolize.png)` }}
            ></View>
            <View className='label'>基础代谢</View>
          </View>
          <View className='value'>1580kcal</View>
          <View className='status'>保持</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/bone.png)` }}
            ></View>
            <View className='label'>内脏脂肪</View>
          </View>
          <View className='value'>5.2</View>
          <View className='status'>-0.3</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/bone-muscle.png)` }}
            ></View>
            <View className='label'>骨骼肌量</View>
          </View>
          <View className='value'>30.1kg</View>
          <View className='status'>+0.5kg</View>
        </View>
        <View className='info-item'>
          <View className='info-title'>
            <View
              className='info-icon'
              style={{ backgroundImage: `url(../../assets/icon/water.png)` }}
            ></View>
            <View className='label'>体水分</View>
          </View>
          <View className='value'>45.8%</View>
          <View className='status'>保持</View>
        </View>
      </View>
      {/* <View className='chart-section'>
        <View className='chart-title'>近期变化趋势</View>
        <Image className='chart-image' src='path/to/your/chart/image.png' />
      </View> */}
      <View className='advice-section'>
        <View className='advice-title'>健康建议</View>
        <View className='advice-content'>{getAdvice(currentBmi)}</View>
      </View>
    </View>
  );
};

export default HealthData;