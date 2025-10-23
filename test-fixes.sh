#!/bin/bash
# ============================================================================
# 本地测试脚本 - 验证所有修复
# ============================================================================

echo "=========================================="
echo "🧪 开始测试修复"
echo "=========================================="

echo ""
echo "1️⃣  测试后端 API 端口配置..."
if grep -q "localhost:8000" frontend/src/utils/dataService.js; then
    echo "✅ dataService.js 使用正确端口 8000"
else
    echo "❌ dataService.js 端口配置错误"
fi

echo ""
echo "2️⃣  测试环境变量配置..."
if [ -f frontend/.env.production ]; then
    echo "✅ 生产环境配置存在"
    cat frontend/.env.production
else
    echo "❌ 缺少生产环境配置"
fi

echo ""
echo "3️⃣  测试 Nginx 反向代理配置..."
if grep -q "proxy_pass http://backend:8000/api/" frontend/nginx.conf; then
    echo "✅ Nginx 代理配置正确"
else
    echo "❌ Nginx 代理配置错误"
fi

echo ""
echo "4️⃣  测试数据库初始化代码..."
if grep -q "check_and_init_database" backend/server.py; then
    echo "✅ 数据库自动初始化代码已添加"
else
    echo "❌ 缺少数据库初始化代码"
fi

echo ""
echo "5️⃣  测试 CSV 数据文件..."
if [ -f backend/data/input/汇总表.csv ]; then
    lines=$(wc -l < backend/data/input/汇总表.csv)
    echo "✅ CSV 文件存在 ($lines 行)"
else
    echo "❌ CSV 文件不存在"
fi

echo ""
echo "6️⃣  测试 .dockerignore 配置..."
if grep -q "!data/input/" .dockerignore; then
    echo "✅ data/input/ 目录将被包含在镜像中"
else
    echo "⚠️  data/input/ 可能被排除"
fi

echo ""
echo "=========================================="
echo "✅ 测试完成"
echo "=========================================="
