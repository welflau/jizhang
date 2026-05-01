import React, { useState, useMemo } from 'react';
import './IconSelector.css';

// 常用图标集合
const ICON_CATEGORIES = {
  '常用': [
    { name: 'home', icon: '🏠', keywords: ['首页', '主页', '房子'] },
    { name: 'user', icon: '👤', keywords: ['用户', '个人', '账户'] },
    { name: 'settings', icon: '⚙️', keywords: ['设置', '配置', '齿轮'] },
    { name: 'search', icon: '🔍', keywords: ['搜索', '查找', '放大镜'] },
    { name: 'heart', icon: '❤️', keywords: ['喜欢', '收藏', '爱心'] },
    { name: 'star', icon: '⭐', keywords: ['星星', '收藏', '标记'] },
    { name: 'bell', icon: '🔔', keywords: ['通知', '提醒', '铃铛'] },
    { name: 'mail', icon: '✉️', keywords: ['邮件', '消息', '信封'] },
  ],
  '符号': [
    { name: 'check', icon: '✓', keywords: ['对勾', '完成', '确认'] },
    { name: 'cross', icon: '✕', keywords: ['叉号', '删除', '关闭'] },
    { name: 'plus', icon: '➕', keywords: ['加号', '添加', '新增'] },
    { name: 'minus', icon: '➖', keywords: ['减号', '删除', '移除'] },
    { name: 'arrow-up', icon: '⬆️', keywords: ['向上', '箭头', '上升'] },
    { name: 'arrow-down', icon: '⬇️', keywords: ['向下', '箭头', '下降'] },
    { name: 'arrow-left', icon: '⬅️', keywords: ['向左', '箭头', '返回'] },
    { name: 'arrow-right', icon: '➡️', keywords: ['向右', '箭头', '前进'] },
  ],
  '表情': [
    { name: 'smile', icon: '😊', keywords: ['微笑', '开心', '笑脸'] },
    { name: 'laugh', icon: '😄', keywords: ['大笑', '开心', '笑'] },
    { name: 'cool', icon: '😎', keywords: ['酷', '墨镜', '帅'] },
    { name: 'love', icon: '😍', keywords: ['喜欢', '爱', '心动'] },
    { name: 'think', icon: '🤔', keywords: ['思考', '想', '疑问'] },
    { name: 'sad', icon: '😢', keywords: ['难过', '哭', '伤心'] },
    { name: 'angry', icon: '😠', keywords: ['生气', '愤怒', '火'] },
    { name: 'surprise', icon: '😲', keywords: ['惊讶', '吃惊', '震惊'] },
  ],
  '物品': [
    { name: 'book', icon: '📚', keywords: ['书', '阅读', '学习'] },
    { name: 'calendar', icon: '📅', keywords: ['日历', '日期', '时间'] },
    { name: 'clock', icon: '⏰', keywords: ['时钟', '闹钟', '时间'] },
    { name: 'phone', icon: '📱', keywords: ['手机', '电话', '移动'] },
    { name: 'camera', icon: '📷', keywords: ['相机', '拍照', '摄影'] },
    { name: 'music', icon: '🎵', keywords: ['音乐', '歌曲', '旋律'] },
    { name: 'gift', icon: '🎁', keywords: ['礼物', '礼品', '奖励'] },
    { name: 'trophy', icon: '🏆', keywords: ['奖杯', '胜利', '冠军'] },
  ],
  '自然': [
    { name: 'sun', icon: '☀️', keywords: ['太阳', '晴天', '光'] },
    { name: 'moon', icon: '🌙', keywords: ['月亮', '夜晚', '月'] },
    { name: 'cloud', icon: '☁️', keywords: ['云', '天气', '阴天'] },
    { name: 'rain', icon: '🌧️', keywords: ['雨', '下雨', '雨天'] },
    { name: 'fire', icon: '🔥', keywords: ['火', '热门', '燃烧'] },
    { name: 'water', icon: '💧', keywords: ['水', '水滴', '液体'] },
    { name: 'tree', icon: '🌲', keywords: ['树', '森林', '植物'] },
    { name: 'flower', icon: '🌸', keywords: ['花', '鲜花', '植物'] },
  ],
};

const PRESET_COLORS = [
  '#e94560', '#1a1a2e', '#0f3460', '#16213e',
  '#2ecc71', '#3498db', '#9b59b6', '#f39c12',
  '#e74c3c', '#1abc9c', '#34495e', '#95a5a6',
  '#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731',
];

