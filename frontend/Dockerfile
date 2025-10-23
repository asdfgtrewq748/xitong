# ============================================================================
# 前端 Dockerfile - 多阶段构建 + Nginx生产优化
# ============================================================================
# 阶段1: 构建 Vue 应用
# 阶段2: Nginx 服务静态文件
# ============================================================================

# ────────────────────────────────────────────────────────────────────────────
# 阶段1: 构建阶段 - 编译Vue应用
# ────────────────────────────────────────────────────────────────────────────
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /build

# 复制package文件（利用Docker缓存）
COPY package*.json ./

# 安装依赖（使用国内镜像加速）
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# ────────────────────────────────────────────────────────────────────────────
# 阶段2: 运行阶段 - Nginx服务
# ────────────────────────────────────────────────────────────────────────────
FROM nginx:1.25-alpine

# 设置环境变量
ENV TZ=Asia/Shanghai

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 删除默认nginx配置
RUN rm /etc/nginx/conf.d/default.conf

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/conf.d/

# 从构建阶段复制dist文件
COPY --from=builder /build/dist /usr/share/nginx/html

# 创建非root用户（nginx已经是非root）
RUN chown -R nginx:nginx /usr/share/nginx/html

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# 暴露端口
EXPOSE 80

# 启动nginx（前台运行）
CMD ["nginx", "-g", "daemon off;"]
