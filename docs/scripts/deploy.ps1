# Mining System Docker Deployment Script
# Windows PowerShell

$ErrorActionPreference = 'Stop'

Write-Host '============================================' -ForegroundColor Cyan
Write-Host '   Mining System Docker Deployment' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

Write-Host 'Checking Docker...' -ForegroundColor Yellow

try {
    docker --version | Out-Null
    Write-Host 'OK Docker installed' -ForegroundColor Green
} catch {
    Write-Host 'ERROR: Docker not found' -ForegroundColor Red
    exit 1
}

try {
    docker-compose --version | Out-Null
    Write-Host 'OK Docker Compose installed' -ForegroundColor Green
} catch {
    Write-Host 'ERROR: Docker Compose not found' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Creating directories...' -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path 'data\input' | Out-Null
New-Item -ItemType Directory -Force -Path 'nginx\ssl' | Out-Null
New-Item -ItemType Directory -Force -Path 'logs' | Out-Null
Write-Host 'OK Directories created' -ForegroundColor Green

Write-Host ''
Write-Host 'Stopping old containers...' -ForegroundColor Yellow
$null = docker-compose down -v 2>&1

$cleanImages = Read-Host 'Clean old images? (y/N)'
if ($cleanImages -eq 'y' -or $cleanImages -eq 'Y') {
    Write-Host 'Cleaning images...' -ForegroundColor Yellow
    $null = docker-compose down --rmi all --volumes --remove-orphans 2>&1
    Write-Host 'OK Images cleaned' -ForegroundColor Green
}

Write-Host ''
Write-Host 'Building images...' -ForegroundColor Yellow
docker-compose build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host 'ERROR: Build failed' -ForegroundColor Red
    exit 1
}

Write-Host 'OK Build complete' -ForegroundColor Green

Write-Host ''
Write-Host 'Starting services...' -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host 'ERROR: Start failed' -ForegroundColor Red
    exit 1
}

Write-Host 'Waiting 10 seconds...' -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ''
docker-compose ps

Write-Host ''
Write-Host 'Health check...' -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries) {
    try {
        $frontendHealth = Invoke-WebRequest -Uri 'http://localhost/health' -UseBasicParsing -TimeoutSec 2
        $backendHealth = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 2
        
        if ($frontendHealth.StatusCode -eq 200 -and $backendHealth.StatusCode -eq 200) {
            Write-Host 'OK All services healthy!' -ForegroundColor Green
            $healthy = $true
            break
        }
    } catch {
        # retry
    }
    
    $retryCount++
    Write-Host 'Waiting... ($retryCount/$maxRetries)'
    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    Write-Host 'WARNING: Services may not be ready' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '============================================' -ForegroundColor Green
Write-Host '   Deployment Complete!' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Green
Write-Host ''
Write-Host 'URLs:' -ForegroundColor Cyan
Write-Host '  Frontend: http://localhost'
Write-Host '  Backend:  http://localhost:8000'
Write-Host '  Docs:     http://localhost:8000/docs'
Write-Host ''
Write-Host 'Commands:' -ForegroundColor Cyan
Write-Host '  Logs:    docker-compose logs -f'
Write-Host '  Stop:    docker-compose stop'
Write-Host '  Restart: docker-compose restart'
Write-Host '  Clean:   docker-compose down -v'
Write-Host ''

$openBrowser = Read-Host 'Open browser? (Y/n)'
if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
    Start-Process 'http://localhost'
}
