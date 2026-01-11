"""用户管理API"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """获取当前用户信息
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        当前用户信息
    """
    return current_user
