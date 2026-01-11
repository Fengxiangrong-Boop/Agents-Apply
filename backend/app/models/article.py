"""文章模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    """文章表"""
    
    __tablename__ = "articles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    style_id: int = Field(foreign_key="styles.id", description="使用的样式ID")
    
    title: str = Field(max_length=200, description="文章标题")
    prompt_input: str = Field(description="用户输入的原始Prompt")
    content_raw: str = Field(description="LLM生成的原始Markdown")
    content_html: str = Field(description="渲染后的HTML")
    
    # 同步状态
    status: str = Field(
        default="draft",
        max_length=20,
        description="状态: draft/synced/failed"
    )
    wechat_media_id: Optional[str] = Field(default=None, max_length=100, description="微信草稿ID")
    
    # 错误信息
    generation_error: Optional[str] = Field(default=None, description="生成失败的错误信息")
    sync_error_message: Optional[str] = Field(default=None, description="同步失败的错误信息")
    retry_count: int = Field(default=0, description="同步重试次数")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    synced_at: Optional[datetime] = Field(default=None, description="同步成功的时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "如何提高工作效率",
                "prompt_input": "写一篇关于提高工作效率的文章",
                "status": "draft",
                "retry_count": 0,
            }
        }
