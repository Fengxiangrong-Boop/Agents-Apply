"""样式服务 - 处理Markdown到HTML的转换"""
import re
from typing import Optional

import markdown
from bs4 import BeautifulSoup

from app.core.logging import logger


class StyleService:
    """样式服务类"""
    
    @staticmethod
    def markdown_to_html(markdown_content: str, css_content: str) -> str:
        """将Markdown转换为带样式的HTML
        
        Args:
            markdown_content: Markdown内容
            css_content: CSS样式
            
        Returns:
            渲染后的HTML
        """
        # 使用markdown库转换
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'extra',  # 支持表格、代码块等
                'codehilite',  # 代码高亮
                'toc',  # 目录
            ]
        )
        
        # 包装HTML并应用样式
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {css_content}
    </style>
</head>
<body>
    <article>
        {html_content}
    </article>
</body>
</html>
"""
        
        return full_html
    
    @staticmethod
    def extract_title_from_markdown(markdown_content: str) -> Optional[str]:
        """从Markdown内容中提取标题
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            提取的标题,如果没有则返回None
        """
        # 查找第一个一级标题
        match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 查找第一个二级标题
        match = re.search(r'^##\s+(.+)$', markdown_content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 如果没有标题,返回第一行非空内容
        lines = markdown_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:50]  # 最多50个字符
        
        return None
    
    @staticmethod
    def extract_images_from_html(html_content: str) -> list[str]:
        """从HTML中提取所有图片URL
        
        Args:
            html_content: HTML内容
            
        Returns:
            图片URL列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(src)
        
        return images
    
    @staticmethod
    def replace_image_urls(html_content: str, url_mapping: dict[str, str]) -> str:
        """替换HTML中的图片URL
        
        Args:
            html_content: HTML内容
            url_mapping: URL映射字典 {原URL: 新URL}
            
        Returns:
            替换后的HTML
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src in url_mapping:
                img['src'] = url_mapping[src]
                logger.debug(f"替换图片URL: {src} -> {url_mapping[src]}")
        
        return str(soup)