const IconSelector = ({ 
  selectedIcon = '⭐', 
  selectedColor = '#e94560',
  onIconSelect,
  onColorSelect,
  showColorPicker = true 
}) => {
  const [activeCategory, setActiveCategory] = useState('常用');
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [customColor, setCustomColor] = useState(selectedColor);

  // 搜索和过滤图标
  const filteredIcons = useMemo(() => {
    if (!searchQuery.trim()) {
      return ICON_CATEGORIES[activeCategory] || [];
    }

    const query = searchQuery.toLowerCase();
    const allIcons = Object.values(ICON_CATEGORIES).flat();
    
    return allIcons.filter(icon => 
      icon.name.toLowerCase().includes(query) ||
      icon.keywords.some(keyword => keyword.includes(query))
    );
  }, [activeCategory, searchQuery]);

  // 处理图标选择
  const handleIconSelect = (icon) => {
    if (onIconSelect) {
      onIconSelect(icon.icon);
    }
    setIsOpen(false);
  };

  // 处理颜色选择
  const handleColorSelect = (color) => {
    setCustomColor(color);
    if (onColorSelect) {
      onColorSelect(color);
    }
  };

  // 处理自定义颜色输入
  const handleCustomColorChange = (e) => {
    const color = e.target.value;
    setCustomColor(color);
    if (onColorSelect) {
      onColorSelect(color);
    }
  };

  return (
    <div className="icon-selector">
      {/* 当前选中的图标显示 */}
      <div className="icon-preview" onClick={() => setIsOpen(!isOpen)}>
        <span 
          className="preview-icon" 
          style={{ color: selectedColor }}
        >
          {selectedIcon}
        </span>
        <span className="preview-label">选择图标</span>
        <span className="preview-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {/* 图标选择器面板 */}
      {isOpen && (
        <div className="icon-selector-panel">
          {/* 搜索框 */}
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="搜索图标..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button 
                className="clear-search"
                onClick={() => setSearchQuery('')}
              >
                ✕
              </button>
            )}
          </div>

          {/* 分类标签 */}
          {!searchQuery && (
            <div className="category-tabs">
              {Object.keys(ICON_CATEGORIES).map(category => (
                <button
                  key={category}
                  className={`category-tab ${activeCategory === category ? 'active' : ''}`}
                  onClick={() => setActiveCategory(category)}
                >
                  {category}
                </button>
              ))}
            </div>
          )}

          {/* 图标网格 */}
          <div className="icon-grid">
            {filteredIcons.length > 0 ? (
              filteredIcons.map((icon, index) => (
                <button
                  key={`${icon.name}-${index}`}
                  className={`icon-item ${selectedIcon === icon.icon ? 'selected' : ''}`}
                  onClick={() => handleIconSelect(icon)}
                  title={icon.name}
                >
                  <span className="icon-symbol">{icon.icon}</span>
                </button>
              ))
            ) : (
              <div className="no-results">
                <span className="no-results-icon">🔍</span>
                <p>未找到匹配的图标</p>
              </div>
            )}
          </div>

          {/* 颜色选择器 */}
          {showColorPicker && (
            <div className="color-picker-section">
              <div className="section-title">图标颜色</div>
              
              {/* 预设颜色 */}
              <div className="preset-colors">
                {PRESET_COLORS.map(color => (
                  <button
                    key={color}
                    className={`color-item ${selectedColor === color ? 'selected' : ''}`}
                    style={{ backgroundColor: color }}
                    onClick={() => handleColorSelect(color)}
                    title={color}
                  />
                ))}
              </div>

              {/* 自定义颜色 */}
              <div className="custom-color">
                <label className="custom-color-label">
                  <span>自定义颜色</span>
                  <input
                    type="color"
                    value={customColor}
                    onChange={handleCustomColorChange}
                    className="color-input"
                  />
                </label>
                <input
                  type="text"
                  value={customColor}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (/^#[0-9A-Fa-f]{0,6}$/.test(value)) {
                      handleCustomColorChange(e);
                    }
                  }}
                  placeholder="#e94560"
                  className="color-text-input"
                  maxLength={7}
                />
              </div>
            </div>
          )}

          {/* 预览区域 */}
          <div className="preview-section">
            <div className="section-title">预览效果</div>
            <div className="preview-display">
              <span 
                className="preview-large-icon"
                style={{ color: selectedColor }}
              >
                {selectedIcon}
              </span>
              <div className="preview-info">
                <div className="preview-detail">
                  <span className="detail-label">图标:</span>
                  <span className="detail-value">{selectedIcon}</span>
                </div>
                <div className="preview-detail">
                  <span className="detail-label">颜色:</span>
                  <span className="detail-value">{selectedColor}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IconSelector;

