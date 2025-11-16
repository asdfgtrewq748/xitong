# ============================================================================
# 生产环境部署指南 - v3.0.3
# ============================================================================
# 最后更新：2025-11-17
# 确保服务器部署版本与开发版本完全一致
# ============================================================================

## 📋 **部署前检查清单**

### ✅ **1. 环境要求**
- Docker: >= 20.10
- Docker Compose: >= 2.0
- 操作系统: Linux/Windows/macOS
- 内存: >= 4GB
- 磁盘空间: >= 10GB

### ✅ **2. 文件完整性检查**

运行验证脚本：
```bash
bash deploy-verification.sh
```

或手动检查：
```bash
# 检查Docker配置
ls -la docker-compose.yml
ls -la backend/Dockerfile
ls -la frontend/Dockerfile
ls -la frontend/nginx.conf

# 检查数据文件
ls -la data/input/汇总表.csv

# 检查依赖配置
cat backend/requirements.txt
cat frontend/package.json | grep -E "svg2pdf|echarts-gl"
```

---

## 🚀 **快速部署流程**

### **方式1：完整构建部署（推荐首次部署）**

```bash
# 1. 清理旧容器和镜像（如果存在）
docker-compose down -v
docker system prune -af

# 2. 构建并启动所有服务
docker-compose up -d --build

# 3. 查看启动日志
docker-compose logs -f

# 4. 等待健康检查通过（约30-60秒）
docker-compose ps
```

### **方式2：增量更新部署（代码更新时）**

```bash
# 1. 停止服务
docker-compose down

# 2. 拉取最新代码
git pull origin master

# 3. 重新构建并启动
docker-compose up -d --build

# 4. 验证服务
curl http://localhost:8000/api/health
curl http://localhost/
```

---

## 🔍 **部署验证**

### **1. 容器状态检查**

```bash
# 查看所有容器状态
docker-compose ps

# 预期输出：
# NAME              STATUS         PORTS
# mining-backend    Up (healthy)   0.0.0.0:8000->8000/tcp
# mining-frontend   Up (healthy)   0.0.0.0:80->80/tcp
```

### **2. 健康检查**

```bash
# 后端健康检查
curl http://localhost:8000/api/health
# 预期返回: {"status":"ok","timestamp":"..."}

# 前端健康检查
curl -I http://localhost/
# 预期返回: HTTP/1.1 200 OK
```

### **3. API功能测试**

```bash
# 测试数据库API
curl http://localhost:8000/api/database/info

# 测试数据导入API
curl http://localhost:8000/api/raw/import
```

### **4. 前端页面验证**

在浏览器访问：
- 首页: http://localhost/
- 数据管理: http://localhost/#/data/management
- 可视化: http://localhost/#/visualization

验证所有7个图表页面：
- ✅ 散点图 - 渐变色header + 高级选项
- ✅ 折线图 - 渐变色header + 高级选项 + "仅导出曲线"
- ✅ 柱状图 - 渐变色header + barWidth + showLabel
- ✅ 箱线图 - 渐变色header + showLegend
- ✅ 直方图 - 渐变色header + showLabel
- ✅ 热力图 - 渐变色header + showValues + colorRange
- ✅ 3D曲面图 - 渐变色header + viewAngle + wireframe

---

## 📊 **关键配置说明**

### **1. Docker Compose配置**

```yaml
# docker-compose.yml 关键配置

services:
  backend:
    image: mining-system-backend:latest
    container_name: mining-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # 关键：数据卷挂载
    environment:
      - DB_PATH=/app/data/database.db
      - DATA_DIR=/app/data

  frontend:
    image: mining-system-frontend:latest
    container_name: mining-frontend
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy  # 等待后端健康
```

### **2. Nginx反向代理配置**

```nginx
# frontend/nginx.conf

location /api/ {
    proxy_pass http://backend:8000/api/;
    client_max_body_size 50M;  # 支持大文件上传
}
```

### **3. 环境变量配置**

生产环境（`frontend/.env.production`）：
```env
VUE_APP_API_BASE_URL=/api  # 使用相对路径，通过Nginx代理
```

开发环境（`frontend/.env.development`）：
```env
VUE_APP_API_BASE_URL=http://localhost:8000  # 直连后端
```

---

## 🛠 **常见问题排查**

