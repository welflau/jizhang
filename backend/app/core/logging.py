import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


class LoggerSetup:
    """日志配置类"""

    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

    def get_log_level(self) -> int:
        """根据环境获取日志级别"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)

    def setup_logger(
        self, name: Optional[str] = None, log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        配置并返回日志记录器

        Args:
            name: 日志记录器名称，默认为根记录器
            log_file: 日志文件名，默认为 app.log

        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(self.get_log_level())

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 日志格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.get_log_level())
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器（生产环境或配置要求时）
        if settings.ENVIRONMENT == "production" or settings.LOG_TO_FILE:
            if log_file is None:
                log_file = "app.log"

            file_handler = logging.FileHandler(
                self.log_dir / log_file, encoding="utf-8"
            )
            file_handler.setLevel(self.get_log_level())
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


# 创建全局日志记录器实例
logger_setup = LoggerSetup()
logger = logger_setup.setup_logger("app")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logger_setup.setup_logger(name)