"""API Key管理API"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import get_current_active_user
from app.core.db import get_session
from app.core.logging import logger
from app.core.security import encrypt_sensitive_data
from app.models.user import User
from app.models.user_api_key import UserApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate
from app.services.mcp_service import MCPService

router = APIRouter(prefix="/api-keys", tags=["API Key管理"])


@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> UserApiKey:
    """创建/配置API Key
    
    Args:
        api_key_data: API Key数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        创建的API Key配置
    """
    # 检查是否已存在
    result = await session.execute(
        select(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    existing_key = result.scalar_one_or_none()
    
    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key已存在,请使用更新接口"
        )
    
    # 加密API Key
    api_key_encrypted = encrypt_sensitive_data(api_key_data.api_key)
    
    # 验证API Key
    try:
        mcp_service = MCPService(api_key_encrypted)
        is_valid = await mcp_service.validate_api_key()
    except Exception as e:
        logger.error(f"API Key验证失败: {e}")
        is_valid = False
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key无效,请检查后重试"
        )
    
    # 创建配置
    new_key = UserApiKey(
        user_id=current_user.id,
        provider=api_key_data.provider,
        api_key_encrypted=api_key_encrypted,
        is_valid=True,
        last_validated_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_key)
    await session.commit()
    await session.refresh(new_key)
    
    logger.info(f"用户 {current_user.username} 配置API Key成功")
    
    return new_key


@router.get("", response_model=ApiKeyResponse)
async def get_api_key(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> UserApiKey:
    """获取API Key配置
    
    Args:
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        API Key配置
    """
    result = await session.execute(
        select(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key配置不存在"
        )
    
    return api_key


@router.put("", response_model=ApiKeyResponse)
async def update_api_key(
    api_key_data: ApiKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> UserApiKey:
    """更新API Key
    
    Args:
        api_key_data: 新的API Key数据
        current_user: 当前用户
        session: 数据库会话
        
    Returns:
        更新后的API Key配置
    """
    result = await session.execute(
        select(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key配置不存在"
        )
    
    # 加密新的API Key
    api_key_encrypted = encrypt_sensitive_data(api_key_data.api_key)
    
    # 验证新的API Key
    try:
        mcp_service = MCPService(api_key_encrypted)
        is_valid = await mcp_service.validate_api_key()
    except Exception as e:
        logger.error(f"API Key验证失败: {e}")
        is_valid = False
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新的API Key无效,请检查后重试"
        )
    
    # 更新
    api_key.api_key_encrypted = api_key_encrypted
    api_key.is_valid = True
    api_key.last_validated_at = datetime.utcnow()
    api_key.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(api_key)
    
    logger.info(f"用户 {current_user.username} 更新API Key成功")
    
    return api_key


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """删除API Key配置
    
    Args:
        current_user: 当前用户
        session: 数据库会话
    """
    result = await session.execute(
        select(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key配置不存在"
        )
    
    await session.delete(api_key)
    await session.commit()
    
    logger.info(f"用户 {current_user.username} 删除API Key成功")