### **问题1：容器无法启动**

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
netstat -tuln | grep -E '80|8000'

# 清理并重新构建
docker-compose down -v
docker-compose up -d --build --force-recreate
```

### **问题2：API请求失败（CORS/404）**

```bash
# 检查Nginx配置
docker exec mining-frontend cat /etc/nginx/conf.d/default.conf

# 检查容器网络
docker network inspect xitong_mining-network

# 测试后端连通性
docker exec mining-frontend wget -qO- http://backend:8000/api/health
```

### **问题3：数据文件找不到**

```bash
# 检查数据卷挂载
docker exec mining-backend ls -la /app/data/input/

# 检查文件权限
ls -la ./data/input/汇总表.csv

# 如果文件缺失，停止容器后复制
docker-compose down
cp your-source/汇总表.csv ./data/input/
docker-compose up -d
```

### **问题4：前端图表功能异常**

```bash
# 检查浏览器控制台
# 1. 打开开发者工具（F12）
# 2. 查看Console是否有错误
# 3. 查看Network请求是否成功

# 检查前端构建产物
docker exec mining-frontend ls -la /usr/share/nginx/html/

# 验证chartWrapper.js是否包含所有函数
docker exec mining-frontend grep -o "generateScatterOption\|generateLineOption\|generateBarOption" /usr/share/nginx/html/js/*.js
```

---

## 🔐 **安全建议**

### **1. 生产环境配置**

```yaml
# docker-compose.yml 添加安全配置

services:
  backend:
    environment:
      - SECRET_KEY=${SECRET_KEY}  # 从环境变量读取
    restart: unless-stopped  # 自动重启策略
    
  frontend:
    restart: unless-stopped
```

### **2. 启用HTTPS（可选）**

修改 `frontend/nginx.conf`：
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    # ... 其他配置
}
```

### **3. 日志管理**

```bash
# 查看日志
docker-compose logs -f --tail=100

# 清理日志
docker-compose down
rm -rf frontend/logs/* backend/logs/*
docker-compose up -d
```

---

## 📈 **性能优化**

### **1. Docker构建缓存**

```bash
# 使用BuildKit加速构建
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

docker-compose build --parallel
```

### **2. 资源限制**

```yaml
# docker-compose.yml

services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### **3. 数据库优化**

```bash
# 定期优化数据库
docker exec mining-backend sqlite3 /app/data/database.db "VACUUM;"
```

---

## 🔄 **升级和回滚**

### **升级流程**

```bash
# 1. 备份数据
docker exec mining-backend tar czf /tmp/backup.tar.gz /app/data
docker cp mining-backend:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# 2. 拉取新代码
git pull origin master

# 3. 重新构建
docker-compose build --no-cache

# 4. 滚动更新
docker-compose up -d
```

### **回滚流程**

```bash
# 1. 切换到上一个版本
git checkout <previous-commit-hash>

# 2. 重新构建
docker-compose build --no-cache

# 3. 启动服务
docker-compose up -d

# 4. 恢复数据（如需要）
docker cp backup-20251117.tar.gz mining-backend:/tmp/
docker exec mining-backend tar xzf /tmp/backup-20251117.tar.gz -C /
```

---

## 📞 **支持和联系**

如遇到部署问题，请提供以下信息：

1. 系统环境：
   ```bash
   docker --version
   docker-compose --version
   uname -a
   ```

2. 容器状态：
   ```bash
   docker-compose ps
   docker-compose logs backend --tail=50
   docker-compose logs frontend --tail=50
   ```

3. 错误截图或日志文件

---

## ✅ **部署检查表**

部署完成后，请确认以下项目：

- [ ] 容器状态全部为 `Up (healthy)`
- [ ] 后端健康检查返回 `{"status":"ok"}`
- [ ] 前端页面能够正常访问
- [ ] 数据导入功能正常
- [ ] 所有7个图表页面渲染正常
- [ ] 所有高级选项功能可用
- [ ] PDF/Excel导出功能正常
- [ ] "仅导出曲线"功能正常（折线图）
- [ ] 所有页面header配色统一为紫色渐变
- [ ] 没有控制台错误或警告

---

**版本信息：**
- 系统版本: v3.0.3
- 文档更新: 2025-11-17
- 支持的功能: 矢量PDF导出、7种图表类型、完整高级选项、统一UI风格
