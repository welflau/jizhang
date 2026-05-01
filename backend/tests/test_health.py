import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_health_check_response_structure():
    """测试健康检查响应结构"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    
    # 验证必需字段
    required_fields = ["status", "timestamp", "version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # 验证字段类型
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str)


def test_health_check_status_value():
    """测试健康检查状态值"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"], "Invalid status value"


def test_health_check_multiple_requests():
    """测试多次健康检查请求"""
    for _ in range(5):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


def test_health_check_headers():
    """测试健康检查响应头"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "content-type" in response.headers
    assert "application/json" in response.headers["content-type"]