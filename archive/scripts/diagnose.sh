#!/bin/bash
# ============================================================================
# 快速诊断脚本 - 排查容器启动问题
# ============================================================================

echo "======================================="
echo "Docker 容器诊断工具"
echo "======================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}[1] 检查容器状态${NC}"
echo "======================================="
sudo docker compose ps
echo ""

echo -e "${CYAN}[2] 查看后端容器日志（最后50行）${NC}"
echo "======================================="
sudo docker compose logs --tail=50 backend
echo ""

echo -e "${CYAN}[3] 检查后端容器详细状态${NC}"
echo "======================================="
sudo docker inspect mining-backend --format='{{json .State.Health}}' | python3 -m json.tool 2>/dev/null || sudo docker inspect mining-backend --format='{{.State.Health}}'
echo ""

echo -e "${CYAN}[4] 尝试进入后端容器执行健康检查${NC}"
echo "======================================="
echo "手动测试健康检查命令..."
sudo docker exec mining-backend python -c "import requests; print(requests.get('http://localhost:8000/api/health', timeout=5).text)" 2>&1 || echo -e "${RED}健康检查命令执行失败${NC}"
echo ""

echo -e "${CYAN}[5] 检查端口占用${NC}"
echo "======================================="
sudo netstat -tulpn | grep -E ':8000|:80' || echo "未发现端口占用"
echo ""

echo -e "${CYAN}[6] 检查数据目录权限${NC}"
echo "======================================="
ls -la backend/data backend/logs 2>/dev/null || echo "目录不存在"
echo ""

echo -e "${YELLOW}建议的排查步骤：${NC}"
echo "1. 查看上面的日志输出，寻找错误信息"
echo "2. 如果看到 ModuleNotFoundError，说明依赖安装不完整"
echo "3. 如果看到 Permission denied，需要修复目录权限"
echo "4. 如果看到端口占用，需要停止占用端口的进程"
echo ""
