# 架构设计 - Design category icon set and color palette

## 架构模式
Design System Extension

## 技术栈

- **design_tools**: Figma / SVG Editor
- **icon_format**: SVG (inline + sprite)
- **color_system**: CSS Custom Properties
- **accessibility**: WCAG 2.1 AA (4.5:1 contrast ratio)
- **delivery**: JSON config + SVG assets

## 模块设计

### 
职责: Category icon SVG collection

### 
职责: Category color system with accessibility compliance

### 
职责: Documentation for frontend integration

## 关键决策
- {'decision': 'Use SVG sprite instead of icon font', 'rationale': 'Better accessibility (semantic HTML), easier customization, no FOIT/FOUT issues, supports multi-color icons'}
- {'decision': 'Outline style icons (2px stroke)', 'rationale': 'Consistent with modern design trends, scales better, lighter visual weight, easier to customize'}
- {'decision': 'Separate color palettes for income/expense', 'rationale': 'Visual distinction helps users quickly identify transaction types, aligns with accounting conventions (green=income, red=expense)'}
- {'decision': 'WCAG AA compliance (4.5:1 contrast)', 'rationale': 'Legal requirement in many jurisdictions, improves usability for users with visual impairments, standard best practice'}
- {'decision': 'JSON-based configuration', 'rationale': 'Easy to parse in frontend, supports future i18n (icon labels), allows dynamic icon/color management'}
- {'decision': 'Provide preview HTML page', 'rationale': 'Enables non-technical stakeholders to review designs, serves as living documentation, aids QA testing'}
