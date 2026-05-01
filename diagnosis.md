# Diagnosis: Create unified response format and exception handler middleware

## 任务目标
创建统一响应格式封装和全局异常处理中间件，确保所有 API 返回统一的 JSON 格式，并自动将异常转换为标准响应。

## 实现方案

### 1. 统一响应格式封装 (app/schemas/response.py)

**目标**: 定义标准的响应模型，包含 code、message、data 字段

**实现要点**:
- 使用 Pydantic 定义 ResponseModel 基类
- 支持泛型，data 字段可以是任意类型
- 提供便捷的成功/失败响应构造方法
- 定义标准的状态码常量

**代码结构**:
```
class ResponseModel(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T]
    
    @classmethod
    def success(cls, data, message="Success")
    
    @classmethod
    def error(cls, code, message, data=None)
```

### 2. 业务异常类定义 (app/core/exceptions.py)

**目标**: 定义常见的业务异常类，便于在业务逻辑中抛出

**需要定义的异常类**:
- BaseAPIException: 基础异常类，包含 code 和 message
- NotFoundError: 资源不存在 (404)
- ValidationError: 数据验证失败 (400)
- UnauthorizedError: 未授权 (401)
- ForbiddenError: 禁止访问 (403)
- ConflictError: 资源冲突 (409)
- InternalServerError: 内部服务器错误 (500)

**实现要点**:
- 每个异常类携带默认的 HTTP 状态码和错误码
- 支持自定义错误消息
- 继承自标准 Exception 类

### 3. 全局异常处理中间件 (app/middleware/exception_handler.py)

**目标**: 捕获所有异常并转换为统一的响应格式

**需要处理的异常类型**:
- 自定义业务异常 (BaseAPIException)
- FastAPI 内置异常 (HTTPException, RequestValidationError)
- Python 标准异常 (Exception)

**实现要点**:
- 使用 @app.exception_handler 装饰器注册异常处理器
- 根据异常类型返回对应的状态码和错误信息
- 记录异常日志，便于调试
- 生产环境隐藏敏感错误信息

### 4. FastAPI 异常处理器配置 (app/main.py)

**目标**: 在 FastAPI 应用中注册所有异常处理器

**配置步骤**:
1. 导入自定义异常类和处理器
2. 使用 app.add_exception_handler() 注册处理器
3. 为不同异常类型配置对应的处理函数
4. 确保中间件执行顺序正确

## 文件清单

1. **app/schemas/response.py** - 统一响应模型
2. **app/core/exceptions.py** - 业务异常类定义
3. **app/middleware/exception_handler.py** - 异常处理中间件
4. **app/core/constants.py** - 状态码和错误码常量
5. **app/main.py** - 异常处理器注册（修改）

## 预期效果

### 成功响应示例:
```json
{
    "code": 200,
    "message": "Success",
    "data": {
        "id": 1,
        "name": "example"
    }
}
```

### 错误响应示例:
```json
{
    "code": 404,
    "message": "Resource not found",
    "data": null
}
```

### 验证错误响应示例:
```json
{
    "code": 400,
    "message": "Validation error",
    "data": {
        "errors": [
            {
                "field": "email",
                "message": "Invalid email format"
            }
        ]
    }
}
```

## 测试要点

1. **正常请求**: 返回统一的成功响应格式
2. **404 错误**: 访问不存在的资源，返回标准 404 响应
3. **验证错误**: 提交无效数据，返回详细的验证错误信息
4. **业务异常**: 抛出自定义异常，返回对应的错误响应
5. **未捕获异常**: 触发未预期的异常，返回 500 错误但不暴露敏感信息

## 注意事项

1. **日志记录**: 所有异常都应记录到日志系统
2. **安全性**: 生产环境不应暴露堆栈跟踪和敏感信息
3. **国际化**: 考虑支持多语言错误消息
4. **性能**: 异常处理不应影响正常请求的性能
5. **一致性**: 确保所有 API 端点都使用统一的响应格式

## 依赖项

- fastapi
- pydantic
- python-multipart (用于处理表单验证错误)

## 后续优化

1. 添加请求 ID 追踪
2. 集成分布式追踪系统
3. 实现错误码国际化
4. 添加错误统计和监控
5. 支持自定义错误处理钩子