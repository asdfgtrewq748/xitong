# Mining System 零基础上手手册

> 本指南面向第一次接触本项目的同学，假设你对 Python / Node.js 了解不多。请按顺序一步步完成，每一步都尽量写得非常详细。

## 📚 文档导航

> **2025-10-29 更新**: 新增巷道支护计算模块

- 📖 **[完整文档索引](docs/INDEX.md)** - 查看所有可用文档
- 🚀 **[快速开始](docs/QUICKSTART.md)** - 快速上手指南
- 🔧 **[巷道支护计算指南](docs/TUNNEL_SUPPORT_GUIDE.md)** - 巷道支护计算完整文档
- ⚡ **[巷道支护快速开始](docs/TUNNEL_SUPPORT_QUICKSTART.md)** - 5分钟上手巷道支护计算
- 🐳 **[Docker 部署](docs/DOCKER部署指南.md)** - 使用 Docker 部署
- 🔧 **[错误修复](docs/错误修复说明.md)** - 常见问题解决
- ⚡ **[性能优化](docs/backend/PERFORMANCE_GUIDE.md)** - 性能优化指南
- 📜 **[部署脚本](docs/scripts/)** - 自动化部署脚本
- 🖥️ **[演示网站独立指南](demo-site/docs/DEMO_SITE_GUIDE.md)** - demo-site 目录下的静态展示站说明

---

## 1. 项目长什么样？

该文件夹里包含一个“后端” (FastAPI + Python) 和一个“前端” (Vue3 + JavaScript)。另外，`demo-site/` 目录保存完全独立的演示站，不依赖主站后端。整体目录大致如下：

```
MiningSystem/
├── backend/                # 后端代码
│   ├── server.py           # 入口：启动 FastAPI
│   ├── db.py               # 数据库工具
│   └── coal_seam_blocks/   # 地质建模相关模块
├── frontend/               # 前端代码
│   ├── package.json        # npm 依赖清单
│   └── src/                # Vue 页面和组件
├── data/
│   └── input/              # SQLite 或 CSV 数据
├── demo-site/              # 演示网站（前端 + 数据 + 脚本）
└── README.md               # 你正在看的文档
```

---

## 2. 准备工作

### 2.1 操作系统

- 推荐 Windows 10 或 11。如果是 macOS / Linux，也可以照做，只是命令略有差别。

### 2.2 安装 Python（用于后端）

