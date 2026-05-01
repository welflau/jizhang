# PRD — Implement responsive layout breakpoints and grid system

> 所属需求：响应式布局适配

## 用户故事
As a 用户，I want to 在不同设备上访问系统时自动适配最佳布局，So that 无论使用桌面、平板还是手机都能获得流畅的操作体验。

## 功能需求
- 断点系统：定义三个响应式断点（桌面 ≥1024px、平板 768-1023px、移动 <768px）
- 栅格系统：配置 Ant Design Grid 组件的响应式列数（桌面 24 列、平板 12 列、移动 6 列）
- 全局样式变量：创建 CSS 变量存储断点值、容器最大宽度、间距规则
- 响应式 Mixins：封装媒体查询工具函数（desktop-only、tablet-and-up、mobile-only）
- 布局容器：实现自适应宽度的主容器组件（桌面固定最大宽度 1440px，移动端 100% 宽度）
- 间距系统：定义响应式 padding/margin 规则（桌面 24px、平板 16px、移动 12px）

## 验收标准
- [ ] 浏览器窗口宽度从 1920px 缩小到 320px 过程中，布局在 1024px、768px 两个断点处发生明显变化（通过 Chrome DevTools 验证）
- [ ] 桌面端（≥1024px）：主容器最大宽度锁定为 1440px 且水平居中，左右 padding = 24px
- [ ] 平板端（768-1023px）：主容器宽度 = 100vw - 32px（左右各 16px padding），栅格列数自动从 24 列切换为 12 列
- [ ] 移动端（<768px）：主容器宽度 = 100vw - 24px（左右各 12px padding），栅格列数切换为 6 列
- [ ] CSS 变量 `--breakpoint-mobile`、`--breakpoint-tablet`、`--breakpoint-desktop` 在全局样式文件中定义且值分别为 768px、1024px
- [ ] 响应式 Mixin `@mixin mobile-only` 生成的媒体查询为 `@media (max-width: 767px)`
- [ ] 响应式 Mixin `@mixin tablet-and-up` 生成的媒体查询为 `@media (min-width: 768px)`
- [ ] 响应式 Mixin `@mixin desktop-only` 生成的媒体查询为 `@media (min-width: 1024px)`
- [ ] Ant Design `<Row>` 组件配置 `gutter` 属性为响应式对象：`{ xs: 8, sm: 12, md: 16, lg: 24 }`
- [ ] 创建 `ResponsiveContainer` 组件，接受 `maxWidth` 属性（默认 1440px），在桌面端应用最大宽度限制
- [ ] 间距工具类 `.p-responsive` 在桌面端生成 `padding: 24px`，平板端 `16px`，移动端 `12px`（通过计算样式验证）
- [ ] 使用 `window.matchMedia('(min-width: 1024px)')` 的 JS Hook 能正确返回当前断点状态（desktop/tablet/mobile）
- [ ] 所有断点切换过程中无水平滚动条出现（`overflow-x: hidden` 生效）
- [ ] 在 iPhone SE（375px）、iPad（768px）、MacBook Pro（1440px）三种设备模拟器下截图对比，布局差异符合设计预期

## 边界条件（不做的事）
- 不包含：具体页面的响应式实现（侧边栏、导航栏、表单、表格等组件的适配逻辑）
- 不包含：触摸手势交互逻辑（滑动、长按等）
- 不包含：移动端专用组件开发（抽屉、底部导航栏、下拉刷新等）
- 不包含：图片/视频的响应式加载策略（srcset、懒加载）
- 不包含：字体大小的响应式缩放（rem/em 配置）
- 暂不支持：横屏模式的特殊适配
- 暂不支持：超宽屏（>1920px）的特殊布局
- 超出范围：性能优化（CSS 压缩、Critical CSS 提取）

## 资产需求线索
暂无

[假设] 本工单为纯技术基础设施搭建，不涉及视觉资产需求。后续响应式组件开发时可能需要：
- 移动端汉堡菜单图标（24x24px SVG）
- 平板端收起/展开侧边栏的箭头图标（16x16px）
- 空状态插画的移动端优化版本（宽度 ≤ 300px）
