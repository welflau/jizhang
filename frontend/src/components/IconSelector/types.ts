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
  /** 图标SVG内容或类名 */
  content: string;
  /** 图标分类 */
  category: string;
  /** 图标标签（用于搜索） */
  tags: string[];
  /** 图标类型 */
  type: 'svg' | 'font' | 'image';
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
 * 颜色选项接口
 */
export interface ColorOption {
  /** 颜色值（HEX格式） */
  value: string;
  /** 颜色名称 */
  label: string;
  /** 是否为自定义颜色 */
  isCustom?: boolean;
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
  /** 是否支持多选 */
  multiSelect?: boolean;
  /** 每页显示数量 */
  pageSize?: number;
  /** 默认选中的图标ID */
  defaultSelectedId?: string;
  /** 默认颜色 */
  defaultColor?: string;
  /** 预设颜色列表 */
  presetColors?: ColorOption[];
  /** 图标大小（像素） */
  iconSize?: number;
  /** 网格列数 */
  gridColumns?: number;
}

/**
 * 图标选择器状态接口
 */
export interface IconSelectorState {
  /** 所有图标列表 */
  icons: IconItem[];
  /** 过滤后的图标列表 */
  filteredIcons: IconItem[];
  /** 当前选中的图标 */
  selectedIcon: IconItem | null;
  /** 选中的多个图标（多选模式） */
  selectedIcons: IconItem[];
  /** 当前选中的颜色 */
  selectedColor: string;
  /** 搜索关键词 */
  searchKeyword: string;
  /** 当前选中的分类 */
  selectedCategory: string | null;
  /** 当前页码 */
  currentPage: number;
  /** 总页数 */
  totalPages: number;
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
  /** 事件时间戳 */
  timestamp: number;
}

/**
 * 图标搜索选项接口
 */
export interface IconSearchOptions {
  /** 搜索关键词 */
  keyword: string;
  /** 分类筛选 */
  category?: string;
  /** 标签筛选 */
  tags?: string[];
  /** 排序方式 */
  sortBy?: 'name' | 'category' | 'recent';
  /** 排序方向 */
  sortOrder?: 'asc' | 'desc';
}

/**
 * 图标选择器回调函数类型
 */
export interface IconSelectorCallbacks {
  /** 图标选择回调 */
  onSelect?: (event: IconSelectEvent) => void;
  /** 颜色变化回调 */
  onColorChange?: (color: string) => void;
  /** 搜索回调 */
  onSearch?: (keyword: string) => void;
  /** 分类变化回调 */
  onCategoryChange?: (category: string | null) => void;
  /** 关闭回调 */
  onClose?: () => void;
}

/**
 * 图标选择器Props接口
 */
export interface IconSelectorProps {
  /** 配置选项 */
  config?: IconSelectorConfig;
  /** 回调函数 */
  callbacks?: IconSelectorCallbacks;
  /** 是否显示选择器 */
  visible?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
}

/**
 * 颜色选择器Props接口
 */
export interface ColorPickerProps {
  /** 当前颜色值 */
  value: string;
  /** 颜色变化回调 */
  onChange: (color: string) => void;
  /** 预设颜色列表 */
  presetColors?: ColorOption[];
  /** 是否显示透明度选择 */
  showAlpha?: boolean;
  /** 是否显示颜色输入框 */
  showInput?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 图标预览Props接口
 */
export interface IconPreviewProps {
  /** 图标项 */
  icon: IconItem;
  /** 图标颜色 */
  color: string;
  /** 图标大小 */
  size?: number;
  /** 是否选中 */
  selected?: boolean;
  /** 点击回调 */
  onClick?: () => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * 图标网格Props接口
 */
export interface IconGridProps {
  /** 图标列表 */
  icons: IconItem[];
  /** 选中的图标ID */
  selectedId?: string;
  /** 图标颜色 */
  color: string;
  /** 图标大小 */
  iconSize?: number;
  /** 网格列数 */
  columns?: number;
  /** 图标点击回调 */
  onIconClick: (icon: IconItem) => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * 图标搜索框Props接口
 */
export interface IconSearchProps {
  /** 搜索关键词 */
  value: string;
  /** 搜索变化回调 */
  onChange: (value: string) => void;
  /** 占位符文本 */
  placeholder?: string;
  /** 是否显示清除按钮 */
  showClear?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 图标分类筛选Props接口
 */
export interface IconCategoryFilterProps {
  /** 分类列表 */
  categories: IconCategory[];
  /** 当前选中的分类 */
  selectedCategory: string | null;
  /** 分类变化回调 */
  onChange: (category: string | null) => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * 分页组件Props接口
 */
export interface PaginationProps {
  /** 当前页码 */
  currentPage: number;
  /** 总页数 */
  totalPages: number;
  /** 页码变化回调 */
  onChange: (page: number) => void;
  /** 是否显示快速跳转 */
  showQuickJumper?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 图标加载器返回类型
 */
export interface IconLoaderResult {
  /** 图标列表 */
  icons: IconItem[];
  /** 分类列表 */
  categories: IconCategory[];
  /** 加载是否成功 */
  success: boolean;
  /** 错误信息 */
  error?: string;
}

/**
 * 图标数据源接口
 */
export interface IconDataSource {
  /** 获取所有图标 */
  getIcons: () => Promise<IconItem[]>;
  /** 根据分类获取图标 */
  getIconsByCategory: (category: string) => Promise<IconItem[]>;
  /** 搜索图标 */
  searchIcons: (options: IconSearchOptions) => Promise<IconItem[]>;
  /** 获取分类列表 */
  getCategories: () => Promise<IconCategory[]>;
}
