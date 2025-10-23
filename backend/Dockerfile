# ============================================================================
# 后端 Dockerfile - 多阶段构建优化
# ============================================================================
# 基于 Python 3.11 slim 镜像（体积小，适合生产环境）
# ============================================================================

# ────────────────────────────────────────────────────────────────────────────
# 阶段1: 构建阶段 - 安装依赖
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /build

# 安装系统依赖（构建时需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装Python依赖（使用国内镜像加速）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# ────────────────────────────────────────────────────────────────────────────
# 阶段2: 运行阶段 - 精简镜像
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    TZ=Asia/Shanghai

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建非root用户（安全性）
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app/data /app/logs

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health', timeout=5)" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令（使用 uvicorn）
CMD ["uvicorn", "server:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]
