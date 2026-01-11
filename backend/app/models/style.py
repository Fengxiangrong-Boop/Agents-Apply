"""样式模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Style(SQLModel, table=True):
    """样式表"""
    
    __tablename__ = "styles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True, description="样式名称")
    description: Optional[str] = Field(default=None, max_length=500, description="样式描述")
    prompt_instruction: str = Field(description="LLM风格指令")
    css_content: str = Field(description="HTML渲染样式")
    
    # 样式归属
    is_system: bool = Field(default=False, description="是否系统预设样式")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", description="自定义样式所属用户")
    
    # 版本和预览
    version: int = Field(default=1, description="样式版本号")
    preview_image: Optional[str] = Field(default=None, max_length=500, description="样式预览图路径")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "专业商务风格",
                "description": "适合企业和商务场景的专业风格",
                "is_system": True,
                "version": 1,
            }
        }
