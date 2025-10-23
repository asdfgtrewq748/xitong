#!/bin/bash
# 后端性能优化 - 一键启动脚本（Linux/Mac）

echo "============================================================"
echo "     Mining System Backend - 性能优化版启动脚本"
echo "============================================================"
echo ""

# 检查虚拟环境
if [ -f ".venv/bin/activate" ]; then
    echo "[1/4] 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "[警告] 虚拟环境不存在，使用系统Python"
fi

# 安装性能监控依赖（可选）
echo ""
echo "[2/4] 检查依赖..."
pip install -q psutil 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ psutil 已安装"
else
    echo "  ✗ psutil 安装失败（可选，系统将继续运行）"
fi

# 优化数据库（首次运行）
echo ""
echo "[3/4] 优化数据库..."
if [ -f "../data/database.db" ]; then
    python optimize_database.py
else
    echo "  ! 数据库文件不存在，跳过优化"
fi

# 启动服务器
echo ""
echo "[4/4] 启动服务器..."
echo ""
echo "------------------------------------------------------------"
echo "  服务器地址: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  性能监控: http://localhost:8000/api/performance/stats"
echo "------------------------------------------------------------"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

uvicorn server:app --host 0.0.0.0 --port 8000 --reload
