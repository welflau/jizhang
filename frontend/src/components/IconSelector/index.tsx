import React, { useState, useMemo } from 'react';
import * as Icons from 'lucide-react';
import './IconSelector.css';

interface IconSelectorProps {
  value?: string;
  onChange?: (iconName: string) => void;
  color?: string;
  onColorChange?: (color: string) => void;
  showColorPicker?: boolean;
}

const IconSelector: React.FC<IconSelectorProps> = ({
  value = 'Circle',
  onChange,
  color = '#e94560',
  onColorChange,
  showColorPicker = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIcon, setSelectedIcon] = useState(value);

  // 获取所有可用的图标
  const allIcons = useMemo(() => {
    return Object.keys(Icons).filter(
      (key) => key !== 'createLucideIcon' && typeof Icons[key as keyof typeof Icons] === 'function'
    );
  }, []);

  // 过滤图标
  const filteredIcons = useMemo(() => {
    if (!searchTerm) return allIcons;
    return allIcons.filter((iconName) =>
      iconName.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [allIcons, searchTerm]);

  // 获取图标组件
  const getIconComponent = (iconName: string) => {
    const IconComponent = Icons[iconName as keyof typeof Icons] as React.ComponentType<any>;
    return IconComponent;
  };

  // 处理图标选择
  const handleIconSelect = (iconName: string) => {
    setSelectedIcon(iconName);
    onChange?.(iconName);
    setIsOpen(false);
    setSearchTerm('');
  };

  // 处理颜色变化
  const handleColorChange = (newColor: string) => {
    onColorChange?.(newColor);
  };

  const SelectedIconComponent = getIconComponent(selectedIcon);

  return (
    <div className="icon-selector">
      <div className="icon-selector-trigger" onClick={() => setIsOpen(!isOpen)}>
        <div className="selected-icon-preview">
          <SelectedIconComponent size={24} color={color} strokeWidth={2} />
          <span className="selected-icon-name">{selectedIcon}</span>
        </div>
        <Icons.ChevronDown
          size={20}
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
        />
      </div>

      {isOpen && (
        <>
          <div className="icon-selector-overlay" onClick={() => setIsOpen(false)} />
          <div className="icon-selector-dropdown">
            <div className="icon-selector-header">
              <div className="search-wrapper">
                <Icons.Search size={18} className="search-icon" />
                <input
                  type="text"
                  className="icon-search-input"
                  placeholder="搜索图标..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  autoFocus
                />
                {searchTerm && (
                  <button
                    className="clear-search-btn"
                    onClick={() => setSearchTerm('')}
                  >
                    <Icons.X size={16} />
                  </button>
                )}
              </div>

              {showColorPicker && (
                <div className="color-picker-section">
                  <label className="color-label">图标颜色</label>
                  <div className="color-input-wrapper">
                    <input
                      type="color"
                      value={color}
                      onChange={(e) => handleColorChange(e.target.value)}
                      className="color-input"
                    />
                    <input
                      type="text"
                      value={color}
                      onChange={(e) => handleColorChange(e.target.value)}
                      className="color-text-input"
                      placeholder="#e94560"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="icon-grid-container">
              {filteredIcons.length > 0 ? (
                <div className="icon-grid">
                  {filteredIcons.map((iconName) => {
                    const IconComponent = getIconComponent(iconName);
                    const isSelected = iconName === selectedIcon;

                    return (
                      <div
                        key={iconName}
                        className={`icon-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => handleIconSelect(iconName)}
                        title={iconName}
                      >
                        <div className="icon-preview">
                          <IconComponent size={24} color={color} strokeWidth={2} />
                        </div>
                        <span className="icon-name">{iconName}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="no-results">
                  <Icons.SearchX size={48} color="var(--text)" opacity={0.3} />
                  <p>未找到匹配的图标</p>
                  <button
                    className="clear-search-link"
                    onClick={() => setSearchTerm('')}
                  >
                    清除搜索
                  </button>
                </div>
              )}
            </div>

            <div className="icon-selector-footer">
              <span className="icon-count">
                显示 {filteredIcons.length} / {allIcons.length} 个图标
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default IconSelector;