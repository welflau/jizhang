// frontend/src/components/IconSelector/utils.ts

/**
 * Icon Selector Utilities
 * 图标选择器工具函数
 */

// 图标类别定义
export interface IconCategory {
  id: string;
  name: string;
  icons: string[];
}

// 图标数据类型
export interface IconData {
  name: string;
  category: string;
  keywords: string[];
  unicode?: string;
}

// 搜索选项
export interface SearchOptions {
  query: string;
  category?: string;
  caseSensitive?: boolean;
}

/**
 * 常用图标集合
 */
export const COMMON_ICONS: IconCategory[] = [
  {
    id: 'basic',
    name: '基础图标',
    icons: [
      '⭐', '❤️', '👍', '✓', '✕', '⚡', '🔥', '💡',
      '📌', '🔔', '⚙️', '🏠', '📁', '📄', '🔍', '➕'
    ]
  },
  {
    id: 'arrows',
    name: '箭头',
    icons: [
      '→', '←', '↑', '↓', '↗', '↘', '↙', '↖',
      '⇒', '⇐', '⇑', '⇓', '↔', '↕', '⟲', '⟳'
    ]
  },
  {
    id: 'shapes',
    name: '形状',
    icons: [
      '●', '○', '■', '□', '▲', '△', '▼', '▽',
      '◆', '◇', '★', '☆', '♦', '♥', '♠', '♣'
    ]
  },
  {
    id: 'symbols',
    name: '符号',
    icons: [
      '©', '®', '™', '§', '¶', '†', '‡', '•',
      '‣', '⁂', '※', '⁕', '⁜', '⁎', '⁑', '⁕'
    ]
  },
  {
    id: 'weather',
    name: '天气',
    icons: [
      '☀️', '🌙', '⭐', '☁️', '⛅', '🌧️', '⛈️', '🌩️',
      '❄️', '🌨️', '🌪️', '🌈', '⚡', '💧', '🌊', '🔥'
    ]
  },
  {
    id: 'emoji',
    name: '表情',
    icons: [
      '😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊',
      '😇', '🙂', '😉', '😌', '😍', '🥰', '😘', '😗'
    ]
  }
];

/**
 * 图标搜索关键词映射
 */
const ICON_KEYWORDS: Record<string, string[]> = {
  '⭐': ['star', 'favorite', 'bookmark', '星星', '收藏', '书签'],
  '❤️': ['heart', 'love', 'like', '心', '爱', '喜欢'],
  '👍': ['thumbs up', 'like', 'good', '赞', '好'],
  '✓': ['check', 'correct', 'yes', '对', '正确', '是'],
  '✕': ['cross', 'wrong', 'no', 'close', '错', '关闭'],
  '⚡': ['lightning', 'fast', 'power', '闪电', '快速', '电'],
  '🔥': ['fire', 'hot', 'trending', '火', '热门'],
  '💡': ['bulb', 'idea', 'light', '灯泡', '想法', '灯'],
  '📌': ['pin', 'mark', 'important', '图钉', '标记', '重要'],
  '🔔': ['bell', 'notification', 'alert', '铃铛', '通知', '提醒'],
  '⚙️': ['settings', 'config', 'gear', '设置', '配置', '齿轮'],
  '🏠': ['home', 'house', '家', '首页'],
  '📁': ['folder', 'directory', '文件夹', '目录'],
  '📄': ['document', 'file', 'page', '文档', '文件', '页面'],
  '🔍': ['search', 'find', 'magnifier', '搜索', '查找', '放大镜'],
  '➕': ['plus', 'add', 'new', '加', '添加', '新建']
};

/**
 * 搜索图标
 * @param options 搜索选项
 * @returns 匹配的图标列表
 */
export function searchIcons(options: SearchOptions): string[] {
  const { query, category, caseSensitive = false } = options;
  
  if (!query.trim()) {
    // 如果没有搜索词，返回指定类别的所有图标
    if (category) {
      const cat = COMMON_ICONS.find(c => c.id === category);
      return cat ? cat.icons : [];
    }
    return getAllIcons();
  }

  const searchQuery = caseSensitive ? query : query.toLowerCase();
  const results: string[] = [];

  // 确定搜索范围
  const categories = category 
    ? COMMON_ICONS.filter(c => c.id === category)
    : COMMON_ICONS;

  categories.forEach(cat => {
    cat.icons.forEach(icon => {
      if (matchesSearch(icon, searchQuery, caseSensitive)) {
        results.push(icon);
      }
    });
  });

  return results;
}

/**
 * 检查图标是否匹配搜索条件
 */
