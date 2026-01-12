"""应用配置模块 - 环境变量加载和配置管理"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "微信公众号文章智能生成与同步系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 服务器配置
    SERVER_IP: str = "localhost"
    BACKEND_PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://wechat_agent:password@localhost:5432/wechat_agent_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str  # 必须通过环境变量提供
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 加密配置
    ENCRYPTION_KEY: str  # 必须通过环境变量提供,用于Fernet加密
    
    # MCP Server配置
    MCP_SERVER_HOST: str = "mcp-server"
    MCP_SERVER_PORT: int = 3000
    
    # 硅基流动API配置
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    SILICONFLOW_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # LLM调用配置
    LLM_MAX_CONCURRENT: int = 5  # 最大并发调用数
    LLM_TIMEOUT: int = 60  # 超时时间(秒)
    LLM_MAX_RETRIES: int = 3  # 最大重试次数
    
    # 微信API配置
    WECHAT_TOKEN_REFRESH_ADVANCE: int = 300  # Token提前刷新时间(秒),默认5分钟
    WECHAT_MAX_RETRIES: int = 3  # 微信API最大重试次数
    
    # API限流配置
    RATE_LIMIT_GENERATE: str = "5/minute"  # 文章生成限流
    RATE_LIMIT_SYNC: str = "10/minute"  # 微信同步限流
    RATE_LIMIT_AUTH: str = "10/minute"  # 认证接口限流
    
    # CORS配置
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:27999"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def get_cors_origins(self) -> list[str]:
        """获取CORS允许的来源列表"""
        origins = self.CORS_ORIGINS.copy()
        if self.SERVER_IP and self.SERVER_IP != "localhost":
            origins.append(f"http://{self.SERVER_IP}")
        return origins


# 全局配置实例
settings = Settings()
