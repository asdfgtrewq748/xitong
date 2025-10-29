@echo off
REM ============================================================================
REM 数据库初始化脚本 - 简化版本
REM ============================================================================

echo ========================================
echo 数据库初始化脚本
echo ========================================

REM 检查容器
echo.
echo [1/4] 检查容器状态...
docker ps | findstr "mining-backend" >nul
if errorlevel 1 (
    echo [错误] 容器未运行,请先执行: docker compose up -d
    pause
    exit /b 1
)
echo [成功] 容器正在运行

REM 检查文件
echo.
echo [2/4] 检查 CSV 文件...
if not exist "data\input\汇总表.csv" (
    echo [错误] 未找到: data\input\汇总表.csv
    pause
    exit /b 1
)
echo [成功] 找到 CSV 文件

REM 复制文件
echo.
echo [3/4] 复制文件到容器...
docker cp "data\input\汇总表.csv" mining-backend:/app/data/input/汇总表.csv
echo [成功] 文件已复制

REM 导入数据 (使用外部 Python 脚本)
echo.
echo [4/4] 导入数据...
docker exec mining-backend python /app/scripts/import_database.py --csv /app/data/input/汇总表.csv --database /app/data/database.db

if errorlevel 1 (
    echo.
    echo [失败] 导入失败,查看日志: docker logs mining-backend
    pause
    exit /b 1
)

echo.
echo ========================================
echo [成功] 数据库初始化完成!
echo ========================================
echo.
echo 访问地址:
echo   前端: http://localhost
echo   API: http://localhost:8000/api/database/overview
echo.
pause
