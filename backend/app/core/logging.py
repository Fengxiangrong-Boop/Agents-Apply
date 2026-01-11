"""日志配置模块"""
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

# 敏感信息脱敏模式
SENSITIVE_PATTERNS = {
    "app_secret": re.compile(r'(app_secret["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', re.IGNORECASE),
    "api_key": re.compile(r'(api_key["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', re.IGNORECASE),
    "access_token": re.compile(r'(access_token["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', re.IGNORECASE),
    "password": re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', re.IGNORECASE),
    "secret": re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', re.IGNORECASE),
}


class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器 - 自动脱敏日志中的敏感信息"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录,替换敏感信息
        
        Args:
            record: 日志记录
            
        Returns:
            总是返回True以保留日志
        """
        message = record.getMessage()
        
        # 替换所有敏感信息
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            message = pattern.sub(r'\1***\3', message)
        
        # 更新日志消息
        record.msg = message
        record.args = ()
        
        return True


def setup_logging() -> logging.Logger:
    """配置应用日志系统
    
    Returns:
        配置好的logger实例
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger("wechat_agent")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    
    # 文件处理器(带轮转)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SensitiveDataFilter())
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(SensitiveDataFilter())
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger


# 全局logger实例
logger = setup_logging()
