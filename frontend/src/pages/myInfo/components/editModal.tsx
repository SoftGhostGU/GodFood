import { View, Text, Input } from '@tarojs/components'
import { Modal } from 'antd'
import UploadAvatar from './uploadAvatar' // 根据实际路径调整

interface EditModalProps {
  isOpen: boolean
  onOk: () => void
  onCancel: () => void
  editForm: {
    avatar: string
    name: string
    sign: string
    age: string
    gender: string
    location: string
    career: string
    phone: string
    email: string
  }
  setEditForm: (form: any) => void
}

export default function EditModal({
  isOpen,
  onOk,
  onCancel,
  editForm,
  setEditForm
}: EditModalProps) {
  return (
    <Modal
      title="编辑资料"
      closable={{ 'aria-label': 'Custom Close Button' }}
      open={isOpen}
      onOk={onOk}
      onCancel={onCancel}
      style={{
        top: '23px',
        margin: '0 auto'
      }}
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
    </Modal>
  )
}