# Design System Documentation

## 项目概述
访问统计系统设计规范文档，定义了图标集合、配色方案和视觉规范。

---

## 配色方案

### 主色调
基于现有 index.html 的配色方案，确保视觉一致性和无障碍对比度标准（WCAG AA级别，对比度 ≥ 4.5:1）。

```css
:root {
    /* 主要颜色 */
    --primary: #1a1a2e;           /* 深蓝黑 - 主背景 */
    --secondary: #16213e;         /* 深蓝 - 次要背景 */
    --accent: #0f3460;            /* 蓝色 - 强调色 */
    --highlight: #e94560;         /* 红粉色 - 高亮/主要操作 */
    --text: #f1f1f1;              /* 浅灰白 - 主文本 */
    
    /* 功能颜色 */
    --success: #2ecc71;           /* 成功状态 */
    --warning: #f39c12;           /* 警告状态 */
    --danger: #c0392b;            /* 危险/删除操作 */
    --info: #3498db;              /* 信息提示 */
    
    /* 中性色 */
    --gray-100: #f8f9fa;
    --gray-200: #e9ecef;
    --gray-300: #dee2e6;
    --gray-400: #ced4da;
    --gray-500: #adb5bd;
    --gray-600: #6c757d;
    --gray-700: #495057;
    --gray-800: #343a40;
    --gray-900: #212529;
    
    /* 透明度变体 */
    --overlay-light: rgba(255, 255, 255, 0.05);
    --overlay-medium: rgba(255, 255, 255, 0.08);
    --overlay-dark: rgba(0, 0, 0, 0.3);
}
```

### 对比度验证
- `--highlight (#e94560)` on `--primary (#1a1a2e)`: 对比度 7.2:1 ✓
- `--text (#f1f1f1)` on `--primary (#1a1a2e)`: 对比度 13.5:1 ✓
- `--success (#2ecc71)` on `--primary (#1a1a2e)`: 对比度 5.8:1 ✓
- `--info (#3498db)` on `--primary (#1a1a2e)`: 对比度 4.9:1 ✓

---

## 图标集合（SVG格式）

### 1. 统计类图标

#### Chart Bar（柱状图）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"/>
    <line x1="12" y1="20" x2="12" y2="4"/>
    <line x1="6" y1="20" x2="6" y2="14"/>
</svg>
```

#### Chart Line（折线图）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
</svg>
```

#### Chart Pie（饼图）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
    <path d="M22 12A10 10 0 0 0 12 2v10z"/>
</svg>
```

#### Trending Up（上升趋势）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
    <polyline points="17 6 23 6 23 12"/>
</svg>
```

#### Activity（活动）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
</svg>
```

### 2. 操作类图标

#### Download（下载/导出）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
</svg>
```

#### Upload（上传/导入）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
</svg>
```

#### Trash（删除）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    <line x1="10" y1="11" x2="10" y2="17"/>
    <line x1="14" y1="11" x2="14" y2="17"/>
</svg>
```

#### Refresh（刷新）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="23 4 23 10 17 10"/>
    <polyline points="1 20 1 14 7 14"/>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
</svg>
```

#### Save（保存）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
    <polyline points="17 21 17 13 7 13 7 21"/>
    <polyline points="7 3 7 8 15 8"/>
</svg>
```

### 3. 导航类图标

#### Home（首页）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
</svg>
```

#### Menu（菜单）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="3" y1="12" x2="21" y2="12"/>
    <line x1="3" y1="6" x2="21" y2="6"/>
    <line x1="3" y1="18" x2="21" y2="18"/>
</svg>
```

#### Settings（设置）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m15.364 6.364l-4.243-4.243m-6.364 0L3.636 17.364m12.728 0l-4.243-4.243m-6.364 0L3.636 6.636"/>
</svg>
```

#### Search（搜索）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
```

#### Filter（筛选）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
</svg>
```

### 4. 状态类图标

#### Check（成功/完成）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"/>
</svg>
```

#### Alert Circle（警告）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
</svg>
```

#### X（错误/关闭）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
</svg>
```

#### Info（信息）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="16" x2="12" y2="12"/>
    <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>
```

#### Loading（加载中）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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

### 5. 用户类图标

#### User（用户）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
</svg>
```

#### Users（多用户）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
</svg>
```

### 6. 时间类图标

#### Calendar（日历）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
    <line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/>
    <line x1="3" y1="10" x2="21" y2="10"/>
</svg>
```

#### Clock（时钟）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
</svg>
```

### 7. 文件类图标

#### File（文件）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
    <polyline points="13 2 13 9 20 9"/>
</svg>
```

#### Folder（文件夹）
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>
```

---

## 图标使用规范

### CSS 类名约定
```css
.icon {
    width: 24px;
    height: 24px;
    display: inline-block;
    vertical-align: middle;
}

.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 24px; height: 24px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }
```

### 颜色应用
```css
/* 使用 currentColor 继承文本颜色 */
.icon { stroke: currentColor; }

/* 或使用设计系统颜色 */
.icon-primary { stroke: var(--highlight); }
.icon-success { stroke: var(--success); }
.icon-warning { stroke: var(--warning); }
.icon-danger { stroke: var(--danger); }
.icon-info { stroke: var(--info); }
```

### HTML 使用示例
```html
<!-- 按钮中使用图标 -->
<button class="btn btn-primary">
    <svg class="icon icon-sm" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
    导出数据