.icon-selector {
  position: relative;
  width: 100%;
}

.icon-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-preview:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(233, 69, 96, 0.5);
  transform: translateY(-2px);
}

.preview-icon {
  font-size: 2em;
  line-height: 1;
}

.preview-label {
  flex: 1;
  font-weight: 600;
  color: var(--text, #f1f1f1);
}

.preview-arrow {
  font-size: 0.8em;
  opacity: 0.6;
  transition: transform 0.3s ease;
}

.icon-selector-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: rgba(22, 33, 62, 0.98);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  z-index: 1000;
  max-height: 600px;
  overflow-y: auto;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-box {
  position: relative;
  margin-bottom: 20px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2em;
  opacity: 0.6;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 40px;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text, #f1f1f1);
  font-size: 1em;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: rgba(233, 69, 96, 0.5);
  background: rgba(255, 255, 255, 0.12);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text, #f1f1f1);
  font-size: 1.2em;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.clear-search:hover {
  opacity: 1;
}

.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.category-tab {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: var(--text, #f1f1f1);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.category-tab:hover {
  background: rgba(255, 255, 255, 0.12);
}

.category-tab.active {
  background: var(--highlight, #e94560);
  border-color: var(--highlight, #e94560);
  color: white;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 8px;
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px;
}

.icon-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-item:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(233, 69, 96, 0.5);
  transform: scale(1.1);
}

.icon-item.selected {
  background: rgba(233, 69, 96, 0.2);
  border-color: var(--highlight, #e94560);
}

.icon-symbol {
  font-size: 2em;
  line-height: 1;
}

.no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.no-results-icon {
  font-size: 3em;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

.color-picker-section {
  border-top: 2px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text, #f1f1f1);
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.8;
}

.preset-colors {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.color-item {
  aspect-ratio: 1;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.color-item:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.color-item.selected {
  border-color: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.color-item.selected::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
}

.custom-color {
  display: flex;
  gap: 12px;
  align-items: center;
}

.custom-color-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text, #f1f1f1);
  font-size: 0.9em;
}

.color-input {
  width: 50px;
  height: 40px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  background: transparent;
}

.color-text-input {
  flex: 1;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: var(--text, #f1f1f1);
  font-family: monospace;
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.color-text-input:focus {
  outline: none;
  border-color: rgba(233, 69, 96, 0.5);
  background: rgba(255, 255, 255, 0.12);
}

.preview-section {
  border-top: 2px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
  margin-top: 20px;
}

.preview-display {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.preview-large-icon {
  font-size: 4em;
  line-height: 1;
}

.preview-info {
  flex: 1;
}

.preview-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.detail-label {
  font-weight: 600;
  opacity: 0.7;
  min-width: 50px;
}

.detail-value {
  font-family: monospace;
  background: rgba(255, 255, 255, 0.08);
  padding: 4px 8px;
  border-radius: 4px;
}

/* 滚动条样式 */
.icon-selector-panel::-webkit-scrollbar,
.icon-grid::-webkit-scrollbar,
.category-tabs::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.icon-selector-panel::-webkit-scrollbar-track,
.icon-grid::-webkit-scrollbar-track,
.category-tabs::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.icon-selector-panel::-webkit-scrollbar-thumb,
.icon-grid::-webkit-scrollbar-thumb,
.category-tabs::-webkit-scrollbar-thumb {
  background: rgba(233, 69, 96, 0.5);
  border-radius: 4px;
}

.icon-selector-panel::-webkit-scrollbar-thumb:hover,
.icon-grid::-webkit-scrollbar-thumb:hover,
.category-tabs::-webkit-scrollbar-thumb:hover {
  background: rgba(233, 69, 96, 0.7);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .icon-selector-panel {
    max-height: 500px;
  }

  .icon-grid {
    grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
    max-height: 250px;
  }

  .preset-colors {
    grid-template-columns: repeat(6, 1fr);
  }

  .preview-display {
    flex-direction: column;
    text-align: center;
  }

  .preview-large-icon {
    font-size: 3em;
  }
}