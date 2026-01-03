# WeChat Agent MCP 🚀

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-green)](https://modelcontextprotocol.io/)

这是一个基于 **MCP (Model Context Protocol)** 协议构建的模块化微信公众号自动化创作 Agent。
它能够像人类主编一样，自动化完成 **选题研究 -> 大纲策划 -> 正文写作 -> AI配图 -> 排版渲染 -> 自动发布** 的全流程。

## ✨ 核心特性

- **🧠 深度研究**: 集成 Tavily Search，自动搜索全网资料、真实用户吐槽和具体数据。
- **✍️ 拟人化写作**: 内置 "De-AI" 策略，生成不仅有逻辑，更具“人味”和情绪感的文章。
- **🎨 智能配图**: 自动提取文中画面需求，调用 Flux.1 生成高质量插图并回填至正文。
- **🎼 多媒体增强**: 自动推荐背景音乐 (BGM) 并生成极简风格封面。
- **🎭 多人设支持**: 支持通过命令行一键切换“科技博主”、“新闻主播”等不同写作风格。
- **🛡️ 鲁棒性设计**: 关键 API (OpenAI, WeChat) 内置自动重试机制，抗网络波动。

---

## 🛠️ 环境准备

### 1. 基础环境
确保您的电脑上安装了 Python 3.10 或更高版本。

### 2. 获取 API Key
为了让 Agent 正常工作，您需要准备以下服务凭证：
*   **LLM 服务**: OpenAI API Key (或兼容的 DeepSeek/Moonshot/硅基流动)。
*   **搜索服务**: [Tavily API](https://tavily.com/) (用于联网研究)。
*   **绘图服务**: [SiliconFlow](https://cloud.siliconflow.cn/) (推荐) 或其他兼容接口。
*   **微信公众号**: AppID 和 AppSecret (支持服务号或订阅号，开发测试建议使用[微信测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login))。

---

## ⚡ 快速开始

### 步骤 1: 克隆项目
```bash
git clone https://github.com/Fengxiangrong-Boop/Agents-Apply.git
cd Agents-Apply/wechat_agent_mcp
```

### 步骤 2: 安装依赖
推荐使用 Conda 创建独立环境（可选但推荐）：
```bash
conda create -n wechat_agent python=3.10
conda activate wechat_agent
```

安装 Python 依赖：
```bash
pip install -r requirements.txt
# 或者如果使用 poetry/uv 等工具，请参照 pyproject.toml
pip install .
```

> **注意**: 如果没有 `requirements.txt`，可以直接使用 `pip install tenacity openai mcp httpx pillow rich` 安装核心包。

### 步骤 3: 配置文件
复制示例配置文件并重命名为 `.env`：

Linux/Mac:
```bash
cp .env.example .env
```
Windows (PowerShell):
```powershell
copy .env.example .env
```

**编辑 `.env` 文件**，填入您的 API Key：
```ini
OPENAI_API_KEY=sk-xxxx...
SEARCH_API_KEY=tvly-xxxx...
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

---

## 🚀 使用指南

### 1. 基础运行
生成一篇关于特定主题的文章：
```bash
python main.py "DeepSeek V3 深度评测"
```

### 2. 切换写作风格 (Persona)
使用 `--persona` 参数切换不同的人设模板：

**新闻资讯风格**:
```bash
python main.py "苹果发布会总结" --persona news
```
*(这将自动加载 `styles_news.md` 模板)*

**自定义风格**:
您可以复制 `styles.md` 创建如 `styles_emotion.md`，然后运行：
```bash
python main.py "深夜情感故事" --persona emotion
```

---

## 📂 项目结构

```
wechat_agent_mcp/
├── main.py              # 🤖 编排器入口 (Orchestrator)
├── config.py            # ⚙️ 配置中心
├── styles.md            # 📝 默认写作风格指南
├── styles_news.md       # 📰 新闻风格指南
├── core/                # MCP 客户端核心逻辑
├── skills/              # ✨ 技能模块 (Skill Servers)
│   ├── research/        # 联网搜索与分析
│   ├── writer/          # 大纲与正文写作 (含重试机制)
│   ├── editor/          # 配图提取与 BGM 推荐
│   ├── media/           # AI 绘图服务
│   └── wechat/          # 渲染排版与草稿箱同步
└── utils/               # 工具函数
```

---

## ❓ 常见问题 (FAQ)

**Q: 运行报错 `invalid content`?**
A: 这通常是微信 API 对 HTML 标签的限制。我们已经优化了渲染引擎，请确保使用的是最新代码。如果仍报错，请检查文章中是否包含特殊字符。

**Q: 封面图上传失败？**
A: 微信对封面图有严格的 64KB 大小限制。本项目内置了自动压缩算法，但如果图片过于复杂可能仍需重试。

**Q: 为什么没有生成图片？**
A: 请检查 `.env` 中是否配置了 `SILICONFLOW_API_KEY`，且该账号有足够的余额（新用户通常有免费额度）。

---

## 🤝 贡献
欢迎提交 Issue 或 PR！
