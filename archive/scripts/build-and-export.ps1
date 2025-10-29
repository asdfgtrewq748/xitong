# ============================================================================
# Docker 镜像本地构建并导出脚本
# ============================================================================
# 用途: 在本地构建镜像并导出为 tar 文件，避免服务器网络问题
# 使用: .\build-and-export.ps1
# ============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Docker 镜像本地构建与导出工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "[1/5] 检查 Docker 状态..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker 运行正常" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker 未运行或未安装，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 清理旧镜像（可选）
Write-Host "[2/5] 清理旧镜像..." -ForegroundColor Yellow
$cleanup = Read-Host "是否删除旧镜像后重新构建？(y/n) [默认: n]"
if ($cleanup -eq 'y' -or $cleanup -eq 'Y') {
    docker rmi mining-system-backend:latest -f 2>$null
    docker rmi mining-system-frontend:latest -f 2>$null
    Write-Host "✓ 旧镜像已清理" -ForegroundColor Green
} else {
    Write-Host "跳过清理" -ForegroundColor Gray
}

Write-Host ""

# 构建后端镜像
Write-Host "[3/5] 构建后端镜像..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Gray
$backendBuildStart = Get-Date

docker build -t mining-system-backend:latest `
    --progress=plain `
    ./backend

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 后端镜像构建失败" -ForegroundColor Red
    exit 1
}

$backendBuildTime = (Get-Date) - $backendBuildStart
Write-Host "✓ 后端镜像构建成功 (耗时: $($backendBuildTime.TotalSeconds.ToString('0.0'))秒)" -ForegroundColor Green

Write-Host ""

# 构建前端镜像
Write-Host "[4/5] 构建前端镜像..." -ForegroundColor Yellow
$frontendBuildStart = Get-Date

docker build -t mining-system-frontend:latest `
    --progress=plain `
    ./frontend

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 前端镜像构建失败" -ForegroundColor Red
    exit 1
}

$frontendBuildTime = (Get-Date) - $frontendBuildStart
Write-Host "✓ 前端镜像构建成功 (耗时: $($frontendBuildTime.TotalSeconds.ToString('0.0'))秒)" -ForegroundColor Green

Write-Host ""

# 导出镜像
Write-Host "[5/5] 导出镜像为 tar 文件..." -ForegroundColor Yellow

# 创建导出目录
$exportDir = ".\docker-images"
if (!(Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
}

# 导出后端镜像
Write-Host "导出后端镜像..." -ForegroundColor Gray
docker save mining-system-backend:latest -o "$exportDir\mining-backend.tar"
$backendSize = (Get-Item "$exportDir\mining-backend.tar").Length / 1MB
Write-Host "✓ 后端镜像已导出: $exportDir\mining-backend.tar ($($backendSize.ToString('0.0')) MB)" -ForegroundColor Green

# 导出前端镜像
Write-Host "导出前端镜像..." -ForegroundColor Gray
docker save mining-system-frontend:latest -o "$exportDir\mining-frontend.tar"
$frontendSize = (Get-Item "$exportDir\mining-frontend.tar").Length / 1MB
Write-Host "✓ 前端镜像已导出: $exportDir\mining-frontend.tar ($($frontendSize.ToString('0.0')) MB)" -ForegroundColor Green

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "构建完成！" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "镜像文件位置:" -ForegroundColor Yellow
Write-Host "  - $exportDir\mining-backend.tar ($($backendSize.ToString('0.0')) MB)" -ForegroundColor White
Write-Host "  - $exportDir\mining-frontend.tar ($($frontendSize.ToString('0.0')) MB)" -ForegroundColor White
Write-Host ""

Write-Host "下一步操作 (上传到服务器):" -ForegroundColor Yellow
Write-Host ""
Write-Host "方法 1: 使用 SCP 上传" -ForegroundColor Cyan
Write-Host "  scp $exportDir\mining-backend.tar admin@your-server:/tmp/" -ForegroundColor White
Write-Host "  scp $exportDir\mining-frontend.tar admin@your-server:/tmp/" -ForegroundColor White
Write-Host ""

Write-Host "方法 2: 使用 Git Bash + SCP" -ForegroundColor Cyan
Write-Host '  在 Git Bash 中运行:' -ForegroundColor Gray
Write-Host "  scp ./docker-images/mining-backend.tar admin@your-server:/tmp/" -ForegroundColor White
Write-Host "  scp ./docker-images/mining-frontend.tar admin@your-server:/tmp/" -ForegroundColor White
Write-Host ""

Write-Host "服务器端操作:" -ForegroundColor Yellow
Write-Host "  cd /var/www/xitong" -ForegroundColor White
Write-Host "  docker load -i /tmp/mining-backend.tar" -ForegroundColor White
Write-Host "  docker load -i /tmp/mining-frontend.tar" -ForegroundColor White
Write-Host "  docker compose up -d" -ForegroundColor White
Write-Host ""

Write-Host "提示: 也可以将镜像推送到 Docker Hub 或私有镜像仓库" -ForegroundColor Gray
Write-Host ""

# 生成上传脚本
$uploadScript = @"
#!/bin/bash
# 上传镜像到服务器的便捷脚本

SERVER="admin@your-server-ip"
REMOTE_PATH="/tmp"

echo "上传后端镜像..."
scp ./docker-images/mining-backend.tar `$SERVER:`$REMOTE_PATH/

echo "上传前端镜像..."
scp ./docker-images/mining-frontend.tar `$SERVER:`$REMOTE_PATH/

echo ""
echo "上传完成！"
echo ""
echo "请在服务器上执行以下命令:"
echo "  cd /var/www/xitong"
echo "  docker load -i /tmp/mining-backend.tar"
echo "  docker load -i /tmp/mining-frontend.tar"
echo "  docker compose up -d"
"@

$uploadScript | Out-File -FilePath "$exportDir\upload-to-server.sh" -Encoding UTF8
Write-Host "✓ 已生成上传脚本: $exportDir\upload-to-server.sh" -ForegroundColor Green
Write-Host "  请修改服务器地址后在 Git Bash 中执行" -ForegroundColor Gray
Write-Host ""
