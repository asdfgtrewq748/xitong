# 数据备份脚本 (Windows PowerShell)
# 用途: 备份数据库和重要数据

$BackupDir = ".\backups"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "mining_system_backup_$Date"

Write-Host "开始备份..." -ForegroundColor Yellow

# 创建备份目录
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# 创建临时目录
$TempDir = "$BackupDir\temp_$Date"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# 备份数据库
Write-Host "备份数据库..." -ForegroundColor Yellow
docker-compose exec -T backend cp /app/data/database.db /app/data/database_backup.db
docker cp mining_backend:/app/data/database.db "$TempDir\database.db"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 数据库备份完成" -ForegroundColor Green
} else {
    Write-Host "✗ 数据库备份失败" -ForegroundColor Red
}

# 备份数据文件
Write-Host "备份数据文件..." -ForegroundColor Yellow
if (Test-Path ".\data\input") {
    Copy-Item -Path ".\data\input" -Destination "$TempDir\input" -Recurse -ErrorAction SilentlyContinue
    Write-Host "✓ 数据文件备份完成" -ForegroundColor Green
}

# 备份配置文件
Write-Host "备份配置文件..." -ForegroundColor Yellow
Copy-Item -Path "docker-compose.yml" -Destination "$TempDir\" -ErrorAction SilentlyContinue
Copy-Item -Path "nginx\nginx.conf" -Destination "$TempDir\nginx.conf" -ErrorAction SilentlyContinue
Copy-Item -Path ".env" -Destination "$TempDir\" -ErrorAction SilentlyContinue
Write-Host "✓ 配置文件备份完成" -ForegroundColor Green

# 打包
Write-Host "打包备份文件..." -ForegroundColor Yellow
$ZipFile = "$BackupDir\$BackupFile.zip"
Compress-Archive -Path "$TempDir\*" -DestinationPath $ZipFile -Force

# 清理临时目录
Remove-Item -Path $TempDir -Recurse -Force

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "备份完成: $ZipFile" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# 清理旧备份(保留最近7天)
Write-Host ""
Write-Host "清理旧备份..." -ForegroundColor Yellow
$OldBackups = Get-ChildItem -Path $BackupDir -Filter "mining_system_backup_*.zip" |
              Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }

if ($OldBackups) {
    $OldBackups | Remove-Item -Force
    Write-Host "✓ 已清理 $($OldBackups.Count) 个旧备份文件" -ForegroundColor Green
} else {
    Write-Host "✓ 无需清理" -ForegroundColor Green
}

Write-Host ""
Write-Host "备份大小: $([math]::Round((Get-Item $ZipFile).Length / 1MB, 2)) MB" -ForegroundColor Cyan
