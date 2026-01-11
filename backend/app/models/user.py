"""用户模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """用户表"""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True, description="登录名")
    password_hash: str = Field(description="密码哈希")
    is_active: bool = Field(default=True, description="账号是否激活")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "is_active": True,
            }
        }
