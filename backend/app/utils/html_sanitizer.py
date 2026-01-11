"""HTML清理工具 - XSS防护"""
import bleach

# 允许的HTML标签
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'div', 'span',
    'ul', 'ol', 'li',
    'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]

# 允许的HTML属性
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}

# 允许的CSS属性
ALLOWED_STYLES = [
    'color', 'background-color', 'font-size', 'font-weight', 'font-family',
    'text-align', 'text-decoration', 'margin', 'padding',
    'border', 'border-radius', 'width', 'height',
]


def sanitize_html(html_content: str) -> str:
    """清理HTML内容,防止XSS攻击
    
    Args:
        html_content: 原始HTML内容
        
    Returns:
        清理后的安全HTML
    """
    cleaned_html = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES,
        strip=True,  # 移除不允许的标签
    )
    
    return cleaned_html