1. 打开浏览器访问 [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. 下载 Python 3.10 或 3.11 的 Windows 安装包。
3. 安装时勾选 **“Add Python to PATH”**（很重要），然后一路“Next”。

> 不确定是否安装了？打开 PowerShell，输入 `python --version`，看到 `Python 3.x.x` 即成功。

### 2.3 安装 Node.js（用于前端）

1. 打开 [https://nodejs.org/](https://nodejs.org/)
2. 下载 “LTS” 版本（一般是绿色按钮）。
3. 双击安装，保持默认即可。

> 验证：在 PowerShell 输入 `node -v` 和 `npm -v`，看到版本号说明成功。

### 2.4 准备 PowerShell 终端

后续命令都在 PowerShell 中执行。建议固定一个窗口操作后端，另开一个窗口操作前端。

---

## 3. 搭建后端（FastAPI）

### 3.1 切换到项目目录

打开 PowerShell，输入：

```powershell
cd d:\MiningSystem
```

确保提示符里出现 `d:\MiningSystem>`。

### 3.2 创建虚拟环境（避免污染系统 Python）

```powershell
python -m venv .venv
```

执行后会多一个 `.venv` 文件夹。

### 3.3 启用虚拟环境

```powershell
.\.venv\Scripts\activate
```

成功后，命令行前面会出现 `(.venv)`。

### 3.4 升级 pip（可选但推荐）

```powershell
pip install --upgrade pip
```

### 3.5 安装后端需要的库

```powershell
pip install fastapi uvicorn[standard] sqlalchemy pandas numpy scipy scikit-learn python-multipart
```

> 如果项目里有 `requirements.txt`，可以改用：`pip install -r requirements.txt`

### 3.6 启动后端开发服务器

```powershell
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

- 若看到 `Application startup complete.` 说明启动成功。
- 保持这个窗口不要关闭。

### 3.7 检查接口是否可用

打开浏览器访问 [http://localhost:8000/docs](http://localhost:8000/docs)。若能看到自动生成的 API 文档页面，则后端无误。

---

## 4. 搭建前端（Vue 3）

新开一个 PowerShell 窗口（后端窗口不要关）。

### 4.1 切换到前端目录

```powershell
cd d:\MiningSystem\frontend
```

### 4.2 安装依赖

```powershell
npm install
```

第一次运行会花点时间下载依赖。

### 4.3 启动前端开发服务器

```powershell
npm run serve
```

成功后终端会显示本地访问地址，例如：

```
App running at:
  - Local:   http://localhost:8080/
```

### 4.4 打开前端页面

在浏览器访问 [http://localhost:8080](http://localhost:8080)。若页面正常展示，说明前端启动成功。

> 若看不到数据,先确认后端窗口是否仍在运行。

---

## 5. Docker 容器化部署（生产环境推荐）⭐

### 5.1 什么是 Docker 部署？

Docker 可以把整个系统（前端+后端+数据库）打包成"容器",一键启动,无需手动配置 Python 和 Node.js 环境。

**优势:**
- ✅ 一键部署,所有依赖都包含在内
- ✅ 环境一致性,避免"在我机器上能跑"的问题
- ✅ 易于上线部署和迁移
- ✅ 包含 Nginx 反向代理,性能更好
- ✅ 生产级配置,支持多进程和健康检查

### 5.2 前置要求

1. **安装 Docker Desktop**
   - Windows: [https://docs.docker.com/desktop/install/windows-install/](https://docs.docker.com/desktop/install/windows-install/)
   - Mac: [https://docs.docker.com/desktop/install/mac-install/](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

2. **启动 Docker Desktop**
   - Windows/Mac: 双击桌面图标启动
   - Linux: `sudo systemctl start docker`

3. **验证安装**
   ```powershell
   docker --version
   docker-compose --version
   ```

### 5.3 一键部署（推荐）

#### Windows 用户:
```powershell
# 在项目根目录执行
.\deploy.ps1
```

#### Linux/Mac 用户:
```bash
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动:
1. 检查 Docker 环境
2. 构建前端和后端镜像
3. 启动所有服务
4. 执行健康检查
5. 显示访问地址

### 5.4 手动部署

如果想逐步了解过程:

```powershell
# 1. 构建镜像（首次需要几分钟）
docker-compose build

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 5.5 访问系统

部署完成后:
- **前端界面**: [http://localhost](http://localhost)
- **后端 API**: [http://localhost:8000](http://localhost:8000)
- **API 文档**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **健康检查**: [http://localhost/health](http://localhost/health)

### 5.6 Docker 常用命令

```powershell
# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看资源使用
docker stats

# 完全清理（删除容器和数据）
docker-compose down -v
```

### 5.7 数据备份

#### Windows:
```powershell
.\backup.ps1
```

#### Linux/Mac:
```bash
chmod +x backup.sh
./backup.sh
```

备份文件保存在 `./backups/` 目录。

### 5.8 详细文档

更多信息请查看:
- **快速开始**: [QUICKSTART.md](./QUICKSTART.md)
- **完整部署文档**: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

---

## 6. 常见问题 Q&A

- **启动后端时报“端口被占用”**：在 `uvicorn` 命令中修改端口，例如 `--port 8001`，同时前端 `frontend/src/utils/api.js` 里也要同步改地址。
- **npm install 很慢**：考虑切换国内镜像（如 `npm config set registry https://registry.npmmirror.com`）。
- **浏览器提示 CORS 或接口 404**：确保后端服务运行且 URL 正确。
- **看到 ResizeObserver 或 DOM 相关警告**：刷新页面或重启前端一次即可。若持续出现，把具体步骤反馈给团队。

---

## 6. 关闭服务与再次启动

### 6.1 停止后端

在运行后端的 PowerShell 窗口按 `Ctrl + C`，看到 `Shutting down` 即表示已停止。

### 6.2 停止前端

在运行 `npm run serve` 的窗口同样按 `Ctrl + C`。

### 6.3 下次再启动

1. 打开 PowerShell，进入项目：
   ```powershell
   cd d:\MiningSystem
   .\.venv\Scripts\activate
   cd backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```
2. 新开窗口：
   ```powershell
   cd d:\MiningSystem\frontend
   npm run serve
   ```

---

## 7. 进一步的事情（可选）

- **部署生产环境**：
  - 后端：`uvicorn server:app --host 0.0.0.0 --port 8000`（去掉 `--reload`）。
  - 前端：`npm run build`，得到 `dist/` 文件夹，用 Nginx 等静态服务器托管。
- **管理依赖**：
  - 后端导出依赖：`pip freeze > requirements.txt`
  - 前端锁定版本：使用 `npm ci`（基于 `package-lock.json`）
- **使用 Git 协作**：提交前运行 `npm run lint` / `pytest`（如有测试），减少冲突。

---

## 8. 想更省事？用 Docker 一键启动

Docker 可以把后端 + 前端一起封装起来，非常适合团队在多台电脑上统一环境。

### 8.1 事先准备

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)（Windows 需要开启 WSL2）。
2. 安装完成后重启电脑一次，再打开 Docker Desktop，确认状态栏显示 **Running**。

### 8.2 第一次启动服务

在 PowerShell 中执行以下命令（确保当前目录是 `d:\MiningSystem`）：

```powershell
cd d:\MiningSystem
docker compose up --build
```

- 该命令会自动构建两个容器：`backend`（FastAPI）和 `frontend`（Vue）。
- 首次构建会比较慢，需要下载 Python / Node 镜像和依赖。
- 看到终端输出 `Uvicorn running on http://0.0.0.0:8000` 和 `App running at: http://localhost:8080/` 就成功了。

### 8.3 访问页面与接口

- 前端：http://localhost:8080
- 后端接口文档：http://localhost:8000/docs

### 8.4 热更新与代码同步

- 我们在 `docker-compose.yml` 中挂载了代码目录，所以你本地修改 `backend/` 或 `frontend/` 文件后，容器会自动刷新。
- 如果新增了 Python 或 npm 依赖，需要重新执行 `docker compose up --build`。

### 8.5 停止与重启

- 停止：在运行 Docker 的终端按 `Ctrl + C`，然后执行 `docker compose down`。
- 重启：
  ```powershell
  docker compose up
  ```
  若代码更新较大或依赖有变化可加 `--build`。

> **提示**：想把服务跑在服务器上供多人访问，只需在服务器拉仓库并运行同样的 `docker compose up -d`（加 `-d` 表示后台运行），再根据需要开放 8000/8080 端口即可。

---

恭喜你完成全部步骤！如果过程中遇到任何卡顿或报错，记录下错误信息和操作步骤，再向团队或我反馈，我们一起排查。祝编程愉快！
