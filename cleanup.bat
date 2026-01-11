@echo off
REM 项目清理脚本 - Windows版本

echo 开始清理项目...

REM 清理Python缓存
echo 清理Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM 清理Node.js依赖和构建文件
echo 清理Node.js文件...
if exist frontend\node_modules rd /s /q frontend\node_modules
if exist frontend\dist rd /s /q frontend\dist
if exist frontend\.vite rd /s /q frontend\.vite

REM 清理日志文件
echo 清理日志文件...
del /q backend\logs\*.log 2>nul
echo. > backend\logs\.gitkeep

REM 清理临时目录
echo 清理临时目录...
if exist frontend_new rd /s /q frontend_new

REM 清理Docker相关
echo 清理Docker容器...
docker-compose down 2>nul

echo.
echo 清理完成！
echo.
echo 下一步操作：
echo 1. 检查并配置 .env 文件
echo 2. 运行: docker-compose up -d

pause
