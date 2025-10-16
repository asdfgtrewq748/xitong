# Mining System 零基础上手手册

> 本指南面向第一次接触本项目的同学，假设你对 Python / Node.js 了解不多。请按顺序一步步完成，每一步都尽量写得非常详细。

---

## 1. 项目长什么样？

该文件夹里包含一个“后端” (FastAPI + Python) 和一个“前端” (Vue3 + JavaScript)。整体目录大致如下：

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

> 若看不到数据，先确认后端窗口是否仍在运行。

---

## 5. 常见问题 Q&A

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
