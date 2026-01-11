"""依赖项 - 用于路由的通用依赖"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import TokenData

# HTTP Bearer认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """获取当前认证用户
    
    Args:
        credentials: HTTP Bearer凭证
        session: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码JWT令牌
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # 从数据库查询用户
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户(别名,用于语义清晰)
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前活跃用户
    """
    return current_user
