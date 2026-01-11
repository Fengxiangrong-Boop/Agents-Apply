"""认证相关API - 注册、登录"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.logging import logger
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    """用户注册
    
    Args:
        user_data: 用户注册数据
        session: 数据库会话
        
    Returns:
        创建的用户对象
        
    Raises:
        HTTPException: 用户名已存在时抛出400错误
    """
    # 检查用户名是否已存在
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    password_hash = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=password_hash,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    logger.info(f"新用户注册成功: {new_user.username} (ID: {new_user.id})")
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """用户登录
    
    Args:
        login_data: 用户登录数据
        session: 数据库会话
        
    Returns:
        JWT访问令牌
        
    Raises:
        HTTPException: 用户名或密码错误时抛出401错误
    """
    # 查询用户
    result = await session.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()
    
    # 验证用户和密码
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用"
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    logger.info(f"用户登录成功: {user.username} (ID: {user.id})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
