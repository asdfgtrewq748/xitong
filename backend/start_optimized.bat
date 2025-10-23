@echo off
REM 后端性能优化 - 一键启动脚本（Windows）

echo ============================================================
echo      Mining System Backend - 性能优化版启动脚本
echo ============================================================
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [1/4] 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo [警告] 虚拟环境不存在，使用系统Python
)

REM 安装性能监控依赖（可选）
echo.
echo [2/4] 检查依赖...
pip install -q psutil 2>nul
if %errorlevel%==0 (
    echo   ✓ psutil 已安装
) else (
    echo   ✗ psutil 安装失败（可选，系统将继续运行）
)

REM 优化数据库（首次运行）
echo.
echo [3/4] 优化数据库...
if exist "..\data\database.db" (
    python optimize_database.py
) else (
    echo   ! 数据库文件不存在，跳过优化
)

REM 启动服务器
echo.
echo [4/4] 启动服务器...
echo.
echo ------------------------------------------------------------
echo   服务器地址: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo   性能监控: http://localhost:8000/api/performance/stats
echo ------------------------------------------------------------
echo.
echo 按 Ctrl+C 停止服务器
echo.

uvicorn server:app --host 0.0.0.0 --port 8000 --reload
