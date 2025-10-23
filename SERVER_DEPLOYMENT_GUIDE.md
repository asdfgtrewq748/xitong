# 🚀 服务器部署指南

## 📋 概述

本指南说明如何在服务器上部署和更新煤层地质建模系统。

## 🔧 当前 CI/CD 配置

**GitHub Actions 配置（简化版）**:
- ✅ 自动检查代码语法
- ✅ 验证文件完整性
- ❌ **不自动构建 Docker 镜像**
- ❌ **不自动部署到服务器**

**原因**: 避免需要配置 Docker Hub 认证和服务器 SSH 密钥。

## 🎯 部署流程

### 方案一: 完整部署（首次部署或大版本更新）

在服务器上执行：

```bash
# 1. 进入项目目录
cd /var/www/xitong

# 2. 修改部署脚本中的项目路径（首次需要）
vim server-deploy.sh
# 将 PROJECT_DIR="/var/www/xitong" 改为实际路径

# 3. 赋予执行权限
chmod +x server-deploy.sh

# 4. 执行部署
./server-deploy.sh
```

**部署脚本会自动完成**:
1. 拉取最新代码
2. 停止旧容器
3. 清理未使用的资源
4. 重新构建 Docker 镜像
5. 启动新容器
6. 健康检查

**适用场景**:
- 首次部署
- 依赖包版本更新（requirements.txt 或 package.json 变化）
- Dockerfile 修改
- 需要清理缓存

---

### 方案二: 快速更新（小改动或配置更新）

在服务器上执行：

```bash
# 1. 进入项目目录
cd /var/www/xitong

# 2. 赋予执行权限（首次需要）
chmod +x server-quick-update.sh

# 3. 执行快速更新
./server-quick-update.sh
```

**快速更新会自动完成**:
1. 拉取最新代码
2. 重启容器（不重新构建）

**适用场景**:
- Python 代码修改（backend/）
- Vue 组件修改（frontend/src/）
- 配置文件修改（docker-compose.yml）
- 数据库初始化脚本更新

**⚠️ 注意**: 如果修改了依赖包，必须使用方案一重新构建。

---

### 方案三: 手动部署（完全控制）

```bash
# 1. 拉取代码
cd /var/www/xitong
git pull origin master

# 2. 停止容器
docker compose down

# 3. 重新构建（如果需要）
docker compose build

# 4. 启动容器
docker compose up -d

# 5. 查看日志
docker compose logs -f
```

---

## 📊 部署后验证

### 1. 检查容器状态
```bash
docker compose ps
```

预期输出：
```
NAME              STATUS          PORTS
mining-backend    Up 30 seconds   0.0.0.0:8000->8000/tcp
mining-frontend   Up 30 seconds   0.0.0.0:80->80/tcp
```

### 2. 检查后端健康
```bash
curl http://localhost:8000/health
```

预期输出：
```json
{"status": "healthy"}
```

### 3. 检查前端访问
```bash
curl http://localhost | grep "煤层"
```

或在浏览器访问: `http://服务器IP`

### 4. 检查数据库
```bash
# 进入后端容器
docker exec -it mining-backend bash

# 检查数据库
python3 -c "
from db import get_engine
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT COUNT(*) FROM records')
    print(f'数据库记录数: {result.fetchone()[0]}')
"
```

预期输出: `数据库记录数: 1341`

---

## 🔄 日常工作流程

### 本地开发完成后

1. **本地提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin master
   ```

2. **GitHub Actions 自动检查**
   - 访问 https://github.com/asdfgtrewq748/xitong/actions
   - 确认 ✅ 检查通过

3. **服务器部署**
   - SSH 登录服务器
   - 执行部署脚本:
     ```bash
     cd /var/www/xitong
     ./server-quick-update.sh  # 快速更新
     # 或
     ./server-deploy.sh        # 完整部署
     ```

---

## 🛠️ 故障排查

### 容器启动失败

```bash
# 查看日志
docker compose logs backend
docker compose logs frontend

# 检查端口占用
netstat -tunlp | grep -E "80|8000"

# 重新构建
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 数据库没有数据

```bash
# 使用初始化脚本
./quick-init-fixed.sh
```

### 前端访问 404

```bash
# 检查 Nginx 配置
docker exec mining-frontend cat /etc/nginx/conf.d/default.conf

# 重启前端
docker compose restart frontend
```

### 后端 API 报错

```bash
# 查看后端日志
docker compose logs -f backend

# 进入容器调试
docker exec -it mining-backend bash
python3 -c "import server; print('OK')"
```

---

## 📈 监控和维护

### 查看实时日志
```bash
# 所有服务
docker compose logs -f

# 仅后端
docker compose logs -f backend

# 仅前端
docker compose logs -f frontend
```

### 磁盘空间管理
```bash
# 查看 Docker 占用空间
docker system df

# 清理未使用的资源
docker system prune -a --volumes
```

### 定期备份
```bash
# 备份数据库
cp backend/data/database.db backend/data/database.db.$(date +%Y%m%d)

# 备份整个项目
tar -czf xitong-backup-$(date +%Y%m%d).tar.gz /var/www/xitong
```

---

## 🔐 安全建议

1. **防火墙配置**
   ```bash
   # 只允许必要端口
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp
   ufw enable
   ```

2. **Nginx 反向代理**（生产环境推荐）
   - 配置 SSL 证书
   - 隐藏后端端口 8000
   - 添加访问日志

3. **定期更新**
   ```bash
   # 更新系统包
   apt update && apt upgrade -y
   
   # 更新 Docker
   apt install docker-ce docker-ce-cli containerd.io
   ```

---

## 📞 常见问题

**Q: 为什么不用 GitHub Actions 自动部署？**  
A: 需要配置 Docker Hub 和 SSH 密钥，简化版只做代码检查，部署手动控制更安全。

**Q: 更新代码后是否需要重新构建？**  
A: 
- Python/Vue 代码改动 → 只需重启（`server-quick-update.sh`）
- 依赖包改动 → 需要重新构建（`server-deploy.sh`）
- Dockerfile 改动 → 需要重新构建

**Q: 如何回滚到之前的版本？**  
A:
```bash
# 查看提交历史
git log --oneline

# 回滚到指定版本
git reset --hard <commit-hash>

# 重新部署
./server-deploy.sh
```

**Q: 生产环境需要修改什么？**  
A:
- 修改 `docker-compose.yml` 中的端口映射
- 配置环境变量（`.env` 文件）
- 设置 Nginx 反向代理和 SSL
- 配置域名解析

---

## 📚 相关文档

- [Docker 部署指南](DOCKER_README.md)
- [数据库初始化指南](docs/DATABASE_INIT_GUIDE.md)
- [性能优化指南](backend/PERFORMANCE_GUIDE.md)

---

**最后更新**: 2025-10-24  
**维护者**: 系统管理员
