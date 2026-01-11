"""FastAPI应用入口"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_keys, article, auth, health, styles, users, wechat
from app.core.config import settings
from app.core.db import create_db_and_tables
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    在应用启动时创建数据库表
    """
    logger.info("应用启动中...")
    await create_db_and_tables()
    logger.info("数据库表已创建/验证")
    yield
    logger.info("应用关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="微信公众号文章智能生成与同步系统 - 后端API",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")
app.include_router(wechat.router, prefix="/api/v1")
app.include_router(styles.router, prefix="/api/v1")
app.include_router(article.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "微信公众号文章智能生成与同步系统 API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
