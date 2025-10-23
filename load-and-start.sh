#!/bin/bash
# ============================================================================
# 服务器端镜像导入和启动脚本
# ============================================================================
# 用途: 在服务器上导入本地构建的镜像并启动服务
# 使用: bash load-and-start.sh
# ============================================================================

set -e  # 遇到错误立即退出

echo "======================================="
echo "Docker 镜像导入与启动工具"
echo "======================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}✗ 错误: 找不到 docker-compose.yml${NC}"
    echo "请在项目根目录执行此脚本"
    exit 1
fi

echo -e "${YELLOW}[1/5] 检查镜像文件...${NC}"

# 检查镜像文件是否存在
BACKEND_TAR="/tmp/mining-backend.tar"
FRONTEND_TAR="/tmp/mining-frontend.tar"

if [ ! -f "$BACKEND_TAR" ]; then
    echo -e "${RED}✗ 找不到后端镜像: $BACKEND_TAR${NC}"
    echo "请先上传镜像文件到 /tmp/ 目录"
    exit 1
fi

if [ ! -f "$FRONTEND_TAR" ]; then
    echo -e "${RED}✗ 找不到前端镜像: $FRONTEND_TAR${NC}"
    echo "请先上传镜像文件到 /tmp/ 目录"
    exit 1
fi

echo -e "${GREEN}✓ 镜像文件检查通过${NC}"
echo "  后端镜像: $(du -h $BACKEND_TAR | cut -f1)"
echo "  前端镜像: $(du -h $FRONTEND_TAR | cut -f1)"
echo ""

# 停止旧容器
echo -e "${YELLOW}[2/5] 停止旧容器...${NC}"
sudo docker compose down || true
echo -e "${GREEN}✓ 旧容器已停止${NC}"
echo ""

# 删除旧镜像（可选）
echo -e "${YELLOW}[3/5] 清理旧镜像...${NC}"
sudo docker rmi mining-system-backend:latest 2>/dev/null || true
sudo docker rmi mining-system-frontend:latest 2>/dev/null || true
echo -e "${GREEN}✓ 旧镜像已清理${NC}"
echo ""

# 导入镜像
echo -e "${YELLOW}[4/5] 导入镜像...${NC}"

echo "导入后端镜像..."
sudo docker load -i "$BACKEND_TAR"
echo -e "${GREEN}✓ 后端镜像导入成功${NC}"

echo "导入前端镜像..."
sudo docker load -i "$FRONTEND_TAR"
echo -e "${GREEN}✓ 前端镜像导入成功${NC}"
echo ""

# 验证镜像
echo "验证导入的镜像:"
sudo docker images | grep mining-system
echo ""

# 启动服务
echo -e "${YELLOW}[5/5] 启动服务...${NC}"
sudo docker compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 服务启动成功${NC}"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    exit 1
fi

echo ""

# 等待几秒后检查状态
echo "等待容器启动..."
sleep 5

echo ""
echo "======================================="
echo "容器状态:"
echo "======================================="
sudo docker compose ps
echo ""

echo "======================================="
echo "健康检查:"
echo "======================================="

# 检查后端
echo -n "后端 API: "
if curl -s -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 正常${NC}"
else
    echo -e "${RED}✗ 异常${NC}"
    echo "查看后端日志:"
    echo "  sudo docker compose logs backend"
fi

# 检查前端
echo -n "前端服务: "
if curl -s -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 正常${NC}"
else
    echo -e "${RED}✗ 异常${NC}"
    echo "查看前端日志:"
    echo "  sudo docker compose logs frontend"
fi

echo ""
echo "======================================="
echo "部署完成！"
echo "======================================="
echo ""
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "常用命令:"
echo "  查看日志: sudo docker compose logs -f"
echo "  重启服务: sudo docker compose restart"
echo "  停止服务: sudo docker compose down"
echo ""

# 清理临时文件
echo -e "${YELLOW}清理临时文件...${NC}"
read -p "是否删除 /tmp/ 中的镜像文件? (y/n) [默认: n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$BACKEND_TAR" "$FRONTEND_TAR"
    echo -e "${GREEN}✓ 临时文件已清理${NC}"
fi

echo ""
