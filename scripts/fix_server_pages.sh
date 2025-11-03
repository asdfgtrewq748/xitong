#!/bin/bash
# ============================================================================
# 服务器页面无法打开 - 紧急修复脚本
# ============================================================================
# 问题: 前端代码分割失败，导致懒加载的页面无法打开
# 修复: 重新构建前端容器，使用修复后的 vue.config.js
# ============================================================================

set -e  # 遇到错误立即退出

echo "========================================"
echo "🔧 开始修复服务器页面无法打开问题"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 未找到 docker-compose.yml"
    echo "请在项目根目录执行此脚本"
    exit 1
fi

echo "📍 当前目录: $(pwd)"
echo ""

# 步骤 1: 停止容器
echo "🛑 步骤 1/5: 停止现有容器..."
docker-compose down
echo "✅ 容器已停止"
echo ""

# 步骤 2: 拉取最新代码（如果在服务器上）
echo "🔄 步骤 2/5: 拉取最新代码..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    git pull origin master
    echo "✅ 代码已更新"
else
    echo "⚠️  警告: 不是 git 仓库，跳过此步骤"
fi
echo ""

# 步骤 3: 强制重新构建前端（关键步骤）
echo "🔨 步骤 3/5: 重新构建前端容器（不使用缓存）..."
echo "这一步可能需要 2-5 分钟，请耐心等待..."
docker-compose build --no-cache frontend
echo "✅ 前端构建完成"
echo ""

# 步骤 4: 启动服务
echo "🚀 步骤 4/5: 启动服务..."
docker-compose up -d
echo "✅ 服务已启动"
echo ""

# 等待服务就绪
echo "⏳ 等待服务启动..."
sleep 5

# 步骤 5: 验证修复
echo "🔍 步骤 5/5: 验证修复结果..."
echo ""

# 检查容器状态
echo "容器状态:"
docker-compose ps
echo ""

# 检查前端文件
echo "检查前端 JS 文件:"
docker exec $(docker-compose ps -q frontend) ls -lh /usr/share/nginx/html/js/ | grep -E "database|modeling|visualization|chunk"
echo ""

# 测试后端健康
echo "测试后端 API:"
curl -s http://localhost:8000/api/health || echo "⚠️  后端 API 测试失败"
echo ""

echo "========================================"
echo "✅ 修复完成！"
echo "========================================"
echo ""
echo "📋 请访问以下页面进行测试："
echo "  • 首页: http://39.97.168.66/"
echo "  • 数据库管理: http://39.97.168.66/database-viewer"
echo "  • 地质建模: http://39.97.168.66/geological-modeling"
echo "  • 科研绘图: http://39.97.168.66/visualization"
echo ""
echo "🔍 如果页面仍然无法打开，请："
echo "  1. 清除浏览器缓存（Ctrl+Shift+Delete）"
echo "  2. 按 F12 打开浏览器控制台，查看错误信息"
echo "  3. 运行: docker-compose logs frontend | tail -50"
echo ""
echo "📄 详细修复文档: 服务器页面无法打开修复指南.md"
echo ""