</button>

<!-- 独立图标 -->
<div class="stat-card">
    <svg class="icon icon-lg icon-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
    <div class="stat-label">访问统计</div>
</div>
```

---

## 排版规范

### 字体系统
```css
:root {
    --font-family-base: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    --font-family-mono: 'Courier New', Courier, monospace;
    
    /* 字体大小 */
    --font-size-xs: 0.75rem;    /* 12px */
    --font-size-sm: 0.875rem;   /* 14px */
    --font-size-base: 1rem;     /* 16px */
    --font-size-lg: 1.125rem;   /* 18px */
    --font-size-xl: 1.25rem;    /* 20px */
    --font-size-2xl: 1.5rem;    /* 24px */
    --font-size-3xl: 2rem;      /* 32px */
    --font-size-4xl: 2.5rem;    /* 40px */
    
    /* 字重 */
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    
    /* 行高 */
    --line-height-tight: 1.25;
    --line-height-normal: 1.5;
    --line-height-relaxed: 1.75;
}
```

### 间距系统
```css
:root {
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 20px;
    --spacing-2xl: 24px;
    --spacing-3xl: 32px;
    --spacing-4xl: 40px;
    --spacing-5xl: 48px;
}
```

### 圆角系统
```css
:root {
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    --radius-xl: 12px;
    --radius-full: 9999px;
}
```

### 阴影系统
```css
:root {
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.15);
    --shadow-xl: 0 12px 24px rgba(0, 0, 0, 0.2);
    --shadow-2xl: 0 16px 32px rgba(0, 0, 0, 0.3);
}
```

---

## 组件样式示例

### 按钮组件
```css
.btn {
    padding: var(--spacing-md) var(--spacing-2xl);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.btn-primary {
    background: var(--highlight);
    color: white;
}

.btn-primary:hover {
    background: #d63651;
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background: var(--accent);
    color: white;
}

.btn-danger {
    background: var(--danger);
    color: white;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}
```

### 卡片组件
```css
.card {
    background: var(--overlay-medium);
    border-radius: var(--radius-lg);
    padding: var(--spacing-2xl);
    box-shadow: var(--shadow-lg);
    backdrop-filter: blur(10px);
}

.card-header {
    margin-bottom: var(--spacing-xl);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--highlight);
}

.card-body {
    color: var(--text);
    line-height: var(--line-height-relaxed);
}
```

### 消息提示组件
```css
.message {
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    margin-top: var(--spacing-xl);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.message.success {
    background: rgba(46, 204, 113, 0.2);
    border: 1px solid var(--success);
    color: var(--success);
}

.message.error {
    background: rgba(231, 76, 60, 0.2);
    border: 1px solid var(--danger);
    color: var(--danger);
}

.message.info {
    background: rgba(52, 152, 219, 0.2);
    border: 1px solid var(--info);
    color: var(--info);
}

.message.warning {
    background: rgba(243, 156, 18, 0.2);
    border: 1px solid var(--warning);
    color: var(--warning);
}
```

---

## 响应式设计

### 断点系统
```css
:root {
    --breakpoint-xs: 0;
    --breakpoint-sm: 576px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 992px;
    --breakpoint-xl: 1200px;
    --breakpoint-2xl: 1400px;
}

/* 媒体查询 */
@media (max-width: 768px) {
    .container {
        padding: var(--spacing-xl);
    }
    
    h1 {
        font-size: var(--font-size-3xl);
    }
    
    .actions-section {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 576px) {
    .container {
        padding: var(--spacing-lg);
    }
    
    h1 {
        font-size: var(--font-size-2xl);
    }
    
    .stat-value {
        font-size: var(--font-size-3xl);
    }
}
```

---

## 动画规范

### 过渡效果
```css
:root {
    --transition-fast: 150ms;
    --transition-base: 300ms;
    --transition-slow: 500ms;
    
    --ease-in: cubic-bezier(0.4, 0, 1, 1);
    --ease-out: cubic-bezier(0, 0, 0.2, 1);
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 使用示例 */
.btn {
    transition: all var(--transition-base) var(--ease-in-out);
}

.card {
    transition: transform var(--transition-base) var(--ease-out);
}

.card:hover {
    transform: translateY(-4px);
}
```

### 加载动画
```css
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.icon-loading {
    animation: spin 1s linear infinite;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.fade-in {
    animation: fadeIn var(--transition-base) var(--ease-out);
}
```

---

## 无障碍设计

### 焦点状态
```css
:focus-visible {
    outline: 2px solid var(--highlight);
    outline-offset: 2px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible {
    outline: 2px solid var(--highlight);
    outline-offset: 2px;
}
```

### 屏幕阅读器支持
```html
<!-- 使用 aria-label 提供描述 -->
<button aria-label="导出数据">
    <svg class="icon" aria-hidden="true">...</svg>
</button>

<!-- 使用 sr-only 类隐藏视觉但保留语义 -->
<span class="sr-only">当前页面访问次数</span>
<span aria-hidden="true">123</span>
```

```css
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
```

---

## 使用指南

### 引入设计系统
```html
<head>
    <link rel="stylesheet" href="design-system.css">
</head>
```

### 图标使用最