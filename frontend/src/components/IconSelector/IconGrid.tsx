import React, { useState, useMemo } from 'react';
import * as Icons from 'lucide-react';
import './IconGrid.css';

interface IconGridProps {
  selectedIcon: string;
  onIconSelect: (iconName: string) => void;
  searchQuery?: string;
}

const IconGrid: React.FC<IconGridProps> = ({
  selectedIcon,
  onIconSelect,
  searchQuery = ''
}) => {
  const [hoveredIcon, setHoveredIcon] = useState<string | null>(null);

  // 获取所有可用的图标
  const allIcons = useMemo(() => {
    const iconList: { name: string; component: React.ComponentType<any> }[] = [];
    
    Object.entries(Icons).forEach(([name, component]) => {
      // 过滤掉非图标组件
      if (
        typeof component === 'function' &&
        name !== 'createLucideIcon' &&
        !name.startsWith('Lucide')
      ) {
        iconList.push({ name, component });
      }
    });
    
    return iconList.sort((a, b) => a.name.localeCompare(b.name));
  }, []);

  // 根据搜索查询过滤图标
  const filteredIcons = useMemo(() => {
    if (!searchQuery.trim()) {
      return allIcons;
    }
    
    const query = searchQuery.toLowerCase();
    return allIcons.filter(icon =>
      icon.name.toLowerCase().includes(query)
    );
  }, [allIcons, searchQuery]);

  const handleIconClick = (iconName: string) => {
    onIconSelect(iconName);
  };

  const handleKeyDown = (e: React.KeyboardEvent, iconName: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleIconClick(iconName);
    }
  };

  if (filteredIcons.length === 0) {
    return (
      <div className="icon-grid-empty">
        <Icons.Search size={48} />
        <p>未找到匹配的图标</p>
        <span>尝试使用其他关键词搜索</span>
      </div>
    );
  }

  return (
    <div className="icon-grid-container">
      <div className="icon-grid-header">
        <span className="icon-count">
          {filteredIcons.length} 个图标
        </span>
      </div>
      
      <div className="icon-grid">
        {filteredIcons.map(({ name, component: IconComponent }) => {
          const isSelected = selectedIcon === name;
          const isHovered = hoveredIcon === name;
          
          return (
            <div
              key={name}
              className={`icon-item ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
              onClick={() => handleIconClick(name)}
              onMouseEnter={() => setHoveredIcon(name)}
              onMouseLeave={() => setHoveredIcon(null)}
              onKeyDown={(e) => handleKeyDown(e, name)}
              tabIndex={0}
              role="button"
              aria-label={`选择图标 ${name}`}
              aria-pressed={isSelected}
            >
              <div className="icon-wrapper">
                <IconComponent size={24} strokeWidth={2} />
              </div>
              <div className="icon-name">{name}</div>
              
              {isSelected && (
                <div className="icon-selected-badge">
                  <Icons.Check size={14} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default IconGrid;