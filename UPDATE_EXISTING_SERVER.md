# 🔄 更新现有服务器到最新版本

## 📋 快速更新步骤

你的服务器已经部署过项目，现在只需要更新到最新版本：

### 方式一：使用自动化脚本（推荐）⭐

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 进入项目目录
cd /var/www/xitong

# 3. 下载最新的部署脚本
git fetch origin
git checkout origin/master -- server-deploy.sh server-quick-update.sh

# 4. 赋予执行权限
chmod +x server-deploy.sh server-quick-update.sh

# 5. 执行完整部署（第一次更新建议用这个）
./server-deploy.sh
```

---

### 方式二：手动更新（完全控制）

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 进入项目目录
cd /var/www/xitong

# 3. 查看当前状态
git status
docker compose ps

# 4. 备份当前配置（可选但推荐）
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup

# 5. 强制同步到最新代码
git fetch origin
git reset --hard origin/master

# 6. 停止容器
docker compose down

# 7. 重新构建镜像
docker compose build --no-cache

# 8. 启动容器
docker compose up -d

# 9. 查看日志确认启动成功
docker compose logs -f
```

---

### 方式三：最简单的快速重启（仅代码改动）

如果只是 Python/Vue 代码改动，不涉及依赖包：

```bash
# SSH 登录
ssh root@你的服务器IP
cd /var/www/xitong

# 拉取代码并重启
git pull origin master
docker compose restart

# 查看状态
docker compose ps
```

---

## ✅ 验证更新成功

### 1. 检查容器状态
```bash
docker compose ps
```

预期看到：
```
NAME              STATUS
mining-backend    Up XX seconds (healthy)
mining-frontend   Up XX seconds (healthy)
```

### 2. 检查后端服务
```bash
curl http://localhost:8000/health
```

预期返回：
```json
{"status":"healthy"}
```

### 3. 检查前端页面
```bash
# 检查前端是否可访问
curl -I http://localhost
```

或直接浏览器访问：`http://服务器IP`

### 4. 查看最新代码版本
```bash
git log --oneline -3
```

预期看到：
```
492e4da feat: 添加服务器部署脚本和完整部署指南
53413c9 fix: 极简化CI检查，完全移除依赖安装步骤
...
```

---

## 🔍 常见问题处理

### 问题1: git pull 提示有冲突

```bash
# 强制覆盖本地修改
git fetch origin
git reset --hard origin/master
```

### 问题2: 容器启动失败

```bash
# 查看详细错误
docker compose logs backend
docker compose logs frontend

# 清理并重建
docker compose down -v
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

### 问题3: 端口被占用

```bash
# 检查端口占用
netstat -tunlp | grep -E "80|8000"

# 停止占用端口的进程
kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### 问题4: 数据库没有数据

```bash
# 重新初始化数据库
./quick-init-fixed.sh

# 或手动执行
docker compose exec backend python3 -c "
import pandas as pd
from sqlalchemy import create_engine
df = pd.read_csv('/app/data/input/汇总表.csv')
engine = create_engine('sqlite:////app/data/database.db')
df.to_sql('records', engine, if_exists='replace', index=False)
print('导入完成')
"
```

---

## 📊 更新前后对比

### 主要更新内容

1. **✅ CI/CD 简化** - 移除了 Docker 构建依赖，GitHub Actions 不再失败
2. **✅ 数据库路径修复** - 修复了 `db.py` 中的路径配置错误
3. **✅ 前端代码清理** - 清除了所有 Git 冲突标记
4. **✅ 部署脚本** - 新增自动化部署脚本，方便后续更新

### 文件变更

- `.github/workflows/deploy.yml` - 简化的 CI/CD 配置
- `backend/db.py` - 修复数据库路径
- `backend/server.py` - 添加启动检查
- `frontend/src/App.vue` - 清理代码
- `frontend/src/main.js` - 清理冲突标记
- `frontend/src/router/index.js` - 清理路由配置
- `frontend/src/components/DashboardView.vue` - 优化布局
- **新增**: `server-deploy.sh` - 自动部署脚本
- **新增**: `server-quick-update.sh` - 快速更新脚本
- **新增**: `SERVER_DEPLOYMENT_GUIDE.md` - 部署指南

---

## ⚡ 推荐操作流程（一键执行）

```bash
#!/bin/bash
# 复制以下内容保存为 update-now.sh，然后执行 bash update-now.sh

echo "🚀 开始更新服务器..."

# 进入项目目录
cd /var/www/xitong || exit 1

# 拉取最新代码
echo "📥 拉取最新代码..."
git fetch origin
git reset --hard origin/master

# 下载部署脚本
chmod +x server-deploy.sh server-quick-update.sh

# 执行完整部署
echo "🔨 重新构建并部署..."
./server-deploy.sh

echo "✅ 更新完成！"
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
```

---

## 📞 需要帮助？

如果更新过程中遇到问题：

1. **查看容器日志**
   ```bash
   docker compose logs backend --tail=50
   docker compose logs frontend --tail=50
   ```

2. **检查磁盘空间**
   ```bash
   df -h
   docker system df
   ```

3. **重置到干净状态**
   ```bash
   cd /var/www/xitong
   git reset --hard origin/master
   docker compose down -v
   docker system prune -a -f
   docker compose up -d
   ```

---

**更新时间**: 2025-10-24  
**适用版本**: master 分支最新代码
