#!/bin/bash
# ============================================================================
# 一键修复并初始化数据库 - 修正版
# ============================================================================

set -e

echo "========================================"
echo "修复权限并初始化数据库"
echo "========================================"

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
sudo docker exec mining-backend python -c "
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# 读取 CSV
csv_path = Path('/app/data/input/汇总表.csv')
print(f'读取 CSV 文件: {csv_path}')

encodings = ('utf-8-sig', 'utf-8', 'gbk', 'gb2312')
df = None
for encoding in encodings:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        print(f'成功使用 {encoding} 编码读取 CSV')
        break
    except Exception as e:
        continue

if df is None:
    print('错误: 无法读取 CSV 文件')
    sys.exit(1)

print(f'读取到 {len(df)} 条记录')

# 创建数据库
db_path = Path('/app/data/database.db')
engine = create_engine(f'sqlite:///{db_path}', future=True)

print(f'创建数据库: {db_path}')
with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS records'))

# 导入数据
df.to_sql('records', engine, if_exists='replace', index=False)
print(f'已导入 {len(df)} 条记录')

# 创建索引
with engine.begin() as conn:
    if '份' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_province ON records (\"份\")')
        print('创建索引: idx_records_province')
    if '矿名' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_mine ON records (\"矿名\")')
        print('创建索引: idx_records_mine')
    if '岩性' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_lithology ON records (\"岩性\")')
        print('创建索引: idx_records_lithology')

print('数据库初始化完成!')
"

echo "✓ 数据导入完成"

echo -e "\n[7/7] 验证结果..."
if [ -f "backend/data/database.db" ]; then
    echo "✓ 数据库文件已创建"
    ls -lh backend/data/database.db
    
    # 验证记录数
    echo -e "\n验证数据..."
    sudo docker exec mining-backend python -c "
from sqlalchemy import create_engine, select, func, MetaData
engine = create_engine('sqlite:////app/data/database.db')
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables.get('records')
if table is not None:
    with engine.connect() as conn:
        count = conn.execute(select(func.count()).select_from(table)).scalar()
        print(f'✓ 数据库中有 {count} 条记录')
else:
    print('✗ 表不存在')
"
else
    echo "✗ 数据库文件不存在"
    exit 1
fi

echo -e "\n========================================"
echo "✓ 全部完成!"
echo "========================================"
echo ""
echo "测试 API:"
echo "  curl http://localhost:8000/api/database/overview"
echo ""
echo "查看日志:"
echo "  sudo docker logs mining-backend --tail 50"
echo ""
echo "访问前端:"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "  http://$SERVER_IP"
