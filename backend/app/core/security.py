"""安全模块 - JWT认证、密码哈希、数据加密"""
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

import hashlib
from app.core.config import settings

# 密码哈希上下文
# 使用 pbkdf2_sha256 避免 bcrypt 的 72 字节限制
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Fernet加密实例(用于加密API Key和AppSecret)
fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌
    
    Args:
        data: 要编码的数据字典
        expires_delta: 过期时间增量,默认使用配置中的值
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码JWT访问令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        解码后的数据字典,如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据(如API Key、AppSecret)
    
    Args:
        data: 明文数据
        
    Returns:
        加密后的数据(base64编码)
    """
    encrypted_bytes = fernet.encrypt(data.encode())
    return encrypted_bytes.decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """解密敏感数据
    
    Args:
        encrypted_data: 加密后的数据(base64编码)
        
    Returns:
        解密后的明文数据
    """
    decrypted_bytes = fernet.decrypt(encrypted_data.encode())
    return decrypted_bytes.decode()
