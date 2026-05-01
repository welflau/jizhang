import React, { useState } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { changePassword } from '../../services/user';

interface ChangePasswordModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: {
    oldPassword: string;
    newPassword: string;
    confirmPassword: string;
  }) => {
    if (values.newPassword !== values.confirmPassword) {
      message.error('两次输入的新密码不一致');
      return;
    }

    setLoading(true);
    try {
      await changePassword({
        oldPassword: values.oldPassword,
        newPassword: values.newPassword,
      });
      message.success('密码修改成功，请重新登录');
      form.resetFields();
      onSuccess();
    } catch (error: any) {
      message.error(error.message || '密码修改失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title="修改密码"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      destroyOnClose
      width={480}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        autoComplete="off"
      >
        <Form.Item
          name="oldPassword"
          label="当前密码"
          rules={[
            { required: true, message: '请输入当前密码' },
            { min: 6, message: '密码长度至少为6位' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="请输入当前密码"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="newPassword"
          label="新密码"
          rules={[
            { required: true, message: '请输入新密码' },
            { min: 6, message: '密码长度至少为6位' },
            { max: 20, message: '密码长度不能超过20位' },
            {
              pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]/,
              message: '密码必须包含大小写字母和数字',
            },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="请输入新密码（6-20位，包含大小写字母和数字）"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          label="确认新密码"
          dependencies={['newPassword']}
          rules={[
            { required: true, message: '请再次输入新密码' },
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
            prefix={<LockOutlined />}
            placeholder="请再次输入新密码"
            size="large"
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <Button onClick={handleCancel}>
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              确认修改
            </Button>
          </div>
        </Form.Item>
      </Form>

      <div style={{ marginTop: 16, padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
        <div style={{ fontSize: '12px', color: '#666' }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>密码要求：</div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>长度为6-20位字符</li>
            <li>必须包含大写字母、小写字母和数字</li>
            <li>可以包含特殊字符 @$!%*?&</li>
          </ul>
        </div>
      </div>
    </Modal>
  );
};

export default ChangePasswordModal;