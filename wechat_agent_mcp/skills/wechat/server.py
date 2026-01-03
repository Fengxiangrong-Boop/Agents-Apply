import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import httpx
from io import BytesIO
from PIL import Image
import markdown
import re
from config import settings
from tenacity import retry, stop_after_attempt, wait_random_exponential

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
            err_msg = f"微信 API 报错: {data.get('errcode')} - {data.get('errmsg')}"
            sys.stderr.write(f"[Error] 获取 Token 失败: {err_msg}\n")
            return f"ERROR: {err_msg}"

@mcp.tool()
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def upload_image(image_url: str, media_type: str = "image") -> Dict[str, Any]:
    """通过 URL 下载图片并上传至微信素材库 (优先使用临时素材接口以兼容测试号)"""
    sys.stderr.write(f"[WeChat] 正在准备上传{media_type}素材: {image_url}\n")
    
    token = await _get_access_token()
    if token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "mock_success", "media_id": f"mock_{media_type}_id_456"}
    
    if token.startswith("ERROR:"):
        return {"status": "error", "message": token}

    # 1. 下载图片
    try:
        async with httpx.AsyncClient() as client:
            img_res = await client.get(image_url, timeout=20.0)
            img_res.raise_for_status()
            img_data = img_res.content
            filename = os.path.basename(image_url.split("?")[0]) or "upload_file.jpg"
            if "." not in filename: filename += ".jpg"
            
            # 针对 thumb 类型进行强制压缩 (微信限制 64KB)
            if media_type == "thumb":
                try:
                    img = Image.open(BytesIO(img_data))
                    # 转换为 RGB 兼容 JPEG
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 调整尺寸，缩略图不需要太大
                    img.thumbnail((512, 512))
                    
                    # 循环压缩直到小于 64KB
                    quality = 85
                    while True:
                        output_buffer = BytesIO()
                        img.save(output_buffer, format="JPEG", quality=quality)
                        img_data = output_buffer.getvalue()
                        size_kb = len(img_data) / 1024
                        
                        if size_kb < 60 or quality <= 10: # 留点余量 60KB
                            sys.stderr.write(f"[WeChat] 封面图已压缩至 {size_kb:.2f}KB (Quality: {quality})\n")
                            break
                        
                        quality -= 10
                    
                    filename = "thumb_cover.jpg" # 强制改名确保格式正确
                except Exception as e:
                    sys.stderr.write(f"[Warning] 图片压缩失败: {e}，将尝试直接上传\n")

    except Exception as e:
        return {"status": "error", "message": f"下载图片失败: {e}"}

    # 2. 上传至微信
    # 策略调整：
    # - thumb (封面): 必须使用【永久素材】接口 (material/add_material)，否则 draft/add 会报 invalid media_id
    # - image (其他): 使用临时素材接口 (media/upload) 即可
    
    if media_type == "thumb":
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        files = {
            "media": (filename, img_data, "image/jpeg")
        }
    else:
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type={media_type}"
        files = {
            "media": (filename, img_data, "image/jpeg")
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=30.0)
            data = response.json()
            # 临时素材接口返回 media_id 或 thumb_media_id (如果是 thumb 类型)
            res_id = data.get("media_id") or data.get("thumb_media_id")
            if res_id:
                sys.stderr.write(f"[Success] {media_type}素材上传成功: {res_id}\n")
                return {"status": "success", "media_id": res_id}
            else:
                err_msg = data.get("errmsg", "素材上传失败")
                sys.stderr.write(f"[Error] 微信返回错误: {data}\n")
                return {"status": "error", "message": err_msg}
    except Exception as e:
        return {"status": "error", "message": f"连接微信服务器失败: {e}"}

