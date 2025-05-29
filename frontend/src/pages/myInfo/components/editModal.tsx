import { View, Text, Input } from '@tarojs/components'
import { Modal } from 'antd'
import UploadAvatar from './uploadAvatar'

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

interface EditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: EditForm) => Promise<boolean>;
  formData: EditForm;
  onFormChange: (data: EditForm) => void;
}

export default function EditModal({
  isOpen,
  onClose,
  onSubmit,
  formData,
  onFormChange
}: EditModalProps) {
  const handleChange = (key: keyof EditForm, value: string) => {
    onFormChange({ ...formData, [key]: value });
  };

  return (
    <Modal 
      title="编辑资料"
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
          <Text className="label">头像:</Text>
          <UploadAvatar imgUrl={formData.avatar} />
        </View>

        <View className="form-item">
          <Text className="label">昵称:</Text>
          <Input
            value={formData.name}
            onInput={(e) => handleChange('name', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">个性签名:</Text>
          <Input
            value={formData.sign}
            onInput={(e) => handleChange('sign', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">年龄:</Text>
          <Input
            type="number"
            value={formData.age}
            onInput={(e) => handleChange('age', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">性别:</Text>
          <Input
            value={formData.gender}
            onInput={(e) => handleChange('gender', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">所在地:</Text>
          <Input
            value={formData.location}
            onInput={(e) => handleChange('location', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">职业:</Text>
          <Input
            value={formData.career}
            onInput={(e) => handleChange('career', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">手机号:</Text>
          <Input
            type="number"
            value={formData.phone}
            onInput={(e) => handleChange('phone', e.detail.value)}
          />
        </View>

        <View className="form-item">
          <Text className="label">邮箱:</Text>
          <Input
            value={formData.email}
            onInput={(e) => handleChange('email', e.detail.value)}
          />
        </View>
      </View>
    </Modal>
  );
}