// 响应式布局配置文件
// 定义断点、栅格系统和响应式样式变量

// 断点定义
export const breakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1440,
  wide: 1920
};

// 媒体查询字符串
export const mediaQueries = {
  mobile: `(max-width: ${breakpoints.mobile - 1}px)`,
  tablet: `(min-width: ${breakpoints.mobile}px) and (max-width: ${breakpoints.tablet - 1}px)`,
  desktop: `(min-width: ${breakpoints.tablet}px)`,
  wide: `(min-width: ${breakpoints.wide}px)`,
  
  // 最大宽度查询
  maxMobile: `(max-width: ${breakpoints.mobile - 1}px)`,
  maxTablet: `(max-width: ${breakpoints.tablet - 1}px)`,
  maxDesktop: `(max-width: ${breakpoints.desktop - 1}px)`,
  
  // 最小宽度查询
  minTablet: `(min-width: ${breakpoints.mobile}px)`,
  minDesktop: `(min-width: ${breakpoints.tablet}px)`,
  minWide: `(min-width: ${breakpoints.wide}px)`
};

// Ant Design 栅格系统配置
export const gridConfig = {
  // 栅格间距
  gutter: {
    mobile: [8, 8],
    tablet: [16, 16],
    desktop: [24, 24]
  },
  
  // 响应式栅格配置
  responsive: {
    xs: breakpoints.mobile,      // <768px
    sm: breakpoints.mobile,       // ≥768px
    md: breakpoints.tablet,       // ≥1024px
    lg: breakpoints.desktop,      // ≥1440px
    xl: breakpoints.wide,         // ≥1920px
    xxl: 2560                     // ≥2560px
  },
  
  // 容器最大宽度
  containerMaxWidth: {
    mobile: '100%',
    tablet: '720px',
    desktop: '960px',
    wide: '1200px'
  }
};

// 常用响应式列配置
export const colSpans = {
  // 全宽
  full: {
    xs: 24,
    sm: 24,
    md: 24,
    lg: 24,
    xl: 24
  },
  
  // 半宽
  half: {
    xs: 24,
    sm: 24,
    md: 12,
    lg: 12,
    xl: 12
  },
  
  // 三分之一
  third: {
    xs: 24,
    sm: 12,
    md: 8,
    lg: 8,
    xl: 8
  },
  
  // 四分之一
  quarter: {
    xs: 24,
    sm: 12,
    md: 6,
    lg: 6,
    xl: 6
  },
  
  // 侧边栏布局
  sidebar: {
    xs: 24,
    sm: 24,
    md: 8,
    lg: 6,
    xl: 6
  },
  
  // 主内容区
  main: {
    xs: 24,
    sm: 24,
    md: 16,
    lg: 18,
    xl: 18
  },
  
  // 表单布局
  formLabel: {
    xs: 24,
    sm: 8,
    md: 6,
    lg: 4,
    xl: 4
  },
  
  formWrapper: {
    xs: 24,
    sm: 16,
    md: 18,
    lg: 20,
    xl: 20
  }
};

// 响应式字体大小
export const fontSizes = {
  mobile: {
    h1: '24px',
    h2: '20px',
    h3: '18px',
    h4: '16px',
    body: '14px',
    small: '12px',
    tiny: '10px'
  },
  tablet: {
    h1: '28px',
    h2: '24px',
    h3: '20px',
    h4: '18px',
    body: '14px',
    small: '12px',
    tiny: '10px'
  },
  desktop: {
    h1: '32px',
    h2: '28px',
    h3: '24px',
    h4: '20px',
    body: '14px',
    small: '12px',
    tiny: '10px'
  }
};

// 响应式间距
export const spacing = {
  mobile: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    xxl: '32px'
  },
  tablet: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px'
  },
  desktop: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '48px',
    xxl: '64px'
  }
};

