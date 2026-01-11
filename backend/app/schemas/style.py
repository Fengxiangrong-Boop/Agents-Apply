"""样式相关的Pydantic模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StyleBase(BaseModel):
    """样式基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="样式名称")
    description: Optional[str] = Field(None, max_length=500, description="样式描述")
    prompt_instruction: str = Field(..., min_length=1, description="LLM风格指令")
    css_content: str = Field(..., min_length=1, description="HTML渲染样式")


class StyleCreate(StyleBase):
    """样式创建模型"""
    preview_image: Optional[str] = Field(None, max_length=500, description="样式预览图路径")


class StyleUpdate(BaseModel):
    """样式更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="样式名称")
    description: Optional[str] = Field(None, max_length=500, description="样式描述")
    prompt_instruction: Optional[str] = Field(None, min_length=1, description="LLM风格指令")
    css_content: Optional[str] = Field(None, min_length=1, description="HTML渲染样式")
    preview_image: Optional[str] = Field(None, max_length=500, description="样式预览图路径")


class StyleResponse(StyleBase):
    """样式响应模型"""
    id: int
    is_system: bool
    user_id: Optional[int]
    version: int
    preview_image: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
