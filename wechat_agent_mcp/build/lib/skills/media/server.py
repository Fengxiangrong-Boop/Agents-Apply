import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI
from config import settings

mcp = FastMCP("Media Skill")

# 初始化 OpenAI 客户端
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

@mcp.tool()
async def generate_article_image(prompt: str, model_override: str = "") -> str:
    """根据描述生成文章配图"""
    # 优先使用覆盖值，其次使用专用的图片模型配置，最后回退
    target_model = model_override or settings.IMAGE_MODEL_NAME or settings.MODEL_NAME
    
    # 如果没配置或还是 gpt 类型模型，则回退到默认文生图模型
    if not target_model or "gpt" in target_model.lower():
        target_model = "dall-e-3"

    print(f"🎨 正在请求 [{target_model}] 生成图片，提示词: {prompt}...")
    
    if not settings.OPENAI_API_KEY:
        print("⚠️ 未配置 API Key，返回模拟图片 URL")
        return f"https://picsum.photos/seed/{hash(prompt)}/800/600"

    try:
        response = await client.images.generate(
            model=target_model,
            prompt=prompt,
            size="1024x1024" if "dall-e" in target_model else "768x1024", # 适配尺寸
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"✅ 图片生成成功: {image_url}")
        return image_url
    except Exception as e:
        print(f"❌ 图片生成失败: {e}")
        return f"https://picsum.photos/seed/error/800/600"

@mcp.tool()
async def optimize_image_size(image_url: str) -> str:
    """优化图片大小以符合公众号限制 (预留)"""
    return image_url

if __name__ == "__main__":
    mcp.run()
