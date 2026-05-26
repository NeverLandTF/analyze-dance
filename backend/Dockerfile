# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# 安装系统依赖（如果需要编译某些包）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Gunicorn 生产级 WSGI 服务器
RUN pip install --no-cache-dir gunicorn

# 复制应用代码
COPY . .

# 创建非 root 用户运行应用
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 启动脚本：先执行数据库迁移，然后启动 Gunicorn
CMD ["sh", "-c", "flask db upgrade && exec gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --worker-class gthread --timeout 120 --access-logfile - --error-logfile - app:app"]
