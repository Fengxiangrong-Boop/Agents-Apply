import sys
import os
# 将项目根目录添加到 python 路径，确保可以导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI
import httpx
from config import settings

mcp = FastMCP("Media Skill")

# 初始化 OpenAI 客户端
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# 初始化绘图专用客户端 (SiliconFlow)
# 注意：如果未配置 SILICONFLOW_API_KEY，且 IMAGE_API_BASE 是默认的 siliconflow，则尝试使用 OPENAI_API_KEY (为了兼容)
image_api_key = settings.SILICONFLOW_API_KEY or settings.OPENAI_API_KEY
image_client = AsyncOpenAI(
    api_key=image_api_key,
    base_url=settings.IMAGE_API_BASE
)

@mcp.tool()
async def generate_article_image(prompt: str, model_override: str = "") -> str:
    """根据描述生成文章配图"""
    # 优先使用覆盖值，其次使用专用的图片模型配置，最后回退
    target_model = model_override or settings.IMAGE_MODEL_NAME or settings.MODEL_NAME
    
    # 如果没配置或还是 gpt 类型模型，则回退到默认文生图模型
    if not target_model or "gpt" in target_model.lower():
        target_model = "dall-e-3"

        target_model = "dall-e-3"

    sys.stderr.write(f"[Media] 正在请求 [{target_model}] 生成图片，原始提示词: {prompt}...\n")
    
    # 1. 调用 LLM 优化提示词 (Prompt Optimizer)
    # 目的：将中文意向转化为 DALL-E 易理解的英文指令，并强制约束文字类型
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", # 使用高智商模型进行指令翻译
            messages=[
                {"role": "system", "content": (
                    "You are a Flux.1 prompt expert. Rewrite the user's image description into a precise English prompt.\n"
                    "Target Model: Flux.1-schnell (Excellent at photorealism and text rendering).\n"
                    "Style: High-end Tech Illustration, 3D Isometric, Soft Lighting, Clay Render texture.\n"
                    "Rules:\n"
                    "1. TRANSLATE EVERYTHING TO ENGLISH. Ensure the final prompt is 100% English.\n"
                    "2. If specific text is requested, wrap it in double quotes (e.g. text 'AI'). Flux can render text perfectly.\n"
                    "3. If the input contains Chinese titles or concepts, translate them to accurate English technical descriptions.\n"
                    "4. ABSOLUTELY NO CHINESE CHARACTERS in the output.\n"
                    "5. DRACONIAN RULE: NO TEXT, NO DIAGRAMS, NO INFOGRAPHICS, NO CHARTS. If the input asks for a 'diagram' or 'structure', YOU MUST CONVERT IT into a PHYSICAL OBJECT (e.g. a machine, a building, a tool) or a CINEMATIC SCENE.\n"
                    "6. ADAPTIVE STYLE: \n"
                    "   - Analyze the mood of the prompt.\n"
                    "   - IF 'Fun/Easy/Intro': Use 'Claymorphism, Soft Lighting, Cute 3D'.\n"
                    "   - IF 'Business/Serious': Use 'Minimalist Product Photography, High Key Lighting, Clean Background'.\n"
                    "   - IF 'Literature/Books/Culture/Emotion': Use 'Cinematic Film Photography, Warm Tone, Soft Focus, Aesthetic composition (文艺风)'.\n"
                    "   - IF 'Creative/Art/Design': Use 'Paper Cutout Art (Origami), Mixed Media, Vibrant Colors'.\n"
                    "   - IF 'Hard Tech/Coding/Programming/AI': Use 'Swiss Design Style, Bauhaus Geometric, Clean White Background, Engineering Blueprint'.\n"
                    "   - DEFAULT: 'Minimalist 3D Render'.\n"
                    "Output ONLY the prompt text, but you can think before outputting to ensure quality."
                )},
                {"role": "user", "content": prompt}
            ],
            timeout=30.0
        )
        enhanced_prompt = completion.choices[0].message.content
        sys.stderr.write(f"[Media] 提示词已优化: {enhanced_prompt}\n")
    except Exception as e:
        sys.stderr.write(f"[Warning] 提示词优化失败: {e}，将使用回退规则\n")
        # 回退到简单的字符串拼接规则
        enhanced_prompt = (
            f"{prompt} -- "
            "Style: 3D Isometric Illustration, Clay Render, High-end Tech Blog Style. "
            "TEXT RULE: English Technical Terms ONLY. NO Chinese."
        )
    
    try:
        # 使用 image_client 调用 Flux 模型
        response = await image_client.images.generate(
            model=target_model,
            prompt=enhanced_prompt,
            size="1024x576", # Flux 16:9 Cinematic Ratio
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        sys.stderr.write(f"[Success] 图片生成成功 ({target_model}): {image_url}\n")
        return image_url
    except Exception as e:
        sys.stderr.write(f"[Error] 图片生成失败: {e}\n")
        return f"https://picsum.photos/seed/error/800/600"

        return f"https://picsum.photos/seed/error/800/600"

@mcp.tool()
async def search_article_image(prompt: str) -> str:
    """
    根据描述搜索网络图片 (替代生成)
    1. LLM 提取搜索关键词
    2. Tavily 搜索图片
    """
    sys.stderr.write(f"[Media] 正在网络搜索图片，原始描述: {prompt}...\n")
    
    # 1. 提取关键词
    try:
        kw_completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract 2-3 most important visual search keywords from the description to find a real photo. English Only. Output ONE line of keywords."},
                {"role": "user", "content": prompt}
            ]
        )
        search_query = kw_completion.choices[0].message.content.strip()
        sys.stderr.write(f"[Media] 搜索关键词: {search_query}\n")
    except:
        search_query = prompt[:20]

    # 2. 调用 Tavily 搜索图片
    if not settings.SEARCH_API_KEY:
        sys.stderr.write("[Warning] 未配置 SEARCH_API_KEY，返回占位图\n")
        return "https://picsum.photos/seed/no-key/800/600"

    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.SEARCH_API_KEY,
                    "query": search_query,
                    "search_depth": "basic",
                    "include_images": True,
                    "include_answer": False,
                    "max_results": 3
                },
                timeout=15.0
            )
            data = response.json()
            images = data.get("images", [])
            
            # 过滤不可用/防盗链的域名
            valid_images = [
                url for url in images 
                if not any(x in url for x in ["tiktok.com", "instagram.com", "facebook.com", "pinterest.com"])
            ]
            
            if valid_images:
                img_url = valid_images[0] # 取第一张可用
                sys.stderr.write(f"[Success] 搜索到图片: {img_url}\n")
                return img_url
            else:
                sys.stderr.write("[Warning] 未搜索到图片，返回随机图\n")
                return "https://picsum.photos/seed/not-found/800/600"
    except Exception as e:
        sys.stderr.write(f"[Error] 图片搜索失败: {e}\n")
        return "https://picsum.photos/seed/error/800/600"

@mcp.tool()
async def optimize_image_size(image_url: str) -> str:
    """优化图片大小以符合公众号限制 (预留)"""
    return image_url

if __name__ == "__main__":
    mcp.run()
