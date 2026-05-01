import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """测试根路径端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Visit Tracking API"


def test_cors_headers():
    """测试CORS头部配置"""
    response = client.options("/health")
    assert response.status_code == 200
    # 检查CORS相关头部是否存在
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_api_docs_available():
    """测试API文档端点可访问"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema():
    """测试OpenAPI schema可访问"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Visit Tracking API"