import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    拦截标准 logging 日志并重定向到 loguru
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    配置日志系统
    根据环境变量决定日志输出方式和级别
    """
    # 移除默认的 loguru handler
    logger.remove()

    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # 根据环境决定是否输出到文件
    if settings.ENVIRONMENT == "production":
        # 生产环境：输出到文件
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)

        # 普通日志文件（按日期轮转）
        logger.add(
            log_path / "app_{time:YYYY-MM-DD}.log",
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="00:00",  # 每天午夜轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            backtrace=True,
            diagnose=True,
        )

        # 错误日志单独记录
        logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="ERROR",
            rotation="00:00",
            retention="90 days",  # 错误日志保留更久
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    elif settings.ENVIRONMENT == "development":
        # 开发环境：可选文件输出
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)

        logger.add(
            log_path / "dev_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="DEBUG",
            rotation="100 MB",  # 按大小轮转
            retention="7 days",
            backtrace=True,
            diagnose=True,
        )

    # 拦截标准 logging 库的日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 拦截 uvicorn 日志
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(f"日志系统初始化完成 - 环境: {settings.ENVIRONMENT}, 级别: {settings.LOG_LEVEL}")


def get_logger(name: Optional[str] = None):
    """
    获取 logger 实例
    
    Args:
        name: logger 名称，通常使用 __name__
    
    Returns:
        logger 实例
    """
    if name:
        return logger.bind(name=name)
    return logger