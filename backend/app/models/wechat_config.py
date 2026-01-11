"""微信配置模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class WechatConfig(SQLModel, table=True):
    """微信配置表"""
    
    __tablename__ = "wechat_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, description="用户ID")
    app_id: str = Field(max_length=100, description="微信AppID")
    app_secret_encrypted: str = Field(description="加密后的AppSecret")
    
    # AccessToken管理
    access_token: Optional[str] = Field(default=None, description="访问令牌")
    token_expires_at: Optional[datetime] = Field(default=None, description="Token过期时间")
    last_refresh_at: Optional[datetime] = Field(default=None, description="上次刷新时间")
    
    # 统计字段
    total_synced: int = Field(default=0, description="总同步次数")
    last_sync_at: Optional[datetime] = Field(default=None, description="上次同步时间")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "wx1234567890abcdef",
                "total_synced": 0,
            }
        }
