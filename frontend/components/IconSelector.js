/**
 * IconSelector Component
 * 图标选择器组件 - 支持图标预览、搜索、选择和颜色定制
 */

class IconSelector {
    constructor(options = {}) {
        this.options = {
            container: options.container || document.body,
            onSelect: options.onSelect || (() => {}),
            defaultColor: options.defaultColor || '#e94560',
            defaultIcon: options.defaultIcon || 'star',
            ...options
        };

        this.selectedIcon = this.options.defaultIcon;
        this.selectedColor = this.options.defaultColor;
        this.searchQuery = '';
        
        // 可用图标列表（使用 Unicode 字符和 Emoji）
        this.icons = [
            { name: 'star', symbol: '⭐', category: 'common' },
            { name: 'heart', symbol: '❤️', category: 'common' },
            { name: 'fire', symbol: '🔥', category: 'common' },
            { name: 'thumbs-up', symbol: '👍', category: 'common' },
            { name: 'check', symbol: '✓', category: 'common' },
            { name: 'cross', symbol: '✗', category: 'common' },
            { name: 'plus', symbol: '➕', category: 'common' },
            { name: 'minus', symbol: '➖', category: 'common' },
            { name: 'home', symbol: '🏠', category: 'places' },
            { name: 'building', symbol: '🏢', category: 'places' },
            { name: 'school', symbol: '🏫', category: 'places' },
            { name: 'hospital', symbol: '🏥', category: 'places' },
            { name: 'shop', symbol: '🏪', category: 'places' },
            { name: 'rocket', symbol: '🚀', category: 'objects' },
            { name: 'trophy', symbol: '🏆', category: 'objects' },
            { name: 'gift', symbol: '🎁', category: 'objects' },
            { name: 'bell', symbol: '🔔', category: 'objects' },
            { name: 'light', symbol: '💡', category: 'objects' },
            { name: 'book', symbol: '📚', category: 'objects' },
            { name: 'calendar', symbol: '📅', category: 'objects' },
            { name: 'clock', symbol: '⏰', category: 'objects' },
            { name: 'phone', symbol: '📱', category: 'objects' },
            { name: 'email', symbol: '📧', category: 'objects' },
            { name: 'camera', symbol: '📷', category: 'objects' },
            { name: 'music', symbol: '🎵', category: 'objects' },
            { name: 'game', symbol: '🎮', category: 'objects' },
            { name: 'paint', symbol: '🎨', category: 'objects' },
            { name: 'flag', symbol: '🚩', category: 'objects' },
            { name: 'key', symbol: '🔑', category: 'objects' },
            { name: 'lock', symbol: '🔒', category: 'objects' },
            { name: 'unlock', symbol: '🔓', category: 'objects' },
            { name: 'search', symbol: '🔍', category: 'objects' },
            { name: 'settings', symbol: '⚙️', category: 'objects' },
            { name: 'warning', symbol: '⚠️', category: 'symbols' },
            { name: 'info', symbol: 'ℹ️', category: 'symbols' },
            { name: 'question', symbol: '❓', category: 'symbols' },
            { name: 'exclamation', symbol: '❗', category: 'symbols' },
            { name: 'circle', symbol: '⭕', category: 'symbols' },
            { name: 'square', symbol: '⬛', category: 'symbols' },
            { name: 'diamond', symbol: '💎', category: 'symbols' },
            { name: 'crown', symbol: '👑', category: 'symbols' },
            { name: 'smile', symbol: '😊', category: 'emoji' },
            { name: 'laugh', symbol: '😂', category: 'emoji' },
            { name: 'cool', symbol: '😎', category: 'emoji' },
            { name: 'love', symbol: '😍', category: 'emoji' },
            { name: 'think', symbol: '🤔', category: 'emoji' },
            { name: 'celebrate', symbol: '🎉', category: 'emoji' },
            { name: 'clap', symbol: '👏', category: 'emoji' },
            { name: 'wave', symbol: '👋', category: 'emoji' }
        ];

        this.categories = [
            { id: 'all', name: '全部' },
            { id: 'common', name: '常用' },
            { id: 'places', name: '地点' },
            { id: 'objects', name: '物品' },
            { id: 'symbols', name: '符号' },
            { id: 'emoji', name: '表情' }
        ];

        this.currentCategory = 'all';
        this.isOpen = false;
        
        this.init();
    }

    init() {
        this.createStyles();
        this.createModal();
        this.attachEventListeners();
    }

