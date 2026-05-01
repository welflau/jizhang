import React, { useState } from 'react';
import { Card, Avatar, Button, Descriptions, Tag, Space, Modal, Form, Input, message, Upload } from 'antd';
import { EditOutlined, LockOutlined, UserOutlined, MailOutlined, PhoneOutlined, CameraOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';

interface UserInfo {
  id: string;
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  nickname?: string;
  role: string;
  status: 'active' | 'inactive';
  createdAt: string;
  lastLoginAt?: string;
}

interface UserInfoCardProps {
  userInfo: UserInfo;
  onUpdate: (values: Partial<UserInfo>) => Promise<void>;
  onPasswordChange: (values: { oldPassword: string; newPassword: string }) => Promise<void>;
}

const UserInfoCard: React.FC<UserInfoCardProps> = ({ userInfo, onUpdate, onPasswordChange }) => {
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(userInfo.avatar);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const handleEdit = () => {
    form.setFieldsValue({
      nickname: userInfo.nickname,
      email: userInfo.email,
      phone: userInfo.phone,
    });
    setEditModalVisible(true);
  };

  const handleEditSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await onUpdate(values);
      message.success('个人信息更新成功');
      setEditModalVisible(false);
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请检查表单填写');
      } else {
        message.error(error.message || '更新失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = () => {
    passwordForm.resetFields();
    setPasswordModalVisible(true);
  };

  const handlePasswordSubmit = async () => {
    try {
      const values = await passwordForm.validateFields();
      setLoading(true);
      await onPasswordChange(values);
      message.success('密码修改成功');
      setPasswordModalVisible(false);
      passwordForm.resetFields();
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请检查表单填写');
      } else {
        message.error(error.message || '密码修改失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = async (info: any) => {
    if (info.file.status === 'uploading') {
      setLoading(true);
      return;
    }
    if (info.file.status === 'done') {
      const url = info.file.response?.url || URL.createObjectURL(info.file.originFileObj);
      setAvatarUrl(url);
      try {
        await onUpdate({ avatar: url });
        message.success('头像更新成功');
      } catch (error: any) {
        message.error(error.message || '头像更新失败');
      } finally {
        setLoading(false);
      }
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件');
      return false;
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('图片大小不能超过 2MB');
      return false;
    }
    return true;
  };

  const getRoleTag = (role: string) => {
    const roleMap: Record<string, { color: string; text: string }> = {
      admin: { color: 'red', text: '管理员' },
      user: { color: 'blue', text: '普通用户' },
      vip: { color: 'gold', text: 'VIP用户' },
    };
    const roleInfo = roleMap[role] || { color: 'default', text: role };
    return <Tag color={roleInfo.color}>{roleInfo.text}</Tag>;
  };

  const getStatusTag = (status: string) => {
    return status === 'active' ? (
      <Tag color="success">正常</Tag>
    ) : (
      <Tag color="error">已停用</Tag>
    );
  };

  return (
    <>
      <Card
        title="个人信息"
        extra={
          <Space>
            <Button icon={<LockOutlined />} onClick={handlePasswordChange}>
              修改密码
            </Button>
            <Button type="primary" icon={<EditOutlined />} onClick={handleEdit}>
              编辑资料
            </Button>
          </Space>
        }
      >
        <div style={{ display: 'flex', gap: '24px' }}>
          <div style={{ position: 'relative' }}>
            <Avatar
              size={120}
              src={avatarUrl}
              icon={<UserOutlined />}
              style={{ border: '2px solid #f0f0f0' }}
            />
            <Upload
              name="avatar"
              showUploadList={false}
              beforeUpload={beforeUpload}
              onChange={handleAvatarChange}
              customRequest={({ file, onSuccess }) => {
                setTimeout(() => {
                  onSuccess?.({ url: URL.createObjectURL(file as File) });
                }, 1000);
              }}
            >
              <Button
                type="primary"
                shape="circle"
                size="small"
                icon={<CameraOutlined />}
                style={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                }}
                loading={loading}
              />
            </Upload>
          </div>

          <div style={{ flex: 1 }}>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="用户名" span={1}>
                <Space>
                  <UserOutlined />
                  {userInfo.username}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="昵称" span={1}>
                {userInfo.nickname || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="邮箱" span={1}>
                <Space>
                  <MailOutlined />
                  {userInfo.email}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="手机号" span={1}>
                <Space>
                  <PhoneOutlined />
                  {userInfo.phone || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="角色" span={1}>
                {getRoleTag(userInfo.role)}
              </Descriptions.Item>
              <Descriptions.Item label="状态" span={1}>
                {getStatusTag(userInfo.status)}
              </Descriptions.Item>
              <Descriptions.Item label="注册时间" span={1}>
                {new Date(userInfo.createdAt).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录" span={1}>
                {userInfo.lastLoginAt
                  ? new Date(userInfo.lastLoginAt).toLocaleString('zh-CN')
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
          </div>
        </div>
      </Card>

      {/* 编辑资料弹窗 */}
      <Modal
        title="编辑个人资料"
        open={editModalVisible}
        onOk={handleEditSubmit}
        onCancel={() => setEditModalVisible(false)}
        confirmLoading={loading}
        width={500}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            label="昵称"
            name="nickname"
            rules={[
              { max: 50, message: '昵称不能超过50个字符' },
            ]}
          >
            <Input placeholder="请输入昵称" prefix={<UserOutlined />} />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" prefix={<MailOutlined />} />
          </Form.Item>

          <Form.Item
            label="手机号"
            name="phone"
            rules={[
              { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
            ]}
          >
            <Input placeholder="请输入手机号" prefix={<PhoneOutlined />} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 修改密码弹窗 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onOk={handlePasswordSubmit}
        onCancel={() => setPasswordModalVisible(false)}
        confirmLoading={loading}
        width={500}
      >
        <Form form={passwordForm} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            label="原密码"
            name="oldPassword"
            rules={[{ required: true, message: '请输入原密码' }]}
          >
            <Input.Password
              placeholder="请输入原密码"
              prefix={<LockOutlined />}
            />
          </Form.Item>

          <Form.Item
            label="新密码"
            name="newPassword"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6个字符' },
              { max: 20, message: '密码不能超过20个字符' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]/,
                message: '密码必须包含大小写字母和数字',
              },
            ]}
          >
            <Input.Password
              placeholder="请输入新密码（6-20位，包含大小写字母和数字）"
              prefix={<LockOutlined />}
            />
          </Form.Item>

          <Form.Item
            label="确认新密码"
            name="confirmPassword"
            dependencies={['newPassword']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('newPassword') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              placeholder="请再次输入新密码"
              prefix={<LockOutlined />}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default UserInfoCard;