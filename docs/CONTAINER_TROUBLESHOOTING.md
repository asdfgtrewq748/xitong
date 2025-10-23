# 🔧 Docker 容器问题排查指南

## 问题: "No such container: mining-backend"

这个错误说明容器名称不对或容器没有运行。

---

## 🚀 快速解决方案

### 步骤 1: 检查容器状态

在服务器上执行:

```bash
cd /var/www/xitong

# 查看所有容器
sudo docker ps -a

# 查看 docker compose 服务
sudo docker compose ps
```

你会看到实际的容器名称，可能是:
- `xitong-backend-1` (常见)
- `xitong_backend_1` (旧版 compose)
- `mining-backend` (如果你设置了)
- 或其他名称

---

### 步骤 2: 使用自动化脚本 (推荐)

```bash
# 赋予执行权限
chmod +x fix-container-names.sh

# 执行脚本
bash fix-container-names.sh
```

这个脚本会:
1. ✅ 自动找到正确的容器名称
2. ✅ 检查容器状态
3. ✅ 复制 CSV 文件
4. ✅ 执行数据导入
5. ✅ 验证结果

---

### 步骤 3: 手动执行 (如果脚本失败)

#### 3.1 查找实际容器名称

```bash
# 列出所有容器
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 输出示例:
# NAMES                STATUS              PORTS
# xitong-backend-1     Up 2 hours         0.0.0.0:8000->8000/tcp
# xitong-frontend-1    Up 2 hours         0.0.0.0:80->80/tcp
```

找到 backend 容器的实际名称，比如 `xitong-backend-1`

#### 3.2 使用正确的容器名称

```bash
# 设置变量（替换为你的实际名称）
BACKEND_CONTAINER="xitong-backend-1"  # ← 改成你的容器名

# 查看日志
sudo docker logs $BACKEND_CONTAINER

# 复制 CSV
sudo docker cp data/input/汇总表.csv $BACKEND_CONTAINER:/app/data/input/汇总表.csv

# 执行导入
sudo docker exec $BACKEND_CONTAINER python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db
```

---

## 🔍 常见容器名称模式

Docker Compose 的容器命名规则:

### 新版本 (Docker Compose v2)
```
格式: <项目名>-<服务名>-<序号>
示例: xitong-backend-1
     xitong-frontend-1
```

### 旧版本 (Docker Compose v1)
```
格式: <项目名>_<服务名>_<序号>
示例: xitong_backend_1
     xitong_frontend_1
```

### 自定义名称
```
通过 container_name 指定
示例: mining-backend
     mining-frontend
```

---

## 📋 完整排查流程

### 1. 检查 Docker Compose 配置

```bash
cd /var/www/xitong

# 查看配置
cat docker-compose.yml | grep container_name

# 如果有 container_name，使用那个名称
# 如果没有，使用项目名-服务名-序号
```

### 2. 检查容器是否存在

```bash
# 查看所有容器（包括停止的）
sudo docker ps -a | grep backend

# 如果没有输出，说明容器不存在，需要创建:
sudo docker compose up -d
```

### 3. 检查容器是否运行

```bash
# 只看运行中的容器
sudo docker ps | grep backend

# 如果容器存在但没运行，启动它:
sudo docker compose start backend
# 或重启所有服务:
sudo docker compose restart
```

### 4. 查看容器日志

```bash
# 使用 docker compose（推荐）
sudo docker compose logs backend

# 或使用容器名
sudo docker logs <实际容器名>

# 实时查看
sudo docker compose logs -f backend
```

### 5. 进入容器检查

```bash
# 进入容器
sudo docker exec -it <容器名> bash

# 检查文件
ls -la /app/data/
ls -la /app/scripts/

# 手动执行导入
python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db

# 退出容器
exit
```

---

## 🛠️ 使用 Docker Compose 命令 (推荐)

不需要记住容器名称，直接用服务名:

```bash
cd /var/www/xitong

# 查看服务状态
sudo docker compose ps

# 查看日志
sudo docker compose logs backend
sudo docker compose logs frontend

# 重启服务
sudo docker compose restart backend

# 执行命令
sudo docker compose exec backend python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db

# 复制文件
sudo docker compose cp data/input/汇总表.csv backend:/app/data/input/汇总表.csv
```

---

## 💡 推荐解决方案

### 方案 A: 使用自动化脚本 (最简单)

```bash
cd /var/www/xitong
chmod +x fix-container-names.sh
bash fix-container-names.sh
```

### 方案 B: 使用 Docker Compose (最可靠)

```bash
cd /var/www/xitong

# 1. 确保容器运行
sudo docker compose up -d

# 2. 等待健康检查
sleep 30

# 3. 复制 CSV
sudo docker compose cp data/input/汇总表.csv backend:/app/data/input/汇总表.csv

# 4. 执行导入
sudo docker compose exec backend python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db

# 5. 验证
sudo docker compose exec backend python -c "
from sqlalchemy import create_engine, select, func, MetaData
engine = create_engine('sqlite:////app/data/database.db')
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables['records']
with engine.connect() as conn:
    count = conn.execute(select(func.count()).select_from(table)).scalar()
    print(f'数据库中有 {count} 条记录')
"
```

---

## ⚠️ 常见错误

### 错误 1: "Cannot connect to the Docker daemon"
```bash
# 解决: 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 错误 2: "permission denied"
```bash
# 解决: 使用 sudo 或将用户添加到 docker 组
sudo usermod -aG docker $USER
# 然后退出并重新登录
```

### 错误 3: "no such file or directory"
```bash
# 解决: 确保在项目根目录
cd /var/www/xitong
pwd  # 应该显示 /var/www/xitong
ls docker-compose.yml  # 应该存在
```

### 错误 4: 容器不断重启
```bash
# 查看日志找原因
sudo docker compose logs backend --tail 100

# 检查健康状态
sudo docker compose ps
```

---

## 📊 完整命令速查表

| 操作 | Docker Compose | 容器名称 |
|-----|---------------|---------|
| 查看状态 | `docker compose ps` | `docker ps` |
| 启动服务 | `docker compose up -d` | `docker start <名称>` |
| 停止服务 | `docker compose down` | `docker stop <名称>` |
| 重启服务 | `docker compose restart` | `docker restart <名称>` |
| 查看日志 | `docker compose logs <服务>` | `docker logs <名称>` |
| 执行命令 | `docker compose exec <服务> <命令>` | `docker exec <名称> <命令>` |
| 复制文件 | `docker compose cp <源> <服务>:<目标>` | `docker cp <源> <名称>:<目标>` |

---

## ✅ 验证成功

执行以下命令确认一切正常:

```bash
# 1. 容器运行
sudo docker compose ps
# 应该都显示 "Up" 或 "Up (healthy)"

# 2. 查看后端日志
sudo docker compose logs backend --tail 20
# 应该看到 "✓ 数据库已加载 (1343 条记录)"

# 3. 测试 API
curl http://localhost:8000/api/database/overview
# 应该返回 JSON 数据，records > 0

# 4. 访问前端
curl http://localhost
# 应该返回 HTML 页面
```

---

## 🎯 下次部署记住

1. **优先使用 Docker Compose 命令** (不需要知道容器名)
2. **使用自动化脚本** (处理各种命名情况)
3. **检查 docker-compose.yml** 中的 `container_name`
4. **使用服务名而不是容器名** (更稳定)

---

需要更多帮助? 运行:
```bash
bash check-containers.sh
```
