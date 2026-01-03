import asyncio
from core.client import MCPClient

async def list_wechat_drafts():
    client = MCPClient()
    try:
        # 仅连接微信技能
        await client.connect_to_server("wechat", "python", ["skills/wechat/server.py"])
        
        print("\n--- 微信草稿箱列表 (测试号验证) ---")
        result = await client.call_tool("wechat", "get_draft_list", {"count": 10})
        
        # 结果处理
        import json
        data = json.loads(result.content[0].text)
        
        if data.get("status") == "error":
            print(f"❌ 微信报错: {data.get('message')}")
        elif "item" in data and data["item"]:
            for i, item in enumerate(data["item"]):
                article = item["content"]["news_item"][0]
                print(f"[{i+1}] 标题: {article['title']}")
                print(f"    作者: {article['author']}")
                print(f"    更新时间: {item['update_time']}")
                print("-" * 30)
        else:
            print("目前草稿箱为空。")
            if "errcode" in data:
                print(f"调试信息: {data}")
            
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(list_wechat_drafts())
