"""测试用例示例 - 用户认证API"""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_user():
    """测试用户注册"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data


@pytest.mark.asyncio
async def test_login_user():
    """测试用户登录"""
    # 先注册用户
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        
        # 登录
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """测试错误的登录凭证"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "wrongpass"
            }
        )
        
        assert response.status_code == 401
