# Makefile for Mining System Docker Deployment

.PHONY: help build up down restart logs ps clean backup

# 默认目标
help:
	@echo "矿山工程分析系统 - Docker 命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make build    - 构建 Docker 镜像"
	@echo "  make up       - 启动所有服务"
	@echo "  make down     - 停止所有服务"
	@echo "  make restart  - 重启所有服务"
	@echo "  make logs     - 查看所有日志"
	@echo "  make ps       - 查看服务状态"
	@echo "  make clean    - 完全清理(删除容器、镜像、数据卷)"
	@echo "  make backup   - 备份数据"
	@echo ""

# 构建镜像
build:
	@echo "构建 Docker 镜像..."
	docker-compose build --no-cache

# 启动服务
up:
	@echo "启动服务..."
	docker-compose up -d
	@echo "等待服务启动..."
	@sleep 10
	@echo "服务已启动!"
	@echo "访问地址: http://localhost"

# 停止服务
down:
	@echo "停止服务..."
	docker-compose down

# 重启服务
restart:
	@echo "重启服务..."
	docker-compose restart

# 查看日志
logs:
	docker-compose logs -f

# 查看状态
ps:
	docker-compose ps

# 完全清理
clean:
	@echo "⚠️  警告: 这将删除所有容器、镜像和数据!"
	@read -p "确认继续? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "清理中..."; \
		docker-compose down -v --rmi all --remove-orphans; \
		echo "清理完成!"; \
	else \
		echo "已取消"; \
	fi

# 备份数据
backup:
	@echo "执行数据备份..."
	@if command -v bash >/dev/null 2>&1; then \
		bash backup.sh; \
	else \
		echo "请手动运行: ./backup.sh (Linux/Mac) 或 .\backup.ps1 (Windows)"; \
	fi

# 开发模式(启动并查看日志)
dev:
	docker-compose up

# 查看后端日志
logs-backend:
	docker-compose logs -f backend

# 查看前端日志
logs-frontend:
	docker-compose logs -f frontend

# 进入后端容器
shell-backend:
	docker-compose exec backend bash

# 进入前端容器
shell-frontend:
	docker-compose exec frontend sh
