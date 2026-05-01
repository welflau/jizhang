# PRD — Setup API router structure and auto-generate Swagger docs

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to set up a clear API router structure with auto-generated Swagger documentation, So that frontend developers can easily discover and test available endpoints through a well-organized API interface.

## 功能需求
- 创建 /app/api/v1 目录结构，包含 __init__.py 和各模块路由文件
- 实现 APIRouter 注册机制，支持模块化路由管理
- 配置全局 API 版本前缀 /api/v1
- 创建示例路由模块：users.py（用户相关）、auth.py（认证相关）、health.py（健康检查）
- 每个路由模块包含至少 1 个占位端点（GET/POST），带完整的 Pydantic schema 定义
- 配置 FastAPI 内置 Swagger UI（/docs）和 ReDoc（/redoc）
- 为所有端点添加 OpenAPI 元数据：summary、description、tags、response_model
- 实现路由自动注册函数（遍历 v1 目录下所有路由模块并挂载到主 app）

## 验收标准
- [ ] 访问 http://localhost:8000/docs 后 500ms 内显示 Swagger UI 界面
- [ ] Swagger UI 中至少展示 3 个 API 分组（tags）：Users、Authentication、Health
- [ ] 每个分组下至少包含 1 个可交互的端点（显示请求参数、响应示例）
- [ ] 所有端点路径以 /api/v1 开头（如 /api/v1/users、/api/v1/auth/login）
- [ ] 点击 Swagger UI 中的「Try it out」按钮后，能成功发送请求并返回 JSON 响应（即使是占位数据）
- [ ] 访问 http://localhost:8000/redoc 能正常显示 ReDoc 文档界面
- [ ] /app/api/v1/__init__.py 中包含 api_router 对象，聚合所有子路由
- [ ] 主应用 main.py 通过 app.include_router(api_router, prefix="/api/v1") 挂载路由
- [ ] 每个路由文件顶部包含 router = APIRouter(prefix="/xxx", tags=["Xxx"]) 声明
- [ ] 至少 1 个端点定义了 Pydantic response_model，Swagger 中显示完整的响应 schema
- [ ] health.py 中包含 GET /health 端点，返回 {"status": "ok", "timestamp": <ISO8601 时间>}
- [ ] 目录结构符合：app/api/v1/{__init__.py, users.py, auth.py, health.py}

## 边界条件（不做的事）
- 不实现真实的业务逻辑（用户 CRUD、JWT 认证等），仅创建占位端点返回 mock 数据
- 不连接数据库，所有端点返回硬编码的示例 JSON
- 不实现请求参数校验的错误处理（422 响应），仅定义 schema
- 不配置 CORS、认证中间件、异常处理（这些属于其他工单范围）
- 不实现 API 版本切换机制（v2/v3），仅支持 v1
- 不添加速率限制、请求日志等中间件
- 不编写单元测试（测试属于独立工单）
- 暂不支持 WebSocket 路由

## 资产需求线索
暂无（纯后端 API 结构搭建，无 UI 资产需求）
