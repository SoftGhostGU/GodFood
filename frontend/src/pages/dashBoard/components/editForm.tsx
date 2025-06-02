import { View, Text, Input } from '@tarojs/components'
import { Modal } from 'antd'

interface HealthForm {
  height_cm: number;
  weight_kg: number;
  blood_sugar: number;
  cooking_skill: string;
  dietary_preference: string;
  disease: string;
  education_level: string;
  fitness_goal: string;
  foodAllergy: string;
  heart_rate_bpm: number;
  sleep_hours_last_night: number;
  steps_today_before_meal: number;
  weather_humidity_percent: number;
  weather_temp_celsius: number;
}

interface HealthEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: HealthForm) => Promise<boolean>;
  formData: HealthForm;
  onFormChange: (data: HealthForm) => void;
}

export default function HealthEditModal({
  isOpen,
  onClose,
  onSubmit,
  formData,
  onFormChange
}: HealthEditModalProps) {
  const handleChange = (key: keyof HealthForm, value: string | number) => {
    onFormChange({ ...formData, [key]: value });
  };

  return (
    <Modal 
      title="编辑健康数据"
      open={isOpen} 
      onCancel={onClose} 
      onOk={() => onSubmit(formData)}
      style={{
        top: '23px',
        margin: '0 auto'
      }}
    >
      <View className="edit-form">
        <View className="form-item">
          <Text className="label">身高(cm):</Text>
          <Input
            type="number"
            value={formData.height_cm.toString()}
            onInput={(e) => handleChange('height_cm', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">体重(kg):</Text>
          <Input
            type="number"
            value={formData.weight_kg.toString()}
            onInput={(e) => handleChange('weight_kg', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">血糖:</Text>
          <Input
            type="number"
            value={formData.blood_sugar.toString()}
            onInput={(e) => handleChange('blood_sugar', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">烹饪技能:</Text>
          <Input
            value={formData.cooking_skill}
            onInput={(e) => handleChange('cooking_skill', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">饮食偏好:</Text>
          <Input
            value={formData.dietary_preference}
            onInput={(e) => handleChange('dietary_preference', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">疾病:</Text>
          <Input
            value={formData.disease}
            onInput={(e) => handleChange('disease', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">教育水平:</Text>
          <Input
            value={formData.education_level}
            onInput={(e) => handleChange('education_level', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">健身目标:</Text>
          <Input
            value={formData.fitness_goal}
            onInput={(e) => handleChange('fitness_goal', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">食物过敏:</Text>
          <Input
            value={formData.foodAllergy}
            onInput={(e) => handleChange('foodAllergy', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">心率(bpm):</Text>
          <Input
            type="number"
            value={formData.heart_rate_bpm.toString()}
            onInput={(e) => handleChange('heart_rate_bpm', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">睡眠时长(小时):</Text>
          <Input
            type="number"
            value={formData.sleep_hours_last_night.toString()}
            onInput={(e) => handleChange('sleep_hours_last_night', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">今日步数:</Text>
          <Input
            type="number"
            value={formData.steps_today_before_meal.toString()}
            onInput={(e) => handleChange('steps_today_before_meal', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">湿度(%):</Text>
          <Input
            type="number"
            value={formData.weather_humidity_percent.toString()}
            onInput={(e) => handleChange('weather_humidity_percent', Number(e.detail.value))}
          />
        </View>

        <View className="form-item">
          <Text className="label">温度(℃):</Text>
          <Input
            type="number"
            value={formData.weather_temp_celsius.toString()}
            onInput={(e) => handleChange('weather_temp_celsius', Number(e.detail.value))}
          />
        </View>
      </View>
    </Modal>
  );
}