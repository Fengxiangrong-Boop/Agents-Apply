import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from typing import List
import httpx
from config import settings

mcp = FastMCP("Research Skill")

@mcp.tool()
async def search_topic(topic: str) -> str:
    """搜索特定主题的背景资料和热门观点"""
    if not settings.SEARCH_API_KEY:
        print(f"⚠️ 未配置 SEARCH_API_KEY，返回关于 '{topic}' 的模拟研究简报...")
        return f"关于 '{topic}' 的模拟研究简报：\n1. 这是一个受关注的领域... \n2. 发展迅速... \n3. 具有巨大潜力。"

    print(f"🚀 正在调用 Tavily 搜索 API 检索主题: {topic}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.SEARCH_API_KEY,
                    "query": topic,
                    "search_depth": "advanced",
                    "max_results": 5
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            summary = "\n".join([f"- {r['title']}: {r['content'][:200]}..." for r in results])
            return f"关于 '{topic}' 的互联网研究简报：\n{summary}"
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return f"搜索过程中出错，仅能提供基础背景：{topic} 相关领域目前发展非常成熟。"

@mcp.tool()
async def analyze_trends(topic: str) -> List[str]:
    """分析该主题下的子选题和趋势关键词"""
    # 简单分析逻辑，后续可接入 LLM 进一步提炼
    return [f"{topic} 最新趋势", f"{topic} 深度解析", f"{topic} 技术选型"]

if __name__ == "__main__":
    mcp.run()
