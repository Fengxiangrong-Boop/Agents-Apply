"""文章相关的Pydantic模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    """文章创建模型"""
    style_id: int = Field(..., description="使用的样式ID")
    prompt_input: str = Field(..., min_length=1, description="用户输入的原始Prompt")


class ArticleUpdate(BaseModel):
    """文章更新模型"""
    title: Optional[str] = Field(None, max_length=200, description="文章标题")
    content_html: Optional[str] = Field(None, description="编辑后的HTML内容")


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    user_id: int
    style_id: int
    title: str
    prompt_input: str
    content_raw: str
    content_html: str
    status: str
    wechat_media_id: Optional[str]
    generation_error: Optional[str]
    sync_error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    synced_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应模型"""
    id: int
    title: str
    status: str
    created_at: datetime
    synced_at: Optional[datetime]
    
    class Config:
        from_attributes = True
