# 本地构建 + 服务器部署指南

本文档介绍如何在本地构建 Docker 镜像，然后上传到服务器部署，避免服务器网络问题导致的构建失败。

## 📋 准备工作

### 本地环境要求
- ✅ Docker Desktop 已安装并运行
- ✅ 有足够的磁盘空间（至少 5GB）
- ✅ Git Bash 或其他 SSH 客户端

### 服务器环境要求
- ✅ Docker 和 Docker Compose 已安装
- ✅ SSH 访问权限
- ✅ `/tmp` 目录有足够空间（至少 3GB）

---

## 🚀 方案一：本地构建 + tar 导出（推荐）

这种方式适合服务器网络不稳定或没有镜像仓库的情况。

### 步骤 1: 本地构建镜像

在项目根目录执行（Windows PowerShell）：

```powershell
.\build-and-export.ps1
```

该脚本会：
1. ✅ 检查 Docker 状态
2. 🗑️ 清理旧镜像（可选）
3. 🔨 构建后端镜像
4. 🔨 构建前端镜像
5. 📦 导出为 tar 文件到 `./docker-images/` 目录

构建完成后会生成：
- `docker-images/mining-backend.tar` （约 800-1200 MB）
- `docker-images/mining-frontend.tar` （约 50-100 MB）

### 步骤 2: 上传镜像到服务器

#### 方法 A: 使用 SCP（Git Bash）

```bash
# 修改服务器地址
SERVER="admin@your-server-ip"

# 上传后端镜像
scp ./docker-images/mining-backend.tar $SERVER:/tmp/

# 上传前端镜像
scp ./docker-images/mining-frontend.tar $SERVER:/tmp/
```

#### 方法 B: 使用生成的脚本

修改 `docker-images/upload-to-server.sh` 中的服务器地址，然后在 Git Bash 中执行：

```bash
cd docker-images
bash upload-to-server.sh
```

### 步骤 3: 服务器端导入并启动

#### 方法 A: 手动执行

```bash
# SSH 登录服务器
ssh admin@your-server

# 进入项目目录
cd /var/www/xitong

# 停止旧容器
sudo docker compose down

# 导入镜像
sudo docker load -i /tmp/mining-backend.tar
sudo docker load -i /tmp/mining-frontend.tar

# 验证镜像
sudo docker images | grep mining-system

# 启动服务
sudo docker compose up -d

# 查看状态
sudo docker compose ps
sudo docker compose logs -f
```

#### 方法 B: 使用脚本（推荐）

先将 `load-and-start.sh` 上传到服务器：

```bash
scp load-and-start.sh admin@your-server:/var/www/xitong/
```

然后在服务器上执行：

```bash
cd /var/www/xitong
bash load-and-start.sh
```

脚本会自动完成导入、启动和健康检查。

---

## 🐳 方案二：推送到镜像仓库（适合团队）

如果有 Docker Hub 账号或私有镜像仓库，可以用这种方式。

### 步骤 1: 本地构建并推送

```bash
# 登录 Docker Hub
docker login

# 构建并打标签
docker build -t yourusername/mining-backend:latest ./backend
docker build -t yourusername/mining-frontend:latest ./frontend

# 推送到仓库
docker push yourusername/mining-backend:latest
docker push yourusername/mining-frontend:latest
```

### 步骤 2: 修改 docker-compose.yml

修改服务器上的 `docker-compose.yml`，将 `build` 改为 `image`：

```yaml
services:
  backend:
    image: yourusername/mining-backend:latest
    # 注释掉 build 配置
    # build:
    #   context: ./backend
    #   dockerfile: Dockerfile
    ...

  frontend:
    image: yourusername/mining-frontend:latest
    # 注释掉 build 配置
    # build:
    #   context: ./frontend
    #   dockerfile: Dockerfile
    ...
```

### 步骤 3: 服务器端拉取并启动

```bash
cd /var/www/xitong

# 停止旧服务
sudo docker compose down

# 拉取最新镜像
sudo docker compose pull

# 启动服务
sudo docker compose up -d
```

---

## 🔍 验证部署

### 检查容器状态

```bash
# 查看容器运行状态
sudo docker compose ps

# 应该看到两个容器都是 Up (healthy)
```

### 测试服务

```bash
# 测试后端 API
curl http://localhost:8000/api/health

# 测试前端
curl http://localhost/

# 查看日志
sudo docker compose logs -f
```

### 浏览器访问

打开浏览器访问：`http://服务器IP`

---

## 🛠️ 常见问题

### 问题 1: 上传速度慢

**解决方案：**
- 使用压缩：`gzip mining-backend.tar` 再上传
- 或使用 rsync：`rsync -avz --progress mining-backend.tar admin@server:/tmp/`

### 问题 2: 镜像导入失败

**错误信息：** `Error processing tar file`

**解决方案：**
```bash
# 检查文件完整性
md5sum mining-backend.tar

# 重新上传或使用 rsync 的校验功能
rsync -avz --checksum mining-backend.tar admin@server:/tmp/
```

### 问题 3: 容器启动失败

**解决方案：**
```bash
# 查看详细日志
sudo docker compose logs backend
sudo docker compose logs frontend

# 检查端口占用
sudo netstat -tulpn | grep -E '80|8000'

# 重新启动
sudo docker compose restart
```

### 问题 4: 健康检查失败

**解决方案：**
```bash
# 进入容器内部排查
sudo docker exec -it mining-backend bash
sudo docker exec -it mining-frontend sh

# 手动测试健康检查命令
python -c "import requests; print(requests.get('http://localhost:8000/api/health').text)"
curl -f http://localhost/health
```

---

## 📝 优化建议

### 1. 使用多阶段构建缓存

在 `.dockerignore` 中排除不必要的文件：

```
# backend/.dockerignore
__pycache__/
*.pyc
*.pyo
.git/
.env
tests/
docs/
```

### 2. 设置构建缓存

```bash
# 使用 BuildKit 加速构建
export DOCKER_BUILDKIT=1

# 本地构建时启用缓存
docker build --cache-from mining-system-backend:latest -t mining-system-backend:latest ./backend
```

### 3. 定期清理

```bash
# 清理未使用的镜像和容器
docker system prune -a

# 清理构建缓存
docker builder prune
```

---

## 🔄 更新流程

当代码更新后，重复以下步骤：

1. 本地构建新镜像
2. 打上新标签（如 `v1.0.1`）
3. 导出或推送镜像
4. 服务器导入或拉取
5. 重启服务

```bash
# 打标签示例
docker tag mining-system-backend:latest mining-system-backend:v1.0.1
docker save mining-system-backend:v1.0.1 -o mining-backend-v1.0.1.tar
```

---

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. 错误日志：`docker compose logs`
2. 容器状态：`docker compose ps`
3. 系统信息：`docker info`
4. 镜像列表：`docker images`

---

## 附录：脚本说明

### build-and-export.ps1
- 功能：本地构建并导出镜像
- 平台：Windows PowerShell
- 输出：`./docker-images/*.tar`

### load-and-start.sh
- 功能：服务器端导入并启动
- 平台：Linux Bash
- 要求：sudo 权限

### upload-to-server.sh
- 功能：自动上传镜像到服务器
- 平台：Git Bash / Linux
- 需要：修改服务器地址
