from typing import List, Optional
from pydantic import BaseModel, Field

class ArticleSection(BaseModel):
    """文章章节"""
    title: str
    content: str
    image_url: Optional[str] = None

class Article(BaseModel):
    """文章模型"""
    title: str
    summary: str
    sections: List[ArticleSection]
    tags: List[str] = Field(default_factory=list)
    markdown_content: str = ""

class ResearchResult(BaseModel):
    """研究结果"""
    topic: str
    key_points: List[str]
    sources: List[str] = Field(default_factory=list)
