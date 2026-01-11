"""任务模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """任务表"""
    
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    task_type: str = Field(
        max_length=50,
        description="任务类型: generate_article/sync_wechat"
    )
    status: str = Field(
        default="pending",
        max_length=20,
        description="状态: pending/running/completed/failed"
    )
    
    article_id: Optional[int] = Field(default=None, foreign_key="articles.id", description="关联文章ID")
    progress: int = Field(default=0, description="任务进度 (0-100)")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "generate_article",
                "status": "pending",
                "progress": 0,
            }
        }
