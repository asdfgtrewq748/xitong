#!/bin/bash
# ============================================================================
# 服务器端完整修复脚本
# ============================================================================
# 修复 API 端口错误和数据库未加载问题
# ============================================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🔧 开始修复系统问题"
echo "=========================================="

# 进入项目目录
PROJECT_DIR="/var/www/xitong"
cd "$PROJECT_DIR" || { echo "❌ 项目目录不存在: $PROJECT_DIR"; exit 1; }

echo ""
echo "📂 当前目录: $(pwd)"

# ──────────────────────────────────────────────────────────────────────────
# 步骤 1: 备份当前状态
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "1️⃣  备份当前容器状态..."
docker compose ps > backup-container-status.txt 2>/dev/null || true
echo "✓ 状态已备份到 backup-container-status.txt"

# ──────────────────────────────────────────────────────────────────────────
# 步骤 2: 拉取最新代码
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "2️⃣  拉取最新代码..."

# 确保使用 HTTPS
git remote set-url origin https://github.com/asdfgtrewq748/xitong.git
echo "✓ 切换到 HTTPS"

# 拉取代码
git fetch origin
git reset --hard origin/master
echo "✓ 代码已更新到最新版本"

# 显示最新提交
echo "最新提交:"
git log --oneline -3

# ──────────────────────────────────────────────────────────────────────────
# 步骤 3: 停止旧容器
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "3️⃣  停止旧容器..."
docker compose down
echo "✓ 容器已停止"

# ──────────────────────────────────────────────────────────────────────────
# 步骤 4: 重新构建镜像（使用 BuildKit 加速）
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "4️⃣  重新构建镜像（启用 BuildKit）..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 只重新构建前端（因为前端代码变了）
echo "   重新构建前端..."
docker compose build frontend

# 后端也需要重新构建（因为添加了数据库初始化代码）
echo "   重新构建后端..."
docker compose build backend

echo "✓ 镜像构建完成"

# ──────────────────────────────────────────────────────────────────────────
# 步骤 5: 启动新容器
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "5️⃣  启动新容器..."
docker compose up -d
echo "✓ 容器已启动"

# ──────────────────────────────────────────────────────────────────────────
# 步骤 6: 等待服务启动
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "6️⃣  等待服务启动..."
sleep 15

# ──────────────────────────────────────────────────────────────────────────
# 步骤 7: 检查容器状态
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "7️⃣  检查容器状态..."
docker compose ps

# ──────────────────────────────────────────────────────────────────────────
# 步骤 8: 验证后端服务
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "8️⃣  验证后端服务..."

# 检查健康状态
if curl -f http://localhost:8000/api/health 2>/dev/null; then
    echo "✓ 后端健康检查通过"
else
    echo "⚠️  后端健康检查失败，查看日志:"
    docker compose logs backend | tail -30
fi

# 检查数据库
echo ""
echo "   检查数据库状态..."
DB_CHECK=$(docker compose exec -T backend python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:////app/data/database.db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM records'))
    count = result.fetchone()[0]
    print(f'{count}')
" 2>&1)

if [ "$DB_CHECK" -gt 0 ] 2>/dev/null; then
    echo "✓ 数据库已加载 ($DB_CHECK 条记录)"
else
    echo "⚠️  数据库为空或检查失败，查看详细日志:"
    docker compose logs backend | grep -A 20 "数据库"
fi

# ──────────────────────────────────────────────────────────────────────────
# 步骤 9: 验证前端服务
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "9️⃣  验证前端服务..."

if curl -f http://localhost 2>/dev/null | grep -q "煤层"; then
    echo "✓ 前端服务正常"
else
    echo "⚠️  前端服务可能未就绪，查看日志:"
    docker compose logs frontend | tail -20
fi

# 检查 Nginx 代理配置
echo ""
echo "   检查 API 代理..."
if curl -f http://localhost/api/health 2>/dev/null; then
    echo "✓ API 反向代理正常"
else
    echo "⚠️  API 反向代理可能有问题"
fi

# ──────────────────────────────────────────────────────────────────────────
# 步骤 10: 显示访问信息
# ──────────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "服务访问地址:"
echo "  - 前端: http://$SERVER_IP"
echo "  - 后端: http://$SERVER_IP:8000"
echo "  - API: http://$SERVER_IP/api/"
echo ""
echo "查看日志:"
echo "  docker compose logs -f backend"
echo "  docker compose logs -f frontend"
echo ""
echo "测试命令:"
echo "  curl http://localhost/api/health"
echo "  curl http://localhost/api/database/overview"
echo "=========================================="
