# ============================================================================
# 服务器页面无法打开 - 紧急修复脚本 (Windows PowerShell)
# ============================================================================
# 问题: 前端代码分割失败，导致懒加载的页面无法打开
# 修复: 重新构建前端容器，使用修复后的 vue.config.js
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 开始修复服务器页面无法打开问题" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ 错误: 未找到 docker-compose.yml" -ForegroundColor Red
    Write-Host "请在项目根目录执行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "📍 当前目录: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# 步骤 1: 停止容器
Write-Host "🛑 步骤 1/5: 停止现有容器..." -ForegroundColor Yellow
docker-compose down
Write-Host "✅ 容器已停止" -ForegroundColor Green
Write-Host ""

# 步骤 2: 拉取最新代码（如果在服务器上）
Write-Host "🔄 步骤 2/5: 拉取最新代码..." -ForegroundColor Yellow
try {
    $gitStatus = git rev-parse --git-dir 2>&1
    if ($LASTEXITCODE -eq 0) {
        git pull origin master
        Write-Host "✅ 代码已更新" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  警告: 不是 git 仓库，跳过此步骤" -ForegroundColor Yellow
}
Write-Host ""

# 步骤 3: 强制重新构建前端（关键步骤）
Write-Host "🔨 步骤 3/5: 重新构建前端容器（不使用缓存）..." -ForegroundColor Yellow
Write-Host "这一步可能需要 2-5 分钟，请耐心等待..." -ForegroundColor Yellow
docker-compose build --no-cache frontend
Write-Host "✅ 前端构建完成" -ForegroundColor Green
Write-Host ""

# 步骤 4: 启动服务
Write-Host "🚀 步骤 4/5: 启动服务..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✅ 服务已启动" -ForegroundColor Green
Write-Host ""

# 等待服务就绪
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 步骤 5: 验证修复
Write-Host "🔍 步骤 5/5: 验证修复结果..." -ForegroundColor Yellow
Write-Host ""

# 检查容器状态
Write-Host "容器状态:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# 检查前端文件
Write-Host "检查前端 JS 文件:" -ForegroundColor Cyan
try {
    $frontendContainer = docker-compose ps -q frontend
    if ($frontendContainer) {
        docker exec $frontendContainer ls -lh /usr/share/nginx/html/js/
    }
} catch {
    Write-Host "⚠️  无法检查前端文件" -ForegroundColor Yellow
}
Write-Host ""

# 测试后端健康
Write-Host "测试后端 API:" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "✅ 后端 API 正常: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  后端 API 测试失败: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 修复完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 请访问以下页面进行测试：" -ForegroundColor Cyan
Write-Host "  • 首页: http://39.97.168.66/" -ForegroundColor White
Write-Host "  • 数据库管理: http://39.97.168.66/database-viewer" -ForegroundColor White
Write-Host "  • 地质建模: http://39.97.168.66/geological-modeling" -ForegroundColor White
Write-Host "  • 科研绘图: http://39.97.168.66/visualization" -ForegroundColor White
Write-Host ""
Write-Host "🔍 如果页面仍然无法打开，请：" -ForegroundColor Yellow
Write-Host "  1. 清除浏览器缓存（Ctrl+Shift+Delete）" -ForegroundColor White
Write-Host "  2. 按 F12 打开浏览器控制台，查看错误信息" -ForegroundColor White
Write-Host "  3. 运行: docker-compose logs frontend" -ForegroundColor White
Write-Host ""
Write-Host "📄 详细修复文档: 服务器页面无法打开修复指南.md" -ForegroundColor Cyan
Write-Host ""
