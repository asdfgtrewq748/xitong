# ✅ 服务器部署检查清单

## 部署前检查

### 1. 服务器环境
- [ ] 操作系统: Linux (推荐 Ubuntu 20.04+ 或 CentOS 7+)
- [ ] Docker 版本: 20.10+
- [ ] Docker Compose 版本: 2.0+
- [ ] 可用内存: >= 2GB
- [ ] 可用磁盘: >= 10GB
- [ ] CPU: >= 2核心

### 2. 网络检查
- [ ] 端口80可用 (前端)
- [ ] 端口8000可用 (后端API)
- [ ] 防火墙规则已配置
- [ ] 能访问Docker Hub或配置镜像加速

### 3. 数据文件准备
- [ ] `data/input/汇总表.csv` 存在
- [ ] CSV文件编码正确 (UTF-8或GBK)
- [ ] 文件权限正确 (可读)

---

## 部署步骤

### Step 1: 上传代码
```bash
# 克隆仓库或上传代码
git clone <repository> /opt/xitong
cd /opt/xitong

# 或使用scp上传
scp -r xitong/ user@server:/opt/
```

### Step 2: 验证文件结构
```bash
ls -la /opt/xitong/
ls -la /opt/xitong/data/input/汇总表.csv
ls -la /opt/xitong/docker-compose.yml
```

### Step 3: 配置环境
```bash
# 检查Docker
docker --version
docker-compose --version

# 测试Docker
docker run hello-world
```

### Step 4: 执行部署
```bash
cd /opt/xitong
chmod +x docs/scripts/deploy.sh
./docs/scripts/deploy.sh
```

### Step 5: 验证部署
```bash
# 检查容器状态
docker-compose ps

# 测试健康检查
curl http://localhost/health
curl http://localhost:8000/api/health

# 查看日志
docker-compose logs --tail=50
```

---

## 部署后验证

### 1. 前端功能检查
- [ ] 访问 http://服务器IP 能打开首页
- [ ] Dashboard页面显示正常
- [ ] 能导入钻孔数据
- [ ] 能查看数据预览
- [ ] 图表显示正常

### 2. 后端功能检查
- [ ] 访问 http://服务器IP:8000/docs 能打开API文档
- [ ] `/api/health` 返回 `{"status":"healthy"}`
- [ ] `/api/dashboard/stats` 返回统计数据
- [ ] 能上传CSV文件
- [ ] 能执行关键层计算

### 3. 核心功能测试
- [ ] 全局数据导入 (选择CSV文件自动导入)
- [ ] 关键层计算功能
- [ ] 地质建模功能
- [ ] 3D可视化显示
- [ ] 数据导出功能
- [ ] 剖面图生成

### 4. 性能检查
```bash
# 查看资源使用
docker stats

# 检查响应时间
time curl http://localhost/api/health

# 查看内存使用
free -h
```

---

## 常见问题快速解决

### 问题1: 容器无法启动
```bash
# 查看具体错误
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
netstat -tuln | grep -E '80|8000'

# 杀死占用进程
lsof -ti:80 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### 问题2: 找不到汇总表.csv
```bash
# 检查文件
docker-compose exec backend ls -la /app/data/input/

# 确认挂载
docker-compose exec backend cat /app/data/input/汇总表.csv | head -3

# 修复: 重新复制文件
cp 汇总表.csv data/input/
docker-compose restart backend
```

### 问题3: 内存不足
```bash
# 减少worker数量
# 编辑 backend/Dockerfile
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# 重新构建
docker-compose build backend
docker-compose up -d backend
```

### 问题4: 前端无法连接后端
```bash
# 检查网络
docker network inspect xitong_mining-network

# 测试连接
docker-compose exec frontend wget -O- http://backend:8000/api/health

# 查看nginx日志
docker-compose logs frontend | grep error
```

### 问题5: 文件上传失败
```bash
# 检查nginx配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf | grep client_max_body_size

# 增大上传限制
# 编辑 docker-compose.yml
environment:
  - MAX_UPLOAD_SIZE_MB=100

# 重启
docker-compose restart
```

---

## 生产环境配置

### 1. 配置域名访问
```nginx
# 编辑 frontend/nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    ...
}
```

### 2. 启用HTTPS
```bash
# 安装certbot
apt-get install certbot

# 获取证书
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# 更新nginx配置
# 添加SSL配置到 frontend/nginx.conf
```

### 3. 配置自动重启
```bash
# 添加到crontab
@reboot cd /opt/xitong && docker-compose up -d

# 或配置systemd服务
cat > /etc/systemd/system/xitong.service << EOF
[Unit]
Description=Xitong Mining System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/xitong
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl enable xitong
systemctl start xitong
```

### 4. 配置日志轮转
```bash
# 编辑 docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 监控和维护

### 每日检查
```bash
# 检查容器状态
docker-compose ps

# 检查磁盘使用
df -h

# 检查日志大小
du -sh backend/logs/ frontend/logs/
```

### 每周维护
```bash
# 清理Docker缓存
docker system prune -f

# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 查看资源使用趋势
docker stats --no-stream
```

### 月度检查
```bash
# 更新系统
./docs/scripts/deploy.sh

# 检查更新
git pull
docker-compose pull

# 安全更新
apt-get update && apt-get upgrade -y
```

---

## 备份策略

### 自动备份脚本
```bash
#!/bin/bash
# /opt/xitong/backup.sh

BACKUP_DIR="/backup/xitong"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/xitong/data/

# 备份数据库
docker-compose exec -T backend \
  sqlite3 /app/data/database.db ".backup /tmp/db_$DATE.db"
docker cp mining-backend:/tmp/db_$DATE.db $BACKUP_DIR/

# 清理旧备份(保留7天)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 配置定时备份
```bash
# 添加到crontab
0 2 * * * /opt/xitong/backup.sh >> /var/log/xitong_backup.log 2>&1
```

---

## 安全建议

### 1. 防火墙配置
```bash
# Ubuntu/Debian
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # 后端API仅内部访问
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 2. 使用反向代理
建议在前面加一层Nginx作为统一入口,不直接暴露8000端口

### 3. 定期更新
```bash
# 更新Docker镜像
docker-compose pull
docker-compose up -d

# 更新系统
apt-get update && apt-get upgrade -y
```

### 4. 监控日志
```bash
# 设置日志告警
tail -f backend/logs/app.log | grep -i error
```

---

## 回滚方案

### 快速回滚
```bash
# 1. 停止当前服务
docker-compose down

# 2. 恢复备份
tar -xzf backup_YYYYMMDD.tar.gz -C /opt/xitong/

# 3. 切换到旧版本
git checkout <previous-commit>

# 4. 重新部署
docker-compose build
docker-compose up -d

# 5. 验证
curl http://localhost/health
```

---

## 联系支持

如遇问题,请提供:
1. `docker-compose ps` 输出
2. `docker-compose logs` 相关日志
3. 服务器系统信息: `uname -a`
4. Docker版本: `docker --version`
5. 部署步骤和错误信息

---

## 附录: 完整部署命令

```bash
# 一键部署完整命令
cd /opt
git clone <repository> xitong
cd xitong
chmod +x docs/scripts/deploy.sh
./docs/scripts/deploy.sh

# 验证
docker-compose ps
curl http://localhost/health
curl http://localhost:8000/api/health

# 查看日志
docker-compose logs -f
```
