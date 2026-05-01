# 架构设计 - Create unified response format and exception handler middleware

## 架构模式
middleware_layer

## 技术栈

- **language**: Python 3.9+
- **framework**: FastAPI
- **validation**: Pydantic v2
- **logging**: Python logging (already configured)
- **dependencies**: fastapi, pydantic, starlette

## 模块设计

### 
职责: Define unified response models and standard response codes
- success(data, message): Create success response
- error(code, message, data=None): Create error response
- paginated(items, total, page, page_size): Create paginated response

### 
职责: Define custom business exception classes
- __init__(detail, status_code, headers=None)
- to_response(): Convert exception to ResponseModel

### 
职责: Global exception handler middleware
- dispatch(request, call_next): Catch all exceptions and convert to unified response
- _handle_api_exception(exc): Handle custom business exceptions
- _handle_validation_error(exc): Handle Pydantic ValidationError
- _handle_http_exception(exc): Handle FastAPI HTTPException
- _handle_generic_exception(exc): Handle unexpected exceptions

### 
职责: Register exception handlers and middleware

### 
职责: Helper functions for common response patterns

## 关键决策
- {'decision': 'Use Generic Pydantic model ResponseModel[T] for type safety', 'rationale': 'Provides IDE autocomplete and type checking for response data, better than plain dict', 'alternatives': 'Plain dict response - rejected due to lack of type safety'}
- {'decision': 'Implement middleware instead of dependency injection for exception handling', 'rationale': 'Middleware catches ALL exceptions including those outside route handlers (e.g., middleware chain errors), more comprehensive than @app.exception_handler decorators alone', 'alternatives': 'Only use @app.exception_handler - rejected as it misses some edge cases'}
- {'decision': "Keep HTTP status codes in response headers, also include 'code' field in JSON body", 'rationale': 'HTTP status for protocol compliance, JSON code field for frontend business logic (e.g., 4001 for token expired vs 4002 for invalid token, both 401 status)', 'alternatives': 'Only use HTTP status - rejected as insufficient granularity for business errors'}
- {'decision': 'Log all 5xx errors with full traceback, log 4xx errors without traceback', 'rationale': '5xx indicates server bugs needing investigation, 4xx is expected client errors not needing stack traces', 'alternatives': 'Log everything with traceback - rejected as too noisy'}
- {'decision': 'Inherit custom exceptions from Python Exception, not FastAPI HTTPException', 'rationale': 'HTTPException is FastAPI-specific and bypasses middleware, custom exceptions give full control over response format', 'alternatives': "Use HTTPException - rejected as it doesn't go through our middleware"}
