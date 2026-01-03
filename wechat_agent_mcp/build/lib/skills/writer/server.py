import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from typing import List
from openai import AsyncOpenAI
from config import settings

mcp = FastMCP("Writer Skill")

# 初始化 OpenAI 客户端
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

@mcp.tool()
async def generate_outline(research_summary: str) -> str:
    """基于研究简报生成文章大纲"""
    if not settings.OPENAI_API_KEY:
        return "# 示例大纲 (请配置 API Key)\n## 引言\n## 核心章节\n## 结论"

    prompt = f"你是一位资深的公众号主编。请根据以下研究素材，策划一篇深度文章的大纲：\n\n{research_summary}"
    
    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": "你是一个专业的文案策划专家，擅长创作公众号爆款大纲。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@mcp.tool()
async def write_content(outline: str, style: str = "专业") -> str:
    """基于大纲撰写正文"""
    if not settings.OPENAI_API_KEY:
        return f"这是基于大纲生成的全文内容（请配置 API Key 以启用真实写作）"

    prompt = f"请根据以下大纲，以{style}的风格撰写一篇完整的公众号文章。要求：逻辑清晰，金句频出，字数在1500字左右：\n\n{outline}"
    
    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": f"你是一个擅长{style}写作风格的内容创作者。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    mcp.run()
