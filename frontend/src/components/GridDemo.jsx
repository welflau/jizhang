import React from 'react';
import { Row, Col, Card, Typography, Space, Tag } from 'antd';
import { DesktopOutlined, TabletOutlined, MobileOutlined } from '@ant-design/icons';
import './GridDemo.css';

const { Title, Paragraph, Text } = Typography;

const GridDemo = () => {
  const breakpoints = [
    {
      name: 'Desktop',
      icon: <DesktopOutlined />,
      range: '≥ 1024px',
      color: 'blue',
      description: '桌面端显示，适用于大屏幕设备'
    },
    {
      name: 'Tablet',
      icon: <TabletOutlined />,
      range: '768px - 1023px',
      color: 'green',
      description: '平板端显示，适用于中等屏幕设备'
    },
    {
      name: 'Mobile',
      icon: <MobileOutlined />,
      range: '< 768px',
      color: 'orange',
      description: '移动端显示，适用于小屏幕设备'
    }
  ];

  const gridExamples = [
    { xs: 24, sm: 24, md: 12, lg: 8, xl: 6 },
    { xs: 24, sm: 24, md: 12, lg: 8, xl: 6 },
    { xs: 24, sm: 24, md: 12, lg: 8, xl: 6 },
    { xs: 24, sm: 24, md: 12, lg: 8, xl: 6 }
  ];

  return (
    <div className="grid-demo-container">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header Section */}
        <Card>
          <Title level={2}>响应式布局系统演示</Title>
          <Paragraph>
            本页面展示了基于 Ant Design 栅格系统的响应式布局实现。
            系统定义了三个主要断点，确保在不同设备上都能提供最佳的用户体验。
          </Paragraph>
        </Card>

        {/* Breakpoints Section */}
        <Card title="断点定义">
          <Row gutter={[16, 16]}>
            {breakpoints.map((bp, index) => (
              <Col xs={24} sm={24} md={8} key={index}>
                <Card 
                  className="breakpoint-card"
                  hoverable
                >
                  <Space direction="vertical" align="center" style={{ width: '100%' }}>
                    <div className="breakpoint-icon" style={{ fontSize: '48px', color: bp.color }}>
                      {bp.icon}
                    </div>
                    <Title level={4}>{bp.name}</Title>
                    <Tag color={bp.color}>{bp.range}</Tag>
                    <Text type="secondary">{bp.description}</Text>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Grid System Demo */}
        <Card title="栅格系统演示">
          <Paragraph>
            <Text strong>响应式列配置：</Text> 移动端(xs)单列，平板端(md)双列，桌面端(lg)三列，超大屏(xl)四列
          </Paragraph>
          <Row gutter={[16, 16]}>
            {gridExamples.map((col, index) => (
              <Col {...col} key={index}>
                <div className="grid-demo-box">
                  <Text strong>列 {index + 1}</Text>
                  <div className="grid-demo-content">
                    <Text type="secondary">xs: {col.xs}</Text>
                    <Text type="secondary">sm: {col.sm}</Text>
                    <Text type="secondary">md: {col.md}</Text>
                    <Text type="secondary">lg: {col.lg}</Text>
                    <Text type="secondary">xl: {col.xl}</Text>
                  </div>
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Nested Grid Demo */}
        <Card title="嵌套栅格演示">
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <div className="grid-demo-box">
                <Text strong>主列 1</Text>
                <Row gutter={[8, 8]} style={{ marginTop: '12px' }}>
                  <Col span={12}>
                    <div className="grid-demo-box nested">
                      <Text>嵌套 1-1</Text>
                    </div>
                  </Col>
                  <Col span={12}>
                    <div className="grid-demo-box nested">
                      <Text>嵌套 1-2</Text>
                    </div>
                  </Col>
                </Row>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div className="grid-demo-box">
                <Text strong>主列 2</Text>
                <Row gutter={[8, 8]} style={{ marginTop: '12px' }}>
                  <Col span={8}>
                    <div className="grid-demo-box nested">
                      <Text>嵌套 2-1</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div className="grid-demo-box nested">
                      <Text>嵌套 2-2</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div className="grid-demo-box nested">
                      <Text>嵌套 2-3</Text>
                    </div>
                  </Col>
                </Row>
              </div>
            </Col>
          </Row>
        </Card>

        {/* Responsive Utilities */}
        <Card title="响应式工具类">
          <Space direction="vertical" style={{ width: '100%' }}>
            <div className="show-desktop">
              <Tag color="blue">仅在桌面端显示 (≥1024px)</Tag>
            </div>
            <div className="show-tablet">
              <Tag color="green">仅在平板端显示 (768px-1023px)</Tag>
            </div>
            <div className="show-mobile">
              <Tag color="orange">仅在移动端显示 (<768px)</Tag>
            </div>
          </Space>
        </Card>

        {/* Technical Details */}
        <Card title="技术说明">
          <Space direction="vertical">
            <Paragraph>
              <Text strong>Ant Design 栅格断点：</Text>
            </Paragraph>
            <ul>
              <li><Text code>xs</Text>: &lt;576px (超小屏)</li>
              <li><Text code>sm</Text>: ≥576px (小屏)</li>
              <li><Text code>md</Text>: ≥768px (中屏 - 平板)</li>
              <li><Text code>lg</Text>: ≥992px (大屏)</li>
              <li><Text code>xl</Text>: ≥1200px (超大屏)</li>
              <li><Text code>xxl</Text>: ≥1600px (超超大屏)</li>
            </ul>
            <Paragraph>
              <Text strong>自定义断点映射：</Text>
            </Paragraph>
            <ul>
              <li>移动端: &lt;768px (xs, sm)</li>
              <li>平板端: 768px-1023px (md)</li>
              <li>桌面端: ≥1024px (lg, xl, xxl)</li>
            </ul>
          </Space>
        </Card>
      </Space>
    </div>
  );
};

export default GridDemo;