FROM python:3.11-slim AS base

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装系统依赖 (添加重试逻辑)
RUN for i in 1 2 3; do \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        gfortran \
        libopenblas-dev \
        liblapack-dev \
        curl \
        sqlite3 && \
    rm -rf /var/lib/apt/lists/* && break || sleep 5; \
    done

# 复制并安装Python依赖
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./

# 创建必要的目录
RUN mkdir -p /app/data/input /app/logs

# 复制数据库和数据文件(如果存在)
COPY --chown=1000:1000 data/ /app/data/

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 健康检查端点
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# 生产环境启动命令(移除--reload)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
