/**
 * Icon Selector Constants
 * 图标选择器常量配置
 */

// 可用的图标列表（使用 Unicode 字符和 Emoji）
export const AVAILABLE_ICONS = [
  // 常用图标
  { id: 'home', icon: '🏠', name: '首页', category: 'common' },
  { id: 'star', icon: '⭐', name: '星标', category: 'common' },
  { id: 'heart', icon: '❤️', name: '喜欢', category: 'common' },
  { id: 'bookmark', icon: '🔖', name: '书签', category: 'common' },
  { id: 'flag', icon: '🚩', name: '旗帜', category: 'common' },
  { id: 'pin', icon: '📌', name: '图钉', category: 'common' },
  { id: 'bell', icon: '🔔', name: '通知', category: 'common' },
  { id: 'search', icon: '🔍', name: '搜索', category: 'common' },
  { id: 'settings', icon: '⚙️', name: '设置', category: 'common' },
  { id: 'user', icon: '👤', name: '用户', category: 'common' },
  
  // 文件和文档
  { id: 'folder', icon: '📁', name: '文件夹', category: 'files' },
  { id: 'file', icon: '📄', name: '文件', category: 'files' },
  { id: 'document', icon: '📃', name: '文档', category: 'files' },
  { id: 'note', icon: '📝', name: '笔记', category: 'files' },
  { id: 'book', icon: '📚', name: '书籍', category: 'files' },
  { id: 'clipboard', icon: '📋', name: '剪贴板', category: 'files' },
  { id: 'calendar', icon: '📅', name: '日历', category: 'files' },
  { id: 'chart', icon: '📊', name: '图表', category: 'files' },
  
  // 通讯和社交
  { id: 'mail', icon: '✉️', name: '邮件', category: 'communication' },
  { id: 'message', icon: '💬', name: '消息', category: 'communication' },
  { id: 'phone', icon: '📞', name: '电话', category: 'communication' },
  { id: 'chat', icon: '💭', name: '聊天', category: 'communication' },
  { id: 'comment', icon: '💬', name: '评论', category: 'communication' },
  { id: 'megaphone', icon: '📣', name: '广播', category: 'communication' },
  
  // 媒体
  { id: 'image', icon: '🖼️', name: '图片', category: 'media' },
  { id: 'camera', icon: '📷', name: '相机', category: 'media' },
  { id: 'video', icon: '🎥', name: '视频', category: 'media' },
  { id: 'music', icon: '🎵', name: '音乐', category: 'media' },
  { id: 'microphone', icon: '🎤', name: '麦克风', category: 'media' },
  { id: 'headphone', icon: '🎧', name: '耳机', category: 'media' },
  
  // 工具
  { id: 'tool', icon: '🔧', name: '工具', category: 'tools' },
  { id: 'wrench', icon: '🔨', name: '扳手', category: 'tools' },
  { id: 'scissors', icon: '✂️', name: '剪刀', category: 'tools' },
  { id: 'lock', icon: '🔒', name: '锁定', category: 'tools' },
  { id: 'unlock', icon: '🔓', name: '解锁', category: 'tools' },
  { id: 'key', icon: '🔑', name: '钥匙', category: 'tools' },
  { id: 'link', icon: '🔗', name: '链接', category: 'tools' },
  { id: 'trash', icon: '🗑️', name: '删除', category: 'tools' },
  
  // 箭头和方向
  { id: 'arrow-up', icon: '⬆️', name: '向上', category: 'arrows' },
  { id: 'arrow-down', icon: '⬇️', name: '向下', category: 'arrows' },
  { id: 'arrow-left', icon: '⬅️', name: '向左', category: 'arrows' },
  { id: 'arrow-right', icon: '➡️', name: '向右', category: 'arrows' },
  { id: 'refresh', icon: '🔄', name: '刷新', category: 'arrows' },
  { id: 'sync', icon: '🔃', name: '同步', category: 'arrows' },
  
  // 状态和标记
  { id: 'check', icon: '✅', name: '完成', category: 'status' },
  { id: 'cross', icon: '❌', name: '错误', category: 'status' },
  { id: 'warning', icon: '⚠️', name: '警告', category: 'status' },
  { id: 'info', icon: 'ℹ️', name: '信息', category: 'status' },
  { id: 'question', icon: '❓', name: '问题', category: 'status' },
  { id: 'exclamation', icon: '❗', name: '感叹', category: 'status' },
  { id: 'plus', icon: '➕', name: '添加', category: 'status' },
  { id: 'minus', icon: '➖', name: '减少', category: 'status' },
  
  // 天气和自然
  { id: 'sun', icon: '☀️', name: '太阳', category: 'nature' },
  { id: 'moon', icon: '🌙', name: '月亮', category: 'nature' },
  { id: 'cloud', icon: '☁️', name: '云', category: 'nature' },
  { id: 'rain', icon: '🌧️', name: '雨', category: 'nature' },
  { id: 'snow', icon: '❄️', name: '雪', category: 'nature' },
  { id: 'fire', icon: '🔥', name: '火', category: 'nature' },
  { id: 'water', icon: '💧', name: '水', category: 'nature' },
  { id: 'tree', icon: '🌲', name: '树', category: 'nature' },
  { id: 'flower', icon: '🌸', name: '花', category: 'nature' },
  
  // 交通
  { id: 'car', icon: '🚗', name: '汽车', category: 'transport' },
  { id: 'plane', icon: '✈️', name: '飞机', category: 'transport' },
  { id: 'train', icon: '🚆', name: '火车', category: 'transport' },
  { id: 'bike', icon: '🚲', name: '自行车', category: 'transport' },
  { id: 'rocket', icon: '🚀', name: '火箭', category: 'transport' },
  
  // 食物
  { id: 'coffee', icon: '☕', name: '咖啡', category: 'food' },
  { id: 'pizza', icon: '🍕', name: '披萨', category: 'food' },
  { id: 'burger', icon: '🍔', name: '汉堡', category: 'food' },
  { id: 'cake', icon: '🎂', name: '蛋糕', category: 'food' },
  { id: 'apple', icon: '🍎', name: '苹果', category: 'food' },
  
  // 运动和娱乐
  { id: 'ball', icon: '⚽', name: '足球', category: 'sports' },
  { id: 'basketball', icon: '🏀', name: '篮球', category: 'sports' },
  { id: 'trophy', icon: '🏆', name: '奖杯', category: 'sports' },
  { id: 'medal', icon: '🏅', name: '奖牌', category: 'sports' },
  { id: 'game', icon: '🎮', name: '游戏', category: 'sports' },
  { id: 'dice', icon: '🎲', name: '骰子', category: 'sports' },
  
  // 办公
  { id: 'briefcase', icon: '💼', name: '公文包', category: 'office' },
  { id: 'laptop', icon: '💻', name: '笔记本', category: 'office' },
  { id: 'desktop', icon: '🖥️', name: '台式机', category: 'office' },
  { id: 'printer', icon: '🖨️', name: '打印机', category: 'office' },
  { id: 'keyboard', icon: '⌨️', name: '键盘', category: 'office' },
  { id: 'mouse', icon: '🖱️', name: '鼠标', category: 'office' },
  
  // 其他
  { id: 'gift', icon: '🎁', name: '礼物', category: 'other' },
  { id: 'bulb', icon: '💡', name: '灯泡', category: 'other' },
  { id: 'battery', icon: '🔋', name: '电池', category: 'other' },
  { id: 'magnet', icon: '🧲', name: '磁铁', category: 'other' },
  { id: 'crown', icon: '👑', name: '皇冠', category: 'other' },
  { id: 'diamond', icon: '💎', name: '钻石', category: 'other' },
];

