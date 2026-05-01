# 架构设计 - Initialize Vite + React + TypeScript project scaffold

## 架构模式
Frontend SPA with Vite + React + TypeScript

## 技术栈

- **build_tool**: Vite 5.x
- **framework**: React 18.x
- **language**: TypeScript 5.x
- **ui_library**: Ant Design 5.x
- **package_manager**: pnpm (recommended) or npm
- **node_version**: >=18.0.0

## 模块设计

### 
职责: Initialize Vite project with React + TypeScript template

### 
职责: Create standardized folder structure for scalable development

### 
职责: Install and configure Ant Design with basic theme setup

### 
职责: Configure Vite with path aliases, dev server options, and build optimizations

### 
职责: Configure TypeScript with strict mode and path mappings

### 
职责: Set up main entry point with basic App component

## 关键决策
- {'decision': 'Use Vite instead of Create React App', 'reason': 'Vite provides faster HMR, native ESM support, and better build performance; CRA is no longer actively maintained'}
- {'decision': 'Use pnpm as recommended package manager', 'reason': 'Faster installation, disk space efficient, strict dependency resolution prevents phantom dependencies'}
- {'decision': 'Configure path alias @ for src/', 'reason': 'Avoids relative import hell (../../..), improves code readability and refactoring safety'}
- {'decision': 'Enable TypeScript strict mode', 'reason': 'Catches more bugs at compile time, enforces better type safety practices from the start'}
- {'decision': 'Use Ant Design 5.x with CSS-in-JS', 'reason': 'Latest version with improved performance, better TypeScript support, and CSS variable theming'}
- {'decision': 'Create barrel exports (index.ts) in each directory', 'reason': "Enables clean imports like `import { Button } from '@/components'`, easier to manage public API surface"}
