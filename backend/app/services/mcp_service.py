"""MCP服务 - 调用LLM生成文章"""
import asyncio
from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.security import decrypt_sensitive_data


class MCPService:
    """MCP服务类 - 调用硅基流动LLM API"""
    
    # 并发控制信号量
    _semaphore = asyncio.Semaphore(settings.LLM_MAX_CONCURRENT)
    
    def __init__(self, api_key_encrypted: str):
        """初始化MCP服务
        
        Args:
            api_key_encrypted: 加密的API Key
        """
        self.api_key = decrypt_sensitive_data(api_key_encrypted)
        self.base_url = settings.SILICONFLOW_BASE_URL
        self.model = settings.SILICONFLOW_MODEL
    
    async def generate_article(
        self,
        prompt: str,
        style_instruction: str,
        max_retries: int = None,
    ) -> str:
        """生成文章内容
        
        Args:
            prompt: 用户输入的主题/关键词
            style_instruction: 样式风格指令
            max_retries: 最大重试次数
            
        Returns:
            生成的Markdown内容
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        if max_retries is None:
            max_retries = settings.LLM_MAX_RETRIES
        
        # 使用信号量控制并发
        async with self._semaphore:
            return await self._generate_with_retry(prompt, style_instruction, max_retries)
    
    async def _generate_with_retry(
        self,
        prompt: str,
        style_instruction: str,
        max_retries: int,
    ) -> str:
        """带重试的生成逻辑
        
        Args:
            prompt: 用户输入
            style_instruction: 样式指令
            max_retries: 最大重试次数
            
        Returns:
            生成的内容
        """
        # 构建完整的Prompt
        system_prompt = f"""你是一位专业的公众号文章写作助手。请根据用户的主题和要求,生成一篇高质量的公众号文章。

写作风格要求: {style_instruction}

请用Markdown格式输出文章内容,包括标题、段落、列表等。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用LLM生成文章(尝试 {attempt + 1}/{max_retries})")
                
                # 调用硅基流动API
                async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": 0.7,
                            "max_tokens": 4000,
                        },
                    )
                    response.raise_for_status()
                    result = response.json()
                
                # 提取生成的内容
                content = result["choices"][0]["message"]["content"]
                logger.info(f"文章生成成功,长度: {len(content)} 字符")
                
                return content
            
            except httpx.HTTPStatusError as e:
                last_error = e
                
                # 处理不同的HTTP错误
                if e.response.status_code == 401:
                    error_msg = "API Key无效,请重新配置"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                elif e.response.status_code == 429:
                    error_msg = "API配额耗尽,请充值后重试"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                else:
                    logger.warning(f"HTTP错误 {e.response.status_code}: {e}")
            
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"请求超时: {e}")
            
            except Exception as e:
                last_error = e
                logger.warning(f"生成失败: {e}")
            
            # 重试前等待(指数退避)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        error_msg = f"文章生成失败,已重试 {max_retries} 次: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    async def validate_api_key(self) -> bool:
        """验证API Key是否有效
        
        Returns:
            API Key是否有效
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                return True
        
        except Exception as e:
            logger.error(f"API Key验证失败: {e}")
            return False
