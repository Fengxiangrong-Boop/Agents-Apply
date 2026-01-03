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
    """搜索特定主题的背景资料和热门观点，包含具体数据"""
    if not settings.SEARCH_API_KEY:
        sys.stderr.write(f"[Warning] 未配置 SEARCH_API_KEY，返回关于 '{topic}' 的模拟研究简报...\n")
        return f"关于 '{topic}' 的模拟研究简报：\n1. 这是一个受关注的领域... \n2. 发展迅速... \n3. 具有巨大潜力。"

    async with httpx.AsyncClient() as client:
        # 1. 宏观搜索 (General Context)
        sys.stderr.write(f"[Research] 阶段 1: 宏观搜索 '{topic}'...\n")
        general_results = []
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.SEARCH_API_KEY,
                    "query": topic,
                    "search_depth": "advanced",
                    "max_results": 4
                },
                timeout=30.0
            )
            response.raise_for_status()
            general_results = response.json().get("results", [])
        except Exception as e:
            sys.stderr.write(f"[Error] 宏观搜索失败: {e}\n")

        # 2. 微观数据/吐槽搜索 (Specific Data/Rants)
        # 搜索具体的评论、吐槽、评测数据，以获取"真实感"
        specific_query = f"{topic} 真实体验 吐槽 缺点 评测数据"
        sys.stderr.write(f"[Research] 阶段 2: 微观搜索 '{specific_query}'...\n")
        specific_results = []
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.SEARCH_API_KEY,
                    "query": specific_query,
                    "search_depth": "advanced",
                    "max_results": 4
                },
                timeout=30.0
            )
            response.raise_for_status()
            specific_results = response.json().get("results", [])
        except Exception as e:
            sys.stderr.write(f"[Error] 微观搜索失败: {e}\n")

        # 3. 结果组装
        summary_lines = []
        
        summary_lines.append(f"### 🌐 宏观背景 (General Context)")
        for r in general_results:
            summary_lines.append(f"- {r['title']}: {r['content'][:200]}...")

        summary_lines.append(f"\n### 🔍 真实吐槽与数据 (Real World Evidence)")
        for r in specific_results:
            summary_lines.append(f"- {r['title']} (Source: {r['url']}):\n  摘要: {r['content'][:250]}")
            
        references = "\n\n### 🔗 参考文献 (References for Citation):\n" 
        all_results = general_results + specific_results
        # 去重
        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r['url'] not in seen_urls:
                unique_results.append(r)
                seen_urls.add(r['url'])
                
        references += "\n".join([f"- [{r['title']}]({r['url']})" for r in unique_results])
        
        return "\n".join(summary_lines) + references

@mcp.tool()
async def analyze_trends(topic: str) -> List[str]:
    """分析该主题下的子选题和趋势关键词"""
    # 简单分析逻辑，后续可接入 LLM 进一步提炼
    return [f"{topic} 最新趋势", f"{topic} 深度解析", f"{topic} 技术选型"]

if __name__ == "__main__":
    mcp.run()
