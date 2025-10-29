#!/bin/bash
# ============================================================================
# 快速修复和重启脚本
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "======================================="
echo "快速修复和重启"
echo "======================================="
echo ""

# 1. 停止所有容器
echo -e "${YELLOW}[1/6] 停止容器...${NC}"
sudo docker compose down
echo -e "${GREEN}✓ 容器已停止${NC}"
echo ""

# 2. 确保数据目录存在且权限正确
echo -e "${YELLOW}[2/6] 检查数据目录...${NC}"
sudo mkdir -p backend/data backend/logs frontend/logs
sudo chmod 777 backend/data backend/logs frontend/logs
echo -e "${GREEN}✓ 数据目录已准备${NC}"
echo ""

# 3. 检查是否需要重新构建
echo -e "${YELLOW}[3/6] 检查镜像...${NC}"
if sudo docker images | grep -q "mining-system-backend.*latest"; then
    echo "发现现有镜像"
    read -p "是否重新构建镜像？(y/n) [默认: n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "重新构建..."
        sudo docker compose build --no-cache
    else
        echo "跳过构建，使用现有镜像"
    fi
else
    echo -e "${RED}未找到镜像，需要构建或导入${NC}"
    echo "选择操作:"
    echo "  1) 重新构建 (较慢)"
    echo "  2) 从 /tmp/ 导入镜像 (较快)"
    read -p "请选择 [1/2]: " choice
    
    if [ "$choice" = "2" ]; then
        if [ -f "/tmp/mining-backend.tar" ] && [ -f "/tmp/mining-frontend.tar" ]; then
            echo "导入镜像..."
            sudo docker load -i /tmp/mining-backend.tar
            sudo docker load -i /tmp/mining-frontend.tar
            echo -e "${GREEN}✓ 镜像导入完成${NC}"
        else
            echo -e "${RED}错误: 找不到镜像文件${NC}"
            echo "请先上传镜像到 /tmp/ 或选择重新构建"
            exit 1
        fi
    else
        echo "开始构建..."
        sudo docker compose build --no-cache
    fi
fi
echo ""

# 4. 清理旧的健康检查失败的容器
echo -e "${YELLOW}[4/6] 清理旧容器...${NC}"
sudo docker rm -f mining-backend mining-frontend 2>/dev/null || true
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 5. 启动服务（不使用 -d，先看日志）
echo -e "${YELLOW}[5/6] 启动服务...${NC}"
echo "提示: 按 Ctrl+C 可以停止查看日志，服务会继续在后台运行"
echo ""
sudo docker compose up -d
echo -e "${GREEN}✓ 服务已启动${NC}"
echo ""

# 6. 等待并检查状态
echo -e "${YELLOW}[6/6] 等待服务就绪...${NC}"
echo "等待 60 秒让服务完全启动..."

for i in {1..12}; do
    sleep 5
    echo -n "."
    
    # 检查后端健康状态
    backend_health=$(sudo docker inspect mining-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
    
    if [ "$backend_health" = "healthy" ]; then
        echo ""
        echo -e "${GREEN}✓ 后端容器已健康！${NC}"
        break
    fi
    
    if [ $i -eq 12 ]; then
        echo ""
        echo -e "${YELLOW}警告: 后端健康检查仍未通过${NC}"
        echo "当前状态: $backend_health"
    fi
done

echo ""
echo "======================================="
echo "容器状态:"
echo "======================================="
sudo docker compose ps
echo ""

echo "======================================="
echo "健康检查结果:"
echo "======================================="
echo -n "后端: "
backend_health=$(sudo docker inspect mining-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
if [ "$backend_health" = "healthy" ]; then
    echo -e "${GREEN}✓ 健康${NC}"
else
    echo -e "${RED}✗ $backend_health${NC}"
    echo ""
    echo "后端日志（最后30行）:"
    sudo docker compose logs --tail=30 backend
fi

echo ""
echo -n "前端: "
frontend_status=$(sudo docker inspect mining-frontend --format='{{.State.Status}}' 2>/dev/null || echo "unknown")
if [ "$frontend_status" = "running" ]; then
    echo -e "${GREEN}✓ 运行中${NC}"
else
    echo -e "${RED}✗ $frontend_status${NC}"
fi

echo ""
echo "======================================="
echo "测试访问:"
echo "======================================="

echo -n "后端 API: "
if curl -s -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 可访问${NC}"
    curl -s http://localhost:8000/api/health
else
    echo -e "${RED}✗ 无法访问${NC}"
fi

echo ""
echo -n "前端页面: "
if curl -s -f http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 可访问${NC}"
else
    echo -e "${RED}✗ 无法访问${NC}"
fi

echo ""
echo "======================================="
echo "常用命令:"
echo "======================================="
echo "  查看实时日志: sudo docker compose logs -f"
echo "  查看后端日志: sudo docker compose logs backend"
echo "  重启服务:     sudo docker compose restart"
echo "  停止服务:     sudo docker compose down"
echo "  进入后端:     sudo docker exec -it mining-backend bash"
echo ""

if [ "$backend_health" != "healthy" ]; then
    echo -e "${YELLOW}提示: 后端未完全健康，建议查看日志排查问题${NC}"
    echo "运行: sudo docker compose logs backend"
fi

echo ""
