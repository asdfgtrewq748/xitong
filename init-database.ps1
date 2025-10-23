# ============================================================================
# 数据库初始化脚本 - 导入 CSV 数据到 Docker 容器中的数据库 (PowerShell)
# ============================================================================
# 用途: 将本地的 CSV 数据导入到运行中的 Docker 容器的数据库
# 使用方法: .\init-database.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "数据库初始化脚本" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

# 检查容器是否运行
Write-Host "`n[1/5] 检查容器状态..." -ForegroundColor Yellow
$containerStatus = docker compose ps --format json | ConvertFrom-Json
$backendRunning = $containerStatus | Where-Object { $_.Name -eq "mining-backend" -and $_.State -eq "running" }

if (-not $backendRunning) {
    Write-Host "错误: backend 容器未运行" -ForegroundColor Red
    Write-Host "请先运行: docker compose up -d"
    exit 1
}
Write-Host "✓ backend 容器正在运行" -ForegroundColor Green

# 检查 CSV 文件是否存在
Write-Host "`n[2/5] 检查 CSV 源文件..." -ForegroundColor Yellow
$csvFile = "data\input\汇总表.csv"
if (-not (Test-Path $csvFile)) {
    Write-Host "错误: 未找到 CSV 文件: $csvFile" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 找到 CSV 文件: $csvFile" -ForegroundColor Green

# 确保容器内的数据目录存在
Write-Host "`n[3/5] 准备数据目录..." -ForegroundColor Yellow
docker exec mining-backend mkdir -p /app/data/input 2>$null
docker exec mining-backend mkdir -p /app/data 2>$null
Write-Host "✓ 数据目录已准备" -ForegroundColor Green

# 复制 CSV 文件到容器
Write-Host "`n[4/5] 复制 CSV 文件到容器..." -ForegroundColor Yellow
docker cp $csvFile mining-backend:/app/data/input/汇总表.csv
Write-Host "✓ CSV 文件已复制到容器" -ForegroundColor Green

# 在容器中运行导入脚本
Write-Host "`n[5/5] 执行数据导入..." -ForegroundColor Yellow

$importScript = @'
import sys
sys.path.insert(0, '/app')
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# 读取 CSV
csv_path = Path('/app/data/input/汇总表.csv')
print(f'读取 CSV 文件: {csv_path}')

encodings = ('utf-8-sig', 'utf-8', 'gbk', 'gb2312')
df = None
for encoding in encodings:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        print(f'成功使用 {encoding} 编码读取 CSV')
        break
    except Exception as e:
        continue

if df is None:
    print('错误: 无法读取 CSV 文件')
    sys.exit(1)

print(f'读取到 {len(df)} 条记录')
print(f'列名: {list(df.columns)}')

# 创建数据库
db_path = Path('/app/data/database.db')
engine = create_engine(f'sqlite:///{db_path}', future=True)

print(f'创建数据库: {db_path}')
with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS records'))

# 导入数据
df.to_sql('records', engine, if_exists='replace', index=False)
print(f'已导入 {len(df)} 条记录')

# 创建索引
with engine.begin() as conn:
    if '份' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_province ON records ("份")')
        print('创建索引: idx_records_province')
    if '矿名' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_mine ON records ("矿名")')
        print('创建索引: idx_records_mine')
    if '岩性' in df.columns:
        conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_lithology ON records ("岩性")')
        print('创建索引: idx_records_lithology')

print('数据库初始化完成!')
'@

try {
    docker exec mining-backend python -c $importScript
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✓ 数据库初始化成功!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`n现在可以访问以下地址查看数据:" -ForegroundColor Blue
    Write-Host "  前端: " -NoNewline; Write-Host "http://localhost" -ForegroundColor Green
    Write-Host "  后端: " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Green
    Write-Host "  数据库概览: " -NoNewline; Write-Host "http://localhost:8000/api/database/overview" -ForegroundColor Green
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "✗ 数据库初始化失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "`n查看容器日志:" -ForegroundColor Yellow
    Write-Host "  docker logs mining-backend"
    exit 1
}
