# PRD — Create unified response format and exception handler middleware

> 所属需求：后端 API 服务搭建

## 用户故事
作为用户，我需要 Create unified response format and exception handler middleware

## 功能需求
- 创建统一响应格式封装（app/schemas/response.py），定义 ResponseModel（code、message、data），实现全局异常处理中间件（捕获所有异常并返回统一格式），定义常见业务异常类（NotFoundError、ValidationError 等），配置 FastAPI 异常处理器。输出：所有 API 返回统一 JSON 格式 + 异常自动转换为标准响应。

## 验收标准
- 功能可正常使用（待细化）

## 边界条件（不做的事）
- 暂无特殊限制

## 资产需求线索
暂无
