"""文章管理API"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import get_current_active_user
from app.core.db import get_session
from app.core.logging import logger
from app.models.article import Article
from app.models.style import Style
from app.models.user import User
from app.models.user_api_key import UserApiKey
from app.models.wechat_config import WechatConfig
from app.schemas.article import ArticleCreate, ArticleListResponse, ArticleResponse, ArticleUpdate
from app.services.mcp_service import MCPService
from app.services.style_service import StyleService
from app.services.wechat_service import WechatService

router = APIRouter(prefix="/articles", tags=["文章管理"])


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Article:
    """生成文章
    
    Args:
        article_data: 文章创建数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        生成的文章
    """
    # 检查样式是否存在
    result = await session.execute(
        select(Style).where(Style.id == article_data.style_id)
    )
    style = result.scalar_one_or_none()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="样式不存在"
        )
    
    # 检查权限
    if not style.is_system and style.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权使用此样式"
        )
    
    # 检查用户是否配置了API Key
    result = await session.execute(
        select(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    api_key_config = result.scalar_one_or_none()
    
    if not api_key_config or not api_key_config.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置有效的API Key"
        )
    
    # 创建文章记录(初始状态为draft)
    new_article = Article(
        user_id=current_user.id,
        style_id=article_data.style_id,
        title="生成中...",
        prompt_input=article_data.prompt_input,
        content_raw="",
        content_html="",
        status="draft",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_article)
    await session.commit()
    await session.refresh(new_article)
    
    # 异步生成文章内容
    try:
        # 调用MCP服务生成Markdown
        mcp_service = MCPService(api_key_config.api_key_encrypted)
        markdown_content = await mcp_service.generate_article(
            article_data.prompt_input,
            style.prompt_instruction
        )
        
        # 提取标题
        title = StyleService.extract_title_from_markdown(markdown_content)
        if not title:
            title = article_data.prompt_input[:50]
        
        # 转换为HTML
        html_content = StyleService.markdown_to_html(markdown_content, style.css_content)
        
        # 更新文章
        new_article.title = title
        new_article.content_raw = markdown_content
        new_article.content_html = html_content
        new_article.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(new_article)
        
        logger.info(f"用户 {current_user.username} 生成文章成功: {title}")
        
    except Exception as e:
        # 记录错误
        new_article.generation_error = str(e)
        new_article.status = "failed"
        await session.commit()
        await session.refresh(new_article)
        
        logger.error(f"文章生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文章生成失败: {str(e)}"
        )
    
    return new_article


@router.get("", response_model=List[ArticleListResponse])
async def list_articles(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 20,
) -> List[Article]:
    """获取文章列表
    
    Args:
        current_user: 当前用户
        session: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        文章列表
    """
    result = await session.execute(
        select(Article)
        .where(Article.user_id == current_user.id)
        .order_by(Article.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    articles = result.scalars().all()
    
    return list(articles)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Article:
    """获取文章详情
    
    Args:
        article_id: 文章ID
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        文章详情
    """
    result = await session.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限
    if article.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文章"
        )
    
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Article:
    """更新文章
    
    Args:
        article_id: 文章ID
        article_data: 更新的文章数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        更新后的文章
    """
    result = await session.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限
    if article.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此文章"
        )
    
    # 更新字段
    if article_data.title is not None:
        article.title = article_data.title
    if article_data.content_html is not None:
        article.content_html = article_data.content_html
    
    article.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(article)
    
    logger.info(f"用户 {current_user.username} 更新文章: {article.title}")
    
    return article


@router.post("/{article_id}/sync", response_model=ArticleResponse)
async def sync_article_to_wechat(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Article:
    """同步文章到微信草稿箱
    
    Args:
        article_id: 文章ID
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        同步后的文章
    """
    # 获取文章
    result = await session.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限
    if article.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权同步此文章"
        )
    
    # 检查微信配置
    result = await session.execute(
        select(WechatConfig).where(WechatConfig.user_id == current_user.id)
    )
    wechat_config = result.scalar_one_or_none()
    
    if not wechat_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置微信公众号"
        )
    
    # 同步到微信
    try:
        wechat_service = WechatService(wechat_config)
        media_id = await wechat_service.sync_article_with_retry(
            article.title,
            article.content_html
        )
        
        # 更新文章状态
        article.wechat_media_id = media_id
        article.status = "synced"
        article.synced_at = datetime.utcnow()
        article.sync_error_message = None
        
        # 更新微信配置统计
        wechat_config.total_synced += 1
        wechat_config.last_sync_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(article)
        await session.refresh(wechat_config)
        
        logger.info(f"用户 {current_user.username} 同步文章成功: {article.title}")
        
    except Exception as e:
        # 记录错误
        article.sync_error_message = str(e)
        article.status = "failed"
        article.retry_count += 1
        
        await session.commit()
        await session.refresh(article)
        
        logger.error(f"文章同步失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文章同步失败: {str(e)}"
        )
    
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """删除文章
    
    Args:
        article_id: 文章ID
        current_user: 当前用户
        session: 数据库会话
    """
    result = await session.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限
    if article.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文章"
        )
    
    await session.delete(article)
    await session.commit()
    
    logger.info(f"用户 {current_user.username} 删除文章: {article.title}")
