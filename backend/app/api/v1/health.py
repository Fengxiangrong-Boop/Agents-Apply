"""健康检查API"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("")
async def health_check(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """健康检查接口
    
    检查数据库连接状态
    
    Args:
        session: 数据库会话
        
    Returns:
        健康状态信息
    """
    try:
        # 测试数据库连接
        await session.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception as e:
        database_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if database_status == "ok" else "unhealthy",
        "database": database_status,
    }
