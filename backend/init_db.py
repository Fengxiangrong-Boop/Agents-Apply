"""数据库初始化脚本 - 创建系统预设样式"""
import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import async_session_maker
from app.core.logging import logger
from app.models.style import Style

# 系统预设样式数据
SYSTEM_STYLES = [
    {
        "name": "专业商务风格",
        "description": "适合企业和商务场景,语言正式、逻辑清晰、数据详实",
        "prompt_instruction": """请使用专业、正式的商务语言风格写作。要求:
1. 语言严谨、逻辑清晰
2. 多使用数据和事实支撑观点
3. 结构完整,包含引言、正文、结论
4. 避免口语化表达
5. 适当使用专业术语""",
        "css_content": """
body {
    font-family: 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.8;
    color: #333;
    background-color: #fff;
}
article {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
h1 {
    font-size: 28px;
    font-weight: bold;
    color: #1a1a1a;
    margin-bottom: 20px;
    border-bottom: 3px solid #0066cc;
    padding-bottom: 10px;
}
h2 {
    font-size: 22px;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 30px;
    margin-bottom: 15px;
}
p {
    margin-bottom: 15px;
    text-align: justify;
}
strong {
    color: #0066cc;
    font-weight: bold;
}
""",
    },
    {
        "name": "轻松活泼风格",
        "description": "适合生活、娱乐类内容,语言轻松、幽默风趣、贴近读者",
        "prompt_instruction": """请使用轻松、活泼的语言风格写作。要求:
1. 语言生动有趣,可以适当使用网络流行语
2. 多用比喻、拟人等修辞手法
3. 可以加入emoji表情
4. 贴近读者生活,引发共鸣
5. 段落短小精悍,易于阅读""",
        "css_content": """
body {
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    line-height: 1.8;
    color: #444;
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}
article {
    max-width: 750px;
    margin: 20px auto;
    padding: 30px;
    background-color: #fff;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}
h1 {
    font-size: 26px;
    font-weight: bold;
    color: #ff6b6b;
    margin-bottom: 20px;
    text-align: center;
}
h2 {
    font-size: 20px;
    font-weight: bold;
    color: #4ecdc4;
    margin-top: 25px;
    margin-bottom: 12px;
}
p {
    margin-bottom: 12px;
    line-height: 1.9;
}
strong {
    color: #ff6b6b;
}
""",
    },
    {
        "name": "科技极客风格",
        "description": "适合科技、技术类文章,专业术语丰富、逻辑严密、注重细节",
        "prompt_instruction": """请使用科技、专业的语言风格写作。要求:
1. 准确使用技术术语和行业黑话
2. 逻辑严密,层次分明
3. 可以包含代码示例或技术细节
4. 客观理性,基于事实和数据
5. 适当引用权威来源""",
        "css_content": """
body {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    line-height: 1.7;
    color: #e0e0e0;
    background-color: #1e1e1e;
}
article {
    max-width: 850px;
    margin: 0 auto;
    padding: 25px;
    background-color: #2d2d2d;
    border-left: 4px solid #00ff00;
}
h1 {
    font-size: 30px;
    font-weight: bold;
    color: #00ff00;
    margin-bottom: 20px;
    font-family: 'Microsoft YaHei', sans-serif;
}
h2 {
    font-size: 24px;
    font-weight: bold;
    color: #00bfff;
    margin-top: 30px;
    margin-bottom: 15px;
    font-family: 'Microsoft YaHei', sans-serif;
}
p {
    margin-bottom: 15px;
    color: #d0d0d0;
}
code {
    background-color: #3a3a3a;
    padding: 2px 6px;
    border-radius: 3px;
    color: #ff79c6;
}
strong {
    color: #ffb86c;
}
""",
    },
]


async def init_database():
    """初始化数据库 - 创建表和系统预设样式"""
    from app.core.db import create_db_and_tables
    
    # 1. 创建所有数据库表
    logger.info("开始创建数据库表...")
    await create_db_and_tables()
    logger.info("数据库表创建完成")
    
    # 2. 初始化系统预设样式
    logger.info("开始初始化系统预设样式...")
    async with async_session_maker() as session:
        # 检查是否已经初始化过
        result = await session.execute(
            select(Style).where(Style.is_system == True)
        )
        existing_styles = result.scalars().all()
        
        if existing_styles:
            logger.info(f"系统样式已存在 ({len(existing_styles)} 个),跳过初始化")
            return
        
        # 创建系统预设样式
        for style_data in SYSTEM_STYLES:
            style = Style(
                name=style_data["name"],
                description=style_data["description"],
                prompt_instruction=style_data["prompt_instruction"],
                css_content=style_data["css_content"],
                is_system=True,
                user_id=None,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(style)
        
        await session.commit()
        logger.info(f"成功创建 {len(SYSTEM_STYLES)} 个系统预设样式")


if __name__ == "__main__":
    asyncio.run(init_database())
