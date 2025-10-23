#!/bin/bash
# ============================================================================
# 修复容器名称并初始化数据库
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker 容器检查与数据库初始化${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 docker compose 是否可用
echo -e "\n${YELLOW}[1/6] 检查 Docker Compose...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker 已安装${NC}"
else
    echo -e "${RED}✗ Docker 未安装${NC}"
    exit 1
fi

# 获取实际的容器信息
echo -e "\n${YELLOW}[2/6] 检查现有容器...${NC}"
CONTAINERS=$(docker compose ps --format json 2>/dev/null || echo "[]")

if [ "$CONTAINERS" = "[]" ] || [ -z "$CONTAINERS" ]; then
    echo -e "${RED}✗ 没有找到运行中的容器${NC}"
    echo -e "${YELLOW}正在启动容器...${NC}"
    docker compose up -d
    sleep 10
    CONTAINERS=$(docker compose ps --format json)
fi

# 查找 backend 容器
echo -e "\n${YELLOW}[3/6] 查找 backend 容器...${NC}"
BACKEND_CONTAINER=""

# 尝试多种方式找到容器
if docker ps --format "{{.Names}}" | grep -q "mining-backend"; then
    BACKEND_CONTAINER="mining-backend"
elif docker ps --format "{{.Names}}" | grep -q "xitong-backend"; then
    BACKEND_CONTAINER="xitong-backend"
elif docker ps --format "{{.Names}}" | grep -q "backend"; then
    BACKEND_CONTAINER=$(docker ps --format "{{.Names}}" | grep "backend" | head -n 1)
else
    # 从 docker compose 获取
    BACKEND_CONTAINER=$(docker compose ps backend --format json 2>/dev/null | grep -o '"Name":"[^"]*"' | cut -d'"' -f4 | head -n 1)
fi

if [ -z "$BACKEND_CONTAINER" ]; then
    echo -e "${RED}✗ 未找到 backend 容器${NC}"
    echo -e "${YELLOW}当前所有容器:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 1
fi

echo -e "${GREEN}✓ 找到 backend 容器: ${BACKEND_CONTAINER}${NC}"

# 检查容器状态
echo -e "\n${YELLOW}[4/6] 检查容器状态...${NC}"
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$BACKEND_CONTAINER" 2>/dev/null || echo "not_found")

if [ "$CONTAINER_STATUS" != "running" ]; then
    echo -e "${RED}✗ 容器未运行 (状态: $CONTAINER_STATUS)${NC}"
    echo -e "${YELLOW}正在启动容器...${NC}"
    docker compose up -d
    sleep 10
fi

echo -e "${GREEN}✓ 容器正在运行${NC}"

# 检查 CSV 文件
echo -e "\n${YELLOW}[5/6] 检查 CSV 文件...${NC}"
if [ ! -f "data/input/汇总表.csv" ]; then
    echo -e "${RED}✗ 未找到 CSV 文件: data/input/汇总表.csv${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 找到 CSV 文件${NC}"

# 复制文件并导入
echo -e "\n${YELLOW}[6/6] 初始化数据库...${NC}"

# 创建目录
docker exec "$BACKEND_CONTAINER" mkdir -p /app/data/input 2>/dev/null || true

# 复制 CSV
echo "  - 复制 CSV 文件到容器..."
docker cp "data/input/汇总表.csv" "$BACKEND_CONTAINER:/app/data/input/汇总表.csv"

# 执行导入
echo "  - 执行数据导入..."
docker exec "$BACKEND_CONTAINER" python /app/scripts/import_database.py \
    --csv /app/data/input/汇总表.csv \
    --database /app/data/database.db

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ 数据库初始化成功!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # 验证数据
    echo -e "\n${BLUE}验证数据...${NC}"
    docker exec "$BACKEND_CONTAINER" python -c "
from sqlalchemy import create_engine, select, func, MetaData
engine = create_engine('sqlite:////app/data/database.db')
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables.get('records')
if table is not None:
    with engine.connect() as conn:
        count = conn.execute(select(func.count()).select_from(table)).scalar()
        print(f'数据库中有 {count} 条记录')
else:
    print('表不存在')
"
    
    echo -e "\n${BLUE}访问地址:${NC}"
    echo -e "  前端: ${GREEN}http://$(hostname -I | awk '{print $1}')${NC}"
    echo -e "  或:   ${GREEN}http://localhost${NC}"
    echo -e "  后端: ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
    
    echo -e "\n${BLUE}查看日志:${NC}"
    echo -e "  ${YELLOW}docker logs $BACKEND_CONTAINER${NC}"
    echo -e "  ${YELLOW}docker compose logs backend${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}✗ 数据库初始化失败${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "\n${YELLOW}查看详细日志:${NC}"
    echo -e "  docker logs $BACKEND_CONTAINER --tail 50"
    exit 1
fi
