import React, { useState } from 'react';
import { Card, Button, Upload, message, Modal, Space, Typography, Divider } from 'antd';
import { DownloadOutlined, UploadOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { confirm } = Modal;

const DataManagement = () => {
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);

  // 导出数据
  const handleExport = async () => {
    try {
      setExporting(true);
      const response = await axios.get('/api/export', {
        responseType: 'blob'
      });
      
      const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace('T', '_').split('.')[0];
      const filename = `visits_backup_${timestamp}.json`;
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('数据导出成功！');
    } catch (error) {
      console.error('Export error:', error);
      message.error('导出失败：' + (error.response?.data?.error || error.message));
    } finally {
      setExporting(false);
    }
  };

  // 导入数据
  const handleImport = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setImporting(true);
      const response = await axios.post('/api/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const { success, failed, total } = response.data;
      Modal.success({
        title: '导入完成',
        content: (
          <div>
            <p>总计: {total} 条</p>
            <p style={{ color: 'green' }}>成功: {success} 条</p>
            {failed > 0 && <p style={{ color: 'red' }}>失败: {failed} 条</p>}
          </div>
        )
      });
    } catch (error) {
      console.error('Import error:', error);
      message.error('导入失败：' + (error.response?.data?.error || error.message));
    } finally {
      setImporting(false);
    }
    
    return false; // 阻止自动上传
  };

  // 清空数据
  const handleClear = () => {
    confirm({
      title: '确定要清空所有数据吗？',
      icon: <ExclamationCircleOutlined />,
      content: '此操作不可恢复！所有访问记录将被永久删除。',
      okText: '确定清空',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await axios.delete('/api/clear');
          message.success('数据已清空');
        } catch (error) {
          console.error('Clear error:', error);
          message.error('清空失败：' + (error.response?.data?.error || error.message));
        }
      }
    });
  };

  return (
    <Card title="数据管理" style={{ marginTop: 24 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 导出功能 */}
        <div>
          <Title level={5}>导出数据</Title>
          <Text type="secondary">将所有访问记录导出为 JSON 文件</Text>
          <br />
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            loading={exporting}
            style={{ marginTop: 8 }}
          >
            导出数据
          </Button>
        </div>

        <Divider />

        {/* 导入功能 */}
        <div>
          <Title level={5}>导入数据</Title>
          <Text type="secondary">从 JSON 文件导入访问记录</Text>
          <br />
          <Upload
            accept=".json"
            beforeUpload={handleImport}
            showUploadList={false}
            disabled={importing}
          >
            <Button
              icon={<UploadOutlined />}
              loading={importing}
              style={{ marginTop: 8 }}
            >
              选择文件导入
            </Button>
          </Upload>
        </div>

        <Divider />

        {/* 清空功能 */}
        <div>
          <Title level={5}>清空数据</Title>
          <Text type="secondary" style={{ color: '#ff4d4f' }}>
            危险操作：将删除所有访问记录，此操作不可恢复！
          </Text>
          <br />
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={handleClear}
            style={{ marginTop: 8 }}
          >
            清空所有数据
          </Button>
        </div>
      </Space>
    </Card>
  );
};

export default DataManagement;