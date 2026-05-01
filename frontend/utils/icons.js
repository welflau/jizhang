// frontend/utils/icons.js
// 图标工具类 - 提供图标数据和相关功能

/**
 * 可用图标列表
 * 使用 Unicode 字符作为图标
 */
export const AVAILABLE_ICONS = [
    { id: 'home', char: '🏠', name: '首页', category: 'common' },
    { id: 'user', char: '👤', name: '用户', category: 'common' },
    { id: 'settings', char: '⚙️', name: '设置', category: 'common' },
    { id: 'search', char: '🔍', name: '搜索', category: 'common' },
    { id: 'star', char: '⭐', name: '星标', category: 'common' },
    { id: 'heart', char: '❤️', name: '喜欢', category: 'common' },
    { id: 'bookmark', char: '🔖', name: '书签', category: 'common' },
    { id: 'bell', char: '🔔', name: '通知', category: 'common' },
    { id: 'mail', char: '📧', name: '邮件', category: 'common' },
    { id: 'message', char: '💬', name: '消息', category: 'common' },
    
    { id: 'folder', char: '📁', name: '文件夹', category: 'file' },
    { id: 'file', char: '📄', name: '文件', category: 'file' },
    { id: 'image', char: '🖼️', name: '图片', category: 'file' },
    { id: 'video', char: '🎬', name: '视频', category: 'file' },
    { id: 'music', char: '🎵', name: '音乐', category: 'file' },
    { id: 'document', char: '📝', name: '文档', category: 'file' },
    { id: 'download', char: '⬇️', name: '下载', category: 'file' },
    { id: 'upload', char: '⬆️', name: '上传', category: 'file' },
    
    { id: 'chart', char: '📊', name: '图表', category: 'business' },
    { id: 'calendar', char: '📅', name: '日历', category: 'business' },
    { id: 'clock', char: '🕐', name: '时钟', category: 'business' },
    { id: 'briefcase', char: '💼', name: '公文包', category: 'business' },
    { id: 'money', char: '💰', name: '金钱', category: 'business' },
    { id: 'cart', char: '🛒', name: '购物车', category: 'business' },
    { id: 'tag', char: '🏷️', name: '标签', category: 'business' },
    
    { id: 'globe', char: '🌐', name: '全球', category: 'web' },
    { id: 'link', char: '🔗', name: '链接', category: 'web' },
    { id: 'wifi', char: '📶', name: 'WiFi', category: 'web' },
    { id: 'cloud', char: '☁️', name: '云', category: 'web' },
    { id: 'database', char: '💾', name: '数据库', category: 'web' },
    { id: 'server', char: '🖥️', name: '服务器', category: 'web' },
    
    { id: 'phone', char: '📱', name: '手机', category: 'device' },
    { id: 'laptop', char: '💻', name: '笔记本', category: 'device' },
    { id: 'tablet', char: '📱', name: '平板', category: 'device' },
    { id: 'camera', char: '📷', name: '相机', category: 'device' },
    { id: 'printer', char: '🖨️', name: '打印机', category: 'device' },
    
    { id: 'check', char: '✅', name: '完成', category: 'status' },
    { id: 'cross', char: '❌', name: '错误', category: 'status' },
    { id: 'warning', char: '⚠️', name: '警告', category: 'status' },
    { id: 'info', char: 'ℹ️', name: '信息', category: 'status' },
    { id: 'question', char: '❓', name: '问题', category: 'status' },
    { id: 'lock', char: '🔒', name: '锁定', category: 'status' },
    { id: 'unlock', char: '🔓', name: '解锁', category: 'status' },
    
    { id: 'plus', char: '➕', name: '添加', category: 'action' },
    { id: 'minus', char: '➖', name: '减少', category: 'action' },
    { id: 'edit', char: '✏️', name: '编辑', category: 'action' },
    { id: 'delete', char: '🗑️', name: '删除', category: 'action' },
    { id: 'refresh', char: '🔄', name: '刷新', category: 'action' },
    { id: 'share', char: '📤', name: '分享', category: 'action' },
    { id: 'copy', char: '📋', name: '复制', category: 'action' },
    
    { id: 'sun', char: '☀️', name: '太阳', category: 'nature' },
    { id: 'moon', char: '🌙', name: '月亮', category: 'nature' },
    { id: 'fire', char: '🔥', name: '火', category: 'nature' },
    { id: 'water', char: '💧', name: '水', category: 'nature' },
    { id: 'tree', char: '🌲', name: '树', category: 'nature' },
    { id: 'flower', char: '🌸', name: '花', category: 'nature' },
    
    { id: 'gift', char: '🎁', name: '礼物', category: 'misc' },
    { id: 'trophy', char: '🏆', name: '奖杯', category: 'misc' },
    { id: 'flag', char: '🚩', name: '旗帜', category: 'misc' },
    { id: 'pin', char: '📌', name: '图钉', category: 'misc' },
    { id: 'key', char: '🔑', name: '钥匙', category: 'misc' },
    { id: 'bulb', char: '💡', name: '灯泡', category: 'misc' },
    { id: 'rocket', char: '🚀', name: '火箭', category: 'misc' },
    { id: 'target', char: '🎯', name: '目标', category: 'misc' }
];

