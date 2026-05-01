tests/test_config.py

import os
import pytest
from app.core.config import settings


def test_settings_loaded():
    """测试配置是否正确加载"""
    assert settings is not None
    assert settings.PROJECT_NAME is not None
    assert settings.VERSION is not None


def test_project_name():
    """测试项目名称"""
    assert settings.PROJECT_NAME == "FastAPI Project"


def test_version():
    """测试版本号"""
    assert settings.VERSION == "1.0.0"


def test_api_prefix():
    """测试 API 前缀"""
    assert settings.API_V1_STR == "/api/v1"


def test_environment():
    """测试环境变量"""
    assert settings.ENVIRONMENT in ["development", "production", "testing"]


def test_debug_mode():
    """测试调试模式"""
    assert isinstance(settings.DEBUG, bool)


def test_cors_origins():
    """测试 CORS 配置"""
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
    assert len(settings.BACKEND_CORS_ORIGINS) > 0


def test_log_level():
    """测试日志级别"""
    assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_log_file_path():
    """测试日志文件路径"""
    assert settings.LOG_FILE is not None
    log_dir = os.path.dirname(settings.LOG_FILE)
    assert os.path.exists(log_dir) or log_dir == "logs"


def test_database_url():
    """测试数据库 URL（如果配置）"""
    if hasattr(settings, 'DATABASE_URL'):
        assert settings.DATABASE_URL is not None


def test_secret_key():
    """测试密钥配置"""
    if hasattr(settings, 'SECRET_KEY'):
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0


def test_settings_immutable():
    """测试配置不可变性"""
    with pytest.raises(Exception):
        settings.PROJECT_NAME = "New Name"


def test_environment_override():
    """测试环境变量覆盖"""
    original_env = os.environ.get("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "testing"
    
    from app.core.config import Settings
    test_settings = Settings()
    
    assert test_settings.ENVIRONMENT == "testing"
    
    if original_env:
        os.environ["ENVIRONMENT"] = original_env
    else:
        os.environ.pop("ENVIRONMENT", None)


def test_cors_origins_format():
    """测试 CORS 源格式"""
    for origin in settings.BACKEND_CORS_ORIGINS:
        assert isinstance(origin, str)
        assert origin.startswith("http://") or origin.startswith("https://") or origin == "*"


def test_log_file_writable():
    """测试日志文件可写"""
    log_dir = os.path.dirname(settings.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    assert os.access(log_dir, os.W_OK)


def test_settings_dict_export():
    """测试配置导出为字典"""
    config_dict = settings.dict()
    assert isinstance(config_dict, dict)
    assert "PROJECT_NAME" in config_dict
    assert "VERSION" in config_dict


def test_api_prefix_format():
    """测试 API 前缀格式"""
    assert settings.API_V1_STR.startswith("/")
    assert not settings.API_V1_STR.endswith("/")