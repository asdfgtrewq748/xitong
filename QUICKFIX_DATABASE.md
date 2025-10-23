# 🚀 快速解决方案 - 数据库界面无数据

## 问题
Docker 部署成功,但数据库界面显示为空。

## 原因
容器中的数据库还没有导入 CSV 数据。

## 解决方法 (只需 1 步!)

### Windows 用户:
在项目根目录打开 PowerShell,执行:

```powershell
.\init-database.ps1
```

### Linux/服务器用户:
在项目根目录执行:

```bash
bash init-database.sh
```

## 执行后会看到

```
========================================
数据库初始化脚本
========================================

[1/5] 检查容器状态...
✓ backend 容器正在运行

[2/5] 检查 CSV 源文件...
✓ 找到 CSV 文件: data/input/汇总表.csv

[3/5] 准备数据目录...
✓ 数据目录已准备

[4/5] 复制 CSV 文件到容器...
✓ CSV 文件已复制到容器

[5/5] 执行数据导入...
读取 CSV 文件: /app/data/input/汇总表.csv
成功使用 utf-8-sig 编码读取 CSV
读取到 1343 条记录
创建数据库: /app/data/database.db
已导入 1343 条记录
创建索引: idx_records_province
创建索引: idx_records_mine
创建索引: idx_records_lithology
数据库初始化完成!

========================================
✓ 数据库初始化成功!
========================================

现在可以访问以下地址查看数据:
  前端: http://localhost
  后端: http://localhost:8000
  数据库概览: http://localhost:8000/api/database/overview
```

## 验证

刷新浏览器页面,访问 **数据库查看器**,应该能看到:
- ✅ 1343 条记录
- ✅ 矿名列表
- ✅ 省份分布图
- ✅ 岩性统计

---

## 如果脚本执行失败

### 错误 1: 容器未运行
```bash
# 启动容器
docker compose up -d

# 等待 30 秒让容器健康检查通过
sleep 30

# 再次执行初始化脚本
.\init-database.ps1  # Windows
bash init-database.sh  # Linux
```

### 错误 2: CSV 文件找不到
```bash
# 检查文件是否存在
ls data/input/汇总表.csv

# 如果不存在,从备份复制
cp BK-2.csv data/input/汇总表.csv
```

### 错误 3: 权限问题
```bash
# 修改数据目录权限
chmod -R 777 backend/data  # Linux
```

---

## 手动执行 (如果脚本不可用)

```bash
# 1. 复制 CSV 到容器
docker cp data/input/汇总表.csv mining-backend:/app/data/input/汇总表.csv

# 2. 导入数据
docker exec mining-backend python -c "
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

csv_path = Path('/app/data/input/汇总表.csv')
encodings = ('utf-8-sig', 'utf-8', 'gbk', 'gb2312')
df = None
for enc in encodings:
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        break
    except:
        continue

db_path = Path('/app/data/database.db')
engine = create_engine(f'sqlite:///{db_path}')
with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS records'))
df.to_sql('records', engine, if_exists='replace', index=False)

with engine.begin() as conn:
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_province ON records (\"份\")')
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_mine ON records (\"矿名\")')
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_lithology ON records (\"岩性\")')

print(f'已导入 {len(df)} 条记录')
"

# 3. 验证
docker exec mining-backend python -c "
from sqlalchemy import create_engine, select, func, MetaData
engine = create_engine('sqlite:////app/data/database.db')
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables['records']
with engine.connect() as conn:
    count = conn.execute(select(func.count()).select_from(table)).scalar()
    print(f'数据库中有 {count} 条记录')
"
```

---

## 相关文档

详细说明请查看: [`docs/DATABASE_INIT_GUIDE.md`](./docs/DATABASE_INIT_GUIDE.md)
