#!/bin/bash
# ============================================================================
# 数据库初始化脚本 - 导入 CSV 数据到 Docker 容器中的数据库
# ============================================================================
# 用途: 将本地的 CSV 数据导入到运行中的 Docker 容器的数据库
# 使用方法: bash init-database.sh
# ============================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}数据库初始化脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查容器是否运行
echo -e "\n${YELLOW}[1/5] 检查容器状态...${NC}"
if ! docker compose ps | grep -q "mining-backend.*Up"; then
    echo -e "${RED}错误: backend 容器未运行${NC}"
    echo "请先运行: docker compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ backend 容器正在运行${NC}"

# 检查 CSV 文件是否存在
echo -e "\n${YELLOW}[2/5] 检查 CSV 源文件...${NC}"
CSV_FILE="data/input/汇总表.csv"
if [ ! -f "$CSV_FILE" ]; then
    echo -e "${RED}错误: 未找到 CSV 文件: $CSV_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 找到 CSV 文件: $CSV_FILE${NC}"

# 确保容器内的数据目录存在
echo -e "\n${YELLOW}[3/5] 准备数据目录...${NC}"
docker exec mining-backend mkdir -p /app/data/input
docker exec mining-backend mkdir -p /app/data
echo -e "${GREEN}✓ 数据目录已准备${NC}"

# 复制 CSV 文件到容器
echo -e "\n${YELLOW}[4/5] 复制 CSV 文件到容器...${NC}"
docker cp "$CSV_FILE" mining-backend:/app/data/input/汇总表.csv
echo -e "${GREEN}✓ CSV 文件已复制到容器${NC}"

# 在容器中运行导入脚本
echo -e "\n${YELLOW}[5/5] 执行数据导入...${NC}"
docker exec mining-backend python -c "
import sys
sys.path.insert(0, '/app')
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
print(f'列名: {list(df.columns)}')

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

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ 数据库初始化成功!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n${BLUE}现在可以访问以下地址查看数据:${NC}"
    echo -e "  前端: ${GREEN}http://localhost${NC}"
    echo -e "  后端: ${GREEN}http://localhost:8000${NC}"
    echo -e "  数据库概览: ${GREEN}http://localhost:8000/api/database/overview${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}✗ 数据库初始化失败${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "\n${YELLOW}查看容器日志:${NC}"
    echo "  docker logs mining-backend"
    exit 1
fi
