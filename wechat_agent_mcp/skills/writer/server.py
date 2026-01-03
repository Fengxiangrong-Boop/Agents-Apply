import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from typing import List
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from config import settings

mcp = FastMCP("Writer Skill")

# 初始化 OpenAI 客户端
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    timeout=180.0 # 设置 3 分钟超时，防止无限卡死
)

@mcp.tool()
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def generate_outline(research_summary: str, style_guide: str = "") -> str:
    """根据研究摘要生成文章大纲，并包含爆款标题方案"""
    sys.stderr.write("[Writer] 正在生成大纲与爆款标题...\n")
    sys.stderr.flush()
    
    system_prompt = "你是一个深谙人性弱点和流量密码的公众号主编。"
    if style_guide:
        system_prompt += f"\n\n请参考以下风格指南的【标题法则】进行创作：\n{style_guide}"

    prompt = f"""
    基于以下研究资料生成文章大纲：
    {research_summary}
    
    特别指令：
    1. 先生成 5 个吸引眼球的**爆款标题**（结合悬念、情绪、实用性）。
    2. 从中选择**最棒的一个**作为最终标题。
    3. 输出格式要求（必须是纯 JSON，不要包含 Markdown 代码块）：
       {{
         "title": "这里是大写的爆款标题",
         "outline": "这里是 Markdown 格式的大纲内容..."
       }}
    """
    
    if not settings.OPENAI_API_KEY:
        return "# 示例大纲 (请配置 API Key)\n## 引言\n## 核心章节\n## 结论"

    try:
        completion = await client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f'{{"error": "{e}", "title": "Error generating title", "outline": "Error generating outline"}}'

@mcp.tool()
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def write_content(outline: str, style_guide: str = "") -> str:
    """基于大纲撰写正文"""
    sys.stderr.write("[Writer] 正在撰写正文...\n")
    sys.stderr.flush()
    
    if not settings.OPENAI_API_KEY:
        return f"这是基于大纲生成的全文内容（请配置 API Key 以启用真实写作）"

    system_prompt = "你是一个专业的内容创作者。"
    
    # --- DE-AI RULES (去除 AI 味 / 人性化指令) ---
    DE_AI_RULES = """
    【🚨 最高指令：必须去除“AI味”！(Must Sound Human)】
    1. **拒绝“教科书式/大模型式”结构**：
       - 严禁使用“首先、其次、最后、综上所述、总而言之、值得注意的是”这些连接词。
       - 严禁使用“随着...的发展”、“在...背景下”作为开头。
       - 严禁“端水大师”式的平衡论述。要有爱憎，有偏向。
    2. **使用“人话”和“口语”**：
       - 把读者当朋友聊天，用“你”、“我”、“咱们”。
       - 多用短句（7-15字）。每段不要超过3行。
       - 允许适当的“情绪化”表达（如：吐槽、感叹、反问）。
       - 必须使用第一人称“我”来讲述，假装你亲自体验过。
    3. **拒绝“正确的废话”**：
       - 不要四平八稳。每一段必须有独特的观点或信息增量。
       - 只要结论，不要推导过程。
    4. **强制“具体的真实感” (The Specifics Rule)**：
       - **必须使用研究资料中的具体数字、具体型号、具体缺点**。
       - ❌ 错误：用户体验不佳。
       - ✅ 正确：它是塑料背壳，摸起来像十年前的诺基亚。
       - ❌ 错误：性能提升有限。
       - ✅ 正确：同样的王者荣耀，它居然比三年前的旧手机还慢了2帧。
    """
    
    if style_guide:
        system_prompt += f"\n\n请严格参考以下写作风格指南（重点执行【语气与修辞】、【多媒体规范】，但必须用【真实人类口吻】来写）：\n{style_guide}"
    
    system_prompt += f"\n\n{DE_AI_RULES}"

    prompt = f"""
    请根据以下大纲撰写一篇完整的公众号文章：
    
    {outline}
    
    要求：
    1. **完全遵循风格指南**：如果指南要求小白友好、幽默或特定排版，必须执行。
    2. **结构要求**：
       - **开头 (Hook)**：必须用一个具体的**小故事**或**直接的吐槽**开场。禁止先讲大道理。
       - **正文**：严格对应大纲，但要把大纲里的“论点”变成“故事”或“实测体验”。
    3. **多媒体元素**：
       - **配图（重要）**：文章核心逻辑处必须插入配图。格式必须严格为：`[[IMG: 画面描述]]`。
       - **超链接**：关键名词必须加 Markdown 超链接。
    4. **引用来源（Critical）**：
       - 请查看大纲附带的 `Reference Material` 中的【🔍 真实吐槽与数据】部分。
       - **你必须在文章中引用至少 2 个具体的真实吐槽或评测数据**，让文章看起来像是真的做过功课。
       - 严禁编造链接，必须使用参考资料中提供的 URL。
    """

    try:
        completion = await client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"撰写失败: {e}"

if __name__ == "__main__":
    mcp.run()
