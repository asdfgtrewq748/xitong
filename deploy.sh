#!/bin/bash

# 矿山工程分析系统 - Docker 部署脚本
# 用途: 一键部署整个系统

set -e

echo "============================================"
echo "   矿山工程分析系统 Docker 部署"
echo "============================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Docker和Docker Compose
echo -e "${YELLOW}检查依赖...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 环境检查通过${NC}"

# 创建必要的目录
echo -e "${YELLOW}创建必要的目录...${NC}"
mkdir -p data/input
mkdir -p nginx/ssl
mkdir -p logs

# 停止并删除旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker-compose down -v 2>/dev/null || true

# 清理旧镜像(可选)
read -p "是否清理旧的Docker镜像? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}清理旧镜像...${NC}"
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
fi

# 构建镜像
echo -e "${YELLOW}构建Docker镜像...${NC}"
docker-compose build --no-cache

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose ps

# 健康检查
echo -e "${YELLOW}执行健康检查...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost/health &> /dev/null && \
       curl -f http://localhost:8000/api/health &> /dev/null; then
        echo -e "${GREEN}✓ 所有服务运行正常!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "等待服务就绪... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}警告: 服务可能未完全启动${NC}"
    echo "请使用以下命令查看日志:"
    echo "  docker-compose logs -f"
fi

# 显示访问信息
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   部署完成!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "访问地址:"
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "查看日志:"
echo "  所有服务: docker-compose logs -f"
echo "  后端: docker-compose logs -f backend"
echo "  前端: docker-compose logs -f frontend"
echo ""
echo "停止服务:"
echo "  docker-compose stop"
echo ""
echo "重启服务:"
echo "  docker-compose restart"
echo ""
echo "完全清理:"
echo "  docker-compose down -v"
echo ""