/**
 * 图标分类
 */
export const ICON_CATEGORIES = [
    { id: 'all', name: '全部' },
    { id: 'common', name: '常用' },
    { id: 'file', name: '文件' },
    { id: 'business', name: '商务' },
    { id: 'web', name: '网络' },
    { id: 'device', name: '设备' },
    { id: 'status', name: '状态' },
    { id: 'action', name: '操作' },
    { id: 'nature', name: '自然' },
    { id: 'misc', name: '其他' }
];

/**
 * 根据ID获取图标
 */
export function getIconById(id) {
    return AVAILABLE_ICONS.find(icon => icon.id === id);
}

/**
 * 根据分类获取图标列表
 */
export function getIconsByCategory(category) {
    if (category === 'all') {
        return AVAILABLE_ICONS;
    }
    return AVAILABLE_ICONS.filter(icon => icon.category === category);
}

/**
 * 搜索图标
 */
export function searchIcons(query) {
    if (!query || query.trim() === '') {
        return AVAILABLE_ICONS;
    }
    
    const lowerQuery = query.toLowerCase().trim();
    return AVAILABLE_ICONS.filter(icon => 
        icon.name.toLowerCase().includes(lowerQuery) ||
        icon.id.toLowerCase().includes(lowerQuery)
    );
}

/**
 * 创建图标选择器组件
 */
