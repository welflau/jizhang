# PRD — Build icon selector component

> 所属需求：分类管理系统

## 用户故事
As a 记账应用用户，I want to 在添加/编辑分类时选择合适的图标和颜色，So that 我的分类列表更直观易识别，提升记账效率和视觉体验。

## 功能需求
- 图标选择器组件：支持从预设图标库中选择图标
- 图标搜索：支持按关键词（中文/英文）实时过滤图标
- 图标预览：网格布局展示所有可选图标，选中状态高亮
- 颜色选择器集成：图标选择器与颜色选择器联动，实时预览图标+颜色组合效果
- 响应式布局：桌面端 6-8 列网格，移动端 4 列网格
- 默认图标：未选择时显示默认图标（如 wallet 钱包图标）

## 验收标准
- [ ] 图标库包含 ≥ 50 个常用图标（餐饮/交通/购物/娱乐/医疗/教育/工资/奖金等场景）
- [ ] 搜索框输入关键词后 200ms 内完成过滤，匹配图标名称或标签
- [ ] 点击图标后 100ms 内切换选中状态（边框高亮 + 背景色变化）
- [ ] 图标网格桌面端每行显示 6-8 个，移动端每行显示 4 个，图标尺寸 32x32px
- [ ] 颜色选择器改变颜色后，选中图标实时更新颜色预览（无需点击确认）
- [ ] 组件支持受控模式：接收 value 属性（当前选中图标名），触发 onChange 回调返回选中图标名
- [ ] 搜索无结果时显示空状态提示「未找到匹配的图标」
- [ ] 组件加载时间 < 500ms（图标资源懒加载或 SVG inline）
- [ ] 支持键盘导航：Tab 键切换图标焦点，Enter 键选中
- [ ] 移动端触摸区域 ≥ 44x44px（符合 iOS/Android 触摸规范）

## 边界条件（不做的事）
- 不包含：自定义上传图标功能（仅使用预设图标库）
- 不包含：图标动画效果（静态图标即可）
- 暂不支持：图标分组/分类（所有图标平铺展示）
- 暂不支持：最近使用图标历史记录
- 超出范围：图标编辑器（不支持修改图标形状/路径）
- [假设] 图标库使用 Ant Design Icons 或 Font Awesome，不自研图标

## 资产需求线索
- 图标库：需准备 50+ 个 SVG 图标，涵盖以下分类：
  - 餐饮：coffee, restaurant, fastfood, cake, beer
  - 交通：car, bus, subway, taxi, bicycle, flight
  - 购物：shopping-cart, gift, clothes, electronics
  - 娱乐：movie, game, music, book, sport
  - 医疗：hospital, medicine, heart
  - 教育：book, school, course
  - 收入：wallet, salary, bonus, investment, gift-income
  - 其他：home, pet, beauty, travel, phone-bill
- 空状态插画：搜索无结果时的占位图（可选，可用文字替代）
- [假设] 使用 Ant Design Icons 图标库（@ant-design/icons-react），无需额外设计资产
