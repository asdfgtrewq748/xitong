# 数据库初始化指南

## 问题说明

Docker 容器部署成功后,数据库界面显示为空,这是因为:

1. **数据库文件未创建**: 容器启动时数据库文件 (`data/database.db`) 不存在
2. **数据未导入**: CSV 源数据 (`data/input/汇总表.csv`) 未被导入到数据库

## 解决方案

### 方案一: 使用自动化脚本 (推荐)

#### Windows (PowerShell):
```powershell
cd E:\xiangmu\xitong
.\init-database.ps1
```

#### Linux/Mac (Bash):
```bash
cd /var/www/xitong  # 或你的项目路径
bash init-database.sh
```

脚本会自动完成以下操作:
1. ✓ 检查容器运行状态
2. ✓ 检查 CSV 源文件
3. ✓ 准备数据目录
4. ✓ 复制 CSV 到容器
5. ✓ 导入数据到数据库
6. ✓ 创建索引优化查询

---

### 方案二: 手动执行

#### 步骤 1: 确保容器运行

```bash
docker compose ps
```

应该看到 `mining-backend` 状态为 `Up (healthy)`

#### 步骤 2: 复制 CSV 文件到容器

**本地环境 (Windows):**
```powershell
docker cp data\input\汇总表.csv mining-backend:/app/data/input/汇总表.csv
```

**服务器环境 (Linux):**
```bash
docker cp data/input/汇总表.csv mining-backend:/app/data/input/汇总表.csv
```

#### 步骤 3: 在容器中执行导入

```bash
docker exec -it mining-backend python /app/scripts/import_database.py \
  --csv /app/data/input/汇总表.csv \
  --database /app/data/database.db
```

**或者直接使用内联 Python 脚本:**

```bash
docker exec mining-backend python -c "
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# 读取 CSV
csv_path = Path('/app/data/input/汇总表.csv')
encodings = ('utf-8-sig', 'utf-8', 'gbk', 'gb2312')
df = None
for enc in encodings:
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        break
    except:
        continue

# 导入数据库
db_path = Path('/app/data/database.db')
engine = create_engine(f'sqlite:///{db_path}')
with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS records'))
df.to_sql('records', engine, if_exists='replace', index=False)

# 创建索引
with engine.begin() as conn:
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_province ON records (\"份\")')
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_mine ON records (\"矿名\")')
    conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_lithology ON records (\"岩性\")')

print(f'已导入 {len(df)} 条记录')
"
```

#### 步骤 4: 验证导入

```bash
# 检查数据库文件是否存在
docker exec mining-backend ls -lh /app/data/database.db

# 查询记录数量
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

### 方案三: 在 Dockerfile 中自动初始化 (未来优化)

**修改 `backend/Dockerfile`,添加初始化步骤:**

```dockerfile
# 在构建阶段复制 CSV 文件
COPY ../data/input/汇总表.csv /app/data/input/汇总表.csv
COPY scripts/import_database.py /app/scripts/

# 在启动脚本中检查并初始化数据库
RUN echo '#!/bin/bash\n\
if [ ! -f /app/data/database.db ]; then\n\
  echo "初始化数据库..."\n\
  python /app/scripts/import_database.py\n\
fi\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
```

**注意**: 这种方式会使镜像体积变大(包含 CSV 文件),适合数据不常变化的场景。

---

## 验证结果

### 1. 通过 API 验证

```bash
# 检查数据库概览
curl http://localhost:8000/api/database/overview

# 应该返回类似:
# {
#   "initialized": true,
#   "records": 1343,
#   "mines": 123,
#   "provinces": [...],
#   ...
# }
```

### 2. 通过前端验证

访问: http://localhost

导航到 **数据库查看器** 页面,应该能看到:
- 记录总数
- 矿名列表
- 省份分布
- 岩性类型

### 3. 通过日志验证

```bash
# 查看后端日志
docker logs mining-backend

# 应该看到类似输出:
# 读取到 1343 条记录
# 已导入 1343 条记录
# 创建索引: idx_records_province
# 创建索引: idx_records_mine
# 创建索引: idx_records_lithology
```

---

## 常见问题

### Q1: 容器重启后数据丢失

**原因**: 数据目录未正确挂载

**解决**: 检查 `docker-compose.yml` 中的 volumes 配置:

```yaml
volumes:
  - ./backend/data:/app/data  # 确保这行存在
