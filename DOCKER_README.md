# Docker 一步一步上手指南

> 这份说明专门写给第一次接触 Docker 的同学，完全不懂也没关系，照着一步一步做就好。

---

## 0. 需要提前准备什么？

- 一台 Windows 10/11 电脑。
- 管理员权限（安装软件时可能需要）。
- 可访问互联网（下载安装包、拉取镜像）。

---

## 1. 安装 Docker Desktop

1. 打开浏览器进入：[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. 点击下载 Windows 版本（会得到一个 `.exe` 安装程序）。
3. 双击安装程序，按照提示一路“Next”。
4. 安装过程中若提示启用 WSL2 或 Hyper-V，按提示勾选并继续。
5. 安装完成后重启电脑。
6. 重启后在开始菜单找到 “Docker Desktop”，点击运行。
7. 等待右下角图标显示绿色，并看到状态 “Docker Desktop is running”。

> 如果运行时提示 WSL 未启用，请搜索“启用或关闭 Windows 功能”，勾选 “适用于 Linux 的 Windows 子系统 (WSL)” 和 “虚拟机平台”，确定后再次重启。

---

## 2. 配置国内镜像（让拉镜像更快）

1. 打开 Docker Desktop 主界面，点击右上角齿轮图标进入 **Settings**。
2. 在左侧选择 **Docker Engine**。
3. 可以看到一段 JSON 配置，将其中内容替换为：
   ```json
   {
     "builder": {
       "gc": {
         "defaultKeepStorage": "20GB",
         "enabled": true
       }
     },
     "experimental": false,
     "registry-mirrors": [
       "https://docker.m.daocloud.io",
       "https://mirror.baidubce.com",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
4. 点击右下角 **Apply & Restart**，等待 Docker 重启。
5. 重新打开 PowerShell，执行：
   ```powershell
   docker pull hello-world
   ```
   如果成功下载并显示 hello-world 的提示，说明网络配置正常。

---

## 3. 准备项目文件

1. 确认你已经在当前电脑上有 `MiningSystem` 项目文件夹，结构包含 `backend/`、`frontend/`、`docker-compose.yml` 等。
2. 如果是通过压缩包拿到项目，请先解压到一个固定位置，比如 `d:\MiningSystem`。

---

## 4. 打开 PowerShell 并进入项目

1. 在开始菜单搜索 “PowerShell”，右键选择 “以管理员身份运行”（推荐）。
2. 在终端输入：
   ```powershell
   cd d:\MiningSystem
   ```
   若成功，你会看到命令提示符变成 `PS D:\MiningSystem>`。

---

## 5. 第一次构建并启动容器

1. 在 `PS D:\MiningSystem>` 中执行：
   ```powershell
   docker compose up --build
   ```
2. 首次运行会：
   - 读取项目里的 Dockerfile。
   - 从网络下载 Python 3.11 和 Node 18 的基础镜像。
   - 安装后端所需的 Python 包以及前端的 npm 依赖。
3. 这个过程需要几分钟，请耐心等待，终端会不断滚动日志。
4. 当你看到类似以下信息时表示成功：
   - `backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000`
   - `frontend-1 | App running at:
       - Local: http://localhost:8080/`
5. 此时请保持这个终端窗口打开，不要关闭。

> 小贴士：如果中途出现 `npm install` 或 `pip install` 报错，请把完整错误信息发给我，我们再排查。

---

## 6. 打开浏览器验证

1. 打开浏览器访问 [http://localhost:8080](http://localhost:8080)。
   - 应该能看到 Mining System 的前端页面。
2. 再访问 [http://localhost:8000/docs](http://localhost:8000/docs)。
   - 这是 FastAPI 自动生成的接口文档。
3. 如果页面打不开：
   - 检查 Docker Desktop 是否仍在运行。
   - 查看 PowerShell 里的日志是否有报错信息。

---

## 7. 修改代码时如何刷新

- 我们已经在 `docker-compose.yml` 配置了代码挂载，意味着：
  - 修改 `backend/` 下的 Python 文件会让后端自动重载。
  - 修改 `frontend/src/` 下的 Vue 文件也会触发热更新。
- 不需要重新执行 `docker compose up`，保存文件即可生效。
- 如果你新增了依赖（例如 `pip install 新包` 或 `npm install 新库`），需要：
  1. 在 PowerShell 按 `Ctrl + C` 停止服务。
  2. 重新运行 `docker compose up --build` 让 Docker 重装依赖。

---

## 8. 如何停止或后台运行

- **停止运行**：在 PowerShell 中按 `Ctrl + C`，等待服务退出，再执行：
  ```powershell
  docker compose down
  ```
- **后台运行**（不想被日志刷屏）：
  ```powershell
  docker compose up -d
  ```
  - 想看日志时用：`docker compose logs -f backend` 或 `docker compose logs -f frontend`。
  - 停止后台服务：`docker compose down`

---

## 9. 在另一台电脑部署

1. 确保另一台电脑同样安装 Docker Desktop 并按步骤配置镜像。
2. 通过 Git 克隆项目或复制压缩包，保持相同的目录结构。
3. 打开 PowerShell 切到项目目录：`cd d:\MiningSystem`
4. 执行 `docker compose up --build`
5. 按上面的步骤访问 `http://localhost:8080` 和 `http://localhost:8000/docs`

---

## 10. 常见问题速查

| 问题 | 解决办法 |
|------|-----------|
| 拉取镜像超时 | 确认 Docker Engine 配置了 `registry-mirrors`；必要时切换网络或使用 VPN。 |
| npm install 报依赖冲突 | 检查 `package.json` 依赖是否满足 peer 依赖，或使用我们已经调整好的版本。 |
| 容器启动后访问不到网页 | 先 `docker compose logs frontend` 查看是否有报错，再确认端口未被其他程序占用。 |
| 想重置一切重新来过 | 运行 `docker compose down --volumes`，再 `docker system prune -a`（慎用，会删除所有未使用镜像/容器）。 |

---

## 11. 有问题怎么办？

- 拍下 PowerShell / Docker Desktop 的完整错误信息。
- 记录你刚才执行的命令和操作步骤。
- 提供这些信息给负责的同学或在项目群里求助，我们会一步步帮你排查。

只要严格按照以上步骤执行，一般都可以顺利用 Docker 在任何一台 Windows 电脑上跑起 Mining System。祝你部署顺利！
