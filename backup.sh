#!/bin/bash

# 数据备份脚本
# 用途: 备份数据库和重要数据

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mining_system_backup_${DATE}"

echo "开始备份..."

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 创建临时目录
TEMP_DIR="${BACKUP_DIR}/temp_${DATE}"
mkdir -p ${TEMP_DIR}

# 备份数据库
echo "备份数据库..."
docker-compose exec -T backend cp /app/data/database.db /app/data/database_backup.db
docker cp mining_backend:/app/data/database.db ${TEMP_DIR}/database.db

# 备份数据文件
echo "备份数据文件..."
cp -r ./data/input ${TEMP_DIR}/input 2>/dev/null || true

# 备份配置文件
echo "备份配置文件..."
cp docker-compose.yml ${TEMP_DIR}/
cp nginx/nginx.conf ${TEMP_DIR}/nginx.conf 2>/dev/null || true
cp .env ${TEMP_DIR}/.env 2>/dev/null || true

# 打包
echo "打包备份文件..."
cd ${BACKUP_DIR}
tar -czf ${BACKUP_FILE}.tar.gz temp_${DATE}/
rm -rf temp_${DATE}

echo "备份完成: ${BACKUP_DIR}/${BACKUP_FILE}.tar.gz"

# 清理旧备份(保留最近7天)
find ${BACKUP_DIR} -name "mining_system_backup_*.tar.gz" -mtime +7 -delete

echo "旧备份已清理(保留最近7天)"
