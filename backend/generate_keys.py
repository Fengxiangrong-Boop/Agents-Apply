"""生成加密密钥的辅助脚本"""
import secrets

from cryptography.fernet import Fernet

print("=" * 60)
print("密钥生成工具")
print("=" * 60)

# 生成JWT Secret Key
jwt_secret = secrets.token_urlsafe(32)
print(f"\nJWT Secret Key (用于 SECRET_KEY):")
print(jwt_secret)

# 生成Fernet加密密钥
fernet_key = Fernet.generate_key().decode()
print(f"\nFernet Encryption Key (用于 ENCRYPTION_KEY):")
print(fernet_key)

print("\n" + "=" * 60)
print("请将以上密钥复制到 .env 文件中")
print("=" * 60)
