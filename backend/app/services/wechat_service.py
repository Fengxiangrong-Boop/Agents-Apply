"""微信服务 - 处理微信API交互"""
import asyncio
import base64
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException

from app.core.config import settings
from app.core.logging import logger
from app.core.security import decrypt_sensitive_data
from app.models.wechat_config import WechatConfig

# 默认封面图 (蓝色背景) Base64
DEFAULT_COVER_BASE64 = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAH0A4QDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9U6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//Z"


class WechatService:
    """微信服务类"""
    
    def __init__(self, wechat_config: WechatConfig):
        """初始化微信服务
        
        Args:
            wechat_config: 微信配置对象
        """
        self.config = wechat_config
        self.app_id = wechat_config.app_id
        self.app_secret = decrypt_sensitive_data(wechat_config.app_secret_encrypted)
        self.client = WeChatClient(self.app_id, self.app_secret)
    
    async def get_access_token(self, force_refresh: bool = False) -> str:
        """获取AccessToken,自动处理刷新逻辑
        
        Args:
            force_refresh: 是否强制刷新Token
            
        Returns:
            有效的AccessToken
        """
        now = datetime.utcnow()
        
        # 检查是否需要刷新Token
        need_refresh = (
            force_refresh
            or self.config.access_token is None
            or self.config.token_expires_at is None
            or (self.config.token_expires_at - now).total_seconds() < settings.WECHAT_TOKEN_REFRESH_ADVANCE
        )
        
        if need_refresh:
            logger.info(f"刷新微信AccessToken: AppID={self.app_id}")
            
            try:
                # 调用微信API获取新Token
                token_data = await asyncio.to_thread(self.client.fetch_access_token)
                
                self.config.access_token = token_data["access_token"]
                self.config.token_expires_at = now + timedelta(seconds=token_data["expires_in"])
                self.config.last_refresh_at = now
                
                logger.info(f"AccessToken刷新成功,过期时间: {self.config.token_expires_at}")
                
            except WeChatClientException as e:
                logger.error(f"刷新AccessToken失败: {e}")
                raise
        
        return self.config.access_token
    
    async def get_or_create_default_cover(self) -> str:
        """获取或创建默认封面图本地文件"""
        try:
            temp_dir = '/tmp'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            
            file_path = os.path.join(temp_dir, 'default_cover.jpg')
            
            if not os.path.exists(file_path):
                logger.info(f"开始下载默认封面图到: {file_path}")
                
                # 使用多个备用 URL，确保至少一个可用
                cover_urls = [
                    "https://via.placeholder.com/900x500/1976D2/FFFFFF?text=AI+Article",
                    "https://dummyimage.com/900x500/1976d2/ffffff&text=AI+Article",
                    "https://fakeimg.pl/900x500/1976d2/ffffff/?text=AI+Article"
                ]
                
                download_success = False
                last_error = None
                
                for url in cover_urls:
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            response = await client.get(url)
                            response.raise_for_status()
                            
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            
                            logger.info(f"成功从 {url} 下载封面图")
                            download_success = True
                            break
                    except Exception as e:
                        last_error = e
                        logger.warning(f"从 {url} 下载失败: {e}, 尝试下一个源")
                        continue
                
                if not download_success:
                    error_msg = f"所有下载源均失败: {last_error}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            return file_path
        except Exception as e:
            logger.error(f"创建默认封面图失败: {e}")
            raise Exception(f"创建默认封面图失败: {e}")

    async def upload_image(self, image_url_or_path: str) -> str:
        """上传图片到微信素材库
        
        Args:
            image_url_or_path: 图片URL或本地路径
            
        Returns:
            微信media_id
        """
        access_token = await self.get_access_token()
        image_data = None

        # 判断是URL还是本地路径
        if image_url_or_path.startswith(('http://', 'https://')):
            # 下载图片
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url_or_path)
                response.raise_for_status()
                image_data = response.content
        else:
            # 读取本地文件
            try:
                # 兼容 Linux/Windows 路径
                path = image_url_or_path
                if not os.path.isabs(path):
                     # 如果是相对路径，尝试基于当前工作目录
                     path = os.path.abspath(path)
                
                with open(path, 'rb') as f:
                    image_data = f.read()
            except Exception as e:
                logger.error(f"读取本地图片失败: {e}")
                raise Exception(f"读取本地图片失败: {e}")
        
        # 上传到微信
        upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
        
        async with httpx.AsyncClient() as client:
            files = {"media": ("image.jpg", image_data, "image/jpeg")}
            response = await client.post(upload_url, files=files)
            result = response.json()
        
        if "errcode" in result and result["errcode"] != 0:
            error_msg = f"上传图片失败: {result.get('errmsg', 'Unknown error')}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        media_id = result.get("media_id")
        logger.info(f"图片上传成功: media_id={media_id}")
        
        return media_id
    
    async def create_draft(
        self,
        title: str,
        content: str,
        author: str = "",
        digest: str = "",
        thumb_media_id: Optional[str] = None,
    ) -> str:
        """创建草稿
        
        Args:
            title: 文章标题
            content: 文章HTML内容
            author: 作者
            digest: 摘要
            thumb_media_id: 封面图片media_id
            
        Returns:
            草稿media_id
        """
        access_token = await self.get_access_token()
        
        # 微信标题限制基于字节长度（UTF-8编码），实际限制约为32-40字节
        # 中文字符通常占3字节，32字节约能容纳10个中文字符
        max_title_bytes = 32
        title_bytes = title.encode('utf-8')
        
        if len(title_bytes) > max_title_bytes:
            # 截断标题，确保不破坏 UTF-8 字符边界
            truncated_bytes = title_bytes[:max_title_bytes]
            # 尝试解码，如果失败则继续向前截断直到成功
            for i in range(max_title_bytes, max_title_bytes - 4, -1):
                try:
                    truncated_title = title_bytes[:i].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果都失败了，使用前10个字符作为兜底
                truncated_title = title[:10]
            
            logger.warning(f"标题字节过长 ({len(title_bytes)} 字节)，已截断至 {len(truncated_title.encode('utf-8'))} 字节: {truncated_title}")
        else:
            truncated_title = title
        
        # 处理摘要（digest）字节长度限制，约54字节
        max_digest_bytes = 54
        digest_text = digest or title
        digest_bytes = digest_text.encode('utf-8')
        
        if len(digest_bytes) > max_digest_bytes:
            # 截断摘要，确保不破坏 UTF-8 字符边界
            for i in range(max_digest_bytes, max_digest_bytes - 4, -1):
                try:
                    truncated_digest = digest_bytes[:i].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 兜底：使用前15个字符
                truncated_digest = digest_text[:15]
            
            logger.warning(f"摘要字节过长 ({len(digest_bytes)} 字节)，已截断至 {len(truncated_digest.encode('utf-8'))} 字节: {truncated_digest}")
        else:
            truncated_digest = digest_text
        
        # 构建草稿数据
        articles = [
            {
                "title": truncated_title,
                "author": author,
                "digest": truncated_digest,
                "content": content,
                "content_source_url": "",
                "thumb_media_id": thumb_media_id or "",
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
        
        # 调用微信API创建草稿
        draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        # 手动序列化 JSON，确保中文字符不被转义
        import json
        json_data = json.dumps({"articles": articles}, ensure_ascii=False)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                draft_url,
                content=json_data.encode('utf-8'),
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30.0,
            )
            result = response.json()
        
        if "errcode" in result and result["errcode"] != 0:
            error_msg = f"创建草稿失败: {result.get('errmsg', 'Unknown error')}"
            logger.error(error_msg)
            
            # 如果是Token过期,尝试刷新后重试
            if result["errcode"] == 40001:
                logger.info("Token过期,刷新后重试")
                await self.get_access_token(force_refresh=True)
                return await self.create_draft(title, content, author, digest, thumb_media_id)
            
            raise Exception(error_msg)
        
        media_id = result.get("media_id")
        logger.info(f"草稿创建成功: media_id={media_id}, title={title}")
        
        return media_id

    async def sync_article_with_retry(
        self,
        title: str,
        content: str,
        max_retries: int = None,
    ) -> str:
        """同步文章到微信草稿箱(带重试机制)"""
        logger.info(f"开始同步文章到微信: title={title}")
        
        if max_retries is None:
            max_retries = settings.WECHAT_MAX_RETRIES
        
        # 1. 准备封面图
        thumb_media_id = None
        logger.info("步骤1: 开始准备封面图")
        
        try:
            # 获取本地默认封面路径
            logger.info("步骤1.1: 调用 get_or_create_default_cover()")
            cover_path = await self.get_or_create_default_cover()
            logger.info(f"步骤1.2: 封面图路径: {cover_path}")
            
            logger.info(f"步骤1.3: 正在上传默认封面图到微信")
            thumb_media_id = await self.upload_image(cover_path)
            logger.info(f"步骤1.4: 封面图上传成功, media_id={thumb_media_id}")
            
            if not thumb_media_id:
                raise Exception("封面图上传后未返回Media ID")
                
        except Exception as e:
            logger.error(f"严重错误: 封面图处理失败: {e}", exc_info=True)
            raise Exception(f"同步前置检查失败: 封面图处理异常 - {str(e)}")
        
        logger.info(f"步骤2: 封面图准备完成, 开始创建草稿, thumb_media_id={thumb_media_id}")
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 传入 thumb_media_id
                logger.info(f"步骤2.{attempt+1}: 尝试创建草稿 (第 {attempt+1}/{max_retries} 次)")
                media_id = await self.create_draft(title, content, thumb_media_id=thumb_media_id)
                logger.info(f"步骤3: 草稿创建成功, media_id={media_id}")
                return media_id
            
            except Exception as e:
                last_error = e
                logger.warning(f"同步失败(尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        error_msg = f"同步失败,已重试 {max_retries} 次: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

