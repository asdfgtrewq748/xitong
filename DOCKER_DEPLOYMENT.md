# 矿山工程分析系统 - Docker 部署指南

## 📦 系统架构

本系统采用Docker容器化部署,包含以下组件:

```
┌─────────────────────────────────────────────┐
│         Nginx (前端 + 反向代理)            │
│              端口: 80, 443                  │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│  Vue.js 前端   │  │  FastAPI 后端   │
│   静态资源     │  │   端口: 8000    │
└────────────────┘  └─────────┬───────┘
                              │
                    ┌─────────▼──────────┐
                    │  SQLite 数据库     │
                    │  (挂载卷持久化)    │
                    └────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

### Windows 一键部署

```powershell
# 使用PowerShell
.\deploy.ps1
```

### Linux/Mac 一键部署

```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 手动部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 检查状态
docker-compose ps
```

## 📁 目录结构

```
MiningSystem/
├── backend/                # 后端代码
│   ├── Dockerfile         # 后端 Dockerfile
│   ├── server.py          # FastAPI 主程序
│   ├── requirements.txt   # Python 依赖
│   └── ...
├── frontend/              # 前端代码
│   ├── Dockerfile         # 前端开发 Dockerfile
│   ├── Dockerfile.prod    # 前端生产 Dockerfile
│   ├── package.json       # Node.js 依赖
│   └── ...
├── nginx/                 # Nginx 配置
│   ├── nginx.conf         # Nginx 主配置
│   └── ssl/               # SSL 证书目录(可选)
├── data/                  # 数据目录(持久化)
│   ├── database.db        # SQLite 数据库
│   └── input/             # 输入数据文件
├── docker-compose.yml     # Docker Compose 配置
├── deploy.sh              # Linux/Mac 部署脚本
├── deploy.ps1             # Windows 部署脚本
└── DOCKER_DEPLOYMENT.md   # 本文档
```

## ⚙️ 配置说明

### docker-compose.yml

```yaml
services:
  backend:
    - 端口: 8000
    - 工作进程: 4 (可根据CPU核心数调整)
    - 数据卷: ./data:/app/data
    
  frontend:
    - 端口: 80 (HTTP), 443 (HTTPS)
    - Nginx 反向代理
    - 静态资源缓存
```

### 环境变量

在 `docker-compose.yml` 中可配置:

```yaml
environment:
  # 后端
  - DATABASE_PATH=/app/data/database.db
  - PYTHONUNBUFFERED=1
  
  # 前端
  - VUE_APP_API_BASE_URL=/api
```

## 🔧 常用命令

### 启动和停止

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器+卷+镜像
docker-compose down -v --rmi all
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart backend
docker-compose restart frontend
```

### 查看状态

```bash
# 查看容器状态
docker-compose ps

# 查看详细信息
docker-compose ps -a

# 查看资源使用
docker stats
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 以root身份进入
docker-compose exec -u root backend bash
```

## 📊 数据持久化

数据通过Docker卷持久化保存:

```yaml
volumes:
  - ./data:/app/data              # 数据库和数据文件
  - backend_logs:/app/logs        # 后端日志
  - frontend_logs:/var/log/nginx  # Nginx日志
```

### 备份数据

```bash
# 备份数据库
docker-compose exec backend cp /app/data/database.db /app/data/database_backup_$(date +%Y%m%d).db

# 从容器复制到宿主机
docker cp mining_backend:/app/data/database.db ./backup/

# 备份整个data目录
tar -czf data_backup_$(date +%Y%m%d).tar.gz ./data/
```

### 恢复数据

```bash
# 复制备份到容器
docker cp ./backup/database.db mining_backend:/app/data/

# 重启服务
docker-compose restart backend
```

## 🔒 安全配置

### HTTPS 配置

1. 将SSL证书放置在 `nginx/ssl/` 目录:
   ```
   nginx/ssl/
   ├── cert.pem
   └── key.pem
   ```

2. 在 `nginx/nginx.conf` 中取消注释HTTPS配置:
   ```nginx
   listen 443 ssl http2;
   ssl_certificate /etc/nginx/ssl/cert.pem;
   ssl_certificate_key /etc/nginx/ssl/key.pem;
   ```

3. 重启服务:
   ```bash
   docker-compose restart frontend
   ```

### 生成自签名证书(测试用)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

## 📈 性能优化

### 后端优化

在 `backend/Dockerfile` 中调整工作进程数:

```dockerfile
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

建议设置为: `CPU核心数 × 2 + 1`

### 前端优化

Nginx已启用:
- Gzip压缩
- 静态资源缓存
- HTTP/2 (如果启用HTTPS)
- Keepalive连接复用

### 资源限制

在 `docker-compose.yml` 中添加资源限制:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs -f

# 检查端口占用
netstat -ano | findstr :80
netstat -ano | findstr :8000

# 清理并重建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查数据库文件权限
docker-compose exec backend ls -la /app/data/

# 重新创建数据库
docker-compose exec backend python -c "import sqlite3; conn = sqlite3.connect('/app/data/database.db'); conn.close()"
```

### 前端无法访问后端API

```bash
# 检查nginx配置
docker-compose exec frontend nginx -t

# 重新加载nginx
docker-compose exec frontend nginx -s reload

# 查看nginx日志
docker-compose logs -f frontend
```

### 容器内存不足

```bash
# 查看容器资源使用
docker stats

# 增加Docker Desktop内存限制
# Settings -> Resources -> Memory
```

## 🌐 生产环境部署建议

1. **使用环境变量管理配置**
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   # 编辑配置
   vim .env
   ```

2. **启用HTTPS**
   - 使用Let's Encrypt免费证书
   - 配置自动续期

3. **配置反向代理**
   - 使用域名访问
   - 配置DNS解析

4. **监控和日志**
   ```bash
   # 使用logrotate管理日志
   # 配置Prometheus+Grafana监控
   ```

5. **备份策略**
   ```bash
   # 定时备份数据库
   0 2 * * * /path/to/backup.sh
   ```

6. **使用PostgreSQL替代SQLite**
   - 取消docker-compose.yml中postgres服务的注释
   - 修改后端数据库连接配置

## 📞 技术支持

- 查看日志: `docker-compose logs -f`
- 健康检查: 
  - 前端: http://localhost/health
  - 后端: http://localhost:8000/api/health
- API文档: http://localhost:8000/docs

## 📝 更新日志

### v1.0.0 (2025-01-16)
- ✅ 完整的Docker容器化配置
- ✅ Nginx反向代理和静态资源服务
- ✅ 生产级后端配置(多进程)
- ✅ 数据持久化和备份方案
- ✅ 健康检查和自动重启
- ✅ 一键部署脚本(Windows/Linux)
- ✅ 完整的部署文档

## 📄 许可证

本项目采用 MIT 许可证
