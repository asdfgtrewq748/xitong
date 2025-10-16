# Docker Registry Mirror Fix Script
# Automatically configure working Docker registry mirrors

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Docker Registry Mirror Configuration" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Current Docker registry mirrors:" -ForegroundColor Yellow
docker info | Select-String "Registry Mirrors" -Context 0,5

Write-Host ""
Write-Host "Recommended configuration:" -ForegroundColor Green
Write-Host ""

$recommendedConfig = @"
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.baidubce.com"
  ]
}
"@

Write-Host $recommendedConfig -ForegroundColor Cyan

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "   Manual Steps Required" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open Docker Desktop" -ForegroundColor White
Write-Host "2. Click Settings (gear icon)" -ForegroundColor White
Write-Host "3. Go to 'Docker Engine'" -ForegroundColor White
Write-Host "4. Replace the config with the above JSON" -ForegroundColor White
Write-Host "5. Click 'Apply & Restart'" -ForegroundColor White
Write-Host "6. Wait for Docker to restart (~30 seconds)" -ForegroundColor White
Write-Host ""

Write-Host "Alternative: Try pulling images manually first:" -ForegroundColor Cyan
Write-Host ""
Write-Host "docker pull python:3.11-slim" -ForegroundColor White
Write-Host "docker pull node:18-alpine" -ForegroundColor White
Write-Host "docker pull nginx:alpine" -ForegroundColor White
Write-Host ""

$tryPull = Read-Host "Try pulling images now? (y/N)"
if ($tryPull -eq 'y' -or $tryPull -eq 'Y') {
    Write-Host ""
    Write-Host "Pulling Python image..." -ForegroundColor Yellow
    docker pull python:3.11-slim
    
    Write-Host ""
    Write-Host "Pulling Node image..." -ForegroundColor Yellow
    docker pull node:18-alpine
    
    Write-Host ""
    Write-Host "Pulling Nginx image..." -ForegroundColor Yellow
    docker pull nginx:alpine
    
    Write-Host ""
    Write-Host "OK Images pulled successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now you can run: .\deploy.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "For more details, see: DOCKER_REGISTRY_FIX.md" -ForegroundColor Yellow
