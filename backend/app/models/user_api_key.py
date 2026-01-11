"""用户API密钥模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserApiKey(SQLModel, table=True):
    """用户API密钥表"""
    
    __tablename__ = "user_api_keys"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, description="用户ID")
    provider: str = Field(default="siliconflow", max_length=50, description="LLM提供商")
    api_key_encrypted: str = Field(description="加密后的API Key")
    is_valid: bool = Field(default=True, description="API Key是否有效")
    last_validated_at: Optional[datetime] = Field(default=None, description="上次验证时间")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "siliconflow",
                "is_valid": True,
            }
        }
