import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.schemas.response import ResponseModel, response_success, response_error
from app.middleware.exception_handler import (
    NotFoundError,
    ValidationError,
    BusinessError,
    AuthenticationError,
    PermissionError,
)


@pytest.fixture
def app():
    app = FastAPI()

    @app.get("/success")
    async def success_endpoint():
        return response_success(data={"message": "success"})

    @app.get("/error")
    async def error_endpoint():
        return response_error(message="error occurred")

    @app.get("/not-found")
    async def not_found_endpoint():
        raise NotFoundError("Resource not found")

    @app.get("/validation-error")
    async def validation_error_endpoint():
        raise ValidationError("Invalid input")

    @app.get("/business-error")
    async def business_error_endpoint():
        raise BusinessError("Business logic error")

    @app.get("/auth-error")
    async def auth_error_endpoint():
        raise AuthenticationError("Authentication failed")

    @app.get("/permission-error")
    async def permission_error_endpoint():
        raise PermissionError("Permission denied")

    @app.get("/unexpected-error")
    async def unexpected_error_endpoint():
        raise Exception("Unexpected error")

    from app.middleware.exception_handler import add_exception_handlers
    add_exception_handlers(app)

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestResponseFormat:
    def test_response_model_structure(self):
        """测试响应模型结构"""
        response = ResponseModel(code=200, message="success", data={"key": "value"})
        assert response.code == 200
        assert response.message == "success"
        assert response.data == {"key": "value"}

    def test_response_success_helper(self):
        """测试成功响应辅助函数"""
        response = response_success(data={"user": "test"}, message="操作成功")
        assert response["code"] == 200
        assert response["message"] == "操作成功"
        assert response["data"] == {"user": "test"}

    def test_response_success_default_message(self):
        """测试成功响应默认消息"""
        response = response_success(data={"id": 1})
        assert response["code"] == 200
        assert response["message"] == "success"
        assert response["data"] == {"id": 1}

    def test_response_error_helper(self):
        """测试错误响应辅助函数"""
        response = response_error(code=400, message="请求错误", data=None)
        assert response["code"] == 400
        assert response["message"] == "请求错误"
        assert response["data"] is None

    def test_response_error_default_code(self):
        """测试错误响应默认状态码"""
        response = response_error(message="服务器错误")
        assert response["code"] == 500
        assert response["message"] == "服务器错误"


class TestExceptionHandlers:
    def test_success_endpoint(self, client):
        """测试成功端点返回统一格式"""
        response = client.get("/success")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "success"
        assert data["data"]["message"] == "success"

    def test_error_endpoint(self, client):
        """测试错误端点返回统一格式"""
        response = client.get("/error")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert data["message"] == "error occurred"

    def test_not_found_error_handler(self, client):
        """测试 NotFoundError 异常处理"""
        response = client.get("/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == 404
        assert data["message"] == "Resource not found"
        assert data["data"] is None

    def test_validation_error_handler(self, client):
        """测试 ValidationError 异常处理"""
        response = client.get("/validation-error")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert data["message"] == "Invalid input"
        assert data["data"] is None

    def test_business_error_handler(self, client):
        """测试 BusinessError 异常处理"""
        response = client.get("/business-error")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert data["message"] == "Business logic error"
        assert data["data"] is None

    def test_authentication_error_handler(self, client):
        """测试 AuthenticationError 异常处理"""
        response = client.get("/auth-error")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401
        assert data["message"] == "Authentication failed"
        assert data["data"] is None

    def test_permission_error_handler(self, client):
        """测试 PermissionError 异常处理"""
        response = client.get("/permission-error")
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == 403
        assert data["message"] == "Permission denied"
        assert data["data"] is None

    def test_unexpected_error_handler(self, client):
        """测试未预期异常处理"""
        response = client.get("/unexpected-error")
        assert response.status_code == 500
        data = response.json()
        assert data["code"] == 500
        assert "Internal server error" in data["message"] or "Unexpected error" in data["message"]


class TestCustomExceptions:
    def test_not_found_error_creation(self):
        """测试 NotFoundError 创建"""
        error = NotFoundError("User not found")
        assert str(error) == "User not found"
        assert error.status_code == 404

    def test_validation_error_creation(self):
        """测试 ValidationError 创建"""
        error = ValidationError("Invalid email format")
        assert str(error) == "Invalid email format"
        assert error.status_code == 400

    def test_business_error_creation(self):
        """测试 BusinessError 创建"""
        error = BusinessError("Insufficient balance")
        assert str(error) == "Insufficient balance"
        assert error.status_code == 400

    def test_authentication_error_creation(self):
        """测试 AuthenticationError 创建"""
        error = AuthenticationError("Invalid token")
        assert str(error) == "Invalid token"
        assert error.status_code == 401

    def test_permission_error_creation(self):
        """测试 PermissionError 创建"""
        error = PermissionError("Access denied")
        assert str(error) == "Access denied"
        assert error.status_code == 403


class TestResponseConsistency:
    def test_all_responses_have_required_fields(self, client):
        """测试所有响应都包含必需字段"""
        endpoints = [
            "/success",
            "/error",
            "/not-found",
            "/validation-error",
            "/business-error",
            "/auth-error",
            "/permission-error",
            "/unexpected-error",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            assert "code" in data
            assert "message" in data
            assert "data" in data
            assert isinstance(data["code"], int)
            assert isinstance(data["message"], str)

    def test_response_format_consistency(self, client):
        """测试响应格式一致性"""
        response1 = client.get("/success")
        response2 = client.get("/not-found")

        data1 = response1.json()
        data2 = response2.json()

        assert set(data1.keys()) == set(data2.keys())
        assert set(data1.keys()) == {"code", "message", "data"}