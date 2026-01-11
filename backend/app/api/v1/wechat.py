"""微信配置API"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import get_current_active_user
from app.core.db import get_session
from app.core.logging import logger
from app.core.security import encrypt_sensitive_data
from app.models.user import User
from app.models.wechat_config import WechatConfig
from app.schemas.wechat import WechatConfigCreate, WechatConfigResponse, WechatConfigUpdate

router = APIRouter(prefix="/wechat", tags=["微信配置"])


@router.post("/config", response_model=WechatConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_wechat_config(
    config_data: WechatConfigCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> WechatConfig:
    """创建微信配置
    
    Args:
        config_data: 微信配置数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        创建的微信配置
    """
    # 检查是否已存在配置
    result = await session.execute(
        select(WechatConfig).where(WechatConfig.user_id == current_user.id)
    )
    existing_config = result.scalar_one_or_none()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信配置已存在,请使用更新接口"
        )
    
    # 加密AppSecret
    app_secret_encrypted = encrypt_sensitive_data(config_data.app_secret)
    
    # 创建配置
    new_config = WechatConfig(
        user_id=current_user.id,
        app_id=config_data.app_id,
        app_secret_encrypted=app_secret_encrypted,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_config)
    await session.commit()
    await session.refresh(new_config)
    
    logger.info(f"用户 {current_user.username} 创建微信配置成功")
    
    return new_config


@router.get("/config", response_model=WechatConfigResponse)
async def get_wechat_config(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> WechatConfig:
    """获取微信配置
    
    Args:
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        微信配置
    """
    result = await session.execute(
        select(WechatConfig).where(WechatConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="微信配置不存在"
        )
    
    return config


@router.put("/config", response_model=WechatConfigResponse)
async def update_wechat_config(
    config_data: WechatConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> WechatConfig:
    """更新微信配置
    
    Args:
        config_data: 更新的配置数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        更新后的微信配置
    """
    result = await session.execute(
        select(WechatConfig).where(WechatConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="微信配置不存在"
        )
    
    # 更新字段
    if config_data.app_id is not None:
        config.app_id = config_data.app_id
    
    if config_data.app_secret is not None:
        config.app_secret_encrypted = encrypt_sensitive_data(config_data.app_secret)
        # 清除旧Token
        config.access_token = None
        config.token_expires_at = None
    
    config.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(config)
    
    logger.info(f"用户 {current_user.username} 更新微信配置成功")
    
    return config


@router.delete("/config", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wechat_config(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """删除微信配置
    
    Args:
        current_user: 当前用户
        session: 数据库会话
    """
    result = await session.execute(
        select(WechatConfig).where(WechatConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="微信配置不存在"
        )
    
    await session.delete(config)
    await session.commit()
    
    logger.info(f"用户 {current_user.username} 删除微信配置成功")
