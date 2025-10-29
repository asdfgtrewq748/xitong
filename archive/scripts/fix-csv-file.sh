#!/bin/bash
# ============================================================================
# 临时修复：手动复制 CSV 文件到后端容器
# ============================================================================

echo "🔍 检查 CSV 文件..."
if [ ! -f "data/input/汇总表.csv" ]; then
    echo "❌ 本地 CSV 文件不存在！"
    exit 1
fi

echo "📋 CSV 文件信息:"
ls -lh data/input/汇总表.csv
wc -l data/input/汇总表.csv

echo ""
echo "📦 复制 CSV 文件到容器..."
docker cp data/input/汇总表.csv mining-backend:/app/data/input/

echo ""
echo "✅ 验证容器内文件..."
docker compose exec backend ls -lh /app/data/input/
docker compose exec backend wc -l /app/data/input/汇总表.csv

echo ""
echo "🔄 重启后端容器（触发数据库初始化）..."
docker compose restart backend

echo ""
echo "⏳ 等待启动..."
sleep 10

echo ""
echo "📊 查看日志..."
docker compose logs backend | tail -30

echo ""
echo "🔍 检查数据库..."
docker compose exec backend python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:////app/data/database.db')
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM records'))
        count = result.fetchone()[0]
        print(f'✅ 数据库记录数: {count}')
except Exception as e:
    print(f'❌ 数据库错误: {e}')
"

echo ""
echo "✨ 完成！"
