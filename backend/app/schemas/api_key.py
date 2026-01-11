"""API Key相关的Pydantic模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """API Key创建模型"""
    provider: str = Field(default="siliconflow", description="LLM提供商")
    api_key: str = Field(..., min_length=10, description="API Key明文")


class ApiKeyUpdate(BaseModel):
    """API Key更新模型"""
    api_key: str = Field(..., min_length=10, description="新的API Key明文")


class ApiKeyResponse(BaseModel):
    """API Key响应模型"""
    id: int
    provider: str
    is_valid: bool
    last_validated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 注意: 不返回加密的API Key
    
    class Config:
        from_attributes = True