@mcp.tool()
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def upload_article_image(image_url: str) -> Dict[str, Any]:
    """上传正文图片并返回可在 HTML 中使用的 CDN URL"""
    sys.stderr.write(f"[WeChat] 正在上传正文图片获取 CDN URL: {image_url}\n")
    
    token = await _get_access_token()
    if token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "mock_success", "url": image_url}
    
    if token.startswith("ERROR:"):
        return {"status": "error", "message": token}

    try:
        async with httpx.AsyncClient() as client:
            img_res = await client.get(image_url, timeout=20.0)
            img_res.raise_for_status()
            img_data = img_res.content
            filename = os.path.basename(image_url.split("?")[0]) or "image.jpg"
    except Exception as e:
        return {"status": "error", "message": f"下载图片失败: {e}"}

    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    files = {"media": (filename, img_data, "image/jpeg")}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=30.0)
            data = response.json()
            if "url" in data:
                return {"status": "success", "url": data["url"]}
            else:
                return {"status": "error", "message": data.get("errmsg", "上传文章图片失败")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def markdown_to_wechat_html(markdown_text: str) -> str:
    """将 Markdown 转换为带样式的微信 HTML"""
    # 基础转换 (移除 codehilite，防止生成不兼容的 class)
    html_content = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
    
    # 使用更稳健的正则替换
    def r(tag, style):
        nonlocal html_content
        # 匹配标签及其现有属性，通过 style 属性注入
        pattern = re.compile(rf'<{tag}(\s+[^>]*)?>', re.IGNORECASE)
        html_content = pattern.sub(rf'<{tag} style="{style}" \1>', html_content)

    r('h2', 'font-size: 20px; font-weight: bold; color: #000; margin: 30px 0 15px 0; line-height: 1.5;')
    r('h3', 'font-size: 18px; font-weight: bold; color: #333; margin: 25px 0 12px 0;')
    r('p', 'margin-bottom: 20px; line-height: 1.8; color: #3f3f3f; text-align: justify;')
    r('ul', 'margin-bottom: 20px; padding-left: 20px;')
    r('ol', 'margin-bottom: 20px; padding-left: 20px;')
    r('li', 'margin-bottom: 8px; line-height: 1.6;')
    r('blockquote', 'background: #f6f7f8; border-left: 4px solid #ddd; padding: 15px; margin: 20px 0; color: #666;')
    r('strong', 'font-weight: bold; color: #000;')
    r('hr', 'border: 0; border-top: 1px solid #eee; margin: 30px 0;')
    
    # 链接处理 (避免重复注入 style)
    html_content = re.sub(r'<a\s+(?!style=)href=', r'<a style="color: #576b95; text-decoration: none;" href=', html_content, flags=re.IGNORECASE)

    # 移除 H1 (如果存在)
    html_content = re.sub(r'<h1.*?>.*?</h1>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

    final_html = f"""
    <section style="font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif; font-size: 16px; color: #333; line-height: 1.75;">
        {html_content}
    </section>
    """
    
    return final_html

@mcp.tool()
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def upload_draft(title: str, content: str, thumb_media_id: str) -> Dict[str, Any]:
    """将文章上传至公众号草稿箱"""
    sys.stderr.write(f"[WeChat] 正在上传草稿: {title}...\n")
    
    token = await _get_access_token()
    if token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "mock_success", "message": "微信配置未完成，已模拟上传", "media_id": "mock_media_id_123"}
    
    if token.startswith("ERROR:"):
        return {"status": "error", "message": token}

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
            sys.stderr.write(f"[Success] 草稿上传成功: {data['media_id']}\n")
            return {"status": "success", "media_id": data["media_id"]}
        else:
            sys.stderr.write(f"[Error] 上传失败: {data}\n")
            return {"status": "error", "message": data.get("errmsg", "未知错误")}

@mcp.tool()
async def get_draft_list(count: int = 10) -> Dict[str, Any]:
    """获取草稿箱列表，用于验证测试号上传结果"""
    sys.stderr.write(f"[WeChat] 正在获取最近 {count} 篇草稿...\n")
    
    token = await _get_access_token()
    if not token or token == "MOCK_TOKEN_UNCONFIGURED":
        return {"status": "error", "message": "未配置正式微信凭证，无法获取列表"}

    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    payload = {
        "offset": 0,
        "count": count,
        "no_content": 1 # 不返回正文以节省流量
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=20.0)
            return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def get_access_token(app_id: str, app_secret: str) -> str:
    """获取微信 Access Token (公开工具)"""
    return await _get_access_token()

if __name__ == "__main__":
    mcp.run()
