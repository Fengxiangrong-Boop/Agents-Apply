import asyncio
import sys
import json
import argparse
from typing import List
from core.client import MCPClient

class WeChatAgentOrchestrator:
    """
    公众号写作 Agent 编排器
    通过 MCP 协议调度 Research, Writer, Media, Editor 和 WeChat 技能。
    """
    
    def __init__(self):
        self.client = MCPClient()
        self.skills = {
            "research": ["python", "skills/research/server.py"],
            "writer": ["python", "skills/writer/server.py"],
            "media": ["python", "skills/media/server.py"],
            "editor": ["python", "skills/editor/server.py"], # 新增 Editor Skill
            "wechat": ["python", "skills/wechat/server.py"]
        }

    async def connect_skills(self):
        """初始化连接所有技能服务器"""
        for name, cmd in self.skills.items():
            try:
                await self.client.connect_to_server(name, cmd[0], [cmd[1]])
            except Exception as e:
                print(f"[Error] 无法连接到 Skill [{name}]: {e}")

    async def write_and_publish(self, topic: str, persona: str = None):
        """执行端到端文章任务"""
        try:
            await self.connect_skills()
            print(f"[Start] 开始任务: {topic} (人设: {persona or '默认'})")
            
            # --- 1. 配置加载 (支持多风格) ---
            style_guide = ""
            style_file = "styles.md"
            if persona:
                style_file = f"styles_{persona}.md"
            
            try:
                import os
                if os.path.exists(style_file):
                    with open(style_file, "r", encoding="utf-8") as f:
                        style_guide = f.read()
                    print(f"[Config] 已加载 {style_file} 写作规范")
                elif persona:
                    print(f"[Config] 未找到 {style_file}，将回退到默认 styles.md")
                    if os.path.exists("styles.md"):
                        with open("styles.md", "r", encoding="utf-8") as f:
                            style_guide = f.read()
            except Exception as e:
                print(f"[Config] 读取风格文件失败: {e}")

            # --- 2. 深度研究 (Research Skill) ---
            print("[Research] 阶段 1: 选题研究...")
            research_data = await self.client.call_tool("research", "search_topic", {"topic": topic})
            print(f"研究快报: {research_data.content}")
            
            # --- 3. 策划与写作 (Writer Skill) ---
            print(f"[Writer] 阶段 2: 策划与大纲生成...")
            outline_response = await self.client.call_tool("writer", "generate_outline", {
                "research_summary": research_data.content[0].text,
                "style_guide": style_guide
            })
            outline_json_str = outline_response.content[0].text
            
            # 解析 JSON 标题和通过 Research 传递的 References
            article_title = topic
            article_outline = outline_json_str
            
            try:
                # 尝试解析 Writer 返回的 JSON (Regex 暴力提取)
                import re
                json_match = re.search(r"\{[\s\S]*\}", outline_json_str)
                
                if json_match:
                    clean_json = json_match.group(0)
                    outline_obj = json.loads(clean_json)
                    article_title = outline_obj.get("title", topic)
                    article_outline = outline_obj.get("outline", "")
                    print(f"[Writer] 已生成爆款标题: {article_title}")
                else:
                    print(f"[Writer] 未找到 JSON 对象，原始返回: {outline_json_str[:100]}...")
            except Exception as e:
                print(f"[Writer] 标题解析失败: {e}, 回退到 JSON 原始字符串")


            print(f"[Writer] 阶段 3: 撰写正文...")
            # 将 Research 阶段带链接的完整摘要附加到 Outline 后，作为参考资料传递给 Writer
            full_context_for_writer = f"{article_outline}\n\nReference Material (Must utilize for citations):\n{research_data.content[0].text}"
            
            content_response = await self.client.call_tool("writer", "write_content", {
                "outline": full_context_for_writer,
                "style_guide": style_guide
            })
            article_content = content_response.content[0].text

            # --- 4. 智能编辑 (Editor + Media Skills) ---
            print("[Editor] 阶段 4: 启动编辑部进行素材装配...")
            
            # 4.1 提取配图需求 (Editor Skill)
            prompts_res = await self.client.call_tool("editor", "extract_image_prompts", {"markdown_text": article_content})
            img_prompts = json.loads(prompts_res.content[0].text)
            
            images_data = [] # 存储生成的图片元数据
            
            if img_prompts:
                print(f"[Media] 检测到 {len(img_prompts)} 个正文插图需求，开始并行生成...")
                for item in img_prompts:
                    try:
                        prompt = item["prompt"]
                        print(f"  > 正在生成: {prompt[:20]}...")
                        
                        # 生成图片 (Media Skill - Flux.1)
                        # 用户决定回退到 AI 生成，配合 Adaptive Style 增强控制力
                        img_res = await self.client.call_tool("media", "generate_article_image", {"prompt": prompt})
                        img_url = img_res.content[0].text
                        
                        # 上传到微信换取正文 URL (WeChat Skill)
                        wx_res = await self.client.call_tool("wechat", "upload_article_image", {"image_url": img_url})
                        wx_data = json.loads(wx_res.content[0].text)
                        wx_url = wx_data.get("url", img_url)
                        
                        images_data.append({"prompt": prompt, "url": wx_url})
                        print(f"  √ 插图处理完成")
                    except Exception as e:
                        print(f"  × 插图处理失败: {e}")
            else:
                print("[Media] 未检测到正文插图需求")

            # 4.2 回填图片到正文 (Editor Skill)
            print("[Editor] 正在将图片回填至文章...")
            injected_res = await self.client.call_tool("editor", "inject_images", {
                "markdown_text": article_content,
                "images_data": json.dumps(images_data)
            })
            final_article_text = injected_res.content[0].text

            # 4.3 生成与上传封面 (Media + WeChat)
            # 4.3 生成与上传封面 (Media + WeChat)
            print("[Media] 正在为文章生成封面图...")
            # Generating cover with AI
            cover_prompt = f"Abstract 3D art concept representing: {article_title}. Clay material, soft lighting, minimalism, single object in center. NO text, NO letters, NO charts."
            cover_res = await self.client.call_tool("media", "generate_article_image", {"prompt": cover_prompt})
            cover_url = cover_res.content[0].text
            
            print("[WeChat] 上传封面素材...")
            # 封面上传 (Permanent Material for Draft)
            upload_res = await self.client.call_tool("wechat", "upload_image", {
                "image_url": cover_url,
                "media_type": "thumb"
            })
            
            thumb_media_id = None
            
            try:
                res_data = json.loads(upload_res.content[0].text)
                if res_data.get("status") in ["success", "mock_success"]:
                    thumb_media_id = res_data.get("media_id")
                else:
                    print(f"[Warning] 封面搜索图上传失败: {res_data.get('message')}")
            except Exception:
                pass
            
            # --- FALLBACK MECHANISM REMOVED (Reverted to pure generation) ---
            if not thumb_media_id:
                sys.stderr.write("[Error] 封面上传失败，且无有效回退方案\n")
                thumb_media_id = "mock_thumb_id_final"

            # 获取封面图链接 (用于文内展示，可选)
            article_cover_res = await self.client.call_tool("wechat", "upload_article_image", {"image_url": cover_url})
            article_cover_url = json.loads(article_cover_res.content[0].text).get("url", cover_url)

            # --- 5. 排版与渲染 (WeChat + Editor Skills) ---
            print("[WeChat] 渲染 HTML...")
            html_res = await self.client.call_tool("wechat", "markdown_to_wechat_html", {
                "markdown_text": final_article_text
            })
            article_html = html_res.content[0].text
            
            print("[Editor] 智能推荐 BGM...")
            music_res = await self.client.call_tool("editor", "recommend_music", {
                "article_title": article_title,
                "article_content": article_content[:500] # 仅用前500字做简单分析
            })
            music_data = json.loads(music_res.content[0].text)
            print(f"[Editor] 选中曲目: {music_data['name']} - {music_data['singer']}")
            
            print("[Editor] 最终排版装配...")
            assemble_res = await self.client.call_tool("editor", "assemble_html", {
                "article_html": article_html,
                "cover_url": article_cover_url,
                "music_xml": music_data["xml"]
            })
            final_content = assemble_res.content[0].text

            # --- 6. 发布 (WeChat Skill) ---
            print("[WeChat] 阶段 6: 同步至微信草稿箱...")
            publish_res = await self.client.call_tool("wechat", "upload_draft", {
                "title": article_title, # 使用爆款标题
                "content": final_content,
                "thumb_media_id": thumb_media_id
            })
            
            print(f"\n✨ 任务反馈: {publish_res.content[0].text}")
            
        except Exception as e:
            print(f"\n💥 系统运行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.client.disconnect_all()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WeChat Agent MCP Orchestrator")
    parser.add_argument("topic", nargs="?", default="AI 时代的个人职业规划", help="文章主题")
    parser.add_argument("--persona", help="写作人设 (对应 styles_{persona}.md)")
    
    args = parser.parse_args()
    
    agent = WeChatAgentOrchestrator()
    asyncio.run(agent.write_and_publish(args.topic, args.persona))
