"""数据库连接模块"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# 将postgresql://转换为postgresql+asyncpg://以支持异步
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# 创建异步引擎
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # 连接池预检查
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
)

# 创建异步会话工厂
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_db_and_tables() -> None:
    """创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话
    
    用作FastAPI依赖项,自动管理会话生命周期
    
    Yields:
        数据库会话
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
