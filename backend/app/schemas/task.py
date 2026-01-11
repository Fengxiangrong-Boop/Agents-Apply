"""任务相关的Pydantic模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    user_id: int
    task_type: str
    status: str
    article_id: Optional[int]
    progress: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
