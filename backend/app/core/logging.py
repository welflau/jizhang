import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


class LogConfig:
    """日志配置类"""

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

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


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    配置日志系统
    
    Args:
        log_file: 日志文件路径，如果为 None 则使用配置中的路径
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
        datefmt=LogConfig.DATE_FORMAT
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（生产环境）
    if settings.ENVIRONMENT == "production":
        log_file_path = log_file or settings.LOG_FILE
        
        # 确保日志目录存在
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_file_path,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # 记录启动信息
    root_logger.info(f"日志系统初始化完成 - 环境: {settings.ENVIRONMENT}, 级别: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


# 导出常用函数
__all__ = ["setup_logging", "get_logger", "LogConfig"]