```

### Q2: CSV 文件找不到

**原因**: CSV 文件路径不正确或文件不存在

**解决**:
```bash
# 检查本地文件
ls -lh data/input/汇总表.csv

# 如果不存在,从备份恢复
cp BK-2.csv data/input/汇总表.csv
```

### Q3: 编码错误

**原因**: CSV 文件编码与脚本不匹配

**解决**: 脚本已自动尝试多种编码 (`utf-8-sig`, `utf-8`, `gbk`, `gb2312`)

如果仍有问题,手动转换编码:
```bash
# 使用 iconv 转换 (Linux)
iconv -f GBK -t UTF-8 data/input/汇总表.csv > data/input/汇总表_utf8.csv
```

### Q4: 权限错误

**原因**: Docker 容器内用户无权限写入

**解决**:
```bash
# 修改本地目录权限
chmod -R 777 backend/data

# 或在容器中以 root 运行
docker exec -u root mining-backend chown -R appuser:appuser /app/data
```

### Q5: 数据库被锁定

**原因**: 多个进程同时访问数据库

**解决**:
```bash
# 重启容器释放锁
docker compose restart backend

# 然后重新导入
bash init-database.sh
```

---

## 数据库文件位置

| 环境 | 容器内路径 | 宿主机路径 |
|------|-----------|-----------|
| CSV 源文件 | `/app/data/input/汇总表.csv` | `./data/input/汇总表.csv` |
| 数据库文件 | `/app/data/database.db` | `./backend/data/database.db` |
| 日志文件 | `/app/logs/` | `./backend/logs/` |

---

## 数据库表结构

**表名**: `records`

**索引**:
- `idx_records_province`: 省份索引 (列: `份`)
- `idx_records_mine`: 矿名索引 (列: `矿名`)
- `idx_records_lithology`: 岩性索引 (列: `岩性`)

**列名示例**:
```
文献, 矿名, 份, 市/县, 岩性, 密度（kg*m3）, 体积模量（Gpa）, 
剪切模量/GPa, 内聚力（MPa）, 内摩擦角, 抗拉强度（MPa）, 
抗压强度/MPa, 弹性模量（Gpa）, 泊松比, 埋深, 厚度
```

---

## 性能优化建议

### 1. 预先创建索引

脚本已自动创建常用索引,如需更多:

```bash
docker exec mining-backend python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:////app/data/database.db')
with engine.begin() as conn:
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_records_depth ON records (埋深)'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_records_thickness ON records (厚度)'))
"
```

### 2. 数据库分析

```bash
docker exec mining-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/database.db')
conn.execute('ANALYZE')
print('数据库统计信息已更新')
"
```

### 3. 清理碎片

```bash
docker exec mining-backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/database.db')
conn.execute('VACUUM')
print('数据库碎片已清理')
"
```

---

## 脚本说明

### `init-database.ps1` (Windows PowerShell)
- **用途**: Windows 环境下自动化数据库初始化
- **依赖**: Docker Desktop, PowerShell 5.1+
- **执行**: `.\init-database.ps1`

### `init-database.sh` (Linux/Mac Bash)
- **用途**: Linux/Mac 环境下自动化数据库初始化
- **依赖**: Docker, Bash 4.0+
- **执行**: `bash init-database.sh`

### `scripts/import_database.py` (Python)
- **用途**: 独立的数据导入脚本
- **执行**: `python scripts/import_database.py --csv <path> --database <path>`

---

## 总结

推荐使用 **方案一 (自动化脚本)** 进行数据库初始化:

1. **快速**: 一键执行,自动完成所有步骤
2. **安全**: 检查容器状态,避免错误操作
3. **可靠**: 自动处理编码问题,创建必要索引
4. **便捷**: 彩色输出,清晰反馈每个步骤

**Windows 用户**:
```powershell
.\init-database.ps1
```

**Linux/Mac 用户**:
```bash
bash init-database.sh
```

初始化完成后,刷新前端页面即可看到数据!
