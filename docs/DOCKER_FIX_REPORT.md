# Docker 配置修复报告

## 修复日期
2025年10月20日

## 问题诊断

在服务器上执行 `docker compose up` 时出现的错误，经过分析发现以下问题：

### 1. 后端健康检查依赖缺失
**问题描述：**
- `backend/Dockerfile` 中的健康检查使用了 `requests` 库
- 但 `backend/requirements.txt` 中未包含此依赖
- 导致容器启动后健康检查失败

**错误表现：**
```bash
ModuleNotFoundError: No module named 'requests'
```

**修复方案：**
在 `backend/requirements.txt` 中添加：
```
requests==2.31.0
```

### 2. 前端健康检查命令错误
**问题描述：**
- `frontend/Dockerfile` 和 `docker-compose.yml` 中使用了 `wget` 命令
- 但 nginx:alpine 镜像默认只包含 `curl`，不包含 `wget`
- 导致健康检查脚本执行失败

**错误表现：**
```bash
/bin/sh: wget: not found
```

**修复方案：**
将健康检查命令从 `wget` 改为 `curl`：
```dockerfile
# 修改前
CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# 修改后
CMD curl -f http://localhost/ || exit 1
```

同时在 `docker-compose.yml` 中也做相应修改。

### 3. 挂载目录不存在
**问题描述：**
- `docker-compose.yml` 中挂载了以下目录：
  - `./backend/data`
  - `./backend/logs`
  - `./frontend/logs`
- 这些目录在首次部署时可能不存在
- 某些 Docker 版本会因此报错

**修复方案：**
创建必要的目录：
```bash
mkdir -p backend/data backend/logs frontend/logs
```

或使用 PowerShell：
```powershell
New-Item -ItemType Directory -Path backend\data,backend\logs,frontend\logs -Force
```

## 修复后的配置文件

### backend/requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
pandas==2.2.2
numpy==1.26.4
scipy==1.13.1
scikit-learn==1.5.0
python-multipart==0.0.9
requests==2.31.0  # 新增
```

### frontend/Dockerfile
```dockerfile
# 健康检查（使用 curl 替代 wget）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1
```

### docker-compose.yml
```yaml
# frontend 服务的健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 5s
```

## 部署验证步骤

修复后，按以下步骤验证：

### 1. 清理旧容器和镜像
```bash
# 停止并删除旧容器
docker compose down

# 删除旧镜像（强制重新构建）
docker rmi mining-system-backend:latest mining-system-frontend:latest
```

### 2. 重新构建并启动
```bash
# 构建镜像
docker compose build --no-cache

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

### 3. 验证服务状态
```bash
# 检查容器状态
docker compose ps

# 检查健康状态
docker inspect mining-backend --format='{{.State.Health.Status}}'
docker inspect mining-frontend --format='{{.State.Health.Status}}'

# 测试后端API
curl http://localhost:8000/api/health

# 测试前端
curl http://localhost/
```

### 4. 预期结果
- 所有容器状态为 `Up (healthy)`
- 后端 API 返回健康状态
- 前端页面正常访问

## 常见问题排查

### 容器无法启动
```bash
# 查看详细日志
docker compose logs backend
docker compose logs frontend
```

### 健康检查一直失败
```bash
# 进入容器内部排查
docker exec -it mining-backend bash
docker exec -it mining-frontend sh

# 手动执行健康检查命令
python -c "import requests; requests.get('http://localhost:8000/api/health')"
curl -f http://localhost/health
```

### 端口冲突
如果 80 或 8000 端口被占用，修改 `docker-compose.yml`：
```yaml
ports:
  - "8080:80"    # 前端改用8080
  - "8001:8000"  # 后端改用8001
```

## 生产环境建议

1. **环境变量配置**
   - 创建 `.env` 文件配置敏感信息
   - 不要在镜像中硬编码密钥

2. **数据持久化**
   - 使用命名卷或绑定挂载保存数据
   - 定期备份 `backend/data` 目录

3. **日志管理**
   - 配置日志轮转避免磁盘占满
   - 使用日志聚合工具（如 ELK）

4. **资源限制**
   - 根据服务器资源调整 `deploy.resources`
   - 监控容器资源使用情况

5. **安全加固**
   - 启用 HTTPS（配置 SSL 证书）
   - 限制容器权限
   - 定期更新基础镜像

## 总结

本次修复解决了三个关键问题：
1. ✅ 添加缺失的 `requests` 依赖
2. ✅ 修正健康检查命令（wget → curl）
3. ✅ 创建必要的挂载目录

修复后系统可以正常启动并通过健康检查。
