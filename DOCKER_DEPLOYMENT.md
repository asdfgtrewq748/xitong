# 🚀 Docker 部署指南

## 快速开始

### 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 可用内存
- 10GB+ 可用磁盘空间

### 2. 一键部署（推荐）

```bash
# 下载或克隆项目
git clone <repository-url>
cd xitong

# 确保data目录存在并包含必要文件
ls -la data/input/汇总表.csv

# 运行部署脚本
chmod +x docs/scripts/deploy.sh
./docs/scripts/deploy.sh
```

### 3. 访问系统

部署成功后：
- **前端界面**: http://localhost (或服务器IP)
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost/health

---

## 手动部署步骤

### 步骤1: 准备数据文件

```bash
# 确保data目录结构正确
mkdir -p data/input data/output
cp 汇总表.csv data/input/

# 验证文件
ls -la data/input/汇总表.csv
```

### 步骤2: 构建镜像

```bash
# 构建所有服务
docker-compose build

# 或分别构建
docker-compose build backend
docker-compose build frontend
```

### 步骤3: 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤4: 验证部署

```bash
# 检查容器状态
docker-compose ps

# 测试前端
curl http://localhost/health

# 测试后端
curl http://localhost:8000/api/health

# 查看后端日志
docker-compose logs backend | tail -50
```

---

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]
```

### 数据管理

```bash
# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf backup_YYYYMMDD.tar.gz

# 清理输出文件
rm -rf data/output/*
```

### 镜像管理

```bash
# 重新构建（不使用缓存）
docker-compose build --no-cache

# 拉取最新镜像
docker-compose pull

# 清理无用镜像
docker image prune -f

# 查看镜像大小
docker images | grep mining-system
```

---

## 配置说明

### docker-compose.yml

核心配置项：

```yaml
backend:
  ports:
    - "8000:8000"  # 后端API端口
  volumes:
    - ./data:/app/data  # 数据目录挂载（重要！）
    - ./backend/logs:/app/logs  # 日志目录
  environment:
    - MAX_UPLOAD_SIZE_MB=50  # 最大上传文件大小
    - CACHE_ENABLED=true  # 启用缓存

frontend:
  ports:
    - "80:80"  # 前端访问端口
  volumes:
    - ./frontend/logs:/var/log/nginx  # Nginx日志
```

### 环境变量

可在`docker-compose.yml`中修改：

- `MAX_UPLOAD_SIZE_MB`: 最大上传文件大小（默认50MB）
- `CACHE_ENABLED`: 是否启用缓存（默认true）
- `DB_PATH`: 数据库文件路径
- `DATA_DIR`: 数据目录路径

---

## 故障排查

### 问题1: 容器启动失败

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
netstat -tuln | grep -E '80|8000'

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 问题2: 找不到汇总表.csv

```bash
# 检查文件是否存在
docker-compose exec backend ls -la /app/data/input/

# 确认挂载正确
docker-compose exec backend cat /app/data/input/汇总表.csv | head -5

# 重新复制文件
cp 汇总表.csv data/input/
docker-compose restart backend
```

### 问题3: 前端无法访问后端

```bash
# 检查网络
docker network ls
docker network inspect xitong_mining-network

# 测试后端连接
docker-compose exec frontend wget -O- http://backend:8000/api/health

# 重启服务
docker-compose restart
```

### 问题4: 内存不足

```bash
# 查看资源使用
docker stats

# 调整worker数量（编辑docker-compose.yml）
CMD ["uvicorn", "server:app", "--workers", "1"]  # 从2改为1

# 清理缓存
docker system prune -a
```

### 问题5: 数据库初始化失败

```bash
# 检查日志
docker-compose logs backend | grep -i "database\|error"

# 手动初始化
docker-compose exec backend python -c "from db import init_db; init_db()"

# 删除并重建
docker-compose down -v
rm -f data/database.db
docker-compose up -d
```

---

## 更新部署

### 方式1: 使用部署脚本（推荐）

```bash
# 拉取最新代码并更新
./docs/scripts/deploy.sh

# 跳过备份快速更新
./docs/scripts/deploy.sh --skip-backup

# 仅重启服务（不重新构建）
./docs/scripts/deploy.sh --skip-build
```

### 方式2: 手动更新

```bash
# 1. 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 2. 拉取代码
git pull

# 3. 重新构建
docker-compose build

# 4. 重启服务
docker-compose down
docker-compose up -d

# 5. 验证
curl http://localhost/health
curl http://localhost:8000/api/health
```

---

## 生产环境优化

### 1. 使用独立的数据卷

```yaml
volumes:
  - mining-data:/app/data
  - mining-logs:/app/logs

volumes:
  mining-data:
  mining-logs:
```

### 2. 配置资源限制

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

### 3. 启用日志轮转

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. 使用HTTPS

在nginx配置中添加SSL证书：

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ...
}
```

---

## 监控和维护

### 健康检查

系统内置健康检查：

```bash
# 前端健康检查
curl http://localhost/health

# 后端健康检查
curl http://localhost:8000/api/health

# Docker健康状态
docker-compose ps
```

### 日志查看

```bash
# 实时日志
docker-compose logs -f

# 指定服务日志
docker-compose logs -f backend

# 最近N行日志
docker-compose logs --tail=100 backend

# 导出日志
docker-compose logs > logs_$(date +%Y%m%d).txt
```

### 性能监控

```bash
# 资源使用统计
docker stats

# 容器详细信息
docker inspect mining-backend
docker inspect mining-frontend
```

---

## 卸载

### 完全清理

```bash
# 停止并删除容器、网络
docker-compose down

# 删除镜像
docker rmi mining-system-backend:latest
docker rmi mining-system-frontend:latest

# 清理数据（可选）
rm -rf data/output/*
rm -rf backend/logs/*

# 清理所有Docker资源
docker system prune -a --volumes
```

---

## 常见问题FAQ

**Q: 如何修改访问端口？**

A: 编辑`docker-compose.yml`中的ports配置：
```yaml
frontend:
  ports:
    - "8080:80"  # 将80改为8080
```

**Q: 如何增加文件上传大小限制？**

A: 修改环境变量和nginx配置：
```yaml
backend:
  environment:
    - MAX_UPLOAD_SIZE_MB=100  # 改为100MB
```

**Q: 数据在哪里？**

A: 数据存储在项目根目录的`data/`文件夹，通过volume挂载到容器中。

**Q: 如何查看Python依赖版本？**

```bash
docker-compose exec backend pip list
```

**Q: 如何进入容器调试？**

```bash
# 进入后端容器
docker-compose exec backend /bin/bash

# 进入前端容器
docker-compose exec frontend /bin/sh
```

---

## 技术支持

- 查看日志: `docker-compose logs -f`
- 检查状态: `docker-compose ps`
- 重启服务: `docker-compose restart`
- 完整重建: `docker-compose down && docker-compose up -d --build`

如有问题，请提供：
1. `docker-compose ps` 输出
2. `docker-compose logs` 相关日志
3. 系统环境信息（OS、Docker版本等）