export function createIconSelector(options = {}) {
    const {
        onSelect = () => {},
        selectedIcon = null,
        showColorPicker = false,
        defaultColor = '#e94560'
    } = options;
    
    let currentCategory = 'all';
    let currentSearch = '';
    let currentColor = defaultColor;
    
    // 创建容器
    const container = document.createElement('div');
    container.className = 'icon-selector';
    container.innerHTML = `
        <style>
            .icon-selector {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                backdrop-filter: blur(10px);
            }
            
            .icon-selector-header {
                margin-bottom: 20px;
            }
            
            .icon-search {
                width: 100%;
                padding: 12px;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #f1f1f1;
                font-size: 14px;
                margin-bottom: 15px;
            }
            
            .icon-search:focus {
                outline: none;
                border-color: #e94560;
                background: rgba(255, 255, 255, 0.1);
            }
            
            .icon-search::placeholder {
                color: rgba(241, 241, 241, 0.5);
            }
            
            .icon-categories {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            
            .category-btn {
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #f1f1f1;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .category-btn:hover {
                background: rgba(255, 255, 255, 0.12);
                transform: translateY(-1px);
            }
            
            .category-btn.active {
                background: #e94560;
                border-color: #e94560;
            }
            
            .icon-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
                gap: 10px;
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }
            
            .icon-grid::-webkit-scrollbar {
                width: 8px;
            }
            
            .icon-grid::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            
            .icon-grid::-webkit-scrollbar-thumb {
                background: rgba(233, 69, 96, 0.5);
                border-radius: 4px;
            }
            
            .icon-grid::-webkit-scrollbar-thumb:hover {
                background: rgba(233, 69, 96, 0.7);
            }
            
            .icon-item {
                aspect-ratio: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid transparent;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                padding: 8px;
            }
            
            .icon-item:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: scale(1.05);
            }
            
            .icon-item.selected {
                border-color: #e94560;
                background: rgba(233, 69, 96, 0.2);
            }
            
            .icon-char {
                font-size: 28px;
                margin-bottom: 4px;
            }
            
            .icon-name {
                font-size: 10px;
                color: rgba(241, 241, 241, 0.7);
                text-align: center;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                width: 100%;
            }
            
            .icon-empty {
                grid-column: 1 / -1;
                text-align: center;
                padding: 40px;
                color: rgba(241, 241, 241, 0.5);
            }
            
            .color-picker-section {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .color-picker-label {
                display: block;
                margin-bottom: 10px;
                color: #f1f1f1;
                font-size: 14px;
            }
            
            .color-picker-wrapper {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .color-input {
                flex: 1;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #f1f1f1;
                font-size: 14px;
            }
            
            .color-preview {
                width: 40px;
                height: 40px;
                border-radius: 6px;
                border: 2px solid rgba(255, 255, 255, 0.2);
                cursor: pointer;
            }
            
            .color-picker-native {
                opacity: 0;
                position: absolute;
                pointer-events: none;
            }
        </style>
        
        <div class="icon-selector-header">
            <input 
                type="text" 
                class="icon-search" 
                placeholder="搜索图标..."
            />
            
            <div class="icon-categories"></div>
        </div>
        
        <div class="icon-grid"></div>
        
        ${showColorPicker ? `
            <div class="color-picker-section">
                <label class="color-picker-label">图标颜色</label>
                <div class="color-picker-wrapper">
                    <input 
                        type="text" 
                        class="color-input" 
                        value="${defaultColor}"
                        placeholder="#e94560"
                    />
                    <div class="color-preview" style="background-color: ${defaultColor}"></div>
                    <input type="color" class="color-picker-native" value="${defaultColor}" />
                </div>
            </div>
        ` : ''}
    `;
    
    // 获取元素
    const searchInput = container.querySelector('.icon-search');
    const categoriesContainer = container.querySelector('.icon-categories');
    const iconGrid = container.querySelector('.icon-grid');
    
    // 渲染分类按钮
    function renderCategories() {
        categoriesContainer.innerHTML = ICON_CATEGORIES.map(cat => `
            <button 
                class="category-btn ${cat.id === currentCategory ? 'active' : ''}"
                data-category="${cat.id}"
            >
                ${cat.name}
            </button>
        `).join('');
        
        // 绑定分类按钮事件
        categoriesContainer.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentCategory = btn.dataset.category;
                renderCategories();
                renderIcons();
            });
        });
    }
    
    // 渲染图标网格
    function renderIcons() {
        let icons = getIconsByCategory(currentCategory);
        
        if (currentSearch) {
            icons = searchIcons(currentSearch);
        }
        
        if (icons.length === 0) {
            iconGrid.innerHTML = '<div class="icon-empty">未找到匹配的图标</div>';
            return;
        }
        
        iconGrid.innerHTML = icons.map(icon => `
            <div 
                class="icon-item ${selectedIcon === icon.id ? 'selected' : ''}"
                data-icon-id="${icon.id}"
                title="${icon.name}"
            >
                <div class="icon-char">${icon.char}</div>
                <div class="icon-name">${icon.name}</div>
            </div>
        `).join('');
        
        // 绑定图标点击事件
        iconGrid.querySelectorAll('.icon-item').forEach(item => {
            item.addEventListener('click', () => {
                const iconId = item.dataset.iconId;
                const icon = getIconById(iconId);
                
                // 更新选中状态
                iconGrid.querySelectorAll('.icon-item').forEach(i => 
                    i.classList.remove('selected')
                );
                item.classList.add('selected');
                
                // 触发回调
                onSelect({
                    icon: icon,
                    color: currentColor
                });
            });
        });
    }
    
    // 搜索事件
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        renderIcons();
    });
    
    // 颜色选择器事件
    if (showColorPicker) {
        const colorInput = container.querySelector('.color-input');
        const colorPreview = container.querySelector('.color-preview');
        const colorPickerNative = container.querySelector('.color-picker-native');
        
        colorInput.addEventListener('input', (e) => {
            const color = e.target.value;
            if (/^#[0-9A-F]{6}$/i.test(color)) {
                currentColor = color;
                colorPreview.style.backgroundColor = color;
                colorPickerNative.value = color;
            }
        });
        
        colorPreview.addEventListener('click', () => {
            colorPickerNative.click();
        });
        
        colorPickerNative.addEventListener('input', (e) => {
            currentColor = e.target.value;
            colorInput.value = currentColor;
            colorPreview.style.backgroundColor = currentColor;
        });
    }
    
    // 初始化渲染
    renderCategories();
    renderIcons();
    
    return container;
}

/**
 * 显示图标选择器对话框
 */
export function showIconSelectorDialog(options = {}) {
    return new Promise((resolve) => {
        // 创建遮罩层
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        `;
        
        // 创建对话框
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            max-width: 600px;
            width: 100%;
            max-height: 90vh;
            overflow: auto;
        `;
        
        // 创建图标选择器
        const selector = createIconSelector({
            ...options,
            onSelect: (result) => {
                document.body.removeChild(overlay);
                resolve(result);
            }
        });
        
        dialog.appendChild(selector);
        overlay.appendChild(dialog);
        
        // 点击遮罩关闭
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
                resolve(null);
            }
        });
        
        document.body.appendChild(overlay);
    });
}