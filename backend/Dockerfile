# 后端 Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# 复制依赖文件
COPY pyproject.toml ./

# 配置 Poetry 不创建虚拟环境
RUN poetry config virtualenvs.create false

# 安装依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 复制应用代码
COPY app ./app
COPY init_db.py ./
COPY generate_keys.py ./

# 创建日志和数据目录
RUN mkdir -p logs data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
