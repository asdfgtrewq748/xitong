# 🔧 服务器问题修复指南

## 问题诊断

当前线上版本存在的问题：
1. ❌ 前端尝试连接 `localhost:5000` 而不是正确的 `/api/` 路径
2. ❌ 数据库可能未初始化（0条记录）

**根本原因**：前端容器使用的是旧版本的代码，需要重新构建。

---

## 🎯 完整修复步骤（在服务器上执行）

### 方式一：使用自动化脚本（推荐）⭐

```bash
# 1. SSH 登录服务器
ssh root@39.97.168.66

# 2. 进入项目目录
cd /var/www/xitong

# 3. 下载最新代码（包含修复）
git remote set-url origin https://github.com/asdfgtrewq748/xitong.git
git fetch origin
git reset --hard origin/master

# 4. 赋予脚本执行权限
chmod +x server-fix-all.sh

# 5. 执行修复脚本
./server-fix-all.sh
```

**预计时间：3-5 分钟**（包含镜像重新构建）

---

### 方式二：手动修复（完全控制）

```bash
# 1. SSH 登录
ssh root@39.97.168.66

# 2. 进入项目目录
cd /var/www/xitong

# 3. 切换到 HTTPS
git remote set-url origin https://github.com/asdfgtrewq748/xitong.git

# 4. 拉取最新代码
git fetch origin
git reset --hard origin/master

# 5. 查看最新提交
git log --oneline -3
# 应该看到:
# 36a6326 fix: 修复前端API端口错误和数据库自动初始化问题
# 52e60cd perf: 优化Docker构建速度...
# ...

# 6. 停止容器
docker compose down

# 7. 启用 BuildKit 加速
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 8. 重新构建前端（重要！）
docker compose build frontend

# 9. 重新构建后端（包含数据库初始化代码）
docker compose build backend

# 10. 启动容器
docker compose up -d

# 11. 等待启动
sleep 15

# 12. 查看日志
docker compose logs -f
# 按 Ctrl+C 退出日志查看
```

---

## ✅ 验证修复成功

### 1. 检查容器状态

```bash
docker compose ps
```

预期输出：
```
NAME              STATUS          PORTS
mining-backend    Up 1 minute     0.0.0.0:8000->8000/tcp
mining-frontend   Up 1 minute     0.0.0.0:80->80/tcp
```

### 2. 检查后端日志（数据库）

```bash
docker compose logs backend | grep -A 5 "数据库"
```

预期看到以下之一：
```
✓ 数据库已加载 (1341 条记录)
```
或
```
📊 开始导入数据...
✅ 数据库初始化完成！导入 1341 条记录
```

### 3. 检查前端配置

```bash
# 进入前端容器
docker compose exec frontend cat /etc/nginx/conf.d/default.conf | grep proxy_pass
```

预期看到：
```
proxy_pass http://backend:8000/api/;
```

### 4. 测试 API 端点

```bash
# 测试后端健康
curl http://localhost:8000/api/health

# 测试前端代理
curl http://localhost/api/health

# 测试数据库 API
curl http://localhost/api/database/overview
```

预期都返回 JSON 数据。

### 5. 浏览器测试

访问：`http://39.97.168.66`

**打开浏览器开发者工具（F12）**：
- ✅ Network 选项卡应该看到 `/api/borehole-data` 请求成功（200 状态）
- ✅ 不再有 `localhost:5000` 的请求
- ✅ Console 没有 `ERR_CONNECTION_REFUSED` 错误

**强制刷新浏览器缓存**：
- Windows: `Ctrl + Shift + R` 或 `Ctrl + F5`
- Mac: `Cmd + Shift + R`

---

## 🔍 故障排查

### 问题1: 前端仍然显示 localhost:5000

**原因**：浏览器缓存旧版本

**解决**：
```bash
# 清除浏览器缓存，或使用隐私模式访问
# Chrome: Ctrl + Shift + N (隐身窗口)
# Firefox: Ctrl + Shift + P (隐私窗口)
```

### 问题2: 数据库仍然为空

**检查 CSV 文件**：
```bash
docker compose exec backend ls -la /app/data/input/
```

应该看到 `汇总表.csv`。

**手动导入**：
```bash
docker compose exec backend python -c "
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

csv_path = Path('/app/data/input/汇总表.csv')
if csv_path.exists():
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    engine = create_engine('sqlite:////app/data/database.db')
    df.to_sql('records', engine, if_exists='replace', index=False)
    
    with engine.connect() as conn:
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_province ON records (省份)'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_mine ON records (矿名)'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_lithology ON records (岩性)'))
        conn.commit()
    
    print(f'✅ 导入 {len(df)} 条记录')
else:
    print('❌ CSV 文件不存在')
"
```

### 问题3: API 返回 502 Bad Gateway

**原因**：后端容器未启动或崩溃

**解决**：
```bash
# 查看后端日志
docker compose logs backend | tail -50

# 重启后端
docker compose restart backend

# 如果持续失败，完全重建
docker compose down
docker compose build backend --no-cache
docker compose up -d
```

### 问题4: Nginx 代理不工作

**检查配置**：
```bash
docker compose exec frontend nginx -t
```

**重新加载配置**：
```bash
docker compose exec frontend nginx -s reload
```

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| API 地址 | `localhost:5000` ❌ | `/api/` 或 `http://backend:8000` ✅ |
| 前端请求 | ERR_CONNECTION_REFUSED ❌ | 200 OK ✅ |
| 数据库 | 未初始化 ❌ | 自动加载 1341 条记录 ✅ |
| 环境变量 | 缺失 ❌ | 正确配置 ✅ |
| Nginx 代理 | 路径错误 ❌ | 正确代理到后端 ✅ |

---

## 📞 常见问题

**Q: 为什么必须重新构建前端？**

A: 前端是编译型应用，代码变化需要重新构建才能生效：
```
源码修改 → npm run build → 生成 dist/ → 打包到镜像
```
单纯重启容器只能看到旧的 dist/ 内容。

**Q: 为什么后端也需要重新构建？**

A: 虽然 Python 代码可以热重载，但为了确保数据库初始化代码生效，建议重新构建。

**Q: 重新构建会很慢吗？**

A: 不会！由于已经优化：
- 使用 BuildKit
- 使用国内镜像源
- 分层缓存
- 预编译二进制包

**首次构建**：3-5 分钟
**后续构建**：1-2 分钟（利用缓存）

**Q: 数据会丢失吗？**

A: 不会！数据存储在宿主机的 `./backend/data/` 目录，容器重建不影响。

---

## 🎯 执行后的预期结果

✅ 前端正常访问 `http://39.97.168.66`
✅ API 请求使用 `/api/` 路径（通过 Nginx 代理）
✅ 数据库自动加载 1341 条记录
✅ 所有页面功能正常工作
✅ 浏览器控制台没有错误

---

**最后更新**: 2025-10-24  
**问题票据**: API 端口错误 + 数据库未初始化
