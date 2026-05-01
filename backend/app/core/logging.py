import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


class LogConfig:
    """日志配置类"""
    
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @staticmethod
    def get_log_level() -> int:
        """根据环境获取日志级别"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)


def setup_logging() -> None:
    """
    配置日志系统
    - 开发环境：输出到控制台
    - 生产环境：输出到文件和控制台
    """
    log_level = LogConfig.get_log_level()
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除已存在的处理器
    root_logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt=LogConfig.LOG_FORMAT,
        datefmt=LogConfig.LOG_DATE_FORMAT
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 生产环境添加文件处理器
    if settings.ENVIRONMENT == "production":
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 应用日志文件
        app_log_file = log_dir / "app.log"
        file_handler = logging.handlers.RotatingFileHandler(
            filename=app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志文件
        error_log_file = log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 环境: {settings.ENVIRONMENT}, 级别: {settings.LOG_LEVEL}")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认使用调用模块名
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name or __name__)


# 导入 RotatingFileHandler
import logging.handlers