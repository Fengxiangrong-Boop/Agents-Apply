"""健康检查API测试"""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查接口"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """测试根路径"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