    createStyles() {
        if (document.getElementById('icon-selector-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'icon-selector-styles';
        styles.textContent = `
            .icon-selector-overlay {
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
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
            }

            .icon-selector-overlay.active {
                opacity: 1;
                visibility: visible;
            }

            .icon-selector-modal {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 12px;
                padding: 30px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                transform: scale(0.9);
                transition: transform 0.3s ease;
                display: flex;
                flex-direction: column;
            }

            .icon-selector-overlay.active .icon-selector-modal {
                transform: scale(1);
            }

            .icon-selector-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .icon-selector-title {
                font-size: 1.5em;
                color: #e94560;
                font-weight: 600;
            }

            .icon-selector-close {
                background: transparent;
                border: none;
                color: #f1f1f1;
                font-size: 1.5em;
                cursor: pointer;
                padding: 5px 10px;
                border-radius: 6px;
                transition: all 0.3s ease;
            }

            .icon-selector-close:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: rotate(90deg);
            }

            .icon-selector-search {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
                color: #f1f1f1;
                font-size: 1em;
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }

            .icon-selector-search:focus {
                outline: none;
                border-color: #e94560;
                background: rgba(255, 255, 255, 0.08);
            }

            .icon-selector-search::placeholder {
                color: rgba(241, 241, 241, 0.5);
            }

            .icon-selector-categories {
                display: flex;
                gap: 8px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .icon-category-btn {
                padding: 8px 16px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.05);
                color: #f1f1f1;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9em;
                font-weight: 500;
            }

            .icon-category-btn:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }

            .icon-category-btn.active {
                background: #e94560;
                border-color: #e94560;
                color: white;
            }

            .icon-selector-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
                gap: 10px;
                overflow-y: auto;
                max-height: 300px;
                padding: 10px;
                margin-bottom: 20px;
            }

            .icon-selector-grid::-webkit-scrollbar {
                width: 8px;
            }

            .icon-selector-grid::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }

            .icon-selector-grid::-webkit-scrollbar-thumb {
                background: rgba(233, 69, 96, 0.5);
                border-radius: 4px;
            }

            .icon-selector-grid::-webkit-scrollbar-thumb:hover {
                background: #e94560;
            }

            .icon-item {
                aspect-ratio: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 2em;
            }

            .icon-item:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: scale(1.1);
            }

            .icon-item.selected {
                background: rgba(233, 69, 96, 0.2);
                border-color: #e94560;
                box-shadow: 0 0 15px rgba(233, 69, 96, 0.5);
            }

            .icon-selector-footer {
                display: flex;
                gap: 15px;
                align-items: center;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .icon-color-picker-wrapper {
                flex: 1;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .icon-color-label {
                color: #f1f1f1;
                font-size: 0.9em;
                white-space: nowrap;
            }

            .icon-color-input {
                width: 50px;
                height: 40px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                cursor: pointer;
                background: transparent;
            }

            .icon-color-input::-webkit-color-swatch-wrapper {
                padding: 0;
            }

            .icon-color-input::-webkit-color-swatch {
                border: none;
                border-radius: 4px;
            }

            .icon-color-value {
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                color: #f1f1f1;
                font-family: monospace;
                font-size: 0.9em;
            }

            .icon-selector-actions {
                display: flex;
                gap: 10px;
            }

            .icon-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 1em;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
            }

            .icon-btn-primary {
                background: #e94560;
                color: white;
            }

            .icon-btn-primary:hover {
                background: #d63651;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
            }

            .icon-btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                color: #f1f1f1;
            }

            .icon-btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }

            .icon-selector-empty {
                text-align: center;
                padding: 40px 20px;
                color: rgba(241, 241, 241, 0.5);
                font-size: 1.1em;
            }

            @media (max-width: 768px) {
                .icon-selector-modal {
                    width: 95%;
                    padding: 20px;
                }

                .icon-selector-grid {
                    grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
                    gap: 8px;
                }

                .icon-item {
                    font-size: 1.5em;
                }

                .icon-selector-footer {
                    flex-direction: column;
                }

                .icon-color-picker-wrapper {
                    width: 100%;
                }

                .icon-selector-actions {
                    width: 100%;
                }

                .icon-btn {
                    flex: 1;
                }
            }
        `;

        document.head.appendChild(styles);
    }

    createModal() {
        const overlay = document.createElement('div');
        overlay.className = 'icon-selector-overlay';
        overlay.innerHTML = `
            <div class="icon-selector-modal">
                <div class="icon-selector-header">
                    <h2 class="icon-selector-title">选择图标</h2>
                    <button class="icon-selector-close" aria-label="关闭">×</button>
                </div>
                
                <input 
                    type="text" 
                    class="icon-selector-search" 
                    placeholder="搜索图标..."
                    aria-label="搜索图标"
                >
                
                <div class="icon-selector-categories"></div>
                
                <div class="icon-selector-grid"></div>
                
                <div class="icon-selector-footer">
                    <div class="icon-color-picker-wrapper">
                        <span class="icon-color-label">颜色:</span>
                        <input 
                            type="color" 
                            class="icon-color-input" 
                            value="${this.selectedColor}"
                            aria-label="选择颜色"
                        >
                        <span class="icon-color-value">${this.selectedColor}</span>
                    </div>
                    <div class="icon-selector-actions">
                        <button class="icon-btn icon-btn-secondary icon-cancel-btn">取消</button>
                        <button class="icon-btn icon-btn-primary icon-confirm-btn">确认</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        this.overlay = overlay;
        this.modal = overlay.querySelector('.icon-selector-modal');
    }

    attachEventListeners() {
        // 关闭按钮
        this.overlay.querySelector('.icon-selector-close').addEventListener('click', () => {
            this.close();
        });

        // 点击遮罩关闭
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        // 搜索
        this.overlay.querySelector('.icon-selector-search').addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.renderIcons();
        });

        // 颜色选择器
        const colorInput = this.overlay.querySelector('.icon-color-input');
        const colorValue = this.overlay.querySelector('.icon-color-value');
        
        colorInput.addEventListener('input', (e) => {
            this.selectedColor = e.target.value;
            colorValue.textContent = this.selectedColor;
            this.updateIconColors();
        });

        // 取消按钮
        this.overlay.querySelector('.icon-cancel-btn').addEventListener('click', () => {
            this.close();
        });

        // 确认按钮
        this.overlay.querySelector('.icon-confirm-btn').addEventListener('click', () => {
            this.confirm();
        });

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (this.isOpen && e.key === 'Escape') {
                this.close();
            }
        });

        // 渲染分类
        this.renderCategories();
    }

    renderCategories() {
        const container = this.overlay.querySelector('.icon-selector-categories');
        container.innerHTML = this.categories.map(cat => `
            <button 
                class="icon-category-btn ${cat.id === this.currentCategory ? 'active' : ''}" 
                data-category="${cat.id}"
            >
                ${cat.name}
            </button>
        `).join('');

        container.querySelectorAll('.icon-category-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentCategory = btn.dataset.category;
                this.renderCategories();
                this.renderIcons();
            });
        });
    }

    renderIcons() {
        const grid = this.overlay.querySelector('.icon-selector-grid');
        
        let filteredIcons = this.icons;

        // 按分类过滤
        if (this.currentCategory !== 'all') {
            filteredIcons = filteredIcons.filter(icon => icon.category === this.currentCategory);
        }

        // 按搜索词过滤
        if (this.searchQuery) {
            filteredIcons = filteredIcons.filter(icon => 
                icon.name.toLowerCase().includes(this.searchQuery)
            );
        }

        if (filteredIcons.length === 0) {
            grid.innerHTML = '<div class="icon-selector-empty">未找到匹配的图标</div>';
            return;
        }

        grid.innerHTML = filteredIcons.map(icon => `
            <div 
                class="icon-item ${icon.name === this.selectedIcon ? 'selected' : ''}" 
                data-icon="${icon.name}"
                title="${icon.name}"
                style="color: ${this.selectedColor}"
            >
                ${icon.symbol}
            </div>
        `).join('');

        grid.querySelectorAll('.icon-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectedIcon = item.dataset.icon;
                this.renderIcons();
            });
        });
    }

    updateIconColors() {
        this.overlay.querySelectorAll('.icon-item').forEach(item => {
            item.style.color = this.selectedColor;
        });
    }

    open() {
        this.isOpen = true;
        this.overlay.classList.add('active');
        this.renderIcons();
        
        // 聚焦搜索框
        setTimeout(() => {
            this.overlay.querySelector('.icon-selector-search').focus();
        }, 100);
    }

    close() {
        this.isOpen = false;
        this.overlay.classList.remove('active');
        this.searchQuery = '';
        this.overlay.querySelector('.icon-selector-search').value = '';
    }

    confirm() {
        const selectedIconData = this.icons.find(icon => icon.name === this.selectedIcon);
        
        if (selectedIconData) {
            this.options.onSelect({
                name: this.selectedIcon,
                symbol: selectedIconData.symbol,
                color: this.selectedColor
            });
        }
        
        this.close();
    }

    // 公共方法：设置默认值
    setDefaults(icon, color) {
        if (icon) this.selectedIcon = icon;
        if (color) {
            this.selectedColor = color;
            const colorInput = this.overlay.querySelector('.icon-color-input');
            const colorValue = this.overlay.querySelector('.icon-color-value');
            if (colorInput) colorInput.value = color;
            if (colorValue) colorValue.textContent = color;
        }
    }

    // 公共方法：获取当前选择
    getSelection() {
        const selectedIconData = this.icons.find(icon => icon.name === this.selectedIcon);
        return {
            name: this.selectedIcon,
            symbol: selectedIconData ? selectedIconData.symbol : '',
            color: this.selectedColor
        };
    }

    // 销毁组件
    destroy() {
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
        
        const styles = document.getElementById('icon-selector-styles');
        if (styles && styles.parentNode) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// 导出为全局变量（用于浏览器环境）
if (typeof window !== 'undefined') {
    window.IconSelector = IconSelector;
}

// 导出为模块（用于模块化环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IconSelector;
}