// CSS-in-JS 样式 Mixins
export const styleMixins = {
  // 响应式容器
  container: (maxWidth = 'desktop') => ({
    width: '100%',
    maxWidth: gridConfig.containerMaxWidth[maxWidth],
    marginLeft: 'auto',
    marginRight: 'auto',
    paddingLeft: '16px',
    paddingRight: '16px',
    
    [`@media ${mediaQueries.mobile}`]: {
      paddingLeft: '12px',
      paddingRight: '12px'
    }
  }),
  
  // 隐藏元素
  hideOnMobile: {
    [`@media ${mediaQueries.mobile}`]: {
      display: 'none'
    }
  },
  
  hideOnTablet: {
    [`@media ${mediaQueries.tablet}`]: {
      display: 'none'
    }
  },
  
  hideOnDesktop: {
    [`@media ${mediaQueries.desktop}`]: {
      display: 'none'
    }
  },
  
  // 显示元素
  showOnMobile: {
    display: 'none',
    [`@media ${mediaQueries.mobile}`]: {
      display: 'block'
    }
  },
  
  showOnTablet: {
    display: 'none',
    [`@media ${mediaQueries.tablet}`]: {
      display: 'block'
    }
  },
  
  showOnDesktop: {
    display: 'none',
    [`@media ${mediaQueries.desktop}`]: {
      display: 'block'
    }
  },
  
  // 响应式文字
  responsiveText: (mobileSize, tabletSize, desktopSize) => ({
    fontSize: desktopSize,
    [`@media ${mediaQueries.tablet}`]: {
      fontSize: tabletSize
    },
    [`@media ${mediaQueries.mobile}`]: {
      fontSize: mobileSize
    }
  }),
  
  // 响应式间距
  responsiveSpacing: (property, mobileValue, tabletValue, desktopValue) => ({
    [property]: desktopValue,
    [`@media ${mediaQueries.tablet}`]: {
      [property]: tabletValue
    },
    [`@media ${mediaQueries.mobile}`]: {
      [property]: mobileValue
    }
  }),
  
  // Flex 布局响应式
  responsiveFlex: (mobileDirection = 'column', desktopDirection = 'row') => ({
    display: 'flex',
    flexDirection: desktopDirection,
    [`@media ${mediaQueries.mobile}`]: {
      flexDirection: mobileDirection
    }
  })
};

// 工具函数：检测当前设备类型
export const getDeviceType = () => {
  const width = window.innerWidth;
  
  if (width < breakpoints.mobile) {
    return 'mobile';
  } else if (width < breakpoints.tablet) {
    return 'tablet';
  } else {
    return 'desktop';
  }
};

// 工具函数：获取当前断点
export const getCurrentBreakpoint = () => {
  const width = window.innerWidth;
  
  if (width < breakpoints.mobile) {
    return 'xs';
  } else if (width < breakpoints.tablet) {
    return 'sm';
  } else if (width < breakpoints.desktop) {
    return 'md';
  } else if (width < breakpoints.wide) {
    return 'lg';
  } else {
    return 'xl';
  }
};

// 工具函数：判断是否为移动设备
export const isMobile = () => {
  return window.innerWidth < breakpoints.mobile;
};

// 工具函数：判断是否为平板设备
export const isTablet = () => {
  return window.innerWidth >= breakpoints.mobile && window.innerWidth < breakpoints.tablet;
};

// 工具函数：判断是否为桌面设备
export const isDesktop = () => {
  return window.innerWidth >= breakpoints.tablet;
};

// 响应式监听 Hook 配置
export const responsiveHookConfig = {
  // 防抖延迟
  debounceDelay: 150,
  
  // 初始化时是否立即执行
  immediate: true,
  
  // 是否使用 ResizeObserver（更高性能）
  useResizeObserver: true
};

// 全局响应式样式变量（用于 CSS 变量）
export const cssVariables = {
  '--breakpoint-mobile': `${breakpoints.mobile}px`,
  '--breakpoint-tablet': `${breakpoints.tablet}px`,
  '--breakpoint-desktop': `${breakpoints.desktop}px`,
  '--breakpoint-wide': `${breakpoints.wide}px`,
  
  '--container-mobile': gridConfig.containerMaxWidth.mobile,
  '--container-tablet': gridConfig.containerMaxWidth.tablet,
  '--container-desktop': gridConfig.containerMaxWidth.desktop,
  '--container-wide': gridConfig.containerMaxWidth.wide,
  
  '--gutter-mobile': '8px',
  '--gutter-tablet': '16px',
  '--gutter-desktop': '24px'
};

// 导出默认配置
export default {
  breakpoints,
  mediaQueries,
  gridConfig,
  colSpans,
  fontSizes,
  spacing,
  styleMixins,
  cssVariables,
  getDeviceType,
  getCurrentBreakpoint,
  isMobile,
  isTablet,
  isDesktop,
  responsiveHookConfig
};