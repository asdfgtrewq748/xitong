#!/bin/bash

# Docker 健康检查脚本
# 用途: 检查所有服务是否正常运行

echo "======================================"
echo "   服务健康检查"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查函数
check_service() {
    local name=$1
    local url=$2
    local timeout=5
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name: 正常"
        return 0
    else
        echo -e "${RED}✗${NC} $name: 异常"
        return 1
    fi
}

# 检查容器状态
echo "1. 容器状态检查"
echo "-------------------------------------"
docker-compose ps
echo ""

# 检查服务健康
echo "2. 服务健康检查"
echo "-------------------------------------"
check_service "前端服务" "http://localhost/health"
check_service "后端API" "http://localhost:8000/api/health"
echo ""

# 检查端口监听
echo "3. 端口监听检查"
echo "-------------------------------------"
if netstat -an 2>/dev/null | grep -q ":80.*LISTEN" || ss -ln 2>/dev/null | grep -q ":80"; then
    echo -e "${GREEN}✓${NC} 端口 80 (前端): 正常"
else
    echo -e "${RED}✗${NC} 端口 80 (前端): 未监听"
fi

if netstat -an 2>/dev/null | grep -q ":8000.*LISTEN" || ss -ln 2>/dev/null | grep -q ":8000"; then
    echo -e "${GREEN}✓${NC} 端口 8000 (后端): 正常"
else
    echo -e "${RED}✗${NC} 端口 8000 (后端): 未监听"
fi
echo ""

# 检查数据库
echo "4. 数据库检查"
echo "-------------------------------------"
if docker-compose exec -T backend test -f /app/data/database.db 2>/dev/null; then
    db_size=$(docker-compose exec -T backend stat -f%z /app/data/database.db 2>/dev/null || docker-compose exec -T backend stat -c%s /app/data/database.db 2>/dev/null)
    echo -e "${GREEN}✓${NC} 数据库文件存在 (大小: $db_size 字节)"
else
    echo -e "${YELLOW}!${NC} 数据库文件不存在或无法访问"
fi
echo ""

# 检查日志错误
echo "5. 最近错误日志"
echo "-------------------------------------"
error_count=$(docker-compose logs --tail=100 2>/dev/null | grep -i "error" | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 未发现错误"
else
    echo -e "${YELLOW}!${NC} 发现 $error_count 个错误,请查看日志: docker-compose logs -f"
fi
echo ""

# 资源使用
echo "6. 资源使用情况"
echo "-------------------------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "无法获取资源使用信息"
echo ""

echo "======================================"
echo "   检查完成"
echo "======================================"
