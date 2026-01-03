import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """项目全局配置"""
    
    # LLM 配置 (支持 OpenAI, 硅基流动等兼容 API)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # 硅基流动 Base URL: https://api.siliconflow.cn/v1
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    # LLM 文本模型配置
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4-turbo")
    
    # === 绘图专用配置 (SiliconFlow) ===
    # 硅基流动 API Key (若未设置则尝试为了兼容读取 OPENAI_API_KEY，但建议单独设置)
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    # 绘图 Base URL
    IMAGE_API_BASE: str = os.getenv("IMAGE_API_BASE", "https://api.siliconflow.cn/v1")
    # 绘图模型 (默认 Flux.1-schnell)
    IMAGE_MODEL_NAME: str = os.getenv("IMAGE_MODEL_NAME", "black-forest-labs/FLUX.1-schnell")
    
    # 微信公众号配置
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "")
    
    # 搜索相关 (以任意搜索服务为例)
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    
    # === 预设音乐库 (解耦) ===
    MUSIC_PLAYLIST: list = [
        {
            "name": "AI 的幕后主旋律", 
            "singer": "WeChat Agent", 
            "listenid": "78369894656188293", 
            "album_url": "https://y.gtimg.cn/music/photo_new/T002R500x500M000001KOzqM1AB9le.jpg",
            "tags": ["tech", "ai", "future", "intro"]
        },
        {
            "name": "Deep Focus (Tech Vibe)", 
            "singer": "Algorithm", 
            "listenid": "78304950328433146",
            "album_url": "https://y.gtimg.cn/music/photo_new/T002R300x300M000003y8dsH2wBHls.jpg",
            "tags": ["focus", "coding", "deep", "study"]
        },
        {
            "name": "Lofi Coding Beats", 
            "singer": "Flow State", 
            "listenid": "78240203139964796",
            "album_url": "https://y.gtimg.cn/music/photo_new/T002R300x300M000000hqbgT002s3N.jpg",
            "tags": ["relax", "lofi", "soft"]
        },
        {
            "name": "Future Glimpse", 
            "singer": "Synthwave", 
            "listenid": "78292730403423711",
            "album_url": "https://y.gtimg.cn/music/photo_new/T002R300x300M000002Neh8l0ucQkf.jpg",
            "tags": ["cyberpunk", "fast", "exciting"]
        }
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
