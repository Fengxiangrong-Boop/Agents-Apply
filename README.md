# WeChat Agent - 微信公众号文章智能生成系统

基于AI的微信公众号文章智能生成与自动同步系统。通过简单的主题输入，自动生成专业的公众号文章并同步到草稿箱。

## ✨ 功能特性

- 🤖 **AI智能生成**：基于SiliconFlow API，输入主题即可生成高质量文章
- 🎨 **多样式支持**：内置多种文章风格模板，支持自定义样式
- 📱 **一键同步**：自动同步到微信公众号草稿箱
- 👥 **用户系统**：完整的注册登录、权限管理
- 🎯 **现代化UI**：Indigo配色方案，响应式设计
- 🐳 **Docker部署**：一键启动，开箱即用

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **ORM**: SQLAlchemy
- **认证**: JWT

### 前端
- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **UI库**: Naive UI
- **状态管理**: Pinia
- **图标**: Lucide Vue

## 🚀 快速开始

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0

### 一键部署

1. **克隆项目**
```bash
git clone https://github.com/yourusername/wechat-agent.git
cd wechat-agent
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端: http://localhost:27999
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 环境变量说明

必填配置：
- `SECRET_KEY`: JWT密钥（使用 `openssl rand -hex 32` 生成）
- `DATABASE_URL`: PostgreSQL连接字符串
- `REDIS_URL`: Redis连接字符串
- `ENCRYPTION_KEY`: 数据加密密钥

可选配置：
- `SILICONFLOW_API_KEY`: 推荐在Web界面"设置"中配置
- `WECHAT_APPID`: 推荐在Web界面"设置"中配置
- `WECHAT_APPSECRET`: 推荐在Web界面"设置"中配置

详细配置说明请查看 [部署文档](./DEPLOYMENT.md)

## 📖 使用指南

1. **注册账号**：访问前端页面注册新用户
2. **配置微信**：在"系统设置"中配置微信公众号信息
3. **配置API Key**：配置SiliconFlow API密钥
4. **创建文章**：
   - 进入"文章创作"页面
   - 输入文章主题
   - 选择"视觉主题"（支持简约白、商务蓝、极客黑等预设）
   - 或者选择自定义"样式"模板
   - 点击"生成文章"
5. **同步微信**：生成后点击"同步到微信"即可推送到草稿箱

## 📸 界面截图

（TODO: 添加截图）

## 🔧 开发指南

### 本地开发

#### 后端
```bash
cd backend
# 使用 Poetry 安装依赖
poetry install
# 启动开发服务器
poetry run uvicorn app.main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

### 项目结构
```
.
├── backend/           # FastAPI后端
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── core/     # 核心配置
│   │   ├── models/   # 数据模型
│   │   ├── schemas/  # Pydantic模型
│   │   ├── services/ # 业务逻辑
│   │   └── utils/    # 通用工具
│   └── pyproject.toml # Poetry依赖配置
├── frontend/          # Vue 3前端
│   ├── src/
│   │   ├── api/      # API调用
│   │   ├── components/ # 组件
│   │   ├── views/    # 页面
│   │   ├── stores/   # 状态管理
│   │   └── assets/   # 静态资源
│   └── package.json
└── docker-compose.yml
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

## ⚠️ 免责声明

本项目仅供学习交流使用。使用本系统生成和发布内容时，请遵守相关法律法规和微信公众平台规范。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Naive UI](https://www.naiveui.com/)
- [SiliconFlow](https://siliconflow.cn/)

## 📮 联系方式

如有问题或建议，欢迎提交Issue。

---

⭐ 如果这个项目对你有帮助，欢迎Star支持！
