import React, { useState, useEffect } from 'react';
import { Form, Switch, Select, Button, message, Card, Divider, Space } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { userAPI } from '../../services/api';

const { Option } = Select;

interface PreferencesData {
  language: string;
  theme: string;
  emailNotifications: boolean;
  smsNotifications: boolean;
  pushNotifications: boolean;
  autoSave: boolean;
  defaultView: string;
  itemsPerPage: number;
}

const PreferencesPanel: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [initialValues, setInitialValues] = useState<PreferencesData | null>(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getPreferences();
      const preferences = response.data || getDefaultPreferences();
      setInitialValues(preferences);
      form.setFieldsValue(preferences);
    } catch (error: any) {
      message.error(error.response?.data?.message || '获取偏好设置失败');
      const defaults = getDefaultPreferences();
      setInitialValues(defaults);
      form.setFieldsValue(defaults);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultPreferences = (): PreferencesData => {
    return {
      language: 'zh-CN',
      theme: 'light',
      emailNotifications: true,
      smsNotifications: false,
      pushNotifications: true,
      autoSave: true,
      defaultView: 'grid',
      itemsPerPage: 20,
    };
  };

  const handleSubmit = async (values: PreferencesData) => {
    try {
      setLoading(true);
      await userAPI.updatePreferences(values);
      message.success('偏好设置保存成功');
      setInitialValues(values);
    } catch (error: any) {
      message.error(error.response?.data?.message || '保存偏好设置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (initialValues) {
      form.setFieldsValue(initialValues);
      message.info('已恢复到上次保存的设置');
    }
  };

  const handleRestoreDefaults = () => {
    const defaults = getDefaultPreferences();
    form.setFieldsValue(defaults);
    message.info('已恢复到默认设置');
  };

  return (
    <Card bordered={false} loading={loading}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={initialValues || undefined}
      >
        <Divider orientation="left">界面设置</Divider>

        <Form.Item
          label="语言"
          name="language"
          rules={[{ required: true, message: '请选择语言' }]}
        >
          <Select placeholder="选择语言">
            <Option value="zh-CN">简体中文</Option>
            <Option value="zh-TW">繁體中文</Option>
            <Option value="en-US">English</Option>
            <Option value="ja-JP">日本語</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="主题"
          name="theme"
          rules={[{ required: true, message: '请选择主题' }]}
        >
          <Select placeholder="选择主题">
            <Option value="light">浅色</Option>
            <Option value="dark">深色</Option>
            <Option value="auto">跟随系统</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="默认视图"
          name="defaultView"
          rules={[{ required: true, message: '请选择默认视图' }]}
        >
          <Select placeholder="选择默认视图">
            <Option value="grid">网格视图</Option>
            <Option value="list">列表视图</Option>
            <Option value="table">表格视图</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="每页显示条数"
          name="itemsPerPage"
          rules={[{ required: true, message: '请选择每页显示条数' }]}
        >
          <Select placeholder="选择每页显示条数">
            <Option value={10}>10 条</Option>
            <Option value={20}>20 条</Option>
            <Option value={50}>50 条</Option>
            <Option value={100}>100 条</Option>
          </Select>
        </Form.Item>

        <Divider orientation="left">通知设置</Divider>

        <Form.Item
          label="邮件通知"
          name="emailNotifications"
          valuePropName="checked"
        >
          <Switch checkedChildren="开启" unCheckedChildren="关闭" />
        </Form.Item>

        <Form.Item
          label="短信通知"
          name="smsNotifications"
          valuePropName="checked"
        >
          <Switch checkedChildren="开启" unCheckedChildren="关闭" />
        </Form.Item>

        <Form.Item
          label="推送通知"
          name="pushNotifications"
          valuePropName="checked"
        >
          <Switch checkedChildren="开启" unCheckedChildren="关闭" />
        </Form.Item>

        <Divider orientation="left">功能设置</Divider>

        <Form.Item
          label="自动保存"
          name="autoSave"
          valuePropName="checked"
          tooltip="编辑内容时自动保存草稿"
        >
          <Switch checkedChildren="开启" unCheckedChildren="关闭" />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              保存设置
            </Button>
            <Button onClick={handleReset} disabled={loading}>
              重置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRestoreDefaults}
              disabled={loading}
            >
              恢复默认
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default PreferencesPanel;