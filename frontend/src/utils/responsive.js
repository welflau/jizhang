/**
 * Responsive Layout Utilities
 * 响应式布局工具
 * 
 * 定义断点、栅格系统配置和响应式样式变量
 */

// ==================== 断点定义 ====================
export const BREAKPOINTS = {
  mobile: {
    max: 767,
    min: 0,
  },
  tablet: {
    max: 1023,
    min: 768,
  },
  desktop: {
    min: 1024,
    max: Infinity,
  },
};

// 断点像素值
export const BREAKPOINT_VALUES = {
  xs: 0,      // 超小屏幕
  sm: 576,    // 小屏幕
  md: 768,    // 中等屏幕（平板）
  lg: 1024,   // 大屏幕（桌面）
  xl: 1280,   // 超大屏幕
  xxl: 1600,  // 超超大屏幕
};

// ==================== 媒体查询字符串 ====================
export const MEDIA_QUERIES = {
  mobile: `(max-width: ${BREAKPOINTS.mobile.max}px)`,
  tablet: `(min-width: ${BREAKPOINTS.tablet.min}px) and (max-width: ${BREAKPOINTS.tablet.max}px)`,
  desktop: `(min-width: ${BREAKPOINTS.desktop.min}px)`,
  tabletAndAbove: `(min-width: ${BREAKPOINTS.tablet.min}px)`,
  mobileAndTablet: `(max-width: ${BREAKPOINTS.tablet.max}px)`,
};

// ==================== Ant Design 栅格系统配置 ====================
export const GRID_CONFIG = {
  // 栅格间距配置
  gutter: {
    mobile: [8, 8],
    tablet: [16, 16],
    desktop: [24, 24],
  },
  
  // 响应式栅格配置
  responsive: {
    xs: { span: 24 },  // 移动端：全宽
    sm: { span: 24 },  // 小屏：全宽
    md: { span: 12 },  // 平板：半宽
    lg: { span: 8 },   // 桌面：三分之一
    xl: { span: 6 },   // 大屏：四分之一
    xxl: { span: 4 },  // 超大屏：六分之一
  },
  
  // 容器最大宽度
  containerMaxWidth: {
    mobile: '100%',
    tablet: '720px',
    desktop: '1200px',
    wide: '1400px',
  },
};

// ==================== 响应式样式变量 ====================
export const RESPONSIVE_STYLES = {
  // 字体大小
  fontSize: {
    mobile: {
      h1: '24px',
      h2: '20px',
      h3: '18px',
      h4: '16px',
      body: '14px',
      small: '12px',
    },
    tablet: {
      h1: '28px',
      h2: '24px',
      h3: '20px',
      h4: '18px',
      body: '14px',
      small: '12px',
    },
    desktop: {
      h1: '32px',
      h2: '28px',
      h3: '24px',
      h4: '20px',
      body: '14px',
      small: '12px',
    },
  },
  
  // 间距
  spacing: {
    mobile: {
      xs: '4px',
      sm: '8px',
      md: '12px',
      lg: '16px',
      xl: '24px',
    },
    tablet: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
    },
    desktop: {
      xs: '8px',
      sm: '12px',
      md: '16px',
      lg: '24px',
      xl: '48px',
    },
  },
  
  // 内边距
  padding: {
    mobile: {
      page: '12px',
      section: '16px',
      card: '12px',
    },
    tablet: {
      page: '16px',
      section: '24px',
      card: '16px',
    },
    desktop: {
      page: '24px',
      section: '32px',
      card: '24px',
    },
  },
};

// ==================== 工具函数 ====================

/**
 * 获取当前设备类型
 * @returns {'mobile' | 'tablet' | 'desktop'}
 */
export const getDeviceType = () => {
  const width = window.innerWidth;
  
  if (width < BREAKPOINTS.tablet.min) {
    return 'mobile';
  } else if (width <= BREAKPOINTS.tablet.max) {
    return 'tablet';
  } else {
    return 'desktop';
  }
};

/**
 * 检查是否为移动设备
 * @returns {boolean}
 */
export const isMobile = () => {
  return window.innerWidth <= BREAKPOINTS.mobile.max;
};

/**
 * 检查是否为平板设备
 * @returns {boolean}
 */
export const isTablet = () => {
  const width = window.innerWidth;
  return width >= BREAKPOINTS.tablet.min && width <= BREAKPOINTS.tablet.max;
};

/**
 * 检查是否为桌面设备
 * @returns {boolean}
 */
export const isDesktop = () => {
  return window.innerWidth >= BREAKPOINTS.desktop.min;
};

/**
 * 根据设备类型获取对应的值
 * @param {Object} values - 包含 mobile, tablet, desktop 的值对象
 * @returns {*}
 */
export const getResponsiveValue = (values) => {
  const deviceType = getDeviceType();
  return values[deviceType] || values.desktop || values.mobile;
};

/**
 * 创建媒体查询监听器
 * @param {string} query - 媒体查询字符串
 * @param {Function} callback - 回调函数
 * @returns {Function} 清理函数
 */
