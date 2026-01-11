"""样式管理API"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from app.api.dependencies import get_current_active_user
from app.core.db import get_session
from app.core.logging import logger
from app.models.style import Style
from app.models.user import User
from app.schemas.style import StyleCreate, StyleResponse, StyleUpdate

router = APIRouter(prefix="/styles", tags=["样式管理"])


@router.get("", response_model=List[StyleResponse])
async def list_styles(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> List[Style]:
    """获取样式列表(系统样式 + 用户自定义样式)
    
    Args:
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        样式列表
    """
    result = await session.execute(
        select(Style).where(
            or_(
                Style.is_system == True,
                Style.user_id == current_user.id
            )
        ).order_by(Style.is_system.desc(), Style.created_at.desc())
    )
    styles = result.scalars().all()
    
    return list(styles)


@router.get("/{style_id}", response_model=StyleResponse)
async def get_style(
    style_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Style:
    """获取样式详情
    
    Args:
        style_id: 样式ID
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        样式详情
    """
    result = await session.execute(
        select(Style).where(Style.id == style_id)
    )
    style = result.scalar_one_or_none()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="样式不存在"
        )
    
    # 检查权限(系统样式或自己的样式)
    if not style.is_system and style.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此样式"
        )
    
    return style


@router.post("", response_model=StyleResponse, status_code=status.HTTP_201_CREATED)
async def create_style(
    style_data: StyleCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Style:
    """创建自定义样式
    
    Args:
        style_data: 样式数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        创建的样式
    """
    new_style = Style(
        name=style_data.name,
        description=style_data.description,
        prompt_instruction=style_data.prompt_instruction,
        css_content=style_data.css_content,
        is_system=False,
        user_id=current_user.id,
        version=1,
        preview_image=style_data.preview_image,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_style)
    await session.commit()
    await session.refresh(new_style)
    
    logger.info(f"用户 {current_user.username} 创建样式: {new_style.name}")
    
    return new_style


@router.put("/{style_id}", response_model=StyleResponse)
async def update_style(
    style_id: int,
    style_data: StyleUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Style:
    """更新自定义样式
    
    Args:
        style_id: 样式ID
        style_data: 更新的样式数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        更新后的样式
    """
    result = await session.execute(
        select(Style).where(Style.id == style_id)
    )
    style = result.scalar_one_or_none()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="样式不存在"
        )
    
    # 检查权限(只能更新自己的样式)
    if style.is_system or style.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此样式"
        )
    
    # 更新字段
    if style_data.name is not None:
        style.name = style_data.name
    if style_data.description is not None:
        style.description = style_data.description
    if style_data.prompt_instruction is not None:
        style.prompt_instruction = style_data.prompt_instruction
    if style_data.css_content is not None:
        style.css_content = style_data.css_content
        style.version += 1  # 增加版本号
    if style_data.preview_image is not None:
        style.preview_image = style_data.preview_image
    
    style.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(style)
    
    logger.info(f"用户 {current_user.username} 更新样式: {style.name}")
    
    return style


@router.delete("/{style_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style(
    style_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """删除自定义样式
    
    Args:
        style_id: 样式ID
        current_user: 当前用户
        session: 数据库会话
    """
    result = await session.execute(
        select(Style).where(Style.id == style_id)
    )
    style = result.scalar_one_or_none()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="样式不存在"
        )
    
    # 检查权限(只能删除自己的样式)
    if style.is_system or style.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此样式"
        )
    
    await session.delete(style)
    await session.commit()
    
    logger.info(f"用户 {current_user.username} 删除样式: {style.name}")
