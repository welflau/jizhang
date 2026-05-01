# 架构设计 - Create unified response format and exception handler middleware

## 架构模式
middleware_layer

## 技术栈

- **framework**: FastAPI
- **validation**: Pydantic v2
- **exception_handling**: FastAPI exception handlers + custom middleware
- **response_format**: Generic Pydantic model with TypeVar
- **logging**: Python logging (already configured)

## 模块设计

### 
职责: Define unified response models and generic wrapper
- ResponseModel.model_validate() for serialization
- Type hints: ResponseModel[UserSchema], ResponseModel[List[Item]]

### 
职责: Define custom business exception classes
- raise NotFoundException(detail='User not found')
- All exceptions inherit from BaseAPIException

### 
职责: Register global exception handlers for FastAPI
- Called in app/main.py: register_exception_handlers(app)
- Returns JSONResponse with ResponseModel structure

### 
职责: Optional middleware for exception logging and preprocessing
- app.add_middleware(ExceptionLoggingMiddleware)
- Integrates with app/core/logger.py

### 
职责: Refactor health check to use ResponseModel
- GET /api/health returns {code: 200, message: 'success', data: {status: 'ok'}}

## 关键决策
- {'decision': 'Use Generic Pydantic model (ResponseModel[T]) instead of dict', 'reason': 'Type safety for response data, automatic validation, better IDE support, consistent with FastAPI/Pydantic ecosystem'}
- {'decision': 'Separate exception classes (app/core/exceptions.py) from handlers (app/core/exception_handlers.py)', 'reason': 'Clear separation of concerns: exceptions define business errors, handlers define HTTP responses. Easier to test and extend'}
- {'decision': "Use FastAPI's built-in exception handler registration instead of pure middleware", 'reason': "FastAPI's @app.exception_handler() is more idiomatic, supports async, and integrates with OpenAPI docs. Middleware is only for logging"}
- {'decision': 'Define ResponseCode as IntEnum instead of string constants', 'reason': 'HTTP status codes are integers, IntEnum provides type checking and prevents magic numbers'}
- {'decision': 'Keep success code as 200 (not 0 or custom codes)', 'reason': 'Align with HTTP standards, avoid confusion. Business-specific codes can be added in data field if needed'}
- {'decision': 'Log all exceptions in middleware before handler processes them', 'reason': 'Centralized logging with request context (path, method, IP) for debugging. Handlers focus on response formatting'}
