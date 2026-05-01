import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Upload, Avatar, Select, DatePicker } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, UploadOutlined, CameraOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import dayjs from 'dayjs';
import { userAPI } from '../../services/api';
import './EditProfileForm.less';

const { Option } = Select;

interface UserProfile {
  id: string;
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  nickname?: string;
  gender?: 'male' | 'female' | 'other';
  birthday?: string;
  bio?: string;
  location?: string;
}

interface EditProfileFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const EditProfileForm: React.FC<EditProfileFormProps> = ({ onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string>('');
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await userAPI.getProfile();
      const profile = response.data;
      setUserProfile(profile);
      setAvatarUrl(profile.avatar || '');
      
      form.setFieldsValue({
        username: profile.username,
        email: profile.email,
        phone: profile.phone,
        nickname: profile.nickname,
        gender: profile.gender,
        birthday: profile.birthday ? dayjs(profile.birthday) : null,
        bio: profile.bio,
        location: profile.location,
      });
    } catch (error: any) {
      message.error(error.response?.data?.message || '获取用户信息失败');
    }
  };

  const handleAvatarChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  const handleAvatarUpload = async (file: File) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('avatar', file);
      
      const response = await userAPI.uploadAvatar(formData);
      const newAvatarUrl = response.data.avatarUrl;
      
      setAvatarUrl(newAvatarUrl);
      message.success('头像上传成功');
      return newAvatarUrl;
    } catch (error: any) {
      message.error(error.response?.data?.message || '头像上传失败');
      throw error;
    } finally {
      setUploading(false);
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return false;
    }
    
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('图片大小不能超过 2MB！');
      return false;
    }

    handleAvatarUpload(file);
    return false;
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const updateData = {
        ...values,
        birthday: values.birthday ? values.birthday.format('YYYY-MM-DD') : undefined,
        avatar: avatarUrl,
      };

      await userAPI.updateProfile(updateData);
      message.success('个人信息更新成功');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="edit-profile-form">
      <div className="avatar-section">
        <div className="avatar-wrapper">
          <Avatar
            size={100}
            src={avatarUrl}
            icon={!avatarUrl && <UserOutlined />}
            className="user-avatar"
          />
          <Upload
            name="avatar"
            showUploadList={false}
            beforeUpload={beforeUpload}
            onChange={handleAvatarChange}
            accept="image/*"
          >
            <Button
              icon={<CameraOutlined />}
              loading={uploading}
              className="upload-btn"
              type="primary"
              shape="circle"
            />
          </Upload>
        </div>
        <div className="avatar-tips">
          <p>点击相机图标更换头像</p>
          <p className="tips-text">支持 JPG、PNG 格式，文件小于 2MB</p>
        </div>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        className="profile-form"
        autoComplete="off"
      >
        <Form.Item
          label="用户名"
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, max: 20, message: '用户名长度为 3-20 个字符' },
            { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' }
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="请输入用户名"
            disabled
          />
        </Form.Item>

        <Form.Item
          label="昵称"
          name="nickname"
          rules={[
            { max: 30, message: '昵称不能超过 30 个字符' }
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="请输入昵称"
          />
        </Form.Item>

        <Form.Item
          label="邮箱"
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="请输入邮箱"
          />
        </Form.Item>

        <Form.Item
          label="手机号"
          name="phone"
          rules={[
            { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
          ]}
        >
          <Input
            prefix={<PhoneOutlined />}
            placeholder="请输入手机号"
          />
        </Form.Item>

        <Form.Item
          label="性别"
          name="gender"
        >
          <Select placeholder="请选择性别" allowClear>
            <Option value="male">男</Option>
            <Option value="female">女</Option>
            <Option value="other">其他</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="生日"
          name="birthday"
        >
          <DatePicker
            style={{ width: '100%' }}
            placeholder="请选择生日"
            format="YYYY-MM-DD"
            disabledDate={(current) => current && current > dayjs().endOf('day')}
          />
        </Form.Item>

        <Form.Item
          label="所在地"
          name="location"
          rules={[
            { max: 100, message: '所在地不能超过 100 个字符' }
          ]}
        >
          <Input placeholder="请输入所在地" />
        </Form.Item>

        <Form.Item
          label="个人简介"
          name="bio"
          rules={[
            { max: 200, message: '个人简介不能超过 200 个字符' }
          ]}
        >
          <Input.TextArea
            rows={4}
            placeholder="介绍一下自己吧..."
            showCount
            maxLength={200}
          />
        </Form.Item>

        <Form.Item className="form-actions">
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            size="large"
            block
          >
            保存修改
          </Button>
          {onCancel && (
            <Button
              onClick={handleCancel}
              size="large"
              block
              style={{ marginTop: '12px' }}
            >
              取消
            </Button>
          )}
        </Form.Item>
      </Form>
    </div>
  );
};

export default EditProfileForm;