# Docker 容器健康检查失败排查指南

## 问题现象

```
dependency failed to start: container mining-backend is unhealthy
```

## 常见原因和解决方案

### 原因 1: 健康检查命令失败

**现象：** 容器启动但健康检查一直失败

**排查步骤：**

```bash
# 1. 查看容器日志
sudo docker compose logs backend

# 2. 检查健康检查状态
sudo docker inspect mining-backend --format='{{json .State.Health}}' | python3 -m json.tool

# 3. 手动进入容器测试健康检查命令
sudo docker exec -it mining-backend bash
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=5)"
```

**解决方案：**

我已经修改了健康检查命令，从使用 `requests` 库改为使用 Python 内置的 `urllib`，避免依赖问题。

修改内容：
- ✅ 使用 `urllib.request` 代替 `requests`（无需额外依赖）
- ✅ 增加启动等待时间 `start_period: 60s`（原来 40s）
- ✅ 增加重试次数 `retries: 5`（原来 3）

### 原因 2: 应用启动太慢

**现象：** 应用需要较长时间初始化，健康检查开始太早

**解决方案：**

```yaml
# docker-compose.yml 中已调整
healthcheck:
  start_period: 60s  # 给应用 60 秒的启动时间
  interval: 30s      # 每 30 秒检查一次
  timeout: 10s       # 单次检查 10 秒超时
  retries: 5         # 失败 5 次才判定为 unhealthy
```

### 原因 3: 端口未正确监听

**排查步骤：**

```bash
# 进入容器检查端口
sudo docker exec -it mining-backend bash
netstat -tulpn | grep 8000

# 或者从外部测试
curl http://localhost:8000/api/health
```

**解决方案：**

确保 `server.py` 中 uvicorn 正确配置：

```python
# backend/server.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 原因 4: 数据目录权限问题

**现象：** 日志显示 `Permission denied`

**排查步骤：**

```bash
# 检查目录权限
ls -la backend/data backend/logs

# 查看容器内的用户
sudo docker exec mining-backend id
```

**解决方案：**

```bash
# 创建目录并设置权限
sudo mkdir -p backend/data backend/logs
sudo chmod 777 backend/data backend/logs

# 或者更安全的方式（匹配容器内的用户）
sudo chown -R 999:999 backend/data backend/logs  # appuser 的 UID/GID
```

### 原因 5: 依赖安装不完整

**现象：** 日志显示 `ModuleNotFoundError`

**排查步骤：**

```bash
# 进入容器检查 Python 包
sudo docker exec -it mining-backend bash
pip list

# 测试导入
python -c "import fastapi, uvicorn, pandas, numpy"
```

**解决方案：**

```bash
# 重新构建镜像（不使用缓存）
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

## 快速修复步骤

### 方法一：使用修复脚本（推荐）

我已经创建了 `quick-fix.sh` 脚本，会自动执行所有修复步骤：

```bash
# 上传脚本到服务器
scp quick-fix.sh admin@server:/var/www/xitong/

# 在服务器上执行
cd /var/www/xitong
bash quick-fix.sh
```

### 方法二：手动修复

```bash
# 1. 停止所有容器
sudo docker compose down

# 2. 创建并修复目录权限
sudo mkdir -p backend/data backend/logs frontend/logs
sudo chmod 777 backend/data backend/logs frontend/logs

# 3. 拉取最新的 docker-compose.yml（已优化健康检查）
git pull

# 4. 如果有本地构建的镜像，导入
sudo docker load -i /tmp/mining-backend.tar
sudo docker load -i /tmp/mining-frontend.tar

# 5. 启动服务
sudo docker compose up -d

# 6. 查看日志
sudo docker compose logs -f backend
```

## 监控和诊断

### 实时监控容器健康状态

```bash
# 持续监控
watch -n 5 'sudo docker compose ps'

# 查看健康检查详情
sudo docker inspect mining-backend --format='{{json .State.Health}}' | python3 -m json.tool
```

### 查看详细日志

```bash
# 实时日志
sudo docker compose logs -f

# 只看后端
sudo docker compose logs -f backend

# 最后 100 行
sudo docker compose logs --tail=100 backend

# 带时间戳
sudo docker compose logs -f -t backend
```

### 手动测试健康检查

```bash
# 从宿主机测试
curl http://localhost:8000/api/health

# 从容器内测试
sudo docker exec mining-backend curl http://localhost:8000/api/health

# 使用 Python 测试（和健康检查一样的命令）
sudo docker exec mining-backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/health', timeout=5).read())"
```

## 预防措施

### 1. 健康检查配置最佳实践

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=5)"]
  interval: 30s        # 检查间隔不要太频繁
  timeout: 10s         # 单次检查超时时间
  retries: 5           # 足够的重试次数
  start_period: 60s    # 给应用足够的启动时间
```

### 2. 确保 /api/health 端点轻量

```python
# backend/server.py
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}  # 不要执行数据库查询等重操作
```

### 3. 构建优化

```dockerfile
# 使用 --prefer-binary 优先使用预编译包
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
```

### 4. 定期清理

```bash
# 清理停止的容器和无用镜像
sudo docker system prune -a

# 清理构建缓存
sudo docker builder prune
```

## 常见错误代码

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `container is unhealthy` | 健康检查失败 | 增加 `start_period` 或修复健康检查命令 |
| `port already in use` | 端口被占用 | 停止占用端口的进程或修改端口 |
| `no such file or directory` | 挂载目录不存在 | 创建目录 `mkdir -p backend/data` |
| `permission denied` | 权限不足 | 修改权限 `chmod 777 backend/data` |
| `ModuleNotFoundError` | Python 包未安装 | 重新构建镜像 |

## 获取帮助

如果问题仍未解决，请提供以下信息：

```bash
# 1. 容器状态
sudo docker compose ps

# 2. 后端日志（最后 100 行）
sudo docker compose logs --tail=100 backend

# 3. 健康检查详情
sudo docker inspect mining-backend --format='{{json .State.Health}}'

# 4. 系统信息
docker info
docker --version
docker compose version
```

将以上信息保存到文本文件并提供给技术支持。
