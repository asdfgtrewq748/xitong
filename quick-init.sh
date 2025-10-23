#!/bin/bash
# ============================================================================
# 一键修复数据库权限并初始化
# ============================================================================

set -e

echo "========================================"
echo "修复权限并初始化数据库"
echo "========================================"

# 进入项目目录
cd /var/www/xitong

echo -e "\n[1/7] 创建必要目录..."
sudo mkdir -p backend/data/input backend/logs
echo "✓ 目录已创建"

echo -e "\n[2/7] 修复权限..."
sudo chmod -R 777 backend/data backend/logs
echo "✓ 权限已修复"

echo -e "\n[3/7] 重启后端容器..."
sudo docker compose restart backend
echo "✓ 容器已重启"

echo -e "\n[4/7] 等待容器启动 (30秒)..."
sleep 30

echo -e "\n[5/7] 复制 CSV 文件到容器..."
sudo docker cp data/input/汇总表.csv mining-backend:/app/data/input/汇总表.csv
echo "✓ CSV 文件已复制"

echo -e "\n[6/7] 执行数据导入..."
sudo docker exec mining-backend python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db
echo "✓ 数据导入完成"

echo -e "\n[7/7] 验证结果..."
if [ -f "backend/data/database.db" ]; then
    echo "✓ 数据库文件已创建"
    ls -lh backend/data/database.db
else
    echo "✗ 数据库文件不存在"
    exit 1
fi

echo -e "\n========================================"
echo "✓ 全部完成!"
echo "========================================"
echo ""
echo "测试命令:"
echo "  curl http://localhost:8000/api/database/overview"
echo ""
echo "查看日志:"
echo "  sudo docker logs mining-backend --tail 50"
echo ""
echo "访问前端:"
echo "  http://$(hostname -I | awk '{print $1}')"
