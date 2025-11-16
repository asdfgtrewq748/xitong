#!/bin/bash
# ============================================================================
# Docker部署验证脚本 - 确保版本一致性
# ============================================================================
# 用途：在部署前验证所有配置是否正确
# 版本：v3.0.3
# ============================================================================

set -e

echo "=========================================="
echo "Docker部署前验证检查"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} 文件存在: $1"
        return 0
    else
        echo -e "${RED}✗${NC} 文件缺失: $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} 目录存在: $1"
        return 0
    else
        echo -e "${RED}✗${NC} 目录缺失: $1"
        return 1
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# 1. 检查Docker配置文件
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "1️⃣  检查Docker配置文件..."
check_file "docker-compose.yml"
check_file "backend/Dockerfile"
check_file "frontend/Dockerfile"
check_file "frontend/nginx.conf"

# ────────────────────────────────────────────────────────────────────────────
# 2. 检查必要的目录结构
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "2️⃣  检查目录结构..."
check_dir "backend"
check_dir "frontend"
check_dir "data"
check_dir "data/input"

# ────────────────────────────────────────────────────────────────────────────
# 3. 检查关键数据文件
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "3️⃣  检查数据文件..."
if check_file "data/input/汇总表.csv"; then
    lines=$(wc -l < "data/input/汇总表.csv")
    echo -e "   ${GREEN}→${NC} CSV文件行数: $lines"
fi

# ────────────────────────────────────────────────────────────────────────────
# 4. 检查依赖配置
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "4️⃣  检查依赖配置..."
check_file "backend/requirements.txt"
check_file "frontend/package.json"

# 检查关键依赖
echo ""
echo "   检查前端关键依赖..."
if grep -q "svg2pdf.js" frontend/package.json; then
    version=$(grep "svg2pdf.js" frontend/package.json | sed -E 's/.*"([^"]+)".*/\1/')
    echo -e "   ${GREEN}✓${NC} svg2pdf.js: $version"
else
    echo -e "   ${RED}✗${NC} 缺少 svg2pdf.js"
fi

if grep -q "echarts-gl" frontend/package.json; then
    version=$(grep "echarts-gl" frontend/package.json | sed -E 's/.*"([^"]+)".*/\1/')
    echo -e "   ${GREEN}✓${NC} echarts-gl: $version"
else
    echo -e "   ${RED}✗${NC} 缺少 echarts-gl"
fi

# ────────────────────────────────────────────────────────────────────────────
# 5. 检查环境变量配置
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "5️⃣  检查环境变量配置..."
check_file "frontend/.env.production"
check_file "frontend/.env.development"

if [ -f "frontend/.env.production" ]; then
    api_url=$(grep "VUE_APP_API_BASE_URL" frontend/.env.production | cut -d= -f2)
    echo -e "   ${GREEN}→${NC} 生产环境API: $api_url"
fi

# ────────────────────────────────────────────────────────────────────────────
# 6. 检查Docker和Docker Compose版本
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "6️⃣  检查Docker环境..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo -e "${GREEN}✓${NC} $docker_version"
else
    echo -e "${RED}✗${NC} Docker未安装"
fi

if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} $compose_version"
else
    echo -e "${RED}✗${NC} Docker Compose未安装"
fi

# ────────────────────────────────────────────────────────────────────────────
# 7. 检查chartWrapper.js配置
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "7️⃣  检查图表配置文件..."
if check_file "frontend/src/utils/chartWrapper.js"; then
    # 检查所有图表生成函数
    functions=(
        "generateScatterOption"
        "generateLineOption"
        "generateBarOption"
        "generateBoxPlotOption"
        "generateHistogramOption"
        "generateHeatmapOption"
        "generateSurfaceOption"
    )
    
    for func in "${functions[@]}"; do
        if grep -q "$func" frontend/src/utils/chartWrapper.js; then
            echo -e "   ${GREEN}✓${NC} $func"
        else
            echo -e "   ${RED}✗${NC} 缺少 $func"
        fi
    done
fi

# ────────────────────────────────────────────────────────────────────────────
# 8. 检查所有图表页面
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "8️⃣  检查图表页面组件..."
pages=(
    "ScatterPlotPage.vue"
    "LineChartPage.vue"
    "BarChartPage.vue"
    "BoxPlotPage.vue"
    "HistogramPage.vue"
    "HeatMapPage.vue"
    "Surface3DPage.vue"
)

for page in "${pages[@]}"; do
    if check_file "frontend/src/components/visualization/pages/$page"; then
        # 检查是否有渐变色header
        if grep -q "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" "frontend/src/components/visualization/pages/$page"; then
            echo -e "   ${GREEN}→${NC} $page 配色已统一"
        else
            echo -e "   ${YELLOW}⚠${NC} $page 配色可能未统一"
        fi
    fi
done

# ────────────────────────────────────────────────────────────────────────────
# 总结
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
echo ""
echo "如果所有检查都通过，可以执行以下命令部署："
echo ""
echo -e "${GREEN}# 构建并启动容器${NC}"
echo "docker-compose up -d --build"
echo ""
echo -e "${GREEN}# 查看容器状态${NC}"
echo "docker-compose ps"
echo ""
echo -e "${GREEN}# 查看容器日志${NC}"
echo "docker-compose logs -f"
echo ""
echo -e "${GREEN}# 健康检查${NC}"
echo "curl http://localhost:8000/api/health"
echo "curl http://localhost/"
echo ""
