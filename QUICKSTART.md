# 矿山工程分析系统 - 快速启动指南 🚀

## Windows 用户

### 方式一: 一键部署(推荐)

1. **打开 PowerShell**
   ```powershell
   # 右键点击 PowerShell,选择"以管理员身份运行"
   ```

2. **进入项目目录**
   ```powershell
   cd D:\MiningSystem
   ```

3. **运行部署脚本**
   ```powershell
   .\deploy.ps1
   ```

4. **访问系统**
   - 浏览器打开: http://localhost
   - API文档: http://localhost:8000/docs

### 方式二: 手动部署

```powershell
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose stop
```

---

## Linux/Mac 用户

### 方式一: 一键部署(推荐)

```bash
# 1. 赋予执行权限
chmod +x deploy.sh

# 2. 运行部署脚本
./deploy.sh

# 3. 访问系统
# 浏览器打开: http://localhost
```

### 方式二: 手动部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose stop
```

---

## 📋 部署前检查清单

- [ ] 已安装 Docker (>= 20.10)
- [ ] 已安装 Docker Compose (>= 2.0)
- [ ] Docker Desktop 已启动(Windows)
- [ ] 端口 80 和 8000 未被占用
- [ ] 至少 2GB 可用内存
- [ ] 至少 5GB 可用磁盘空间

### 检查 Docker 安装

```bash
# Windows PowerShell
docker --version
docker-compose --version

# Linux/Mac
docker --version
docker compose version
```

### 检查端口占用

```bash
# Windows
netstat -ano | findstr :80
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :80
lsof -i :8000
```

---

## 🎯 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost | 主界面 |
| 后端API | http://localhost:8000 | API服务 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost/health | 服务状态 |

---

## 🔧 常用命令

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 仅后端
docker-compose logs -f backend

# 仅前端
docker-compose logs -f frontend

# 最近100行
docker-compose logs --tail=100
```

### 重启服务
```bash
# 重启所有
docker-compose restart

# 重启指定服务
docker-compose restart backend
```

### 停止服务
```bash
# 停止
docker-compose stop

# 停止并删除容器
docker-compose down

# 完全清理(包括数据卷)
docker-compose down -v
```

### 查看状态
```bash
# 容器状态
docker-compose ps

# 资源使用
docker stats
```

---

## 🔄 数据备份

### Windows
```powershell
.\backup.ps1
```

### Linux/Mac
```bash
chmod +x backup.sh
./backup.sh
```

备份文件位置: `./backups/`

---

## 🐛 常见问题

### 1. 端口被占用

**问题**: `Error: bind: address already in use`

**解决**:
```bash
# Windows - 查找并结束占用进程
netstat -ano | findstr :80
taskkill /PID <进程ID> /F

# Linux/Mac
sudo lsof -ti:80 | xargs kill -9
```

### 2. Docker未启动

**问题**: `Cannot connect to the Docker daemon`

**解决**:
- Windows: 启动 Docker Desktop
- Linux: `sudo systemctl start docker`
- Mac: 启动 Docker Desktop

### 3. 内存不足

**问题**: `docker: Error response from daemon: OCI runtime create failed`

**解决**:
- Docker Desktop → Settings → Resources → Memory
- 增加到至少 2GB

### 4. 服务无法访问

**问题**: 浏览器无法打开 http://localhost

**解决**:
```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

### 5. 数据库错误

**问题**: `database is locked` 或 `unable to open database file`

**解决**:
```bash
# 停止所有服务
docker-compose down

# 删除数据卷
docker-compose down -v

# 重新启动
docker-compose up -d
```

---

## 📞 获取帮助

1. **查看完整文档**: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)
2. **查看日志**: `docker-compose logs -f`
3. **检查健康状态**: http://localhost/health

---

## 🎉 部署成功后

1. ✅ 访问 http://localhost
2. ✅ 导入钻孔数据
3. ✅ 开始使用关键层计算和地质建模功能

**祝您使用愉快!** 🎊