// 图标分类
export const ICON_CATEGORIES = [
  { id: 'all', name: '全部', icon: '📦' },
  { id: 'common', name: '常用', icon: '⭐' },
  { id: 'files', name: '文件', icon: '📁' },
  { id: 'communication', name: '通讯', icon: '💬' },
  { id: 'media', name: '媒体', icon: '🎵' },
  { id: 'tools', name: '工具', icon: '🔧' },
  { id: 'arrows', name: '箭头', icon: '➡️' },
  { id: 'status', name: '状态', icon: '✅' },
  { id: 'nature', name: '自然', icon: '🌲' },
  { id: 'transport', name: '交通', icon: '🚗' },
  { id: 'food', name: '食物', icon: '🍕' },
  { id: 'sports', name: '运动', icon: '⚽' },
  { id: 'office', name: '办公', icon: '💼' },
  { id: 'other', name: '其他', icon: '🎁' },
];

// 预设颜色方案
export const PRESET_COLORS = [
  '#e94560', // 主题红色
  '#0f3460', // 主题蓝色
  '#1a1a2e', // 主题深色
  '#2ecc71', // 绿色
  '#3498db', // 蓝色
  '#9b59b6', // 紫色
  '#f39c12', // 橙色
  '#e74c3c', // 红色
  '#1abc9c', // 青色
  '#34495e', // 灰蓝色
  '#95a5a6', // 灰色
  '#ecf0f1', // 浅灰色
  '#ff6b6b', // 粉红色
  '#4ecdc4', // 青绿色
  '#ffe66d', // 黄色
  '#a8e6cf', // 薄荷绿
];

// 默认图标配置
export const DEFAULT_ICON_CONFIG = {
  icon: '⭐',
  color: '#e94560',
  size: 24,
};

// 图标大小选项
export const ICON_SIZE_OPTIONS = [
  { value: 16, label: '小' },
  { value: 24, label: '中' },
  { value: 32, label: '大' },
  { value: 48, label: '特大' },
];

// 搜索配置
export const SEARCH_CONFIG = {
  placeholder: '搜索图标...',
  debounceDelay: 300,
  minSearchLength: 1,
};

// 显示配置
export const DISPLAY_CONFIG = {
  iconsPerRow: 8,
  iconGap: 8,
  categoryPadding: 16,
  maxHeight: 400,
};

// 动画配置
export const ANIMATION_CONFIG = {
  transitionDuration: 200,
  hoverScale: 1.1,
  activeScale: 0.95,
};
