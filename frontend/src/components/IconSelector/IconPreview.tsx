import React from 'react';
import * as Icons from 'lucide-react';

interface IconPreviewProps {
  iconName: string;
  color?: string;
  size?: number;
  className?: string;
  onClick?: () => void;
  selected?: boolean;
}

const IconPreview: React.FC<IconPreviewProps> = ({
  iconName,
  color = '#e94560',
  size = 24,
  className = '',
  onClick,
  selected = false,
}) => {
  // 获取图标组件
  const IconComponent = (Icons as any)[iconName];

  // 如果图标不存在，显示占位符
  if (!IconComponent) {
    return (
      <div
        className={`icon-preview-placeholder ${className} ${selected ? 'selected' : ''}`}
        onClick={onClick}
        style={{
          width: size + 16,
          height: size + 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          border: selected ? '2px solid var(--highlight)' : '2px solid transparent',
          cursor: onClick ? 'pointer' : 'default',
          transition: 'all 0.3s ease',
        }}
      >
        <span style={{ fontSize: '12px', opacity: 0.5 }}>?</span>
      </div>
    );
  }

  return (
    <div
      className={`icon-preview ${className} ${selected ? 'selected' : ''}`}
      onClick={onClick}
      style={{
        width: size + 16,
        height: size + 16,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '8px',
        border: selected ? '2px solid var(--highlight)' : '2px solid transparent',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        position: 'relative',
      }}
      title={iconName}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'none';
        }
      }}
    >
      <IconComponent
        size={size}
        color={color}
        strokeWidth={2}
      />
      {selected && (
        <div
          style={{
            position: 'absolute',
            top: '-4px',
            right: '-4px',
            width: '12px',
            height: '12px',
            background: 'var(--highlight)',
            borderRadius: '50%',
            border: '2px solid var(--primary)',
          }}
        />
      )}
    </div>
  );
};

export default IconPreview;