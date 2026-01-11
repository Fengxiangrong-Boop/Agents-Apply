"""微信配置相关的Pydantic模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WechatConfigCreate(BaseModel):
    """微信配置创建模型"""
    app_id: str = Field(..., min_length=10, max_length=100, description="微信AppID")
    app_secret: str = Field(..., min_length=10, description="微信AppSecret明文")


class WechatConfigUpdate(BaseModel):
    """微信配置更新模型"""
    app_id: Optional[str] = Field(None, min_length=10, max_length=100, description="微信AppID")
    app_secret: Optional[str] = Field(None, min_length=10, description="微信AppSecret明文")


class WechatConfigResponse(BaseModel):
    """微信配置响应模型"""
    id: int
    app_id: str
    total_synced: int
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 注意: 不返回加密的AppSecret和AccessToken
    
    class Config:
        from_attributes = True
