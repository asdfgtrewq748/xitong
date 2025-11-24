#!/bin/bash
# ============================================================================
# 一键部署脚本 - 煤层地质建模系统
# ============================================================================
# 用途: 快速部署或更新系统
# 使用: ./deploy.sh [选项]
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ────────────────────────────────────────────────────────────────────────────
# 检查依赖
# ────────────────────────────────────────────────────────────────────────────
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# ────────────────────────────────────────────────────────────────────────────
# 拉取最新代码（如果是Git仓库）
# ────────────────────────────────────────────────────────────────────────────
pull_latest_code() {
    if [ -d .git ]; then
        log_info "拉取最新代码..."
        git pull origin main || git pull origin master
    else
        log_warn "不是Git仓库，跳过代码拉取"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# 备份数据
# ────────────────────────────────────────────────────────────────────────────
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份项目根目录的data文件夹（包含汇总表.csv等重要数据）
    if [ -d data ]; then
        cp -r data "$BACKUP_DIR/"
        log_info "数据已备份到 $BACKUP_DIR/data"
    else
        log_warn "没有找到data目录，跳过备份"
    fi
    
    # 备份日志
    if [ -d backend/logs ]; then
        cp -r backend/logs "$BACKUP_DIR/"
        log_info "日志已备份到 $BACKUP_DIR/logs"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# 构建镜像
# ────────────────────────────────────────────────────────────────────────────
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_info "镜像构建完成"
}

# ────────────────────────────────────────────────────────────────────────────
# 停止旧服务
# ────────────────────────────────────────────────────────────────────────────
stop_services() {
    log_info "停止旧服务..."
    
    docker-compose down
    
    log_info "服务已停止"
}

# ────────────────────────────────────────────────────────────────────────────
# 启动服务
# ────────────────────────────────────────────────────────────────────────────
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_info "服务启动中..."
}

# ────────────────────────────────────────────────────────────────────────────
# 健康检查
# ────────────────────────────────────────────────────────────────────────────
health_check() {
    log_info "等待服务启动..."
    sleep 15
    
    log_info "执行健康检查..."
    
    # 检查前端
    if curl -f http://localhost/health &> /dev/null; then
        log_info "✓ 前端服务正常"
    else
        log_error "✗ 前端服务异常"
        return 1
    fi
    
    # 检查后端
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        log_info "✓ 后端服务正常"
    else
        log_error "✗ 后端服务异常"
        return 1
    fi
    
    log_info "所有服务运行正常"
}

# ────────────────────────────────────────────────────────────────────────────
# 查看日志
# ────────────────────────────────────────────────────────────────────────────
view_logs() {
    log_info "查看服务日志..."
    docker-compose logs --tail=50 -f
}

# ────────────────────────────────────────────────────────────────────────────
# 清理旧镜像
# ────────────────────────────────────────────────────────────────────────────
cleanup() {
    log_info "清理旧镜像..."
    docker image prune -f
    log_info "清理完成"
}

# ────────────────────────────────────────────────────────────────────────────
# 显示状态
# ────────────────────────────────────────────────────────────────────────────
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    echo ""
    log_info "访问地址:"
    echo "  前端: http://localhost"
    echo "  后端API: http://localhost:8000/docs"
}

# ────────────────────────────────────────────────────────────────────────────
# 主函数
# ────────────────────────────────────────────────────────────────────────────
main() {
    echo "============================================================"
    echo "  煤层地质建模系统 - 一键部署脚本"
    echo "============================================================"
    echo ""
    
    # 解析参数
    SKIP_BACKUP=false
    SKIP_BUILD=false
    VIEW_LOGS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --logs)
                VIEW_LOGS=true
                shift
                ;;
            --help)
                echo "用法: ./deploy.sh [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-backup   跳过数据备份"
                echo "  --skip-build    跳过镜像构建（仅重启）"
                echo "  --logs          部署后查看日志"
                echo "  --help          显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行部署流程
    check_dependencies
    
    if [ "$SKIP_BACKUP" = false ]; then
        backup_data
    fi
    
    pull_latest_code
    
    if [ "$SKIP_BUILD" = false ]; then
        build_images
    fi
    
    stop_services
    start_services
    
    if health_check; then
        cleanup
        show_status
        
        echo ""
        log_info "部署成功！"
        
        if [ "$VIEW_LOGS" = true ]; then
            view_logs
        fi
    else
        log_error "部署失败，请检查日志"
        docker-compose logs --tail=100
        exit 1
    fi
}

# 运行主函数
main "$@"