export const createMediaQueryListener = (query, callback) => {
  const mediaQuery = window.matchMedia(query);
  
  // 初始调用
  callback(mediaQuery.matches);
  
  // 监听变化
  const handler = (e) => callback(e.matches);
  
  // 兼容不同浏览器
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handler);
  } else {
    mediaQuery.addListener(handler);
  }
  
  // 返回清理函数
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', handler);
    } else {
      mediaQuery.removeListener(handler);
    }
  };
};

/**
 * 获取栅格间距
 * @returns {Array}
 */
export const getGridGutter = () => {
  return getResponsiveValue(GRID_CONFIG.gutter);
};

/**
 * 获取容器最大宽度
 * @param {string} size - 容器尺寸类型
 * @returns {string}
 */
export const getContainerMaxWidth = (size = 'desktop') => {
  return GRID_CONFIG.containerMaxWidth[size] || GRID_CONFIG.containerMaxWidth.desktop;
};

// ==================== CSS-in-JS Mixins ====================

/**
 * 生成响应式样式对象
 * @param {Object} styles - 包含不同断点样式的对象
 * @returns {Object}
 */
export const responsiveStyles = (styles) => {
  const result = {};
  
  if (styles.mobile) {
    result[`@media ${MEDIA_QUERIES.mobile}`] = styles.mobile;
  }
  
  if (styles.tablet) {
    result[`@media ${MEDIA_QUERIES.tablet}`] = styles.tablet;
  }
  
  if (styles.desktop) {
    result[`@media ${MEDIA_QUERIES.desktop}`] = styles.desktop;
  }
  
  return result;
};

/**
 * 生成容器样式
 * @param {string} maxWidth - 最大宽度类型
 * @returns {Object}
 */
export const containerStyles = (maxWidth = 'desktop') => ({
  width: '100%',
  maxWidth: getContainerMaxWidth(maxWidth),
  marginLeft: 'auto',
  marginRight: 'auto',
  paddingLeft: getResponsiveValue(RESPONSIVE_STYLES.padding).page,
  paddingRight: getResponsiveValue(RESPONSIVE_STYLES.padding).page,
});

/**
 * 生成隐藏样式（根据设备类型）
 * @param {Array<string>} devices - 需要隐藏的设备类型数组
 * @returns {Object}
 */
export const hideOn = (devices = []) => {
  const styles = {};
  
  devices.forEach(device => {
    if (MEDIA_QUERIES[device]) {
      styles[`@media ${MEDIA_QUERIES[device]}`] = {
        display: 'none !important',
      };
    }
  });
  
  return styles;
};

/**
 * 生成显示样式（仅在指定设备显示）
 * @param {Array<string>} devices - 需要显示的设备类型数组
 * @returns {Object}
 */
export const showOn = (devices = []) => {
  const allDevices = ['mobile', 'tablet', 'desktop'];
  const hideDevices = allDevices.filter(d => !devices.includes(d));
  return hideOn(hideDevices);
};

// ==================== Ant Design 响应式配置 ====================

/**
 * 获取 Ant Design Col 组件的响应式配置
 * @param {Object} config - 自定义配置
 * @returns {Object}
 */
export const getColResponsive = (config = {}) => {
  return {
    xs: config.xs || 24,
    sm: config.sm || 24,
    md: config.md || 12,
    lg: config.lg || 8,
    xl: config.xl || 6,
    xxl: config.xxl || 4,
  };
};

/**
 * 获取 Ant Design Form 的响应式布局配置
 * @returns {Object}
 */
export const getFormResponsiveLayout = () => {
  const deviceType = getDeviceType();
  
  if (deviceType === 'mobile') {
    return {
      labelCol: { span: 24 },
      wrapperCol: { span: 24 },
    };
  } else if (deviceType === 'tablet') {
    return {
      labelCol: { span: 6 },
      wrapperCol: { span: 18 },
    };
  } else {
    return {
      labelCol: { span: 4 },
      wrapperCol: { span: 20 },
    };
  }
};

/**
 * 获取 Ant Design Table 的响应式配置
 * @returns {Object}
 */
export const getTableResponsive = () => {
  const deviceType = getDeviceType();
  
  return {
    scroll: deviceType === 'mobile' ? { x: 'max-content' } : undefined,
    size: deviceType === 'mobile' ? 'small' : 'middle',
    pagination: {
      pageSize: deviceType === 'mobile' ? 5 : 10,
      showSizeChanger: deviceType !== 'mobile',
      showQuickJumper: deviceType === 'desktop',
    },
  };
};

// ==================== 导出默认配置 ====================
export default {
  BREAKPOINTS,
  BREAKPOINT_VALUES,
  MEDIA_QUERIES,
  GRID_CONFIG,
  RESPONSIVE_STYLES,
  getDeviceType,
  isMobile,
  isTablet,
  isDesktop,
  getResponsiveValue,
  createMediaQueryListener,
  getGridGutter,
  getContainerMaxWidth,
  responsiveStyles,
  containerStyles,
  hideOn,
  showOn,
  getColResponsive,
  getFormResponsiveLayout,
  getTableResponsive,
};