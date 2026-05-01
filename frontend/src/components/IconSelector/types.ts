/**
 * Icon Selector Component Types
 * 图标选择器组件类型定义
 */

/**
 * 图标项接口
 */
export interface IconItem {
  /** 图标唯一标识 */
  id: string;
  /** 图标名称 */
  name: string;
  /** 图标SVG内容或路径 */
  content: string;
  /** 图标分类 */
  category: string;
  /** 图标标签（用于搜索） */
  tags?: string[];
  /** 图标关键词（用于搜索） */
  keywords?: string[];
}

/**
 * 图标分类接口
 */
export interface IconCategory {
  /** 分类ID */
  id: string;
  /** 分类名称 */
  name: string;
  /** 分类图标数量 */
  count: number;
}

/**
 * 图标选择器配置接口
 */
export interface IconSelectorConfig {
  /** 是否显示搜索框 */
  showSearch?: boolean;
  /** 是否显示分类筛选 */
  showCategories?: boolean;
  /** 是否显示颜色选择器 */
  showColorPicker?: boolean;
  /** 默认颜色 */
  defaultColor?: string;
  /** 每行显示图标数量 */
  iconsPerRow?: number;
  /** 图标大小 */
  iconSize?: number;
  /** 是否允许多选 */
  multiSelect?: boolean;
  /** 最大选择数量（多选模式） */
  maxSelection?: number;
  /** 是否显示图标名称 */
  showIconName?: boolean;
  /** 搜索防抖延迟（毫秒） */
  searchDebounce?: number;
}

/**
 * 图标选择器状态接口
 */
export interface IconSelectorState {
  /** 所有图标列表 */
  icons: IconItem[];
  /** 过滤后的图标列表 */
  filteredIcons: IconItem[];
  /** 所有分类列表 */
  categories: IconCategory[];
  /** 当前选中的分类ID */
  selectedCategory: string | null;
  /** 搜索关键词 */
  searchKeyword: string;
  /** 当前选中的图标ID（单选） */
  selectedIconId: string | null;
  /** 当前选中的图标ID列表（多选） */
  selectedIconIds: string[];
  /** 当前选中的颜色 */
  selectedColor: string;
  /** 是否正在加载 */
  loading: boolean;
  /** 错误信息 */
  error: string | null;
}

/**
 * 图标选择事件接口
 */
export interface IconSelectEvent {
  /** 选中的图标 */
  icon: IconItem;
  /** 选中的颜色 */
  color: string;
  /** 时间戳 */
  timestamp: number;
}

/**
 * 图标选择器回调函数类型
 */
export interface IconSelectorCallbacks {
  /** 图标选择回调 */
  onSelect?: (event: IconSelectEvent) => void;
  /** 图标取消选择回调 */
  onDeselect?: (iconId: string) => void;
  /** 颜色变化回调 */
  onColorChange?: (color: string) => void;
  /** 搜索回调 */
  onSearch?: (keyword: string) => void;
  /** 分类切换回调 */
  onCategoryChange?: (categoryId: string | null) => void;
  /** 错误回调 */
  onError?: (error: Error) => void;
}

/**
 * 图标选择器属性接口
 */
export interface IconSelectorProps {
  /** 图标列表 */
  icons?: IconItem[];
  /** 配置选项 */
  config?: IconSelectorConfig;
  /** 回调函数 */
  callbacks?: IconSelectorCallbacks;
  /** 初始选中的图标ID */
  initialSelectedIconId?: string;
  /** 初始选中的图标ID列表（多选） */
  initialSelectedIconIds?: string[];
  /** 初始颜色 */
  initialColor?: string;
  /** 自定义类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
}

/**
 * 图标搜索过滤器接口
 */
export interface IconSearchFilter {
  /** 搜索关键词 */
  keyword: string;
  /** 分类ID */
  categoryId?: string | null;
  /** 标签过滤 */
  tags?: string[];
}

/**
 * 图标渲染选项接口
 */
export interface IconRenderOptions {
  /** 图标颜色 */
  color?: string;
  /** 图标大小 */
  size?: number;
  /** 是否选中状态 */
  selected?: boolean;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 颜色选择器配置接口
 */
export interface ColorPickerConfig {
  /** 预设颜色列表 */
  presetColors?: string[];
  /** 是否显示透明度选择 */
  showAlpha?: boolean;
  /** 是否显示颜色输入框 */
  showInput?: boolean;
  /** 颜色格式 */
  format?: 'hex' | 'rgb' | 'hsl';
}

/**
 * 图标加载器接口
 */
export interface IconLoader {
  /** 加载图标数据 */
  load: () => Promise<IconItem[]>;
  /** 加载分类数据 */
  loadCategories?: () => Promise<IconCategory[]>;
}

/**
 * 图标搜索结果接口
 */
export interface IconSearchResult {
  /** 匹配的图标列表 */
  icons: IconItem[];
  /** 总数量 */
  total: number;
  /** 搜索关键词 */
  keyword: string;
  /** 搜索耗时（毫秒） */
  duration?: number;
}

/**
 * 图标预览配置接口
 */
export interface IconPreviewConfig {
  /** 是否显示预览 */
  enabled?: boolean;
  /** 预览大小 */
  size?: number;
  /** 预览位置 */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /** 是否显示图标信息 */
  showInfo?: boolean;
}

/**
 * 图标选择器主题接口
 */
export interface IconSelectorTheme {
  /** 主色调 */
  primary?: string;
  /** 次要色调 */
  secondary?: string;
  /** 强调色 */
  accent?: string;
  /** 高亮色 */
  highlight?: string;
  /** 文本颜色 */
  text?: string;
  /** 背景颜色 */
  background?: string;
  /** 边框颜色 */
  border?: string;
  /** 悬停背景色 */
  hoverBackground?: string;
  /** 选中背景色 */
  selectedBackground?: string;
}

/**
 * 默认配置常量
 */
export const DEFAULT_ICON_SELECTOR_CONFIG: Required<IconSelectorConfig> = {
  showSearch: true,
  showCategories: true,
  showColorPicker: true,
  defaultColor: '#e94560',
  iconsPerRow: 6,
  iconSize: 32,
  multiSelect: false,
  maxSelection: 1,
  showIconName: true,
  searchDebounce: 300,
};

/**
 * 默认颜色选择器配置
 */
export const DEFAULT_COLOR_PICKER_CONFIG: Required<ColorPickerConfig> = {
  presetColors: [
    '#e94560',
    '#1a1a2e',
    '#16213e',
    '#0f3460',
    '#f1f1f1',
    '#2ecc71',
    '#3498db',
    '#e74c3c',
    '#f39c12',
    '#9b59b6',
  ],
  showAlpha: false,
  showInput: true,
  format: 'hex',
};

/**
 * 默认主题配置
 */
export const DEFAULT_ICON_SELECTOR_THEME: Required<IconSelectorTheme> = {
  primary: '#1a1a2e',
  secondary: '#16213e',
  accent: '#0f3460',
  highlight: '#e94560',
  text: '#f1f1f1',
  background: 'rgba(255, 255, 255, 0.05)',
  border: 'rgba(255, 255, 255, 0.1)',
  hoverBackground: 'rgba(255, 255, 255, 0.08)',
  selectedBackground: 'rgba(233, 69, 96, 0.2)',
};