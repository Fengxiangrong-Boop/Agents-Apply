#!/bin/bash
# 项目清理脚本 - 清理所有临时和垃圾文件

echo "开始清理项目..."

# 清理Python缓存
echo "清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# 清理Node.js依赖和构建文件
echo "清理Node.js文件..."
rm -rf frontend/node_modules 2>/dev/null
rm -rf frontend/dist 2>/dev/null
rm -rf frontend/.vite 2>/dev/null

# 清理日志文件
echo "清理日志文件..."
rm -f backend/logs/*.log 2>/dev/null
touch backend/logs/.gitkeep

# 清理临时目录
echo "清理临时目录..."
rm -rf frontend_new 2>/dev/null

# 清理Docker相关
echo "清理Docker容器和镜像..."
docker-compose down 2>/dev/null

echo "清理完成！"
echo ""
echo "下一步操作："
echo "1. 检查并配置 .env 文件"
echo "2. 运行: docker-compose up -d"
