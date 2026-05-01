import React, { useState, useMemo, useCallback } from 'react';
import './IconSelector.css';

// 常用图标列表
const ICON_LIST = [
  'home', 'user', 'settings', 'search', 'heart', 'star', 'bookmark',
  'bell', 'mail', 'phone', 'camera', 'image', 'video', 'music',
  'file', 'folder', 'download', 'upload', 'cloud', 'link', 'lock',
  'unlock', 'key', 'shield', 'eye', 'eye-off', 'edit', 'trash',
  'plus', 'minus', 'check', 'x', 'arrow-up', 'arrow-down', 'arrow-left',
  'arrow-right', 'chevron-up', 'chevron-down', 'chevron-left', 'chevron-right',
  'menu', 'more-vertical', 'more-horizontal', 'grid', 'list', 'calendar',
  'clock', 'map', 'navigation', 'compass', 'target', 'flag', 'tag',
  'filter', 'refresh', 'share', 'external-link', 'maximize', 'minimize',
  'copy', 'clipboard', 'scissors', 'paperclip', 'printer', 'monitor',
  'smartphone', 'tablet', 'laptop', 'cpu', 'hard-drive', 'wifi',
  'bluetooth', 'battery', 'zap', 'sun', 'moon', 'cloud-rain', 'wind',
  'thermometer', 'droplet', 'umbrella', 'coffee', 'gift', 'shopping-cart',
  'credit-card', 'dollar-sign', 'trending-up', 'trending-down', 'pie-chart',
  'bar-chart', 'activity', 'award', 'briefcase', 'package', 'inbox',
  'send', 'message-circle', 'message-square', 'users', 'user-plus', 'user-minus',
  'user-check', 'user-x', 'smile', 'frown', 'meh', 'thumbs-up', 'thumbs-down',
  'help-circle', 'info', 'alert-circle', 'alert-triangle', 'check-circle', 'x-circle'
];

interface IconSelectorProps {
  value?: string;
  color?: string;
  onChange?: (icon: string) => void;
  onColorChange?: (color: string) => void;
  showColorPicker?: boolean;
}

const IconSelector: React.FC<IconSelectorProps> = ({
  value = '',
  color = '#e94560',
  onChange,
  onColorChange,
  showColorPicker = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIcon, setSelectedIcon] = useState(value);
  const [iconColor, setIconColor] = useState(color);

  // 过滤图标
  const filteredIcons = useMemo(() => {
    if (!searchQuery.trim()) {
      return ICON_LIST;
    }
    const query = searchQuery.toLowerCase();
    return ICON_LIST.filter(icon => icon.toLowerCase().includes(query));
  }, [searchQuery]);

  // 选择图标
  const handleIconSelect = useCallback((icon: string) => {
    setSelectedIcon(icon);
    onChange?.(icon);
    setIsOpen(false);
    setSearchQuery('');
  }, [onChange]);

  // 改变颜色
  const handleColorChange = useCallback((newColor: string) => {
    setIconColor(newColor);
    onColorChange?.(newColor);
  }, [onColorChange]);

  // 预设颜色
  const presetColors = [
    '#e94560', '#0f3460', '#16213e', '#1a1a2e',
    '#2ecc71', '#3498db', '#9b59b6', '#f39c12',
    '#e74c3c', '#1abc9c', '#34495e', '#95a5a6'
  ];

  return (
    <div className="icon-selector">
      <div className="icon-selector-trigger" onClick={() => setIsOpen(!isOpen)}>
        <div className="selected-icon-preview">
          {selectedIcon ? (
            <span className="icon-display" style={{ color: iconColor }}>
              <i className={`icon-${selectedIcon}`}>📌</i>
            </span>
          ) : (
            <span className="icon-placeholder">选择图标</span>
          )}
        </div>
        <span className="icon-selector-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {isOpen && (
        <div className="icon-selector-dropdown">
          <div className="icon-selector-header">
            <input
              type="text"
              className="icon-search-input"
              placeholder="搜索图标..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
          </div>

          {showColorPicker && (
            <div className="color-picker-section">
              <div className="color-picker-label">图标颜色</div>
              <div className="color-picker-wrapper">
                <input
                  type="color"
                  className="color-input"
                  value={iconColor}
                  onChange={(e) => handleColorChange(e.target.value)}
                />
                <input
                  type="text"
                  className="color-text-input"
                  value={iconColor}
                  onChange={(e) => handleColorChange(e.target.value)}
                  placeholder="#e94560"
                />
              </div>
              <div className="preset-colors">
                {presetColors.map((presetColor) => (
                  <button
                    key={presetColor}
                    className={`preset-color-btn ${iconColor === presetColor ? 'active' : ''}`}
                    style={{ backgroundColor: presetColor }}
                    onClick={() => handleColorChange(presetColor)}
                    title={presetColor}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="icon-grid-container">
            {filteredIcons.length > 0 ? (
              <div className="icon-grid">
                {filteredIcons.map((icon) => (
                  <button
                    key={icon}
                    className={`icon-item ${selectedIcon === icon ? 'selected' : ''}`}
                    onClick={() => handleIconSelect(icon)}
                    title={icon}
                    style={{ color: iconColor }}
                  >
                    <i className={`icon-${icon}`}>📌</i>
                    <span className="icon-name">{icon}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="no-icons-found">
                <p>未找到匹配的图标</p>
                <p className="no-icons-hint">尝试其他关键词</p>
              </div>
            )}
          </div>

          <div className="icon-selector-footer">
            <button
              className="btn-clear"
              onClick={() => {
                setSelectedIcon('');
                onChange?.('');
                setIsOpen(false);
              }}
            >
              清除选择
            </button>
            <button
              className="btn-close"
              onClick={() => setIsOpen(false)}
            >
              关闭
            </button>
          </div>
        </div>
      )}

      {isOpen && (
        <div
          className="icon-selector-overlay"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default IconSelector;