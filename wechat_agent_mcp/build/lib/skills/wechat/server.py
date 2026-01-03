import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import httpx
from config import settings

mcp = FastMCP("WeChat Publisher")

async def _get_access_token() -> str:
    """内部函数：获取微信 Access Token"""
    if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
        return "MOCK_TOKEN_UNCONFIGURED"
    
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        else:
            print(f"❌ 获取 Token 失败: {data}")
            return ""

@mcp.tool()
async def upload_image(image_url: str) -> Dict[str, Any]:
    """通过 URL 下载图片并上传至微信素材库"""
    print(f"🚀 正在准备上传图片素材: {image_url}")
    
    token = await _get_access_token()
    if token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "mock_success", "media_id": "mock_thumb_id_456"}
    
    if not token:
        return {"status": "error", "message": "无法获取 Access Token"}

    # 1. 下载图片
    try:
        async with httpx.AsyncClient() as client:
            img_res = await client.get(image_url, timeout=20.0)
            img_res.raise_for_status()
            img_data = img_res.content
            # 简单获取文件名
            filename = os.path.basename(image_url.split("?")[0]) or "thumb.jpg"
            if "." not in filename: filename += ".jpg"
    except Exception as e:
        return {"status": "error", "message": f"下载图片失败: {e}"}

    # 2. 上传至微信
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    files = {
        "media": (filename, img_data, "image/jpeg")
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=30.0)
            data = response.json()
            if "media_id" in data:
                print(f"✅ 图片素材上传成功: {data['media_id']}")
                return {"status": "success", "media_id": data["media_id"]}
            else:
                return {"status": "error", "message": data.get("errmsg", "素材上传失败")}
    except Exception as e:
        return {"status": "error", "message": f"连接微信服务器失败: {e}"}

@mcp.tool()
async def upload_draft(title: str, content: str, thumb_media_id: str) -> Dict[str, Any]:
    """将文章上传至公众号草稿箱"""
    print(f"🚀 正在上传草稿: {title}...")
    
    token = await _get_access_token()
    if token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "mock_success", "message": "微信配置未完成，已模拟上传", "media_id": "mock_media_id_123"}
    
    if not token:
        return {"status": "error", "message": "无法获取 Access Token"}

    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {
        "articles": [
            {
                "title": title,
                "author": "AI Agent",
                "digest": title,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=20.0)
        data = response.json()
        if "media_id" in data:
            print(f"✅ 草稿上传成功: {data['media_id']}")
            return {"status": "success", "media_id": data["media_id"]}
        else:
            print(f"❌ 上传失败: {data}")
            return {"status": "error", "message": data.get("errmsg", "未知错误")}

@mcp.tool()
async def get_access_token(app_id: str, app_secret: str) -> str:
    """获取微信 Access Token (公开工具)"""
    return await _get_access_token()

if __name__ == "__main__":
    mcp.run()
