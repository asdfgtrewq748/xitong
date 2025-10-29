@echo off
REM ============================================================================
REM 数据库初始化脚本 - Windows 批处理版本
REM ============================================================================
REM 用途: 将本地的 CSV 数据导入到运行中的 Docker 容器的数据库
REM 使用方法: init-database.bat
REM ============================================================================

echo ========================================
echo 数据库初始化脚本
echo ========================================

REM 检查容器是否运行
echo.
echo [1/5] 检查容器状态...
docker ps --filter "name=mining-backend" --filter "status=running" --format "{{.Names}}" | findstr "mining-backend" >nul 2>&1
if errorlevel 1 (
    echo [错误] backend 容器未运行
    echo 请先运行: docker compose up -d
    pause
    exit /b 1
)
echo [成功] backend 容器正在运行

REM 检查 CSV 文件是否存在
echo.
echo [2/5] 检查 CSV 源文件...
if not exist "data\input\汇总表.csv" (
    echo [错误] 未找到 CSV 文件: data\input\汇总表.csv
    pause
    exit /b 1
)
echo [成功] 找到 CSV 文件: data\input\汇总表.csv

REM 确保容器内的数据目录存在
echo.
echo [3/5] 准备数据目录...
docker exec mining-backend mkdir -p /app/data/input 2>nul
docker exec mining-backend mkdir -p /app/data 2>nul
echo [成功] 数据目录已准备

REM 复制 CSV 文件到容器
echo.
echo [4/5] 复制 CSV 文件到容器...
docker cp "data\input\汇总表.csv" mining-backend:/app/data/input/汇总表.csv
if errorlevel 1 (
    echo [错误] 复制文件失败
    pause
    exit /b 1
)
echo [成功] CSV 文件已复制到容器

REM 在容器中运行导入脚本
echo.
echo [5/5] 执行数据导入...
docker exec mining-backend python -c "import sys; sys.path.insert(0, '/app'); from pathlib import Path; import pandas as pd; from sqlalchemy import create_engine, text; csv_path = Path('/app/data/input/汇总表.csv'); print(f'读取 CSV 文件: {csv_path}'); encodings = ('utf-8-sig', 'utf-8', 'gbk', 'gb2312'); df = None; exec('for encoding in encodings:\n    try:\n        df = pd.read_csv(csv_path, encoding=encoding)\n        print(f\"成功使用 {encoding} 编码读取 CSV\")\n        break\n    except Exception as e:\n        continue'); exec('if df is None:\n    print(\"错误: 无法读取 CSV 文件\")\n    sys.exit(1)'); print(f'读取到 {len(df)} 条记录'); print(f'列名: {list(df.columns)}'); db_path = Path('/app/data/database.db'); engine = create_engine(f'sqlite:///{db_path}', future=True); print(f'创建数据库: {db_path}'); exec('with engine.begin() as conn:\n    conn.execute(text(\"DROP TABLE IF EXISTS records\"))'); df.to_sql('records', engine, if_exists='replace', index=False); print(f'已导入 {len(df)} 条记录'); exec('with engine.begin() as conn:\n    if \"份\" in df.columns:\n        conn.exec_driver_sql(\"CREATE INDEX IF NOT EXISTS idx_records_province ON records (\\\"份\\\")\")\n        print(\"创建索引: idx_records_province\")\n    if \"矿名\" in df.columns:\n        conn.exec_driver_sql(\"CREATE INDEX IF NOT EXISTS idx_records_mine ON records (\\\"矿名\\\")\")\n        print(\"创建索引: idx_records_mine\")\n    if \"岩性\" in df.columns:\n        conn.exec_driver_sql(\"CREATE INDEX IF NOT EXISTS idx_records_lithology ON records (\\\"岩性\\\")\")\n        print(\"创建索引: idx_records_lithology\")'); print('数据库初始化完成!')"

if errorlevel 1 (
    echo.
    echo ========================================
    echo [失败] 数据库初始化失败
    echo ========================================
    echo.
    echo 查看容器日志:
    echo   docker logs mining-backend
    pause
    exit /b 1
)

echo.
echo ========================================
echo [成功] 数据库初始化成功!
echo ========================================
echo.
echo 现在可以访问以下地址查看数据:
echo   前端: http://localhost
echo   后端: http://localhost:8000
echo   数据库概览: http://localhost:8000/api/database/overview
echo.
pause
