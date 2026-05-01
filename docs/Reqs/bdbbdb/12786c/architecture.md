# 架构设计 - Build icon selector component

## 架构模式
Component-Based Frontend Architecture

## 技术栈

- **framework**: React 18+
- **language**: TypeScript
- **ui_library**: Ant Design / Material-UI
- **state_management**: React Hooks (useState, useCallback)
- **styling**: CSS Modules / Styled Components
- **icon_library**: React Icons / Lucide React
- **color_picker**: @uiw/react-color / react-colorful

## 模块设计

### 
职责: Main icon selector component, manages icon display, search, selection state

### 
职责: Grid layout for icon display, handles icon click events, supports pagination/virtual scrolling

### 
职责: Single icon display unit, shows icon with hover/selected state

### 
职责: Search input with debounce, filters icons by name/category

### 
职责: Color selection component, integrates with icon preview

### 
职责: Icon metadata registry, maps icon names to React components and categories

### 
职责: Custom hook for icon search logic, fuzzy matching, category filtering

## 关键决策
- {'decision': 'Use React Icons library as icon source', 'rationale': 'Provides 20,000+ icons from popular sets (Feather, Material, Ant Design), tree-shakable, TypeScript support, no SVG file management needed', 'alternatives': 'Custom SVG sprite sheet (harder to maintain), icon font (accessibility issues)'}
- {'decision': 'Implement icon registry with metadata', 'rationale': 'Enables search/filter by category and tags, allows curated subset of icons (avoid overwhelming users with 20k icons), easy to extend with custom icons', 'alternatives': 'Import all icons dynamically (performance issue), hardcode icon list (not scalable)'}
- {'decision': 'Separate ColorPicker as independent component', 'rationale': 'Reusable across app (budget color selection, theme customization), testable in isolation, follows single responsibility principle', 'alternatives': 'Inline color picker in IconSelector (tight coupling)'}
- {'decision': 'Use controlled component pattern', 'rationale': 'Parent component (CategoryForm) controls selected icon/color state, enables validation, easier to integrate with form libraries (React Hook Form, Formik)', 'alternatives': 'Uncontrolled component with internal state (harder to sync with form)'}
- {'decision': 'Implement virtual scrolling for icon grid (optional optimization)', 'rationale': 'If showing 500+ icons, virtual scrolling (react-window) improves render performance, reduces DOM nodes', 'alternatives': 'Pagination (requires extra clicks), load all icons (potential lag on low-end devices)'}
- {'decision': 'Use CSS Grid for IconGrid layout', 'rationale': 'Responsive grid without media queries (auto-fit/auto-fill), better than flexbox for equal-width items, native browser support', 'alternatives': 'Flexbox with manual wrapping (more CSS), CSS framework grid (extra dependency)'}