function matchesSearch(icon: string, query: string, caseSensitive: boolean): boolean {
  // 检查图标本身
  if (icon.includes(query)) {
    return true;
  }

  // 检查关键词
  const keywords = ICON_KEYWORDS[icon] || [];
  return keywords.some(keyword => {
    const kw = caseSensitive ? keyword : keyword.toLowerCase();
    return kw.includes(query);
  });
}

/**
 * 获取所有图标
 */
export function getAllIcons(): string[] {
  return COMMON_ICONS.flatMap(category => category.icons);
}

/**
 * 根据类别获取图标
 */
export function getIconsByCategory(categoryId: string): string[] {
  const category = COMMON_ICONS.find(c => c.id === categoryId);
  return category ? category.icons : [];
}

/**
 * 获取图标的关键词
 */
export function getIconKeywords(icon: string): string[] {
  return ICON_KEYWORDS[icon] || [];
}

/**
 * 验证图标是否存在
 */
export function isValidIcon(icon: string): boolean {
  return getAllIcons().includes(icon);
}

/**
 * 获取图标的 Unicode 编码
 */
export function getIconUnicode(icon: string): string {
  return Array.from(icon)
    .map(char => char.codePointAt(0)?.toString(16).toUpperCase().padStart(4, '0'))
    .join(' ');
}

/**
 * 从 Unicode 创建图标
 */
export function createIconFromUnicode(unicode: string): string {
  const codes = unicode.split(' ').map(code => parseInt(code, 16));
  return String.fromCodePoint(...codes);
}

/**
 * 过滤重复图标
 */
export function uniqueIcons(icons: string[]): string[] {
  return Array.from(new Set(icons));
}

/**
 * 按使用频率排序图标
 */
export function sortIconsByFrequency(icons: string[], usageMap: Record<string, number>): string[] {
  return [...icons].sort((a, b) => {
    const freqA = usageMap[a] || 0;
    const freqB = usageMap[b] || 0;
    return freqB - freqA;
  });
}

/**
 * 获取最近使用的图标
 */
export function getRecentIcons(maxCount: number = 16): string[] {
  try {
    const recent = localStorage.getItem('recentIcons');
    if (recent) {
      const icons = JSON.parse(recent) as string[];
      return icons.slice(0, maxCount);
    }
  } catch (error) {
    console.error('Failed to load recent icons:', error);
  }
  return [];
}

/**
 * 保存最近使用的图标
 */
export function saveRecentIcon(icon: string, maxCount: number = 16): void {
  try {
    const recent = getRecentIcons(maxCount);
    const filtered = recent.filter(i => i !== icon);
    const updated = [icon, ...filtered].slice(0, maxCount);
    localStorage.setItem('recentIcons', JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to save recent icon:', error);
  }
}

/**
 * 清除最近使用的图标
 */
export function clearRecentIcons(): void {
  try {
    localStorage.removeItem('recentIcons');
  } catch (error) {
    console.error('Failed to clear recent icons:', error);
  }
}

/**
 * 获取图标使用统计
 */
export function getIconUsageStats(): Record<string, number> {
  try {
    const stats = localStorage.getItem('iconUsageStats');
    if (stats) {
      return JSON.parse(stats);
    }
  } catch (error) {
    console.error('Failed to load icon usage stats:', error);
  }
  return {};
}

/**
 * 更新图标使用统计
 */
export function updateIconUsageStats(icon: string): void {
  try {
    const stats = getIconUsageStats();
    stats[icon] = (stats[icon] || 0) + 1;
    localStorage.setItem('iconUsageStats', JSON.stringify(stats));
  } catch (error) {
    console.error('Failed to update icon usage stats:', error);
  }
}

/**
 * 获取推荐图标
 */
export function getRecommendedIcons(count: number = 12): string[] {
  const stats = getIconUsageStats();
  const allIcons = getAllIcons();
  const sorted = sortIconsByFrequency(allIcons, stats);
  return sorted.slice(0, count);
}

/**
 * 复制图标到剪贴板
 */
export async function copyIconToClipboard(icon: string): Promise<boolean> {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(icon);
      return true;
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = icon;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    }
  } catch (error) {
    console.error('Failed to copy icon:', error);
    return false;
  }
}

/**
 * 导出图标配置
 */
export function exportIconConfig(): string {
  const config = {
    categories: COMMON_ICONS,
    recent: getRecentIcons(),
    stats: getIconUsageStats(),
    timestamp: new Date().toISOString()
  };
  return JSON.stringify(config, null, 2);
}

/**
 * 格式化图标显示大小
 */
export function getIconSizeClass(size: 'small' | 'medium' | 'large' | 'xlarge'): string {
  const sizeMap = {
    small: '1.2em',
    medium: '1.8em',
    large: '2.4em',
    xlarge: '3.2em'
  };
  return sizeMap[size] || sizeMap.medium;
}