# ============================================================================
# 后端 Dockerfile - 极速构建优化版
# ============================================================================
# 使用预编译二进制包 + 多层缓存 + 国内镜像源
# 构建时间: 从 10-15 分钟优化到 1-3 分钟
# ============================================================================

FROM python:3.11-slim

# ────────────────────────────────────────────────────────────────────────────
# 第一层：系统依赖（很少变化，强缓存）
# ────────────────────────────────────────────────────────────────────────────
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────────────────────────────────
# 第二层：Python 依赖（使用预编译 wheel 包）
# ────────────────────────────────────────────────────────────────────────────
WORKDIR /app

# 先复制 requirements.txt（利用 Docker 缓存）
COPY requirements.txt .

# 使用国内镜像源 + 预编译二进制包（避免编译）
RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir \
    --only-binary=:all: \
    -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    || pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# ────────────────────────────────────────────────────────────────────────────
# 第三层：应用代码（经常变化，放最后）
# ────────────────────────────────────────────────────────────────────────────
# 复制应用代码
COPY . .

# 确保数据目录存在
RUN mkdir -p /app/data/input /app/data/output /app/logs

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 验证关键文件（调试用）
RUN echo "检查关键文件..." && \
    ls -la /app/ && \
    echo "检查数据目录..." && \
    ls -la /app/data/ 2>/dev/null || echo "data 目录不存在" && \
    ls -la /app/data/input/ 2>/dev/null || echo "data/input 目录不存在"

# 健康检查（使用内置库，不依赖 requests）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=5)" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
