# PowerShell API 测试脚本
$baseUrl = "http://localhost:8000"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "前后端联调测试" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. 测试默认常量
Write-Host "`n1. 测试 GET /api/tunnel-support/default-constants" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/tunnel-support/default-constants" -Method Get
    Write-Host "   [OK] 获取成功" -ForegroundColor Green
    Write-Host "   - 常量数量: $($response.constants.Count)"
    Write-Host "   - Sn: $($response.constants.Sn)"
} catch {
    Write-Host "   [ERROR] 请求失败: $_" -ForegroundColor Red
}

# 2. 测试单次计算
Write-Host "`n2. 测试 POST /api/tunnel-support/calculate" -ForegroundColor Yellow
$testParams = @{
    B = 4.0
    H = 3.0
    K = 1.0
    depth = 200
    gamma = 18.0
    C = 0.5
    phi = 30.0
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/tunnel-support/calculate" -Method Post -Body $testParams -ContentType "application/json"
    Write-Host "   [OK] 计算成功" -ForegroundColor Green
    Write-Host "   - R = $($response.result.basic.R) m"
    Write-Host "   - hct = $($response.result.basic.hct) m"
    Write-Host "   - 锚索 Nt = $($response.result.anchor.Nt) kN"
} catch {
    Write-Host "   [ERROR] 请求失败: $_" -ForegroundColor Red
}

# 3. 测试批量计算
Write-Host "`n3. 测试 POST /api/tunnel-support/batch-calculate" -ForegroundColor Yellow
$batchParams = @{
    data = @(
        @{ B=4.0; H=3.0; K=1.0; depth=200; gamma=18.0; C=0.5; phi=30.0 }
        @{ B=5.0; H=3.5; K=1.2; depth=250; gamma=20.0; C=0.6; phi=32.0 }
    )
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/tunnel-support/batch-calculate" -Method Post -Body $batchParams -ContentType "application/json"
    Write-Host "   [OK] 批量计算成功" -ForegroundColor Green
    Write-Host "   - 计算数量: $($response.count)"
    Write-Host "   - 第一条 R = $($response.results[0].'R(m)') m"
} catch {
    Write-Host "   [ERROR] 请求失败: $_" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] 前后端联调测试完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n下一步:" -ForegroundColor Yellow
Write-Host "1. 启动前端: cd frontend && npm run serve"
Write-Host "2. 访问: http://localhost:8080/#/tunnel-support"
Write-Host "3. 测试单次计算和 Excel 导入功能"
