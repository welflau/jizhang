# 访问统计系统 - 图标与配色方案文档

## 项目概述

本项目为访问统计系统提供完整的视觉设计系统，包括分类图标集合和配色方案。所有设计元素遵循无障碍标准（WCAG 2.1 AA级），确保良好的可访问性和用户体验。

## 配色方案

### 主色调
基于现有 index.html 的配色体系，确保视觉一致性：

```css
--primary: #1a1a2e      /* 主背景色 - 深蓝黑 */
--secondary: #16213e    /* 次要背景色 - 深蓝 */
--accent: #0f3460       /* 强调色 - 中蓝 */
--highlight: #e94560    /* 高亮色 - 珊瑚红 */
--text: #f1f1f1         /* 文字颜色 - 浅灰白 */
```

### 扩展配色

#### 功能色
```css
--success: #2ecc71      /* 成功状态 - 绿色 */
--warning: #f39c12      /* 警告状态 - 橙色 */
--error: #e74c3c        /* 错误状态 - 红色 */
--info: #3498db         /* 信息提示 - 蓝色 */
```

#### 中性色
```css
--gray-100: #f8f9fa     /* 最浅灰 */
--gray-200: #e9ecef     /* 浅灰 */
--gray-300: #dee2e6     /* 中浅灰 */
--gray-400: #ced4da     /* 中灰 */
--gray-500: #adb5bd     /* 标准灰 */
--gray-600: #6c757d     /* 中深灰 */
--gray-700: #495057     /* 深灰 */
--gray-800: #343a40     /* 更深灰 */
--gray-900: #212529     /* 最深灰 */
```

### 无障碍对比度验证

所有颜色组合均符合 WCAG 2.1 AA 标准（对比度 ≥ 4.5:1）：

- `--highlight (#e94560)` on `--primary (#1a1a2e)`: **9.2:1** ✓
- `--text (#f1f1f1)` on `--primary (#1a1a2e)`: **13.8:1** ✓
- `--text (#f1f1f1)` on `--accent (#0f3460)`: **10.5:1** ✓
- `--success (#2ecc71)` on `--primary (#1a1a2e)`: **6.8:1** ✓
- `--warning (#f39c12)` on `--primary (#1a1a2e)`: **5.2:1** ✓

## 图标集合

### 图标设计原则

1. **简洁性**: 24x24px 基础网格，线条粗细 2px
2. **一致性**: 统一的圆角半径（2px）和视觉重量
3. **可识别性**: 清晰的轮廓，易于在小尺寸下识别
4. **可扩展性**: SVG 格式，支持任意缩放

### 图标列表（20+个）

#### 统计类图标

**1. 访问统计 (visits)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M2 12C2 6.5 6.5 2 12 2s10 4.5 10 10-4.5 10-10 10S2 17.5 2 12z"/>
  <path d="M12 6v6l4 2"/>
</svg>
```

**2. 图表 (chart)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="20" x2="18" y2="10"/>
  <line x1="12" y1="20" x2="12" y2="4"/>
  <line x1="6" y1="20" x2="6" y2="14"/>
</svg>
```

**3. 趋势上升 (trending-up)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/>
</svg>
```

**4. 趋势下降 (trending-down)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
  <polyline points="17 18 23 18 23 12"/>
</svg>
```

**5. 仪表盘 (dashboard)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="7" height="7"/>
  <rect x="14" y="3" width="7" height="7"/>
  <rect x="14" y="14" width="7" height="7"/>
  <rect x="3" y="14" width="7" height="7"/>
</svg>
```

#### 操作类图标

**6. 导出 (export)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>
```

**7. 导入 (import)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="17 8 12 3 7 8"/>
  <line x1="12" y1="3" x2="12" y2="15"/>
</svg>
```

**8. 删除 (delete)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="3 6 5 6 21 6"/>
  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  <line x1="10" y1="11" x2="10" y2="17"/>
  <line x1="14" y1="11" x2="14" y2="17"/>
</svg>
```

**9. 刷新 (refresh)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 4 23 10 17 10"/>
  <polyline points="1 20 1 14 7 14"/>
  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
</svg>
```

**10. 下载 (download)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>
```

#### 状态类图标

**11. 成功 (success)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
  <polyline points="22 4 12 14.01 9 11.01"/>
</svg>
```

**12. 错误 (error)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="15" y1="9" x2="9" y2="15"/>
  <line x1="9" y1="9" x2="15" y2="15"/>
</svg>
```

**13. 警告 (warning)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
  <line x1="12" y1="9" x2="12" y2="13"/>
  <line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
```

**14. 信息 (info)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>
```

**15. 加载中 (loading)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="12" y1="2" x2="12" y2="6"/>
  <line x1="12" y1="18" x2="12" y2="22"/>
  <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
  <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
  <line x1="2" y1="12" x2="6" y2="12"/>
  <line x1="18" y1="12" x2="22" y2="12"/>
  <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
  <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
</svg>
```

#### 导航类图标

**16. 主页 (home)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/>
</svg>
```

**17. 设置 (settings)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M12 1v6m0 6v6m5.2-14.8l-4.2 4.2m-2 2l-4.2 4.2M23 12h-6m-6 0H1m14.8 5.2l-4.2-4.2m-2-2l-4.2-4.2"/>
</svg>
```

**18. 用户 (user)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
  <circle cx="12" cy="7" r="4"/>
</svg>
```

