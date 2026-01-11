# 部署文档

本文档详细说明如何通过Docker部署WeChat Agent系统。

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [环境变量配置](#环境变量配置)
- [服务管理](#服务管理)
- [故障排查](#故障排查)
- [生产环境部署建议](#生产环境部署建议)

---

## 系统要求

### 硬件要求
- CPU: 2核及以上
- 内存: 4GB及以上
- 磁盘: 20GB可用空间

### 软件要求
- Docker: >= 20.10
- Docker Compose: >= 2.0
- 操作系统: Linux / macOS / Windows

### 网络要求
- 需要访问外网（用于AI API调用）
- 如需微信同步功能，需要微信公众平台API访问权限

---

## 快速开始

### 1. 获取项目代码

```bash
# 克隆仓库
git clone https://github.com/yourusername/wechat-agent.git
cd wechat-agent
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
# Linux/macOS
nano .env

# Windows
notepad .env
```

### 3. 启动所有服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **前端界面**: http://localhost:27999
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 5. 初始化使用

1. 在前端页面注册新用户账号
2. 登录后进入"系统设置"
3. 配置微信公众号信息（可选）
4. 配置SiliconFlow API Key
5. 开始创作文章！

---

## 环境变量配置

### 必填配置

#### SECRET_KEY
JWT令牌加密密钥，**必须修改**为强随机密钥。

生成方式：
```bash
# 方法1: 使用openssl
openssl rand -hex 32

# 方法2: 使用Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

示例：
```env
SECRET_KEY=3d6f45a5fc12445dbac2f59c3b6c7cb1d32a0f6e8e84d43dabc95c6f7e8a9b0c
```

#### DATABASE_URL
PostgreSQL数据库连接字符串。

格式：
```env
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名
```

Docker Compose部署（默认）：
```env
DATABASE_URL=postgresql://wechat_agent:your_password@db:5432/wechat_agent
```

外部数据库：
```env
DATABASE_URL=postgresql://user:password@your-db-host:5432/dbname
```

#### REDIS_URL
Redis连接字符串。

Docker Compose部署（默认）：
```env
REDIS_URL=redis://redis:6379/0
```

外部Redis：
```env
REDIS_URL=redis://your-redis-host:6379/0
```

### 可选配置

#### AI服务配置

```env
# SiliconFlow API Key (用于文章生成)
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxx
```

获取方式：访问 [SiliconFlow](https://siliconflow.cn/) 注册并获取API Key

#### 微信公众号配置

```env
WECHAT_APPID=wx1234567890abcdef
WECHAT_APPSECRET=abcdef1234567890abcdef1234567890
```

获取方式：在微信公众平台后台的"开发 - 基本配置"中获取

#### 端口配置

```env
# 后端API服务端口
BACKEND_PORT=8000

# 前端Web服务端口
FRONTEND_PORT=27999
```

#### 运行环境

```env
# development / production
ENVIRONMENT=production

# 日志级别: DEBUG / INFO / WARNING / ERROR
LOG_LEVEL=INFO
```

#### CORS配置（生产环境）

```env
CORS_ORIGINS=https://yourdomain.com
```

### 完整配置示例

```env
# ===== 数据库配置 =====
DATABASE_URL=postgresql://wechat_agent:StrongPassword123!@db:5432/wechat_agent

# ===== Redis配置 =====
REDIS_URL=redis://redis:6379/0

# ===== JWT配置 =====
SECRET_KEY=3d6f45a5fc12445dbac2f59c3b6c7cb1d32a0f6e8e84d43dabc95c6f7e8a9b0c

# ===== AI服务配置 =====
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxx

# ===== 微信公众号配置 =====
WECHAT_APPID=wx1234567890abcdef
WECHAT_APPSECRET=abcdef1234567890abcdef1234567890

# ===== 应用配置 =====
BACKEND_PORT=8000
FRONTEND_PORT=27999
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 服务管理

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d backend frontend
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止但保留数据卷
docker-compose stop
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart backend
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看指定服务日志
docker-compose logs backend

# 查看最近100行日志
docker-compose logs --tail=100
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 清理旧镜像
docker image prune -f
```

### 数据备份

```bash
# 备份数据库
docker exec wechat_agent_db pg_dump -U wechat_agent wechat_agent > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i wechat_agent_db psql -U wechat_agent wechat_agent < backup_20260111.sql
```

---

## 故障排查

### 服务无法启动

**问题**: docker-compose up -d 失败

**排查步骤**:
1. 检查Docker是否正常运行
   ```bash
   docker --version
   docker-compose --version
   ```

2. 检查端口是否被占用
   ```bash
   # Linux/macOS
   lsof -i :8000
   lsof -i :27999
   
   # Windows
   netstat -ano | findstr :8000
   ```

3. 查看详细错误日志
   ```bash
   docker-compose logs
   ```

### 数据库连接失败

**问题**: 后端日志显示数据库连接错误

**解决方案**:
1. 检查DATABASE_URL配置是否正确
2. 确认数据库服务已启动
   ```bash
   docker-compose ps db
   ```
3. 检查数据库密码是否匹配

### 前端无法访问

**问题**: 访问localhost:27999无响应

**解决方案**:
1. 检查前端容器状态
   ```bash
   docker-compose ps frontend
   docker-compose logs frontend
   ```
2. 确认端口配置正确
3. 清除浏览器缓存

### AI生成失败

**问题**: 文章生成时报错

**排查步骤**:
1. 检查SILICONFLOW_API_KEY是否配置
2. 确认API Key有效且有余额
3. 检查网络是否能访问外网

### 微信同步失败

**常见错误**:

1. **invalid_media_id**
   - 原因：封面图未正确上传
   - 解决：系统会自动生成默认封面图

2. **标题/摘要超长**
   - 原因：内容超过微信限制
   - 解决：系统会自动截断

3. **access_token失效**
   - 原因：AppSecret错误或已更换
   - 解决：重新配置正确的AppSecret

---

## 生产环境部署建议

### 1. 使用HTTPS

配置Nginx反向代理：

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:27999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 定期备份数据

设置定时任务：
```bash
# 每天凌晨3点备份
0 3 * * * /path/to/backup.sh
```

### 3. 监控服务状态

使用健康检查：
```bash
# 检查后端API
curl http://localhost:8000/health

# 检查前端
curl http://localhost:27999
```

### 4. 日志管理

配置日志轮转，避免磁盘占满：
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 安全加固

- 修改默认端口
- 使用强密码
- 定期更新依赖
- 配置防火墙规则

---

## 常见问题

### Q: 如何修改数据库密码？

A: 修改.env中的DATABASE_URL，然后重启服务
```bash
docker-compose down
docker-compose up -d
```

### Q: 如何清空所有数据重新开始？

A: 删除数据卷
```bash
docker-compose down -v
docker-compose up -d
```

### Q: 如何查看数据库内容？

A: 进入数据库容器
```bash
docker exec -it wechat_agent_db psql -U wechat_agent
```

### Q: 支持哪些浏览器？

A: 推荐使用Chrome、Firefox、Edge最新版本

---

## 技术支持

如遇到部署问题，请：
1. 查看项目Issues: https://github.com/yourusername/wechat-agent/issues
2. 提交新Issue并附带详细日志
3. 参考官方文档

---

**祝部署顺利！** 🎉
