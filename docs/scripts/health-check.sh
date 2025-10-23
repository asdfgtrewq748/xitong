#!/bin/bash
# ============================================================================
# 健康检查脚本 - 煤层地质建模系统
# ============================================================================
# 用途: 检查系统各组件运行状态
# 使用: ./health-check.sh
# ============================================================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查结果统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
check_item() {
    local name=$1
    local command=$2
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "检查 $name ... "
    
    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Docker检查
# ────────────────────────────────────────────────────────────────────────────
check_docker() {
    echo -e "${BLUE}[Docker检查]${NC}"
    
    check_item "Docker服务" "docker info"
    check_item "Docker Compose" "docker-compose version"
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 容器检查
# ────────────────────────────────────────────────────────────────────────────
check_containers() {
    echo -e "${BLUE}[容器检查]${NC}"
    
    check_item "后端容器运行" "docker ps | grep mining-backend"
    check_item "前端容器运行" "docker ps | grep mining-frontend"
    
    # 检查容器健康状态
    if docker ps --format '{{.Names}}\t{{.Status}}' | grep mining-backend | grep -q "healthy"; then
        echo -e "后端容器健康状态 ... ${GREEN}✓ healthy${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "后端容器健康状态 ... ${YELLOW}⚠ 检查中或不健康${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if docker ps --format '{{.Names}}\t{{.Status}}' | grep mining-frontend | grep -q "healthy"; then
        echo -e "前端容器健康状态 ... ${GREEN}✓ healthy${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "前端容器健康状态 ... ${YELLOW}⚠ 检查中或不健康${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 服务端点检查
# ────────────────────────────────────────────────────────────────────────────
check_endpoints() {
    echo -e "${BLUE}[服务端点检查]${NC}"
    
    check_item "前端首页" "curl -f -s http://localhost/ -o /dev/null"
    check_item "前端健康检查" "curl -f -s http://localhost/health -o /dev/null"
    check_item "后端健康检查" "curl -f -s http://localhost:8000/api/health -o /dev/null"
    check_item "后端API文档" "curl -f -s http://localhost:8000/docs -o /dev/null"
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 资源使用检查
# ────────────────────────────────────────────────────────────────────────────
check_resources() {
    echo -e "${BLUE}[资源使用情况]${NC}"
    
    # CPU和内存使用
    echo "容器资源使用:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep mining
    
    echo ""
    
    # 磁盘使用
    echo "Docker磁盘使用:"
    docker system df
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 日志检查
# ────────────────────────────────────────────────────────────────────────────
check_logs() {
    echo -e "${BLUE}[最近日志（最后10行）]${NC}"
    
    echo -e "${YELLOW}后端日志:${NC}"
    docker-compose logs --tail=10 backend
    
    echo ""
    echo -e "${YELLOW}前端日志:${NC}"
    docker-compose logs --tail=10 frontend
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 端口检查
# ────────────────────────────────────────────────────────────────────────────
check_ports() {
    echo -e "${BLUE}[端口检查]${NC}"
    
    check_item "端口80 (前端)" "netstat -tuln 2>/dev/null | grep ':80 ' || ss -tuln 2>/dev/null | grep ':80 '"
    check_item "端口8000 (后端)" "netstat -tuln 2>/dev/null | grep ':8000 ' || ss -tuln 2>/dev/null | grep ':8000 '"
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 数据目录检查
# ────────────────────────────────────────────────────────────────────────────
check_data() {
    echo -e "${BLUE}[数据目录检查]${NC}"
    
    check_item "后端数据目录" "[ -d backend/data ]"
    check_item "后端日志目录" "[ -d backend/logs ]"
    
    if [ -d backend/data ]; then
        echo "数据目录大小: $(du -sh backend/data | cut -f1)"
    fi
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 网络检查
# ────────────────────────────────────────────────────────────────────────────
check_network() {
    echo -e "${BLUE}[Docker网络检查]${NC}"
    
    check_item "mining-network网络" "docker network ls | grep mining-network"
    
    # 检查容器网络连接
    if docker network inspect mining-network &> /dev/null; then
        echo "网络中的容器:"
        docker network inspect mining-network --format '{{range .Containers}}  - {{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'
    fi
    
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# 主函数
# ────────────────────────────────────────────────────────────────────────────
main() {
    echo "============================================================"
    echo "  煤层地质建模系统 - 健康检查"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
    echo ""
    
    # 执行所有检查
    check_docker
    check_containers
    check_ports
    check_network
    check_endpoints
    check_data
    check_resources
    
    # 如果传入 --logs 参数，显示日志
    if [[ "$1" == "--logs" ]]; then
        check_logs
    fi
    
    # 统计结果
    echo "============================================================"
    echo -e "检查完成: 总计 ${TOTAL_CHECKS} 项"
    echo -e "${GREEN}通过: ${PASSED_CHECKS}${NC}"
    echo -e "${RED}失败: ${FAILED_CHECKS}${NC}"
    echo "============================================================"
    
    # 返回状态码
    if [ $FAILED_CHECKS -gt 0 ]; then
        echo -e "${YELLOW}存在失败项，请检查上述输出${NC}"
        exit 1
    else
        echo -e "${GREEN}所有检查通过！系统运行正常${NC}"
        exit 0
    fi
}

# 运行主函数
main "$@"