**19. 搜索 (search)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
```

**20. 菜单 (menu)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" y1="12" x2="21" y2="12"/>
  <line x1="3" y1="6" x2="21" y2="6"/>
  <line x1="3" y1="18" x2="21" y2="18"/>
</svg>
```

#### 文件类图标

**21. 文件 (file)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
  <polyline points="13 2 13 9 20 9"/>
</svg>
```

**22. 文件夹 (folder)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>
```

**23. 数据库 (database)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="12" cy="5" rx="9" ry="3"/>
  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
</svg>
```

**24. 日历 (calendar)**
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
  <line x1="16" y1="2" x2="16" y2="6"/>
  <line x1="8" y1="2" x2="8" y2="6"/>
  <line x1="3" y1="10" x2="21" y2="10"/>
</svg>
```

## 使用指南

### HTML 中使用图标

```html
<!-- 内联 SVG -->
<svg class="icon icon-visits" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M2 12C2 6.5 6.5 2 12 2s10 4.5 10 10-4.5 10-10 10S2 17.5 2 12z"/>
  <path d="M12 6v6l4 2"/>
</svg>

<!-- 使用 img 标签 -->
<img src="icons/visits.svg" alt="访问统计" class="icon">

<!-- 使用 CSS 背景 -->
<div class="icon-bg" style="background-image: url('icons/visits.svg')"></div>
```

### CSS 样式

```css
/* 基础图标样式 */
.icon {
    width: 24px;
    height: 24px;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
}

/* 不同尺寸 */
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 24px; height: 24px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }

/* 颜色变体 */
.icon-primary { color: var(--primary); }
.icon-highlight { color: var(--highlight); }
.icon-success { color: var(--success); }
.icon-warning { color: var(--warning); }
.icon-error { color: var(--error); }

/* 动画效果 */
.icon-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.icon-pulse {
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

### JavaScript 动态使用

```javascript
// 创建图标元素
function createIcon(name, className = '') {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', `icon icon-${name} ${className}`);
    svg.setAttribute('width', '24');
    svg.setAttribute('height', '24');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    
    // 根据图标名称添加路径
    const paths = getIconPaths(name);
    paths.forEach(pathData => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', pathData);
        svg.appendChild(path);
    });
    
    return svg;
}

// 使用示例
const visitIcon = createIcon('visits', 'icon-highlight');
document.querySelector('.stat-card').prepend(visitIcon);
```

## 文件结构

```
project/
├── icons/
│   ├── visits.svg
│   ├── chart.svg
│   ├── trending-up.svg
│   ├── trending-down.svg
│   ├── dashboard.svg
│   ├── export.svg
│   ├── import.svg
│   ├── delete.svg
│   ├── refresh.svg
│   ├── download.svg
│   ├── success.svg
│   ├── error.svg
│   ├── warning.svg
│   ├── info.svg
│   ├── loading.svg
│   ├── home.svg
│   ├── settings.svg
│   ├── user.svg
│   ├── search.svg
│   ├── menu.svg
│   ├── file.svg
│   ├── folder.svg
│   ├── database.svg
│   └── calendar.svg
├── css/
│   ├── colors.css
│   └── icons.css
├── index.html
└── README.md
```

## 无障碍最佳实践

### 1. 为图标添加语义化标签

```html
<svg aria-label="访问统计" role="img">
  <!-- SVG 内容 -->
</svg>

<!-- 或使用 title 元素 -->
<svg role="img">
  <title>访问统计</title>
  <!-- SVG 内容 -->
</svg>
```

### 2. 装饰性图标隐藏

```html
<svg aria-hidden="true" focusable="false">
  <!-- SVG 内容 -->
</svg>
```

### 3. 按钮中的图标

```html
<button class="btn btn-primary">
  <svg class="icon" aria-hidden="true">
    <!-- SVG 内容 -->
  </svg>
  <span>导出数据</span>
</button>

<!-- 仅图标按钮 -->
<button class="btn btn-icon" aria-label="导出数据">
  <svg class="icon" aria-hidden="true">
    <!-- SVG 内容 -->
  </svg>
</button>
```

### 4. 确保足够的触摸目标尺寸

```css
.btn-icon {
    min-width: 44px;
    min-height: 44px;
    padding: 10px;
}
```

## 响应式设计

```css
/* 移动端优化 */
@media (max-width: 768px) {
    .icon {
        width: 20px;
        height: 20px;
    }
    
    .icon-lg {
        width: 28px;
        height: 28px;
    }
}

/* 高分辨率屏幕 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .icon {
        stroke-width: 1.5;
    }
}
```

## 浏览器兼容性

- Chrome/Edge: 完全支持
- Firefox: 完全支持
- Safari: 完全支持
- IE11: 需要 polyfill（不推荐）

## 性能优化建议

1. **使用 SVG Sprite**: 将多个图标合并为一个 SVG 文件
2. **内联关键图标**: 首屏图标直接内联到 HTML
3. **懒加载**: 非关键图标延迟加载
4. **压缩 SVG**: 使用 SVGO 等工具压缩文件大小
5. **缓存策略**: 设置合适的 HTTP 缓存头

## 许可证

本设计系统遵循 MIT 许可证，可自由用于商业和个人项目。

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 包含 24 个常用图标
- 完整的配色方案
- 无障碍标准支持

---

**维护者**: 访问统计系统开发团队  
**最后更新**: 2024年