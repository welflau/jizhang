import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import NotFoundError, ValidationError, BusinessError

client = TestClient(app)


def test_success_response():
    """测试成功响应格式"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["message"] == "success"


def test_not_found_exception():
    """测试 404 异常处理"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "message" in data
    assert data["data"] is None


def test_validation_error():
    """测试验证错误"""
    response = client.post("/api/v1/test/validate", json={"invalid": "data"})
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == 422
    assert "message" in data


def test_business_exception():
    """测试业务异常"""
    response = client.get("/api/v1/test/business-error")
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "message" in data
    assert data["data"] is None


def test_internal_server_error():
    """测试服务器内部错误"""
    response = client.get("/api/v1/test/server-error")
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == 500
    assert "message" in data


def test_custom_not_found_error():
    """测试自定义 NotFoundError"""
    response = client.get("/api/v1/test/not-found")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "not found" in data["message"].lower()


def test_custom_validation_error():
    """测试自定义 ValidationError"""
    response = client.get("/api/v1/test/validation-error")
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "validation" in data["message"].lower()


def test_response_model_structure():
    """测试响应模型结构"""
    response = client.get("/api/v1/test/response-model")
    assert response.status_code == 200
    data = response.json()
    
    # 验证必需字段
    assert "code" in data
    assert "message" in data
    assert "data" in data
    
    # 验证字段类型
    assert isinstance(data["code"], int)
    assert isinstance(data["message"], str)
    
    # 验证成功响应的值
    assert data["code"] == 200
    assert data["message"] == "success"


def test_response_with_data():
    """测试带数据的响应"""
    response = client.get("/api/v1/test/with-data")
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == 200
    assert data["message"] == "success"
    assert data["data"] is not None
    assert isinstance(data["data"], dict)


def test_response_without_data():
    """测试无数据的响应"""
    response = client.get("/api/v1/test/without-data")
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == 200
    assert data["message"] == "success"
    assert data["data"] is None


def test_exception_handler_middleware():
    """测试异常处理中间件"""
    response = client.get("/api/v1/test/raise-exception")
    assert response.status_code in [400, 500]
    data = response.json()
    
    # 验证异常被正确捕获并转换为统一格式
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] != 200


def test_multiple_exceptions():
    """测试多种异常类型"""
    test_cases = [
        ("/api/v1/test/not-found", 404),
        ("/api/v1/test/validation-error", 400),
        ("/api/v1/test/business-error", 400),
        ("/api/v1/test/server-error", 500),
    ]
    
    for endpoint, expected_code in test_cases:
        response = client.get(endpoint)
        data = response.json()
        assert data["code"] == expected_code
        assert "message" in data
        assert "data" in data