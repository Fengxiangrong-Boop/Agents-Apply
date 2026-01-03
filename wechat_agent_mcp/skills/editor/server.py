import sys
import os
import re
import json
import random

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from config import settings

mcp = FastMCP("Editor Skill")

# 音乐库现已迁移至 config.py

@mcp.tool()
async def extract_image_prompts(markdown_text: str) -> str:
    """
    从 Markdown 文本中提取所有 [[IMG: description]] 占位符
    返回 JSON 格式的列表: [{"index": 0, "prompt": "..."}]
    """
    # 兼容中文冒号和英文冒号
    matches = re.findall(r'\[\[IMG[:：](.*?)\]\]', markdown_text)
    results = []
    for i, match in enumerate(matches):
        results.append({
            "index": i,
            "prompt": match.strip()
        })
    return json.dumps(results, ensure_ascii=False)

@mcp.tool()
async def inject_images(markdown_text: str, images_data: str) -> str:
    """
    将生成的图片 URL 回填到 Markdown 文本中
    images_data 格式: [{"prompt": "...", "url": "..."}] (JSON string)
    """
    try:
        images = json.loads(images_data)
        final_text = markdown_text
        
        for img in images:
            prompt = img.get("prompt", "")
            url = img.get("url", "")
            if not prompt or not url:
                continue
                
            # 构建微信图片 HTML
            # 简化样式，移除可能冲突的阴影
            img_html = (
                f'\n<img src="{url}" '
                'style="width: 100%; border-radius: 8px; margin: 15px 0; display: block;" />\n'
            )
            
            # 策略：使用 Regex 进行模糊匹配，忽略冒号后的空格差异
            # 模式：[[IMG (中文或英文冒号) \s* prompt \s* ]]
            # 注意 regex 转义
            import re
            
            # 由于 prompt 可能包含 regex 特殊字符，先进行 escape
            safe_prompt = re.escape(prompt)
            
            # 构建正则：支持中英文冒号，支持冒号前后空格
            pattern = re.compile(r"\[\[IMG[:：]\s*" + safe_prompt + r"\s*\]\]", re.IGNORECASE)
            
            # 执行替换 (全部替换)
            final_text = pattern.sub(img_html, final_text)
            
            # 二次检查：如果没替换成功，打印警告
            if pattern.search(markdown_text) and not pattern.search(final_text):
                 pass # Success
            elif pattern.search(markdown_text):
                 sys.stderr.write(f"[Editor] Replacement check failed for: {prompt}\n")

        return final_text
    except Exception as e:
        sys.stderr.write(f"[Editor] Error injecting images: {e}\n")
        return markdown_text

@mcp.tool()
async def recommend_music(article_title: str, article_content: str) -> str:
    """
    根据文章标题和内容推荐背景音乐
    返回 JSON: {"name": "...", "singer": "...", "listenid": "...", "xml": "..."}
    """
    # 简单的关键词匹配逻辑 (后续可升级为 LLM 情感分析)
    content_lower = (article_title + article_content).lower()
    
    content_lower = (article_title + article_content).lower()
    
    selected_music = settings.MUSIC_PLAYLIST[0] # 默认
    
    if any(k in content_lower for k in ["未来", "cyber", "赛博", "快"]):
        selected_music = next((m for m in settings.MUSIC_PLAYLIST if "cyberpunk" in m["tags"]), settings.MUSIC_PLAYLIST[0])
    elif any(k in content_lower for k in ["学习", "教程", "笔记", "guide"]):
        selected_music = next((m for m in settings.MUSIC_PLAYLIST if "study" in m["tags"]), settings.MUSIC_PLAYLIST[0])
    elif any(k in content_lower for k in ["轻松", "摸鱼", "休息"]):
        selected_music = next((m for m in settings.MUSIC_PLAYLIST if "relax" in m["tags"]), settings.MUSIC_PLAYLIST[0])
        
    sys.stderr.write(f"[Editor] 推荐音乐: {selected_music['name']} (匹配标签)\n")
    
    # 构建微信音乐 XML (虽然现在都用卡片，但为了兼容性保留 XML 结构或 meta 数据)
    music_xml = f'''<mp-common-clmusic 
        class="res_iframe clmusic_iframe js_uneditable custom_select_card mp_common_widget js_wx_tap_highlight" 
        data-pluginname="insertaudio" 
        type="1" 
        music_name="{selected_music['name']}" 
        albumurl="{selected_music['album_url']}" 
        singer="{selected_music['singer']}" 
        count="0" 
        is_vip="0" 
        duration="203" 
        music_source="1" 
        style="visibility: visible; margin-bottom: 20px;" 
        posindex="0" 
        listenid="{selected_music['listenid']}">
    </mp-common-clmusic>'''
    
    result = selected_music.copy()
    result["xml"] = music_xml
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def assemble_html(article_html: str, cover_url: str, music_xml: str) -> str:
    """
    组装最终的微信文章 HTML
    顺序：音乐 -> 封面图 -> 正文
    """
    # 封面图 HTML
    cover_html = f'<img src="{cover_url}" style="width: 100%; border-radius: 8px; margin-bottom: 15px; display: block;" />'
    
    # 最终拼接 (暂时移除 music_xml 以调试 invalid content 问题)
    final_content = f"{cover_html}\n{article_html}"
    return final_content

if __name__ == "__main__":
    mcp.run()
