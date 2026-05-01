# PRD — Initialize Vite + React + TypeScript project scaffold

> 所属需求：前端项目基础架构搭建

## 用户故事
As a 前端开发者，I want to 快速搭建一个标准化的 React + TypeScript 项目脚手架，So that 可以立即开始业务功能开发，而不需要从零配置工具链和目录结构。

## 功能需求
- 使用 Vite 创建 React 18 + TypeScript 5.x 项目
- 安装并配置 Ant Design 5.x UI 组件库
- 创建标准化目录结构：/src/components（公共组件）、/src/pages（页面）、/src/api（接口层）、/src/utils（工具函数）、/src/types（TypeScript 类型定义）
- 配置 vite.config.ts：开发服务器端口、路径别名（@/ 指向 src/）、构建优化选项
- 配置 tsconfig.json：严格模式、路径映射、JSX 支持
- 创建基础入口文件（main.tsx、App.tsx）和示例页面
- 配置 .gitignore 排除 node_modules、dist、.env 等文件

## 验收标准
- [ ] 执行 `npm create vite@latest` 后生成的项目包含 package.json，其中 dependencies 包含 react@^18.0.0、react-dom@^18.0.0
- [ ] package.json 的 devDependencies 包含 typescript@^5.0.0、vite@^5.0.0、@vitejs/plugin-react@^4.0.0
- [ ] 执行 `npm install antd` 后 package.json 包含 antd@^5.0.0
- [ ] src/ 目录下存在 5 个子目录：components/、pages/、api/、utils/、types/，每个目录包含 .gitkeep 或示例文件
- [ ] vite.config.ts 配置项包含：server.port（如 3000）、resolve.alias（@/ 映射到 /src）
- [ ] tsconfig.json 包含："strict": true、"paths": {"@/*": ["./src/*"]}、"jsx": "react-jsx"
- [ ] 执行 `npm run dev` 后 2s 内终端输出包含 "Local: http://localhost:[端口号]" 且端口号与 vite.config.ts 一致
- [ ] 浏览器访问开发服务器地址后 1s 内页面渲染完成，显示 React + Vite 默认欢迎页或自定义首页
- [ ] src/main.tsx 文件存在且包含 `import 'antd/dist/reset.css'` 或等效的 Ant Design 样式引入
- [ ] .gitignore 文件包含以下行：node_modules、dist、.env、.env.local、*.log
- [ ] 项目根目录存在 README.md，包含「项目启动」章节，说明 `npm install` 和 `npm run dev` 命令

## 边界条件（不做的事）
- 不包含：路由配置（React Router 在后续工单实现）
- 不包含：状态管理方案（Context API / Zustand 在后续工单实现）
- 不包含：API 请求封装（Axios 拦截器在后续工单实现）
- 不包含：ESLint / Prettier 配置（代码规范在后续工单实现）
- 不包含：环境变量业务配置（.env 文件结构在后续工单实现，本工单仅添加到 .gitignore）
- 不包含：全局样式主题定制（Ant Design 主题配置在后续工单实现）
- 暂不支持：服务端渲染（SSR）、静态站点生成（SSG）
- 超出范围：单元测试配置（Vitest / Jest）、E2E 测试（Playwright）、CI/CD 流程

## 资产需求线索
暂无（本工单为纯技术基础设施搭建，不涉及视觉资产）
