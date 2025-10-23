# Docker部署指南

## 概述

本文档详细说明如何使用Docker部署煤层地质建模系统，包括本地开发、生产环境部署和CI/CD自动化流程。

---

## 快速开始

### 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd xitong

# 2. 运行部署脚本
./deploy.sh

# 3. 访问系统
# 前端: http://localhost
# 后端API文档: http://localhost:8000/docs
```

---

## 架构说明

### 系统架构

前端容器(Nginx) ←→ 后端容器(FastAPI)

- 前端: 端口80, Nginx + Vue 3
- 后端: 端口8000, Python 3.11 + FastAPI
- 网络: mining-network (bridge)

---

## 环境要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘: 10GB
- OS: Linux/macOS/Windows 10+

### 软件依赖
- Docker >= 20.10
- Docker Compose >= 1.29

---

## 本地部署

### 1. 构建镜像
```bash
docker-compose build
```

### 2. 启动服务
```bash
docker-compose up -d
```

### 3. 验证部署
```bash
./health-check.sh
# 或
curl http://localhost/health
curl http://localhost:8000/api/health
```

---

## 生产部署

### 1. 服务器准备
```bash
sudo mkdir -p /opt/mining-system
cd /opt/mining-system
git clone <your-repo-url> .
```

### 2. 一键部署
```bash
./deploy.sh
```

### 3. 配置防火墙
```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 常用命令

### 启动和停止
```bash
docker-compose up -d          # 启动
docker-compose down           # 停止
docker-compose restart        # 重启
docker-compose ps             # 查看状态
```

### 查看日志
```bash
docker-compose logs           # 所有日志
docker-compose logs -f backend   # 跟踪后端日志
docker-compose logs --tail=100   # 最后100行
```

### 执行命令
```bash
docker-compose exec backend bash    # 进入后端容器
docker-compose exec frontend sh     # 进入前端容器
```

---

## 故障排查

### 容器无法启动
```bash
# 查看日志
docker-compose logs backend

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 健康检查失败
```bash
# 手动测试
curl http://localhost/health
curl http://localhost:8000/api/health

# 查看详细状态
docker inspect mining-backend
```

### 数据丢失
```bash
# 检查数据卷
ls -la backend/data

# 从备份恢复
cp -r backups/最新备份/* backend/data/
```

---

## CI/CD配置

### GitHub Secrets设置
- `DOCKER_USERNAME`: Docker Hub用户名
- `DOCKER_PASSWORD`: Docker Hub密码
- `SERVER_HOST`: 服务器IP
- `SERVER_USER`: SSH用户名
- `SERVER_SSH_KEY`: SSH私钥

### 自动部署流程
1. Push代码到main分支
2. GitHub Actions自动构建镜像
3. 推送到Docker Hub
4. SSH连接服务器部署
5. 健康检查

---

## 备份和恢复

### 自动备份
```bash
# 创建定时任务
crontab -e
# 每天凌晨3点备份
0 3 * * * cd /opt/mining-system && ./deploy.sh --skip-build
```

### 手动备份
```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data

# 恢复数据
tar -xzf backup-20250119.tar.gz
```

---

## 附录

### 部署脚本选项
```bash
./deploy.sh                  # 完整部署
./deploy.sh --skip-backup    # 跳过备份
./deploy.sh --skip-build     # 只重启
./deploy.sh --logs           # 查看日志
```

### 健康检查选项
```bash
./health-check.sh            # 完整检查
./health-check.sh --logs     # 包含日志
```

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19
