# 巷道支护计算 - 快速开始

## 5分钟上手指南

### 第一步：启动服务

```bash
# 启动后端
cd backend
python server.py

# 启动前端（新终端）
cd frontend
npm run serve
```

### 第二步：访问页面

打开浏览器访问：`http://localhost:8080/#/tunnel-support`

### 第三步：计算示例

#### 方式一：手动输入

1. 在左侧表单填写参数：
   - B = 4.0 m
   - H = 3.0 m
   - K = 1.0
   - 埋深 = 200 m
   - 容重 = 18.0 kN/m³
   - 粘聚力 = 0.5 MPa
   - 内摩擦角 = 30.0°

2. 点击"计算"

3. 查看右侧结果

#### 方式二：Excel 批量导入

1. 准备 Excel 文件（参考下面的模板）

2. 点击"导入参数 Excel"

3. 自动完成批量计算并显示结果表格

4. 点击"导出批量结果 CSV"保存

### Excel 模板

创建一个 Excel 文件，包含以下列：

| B | H | 应力集中系数K | 埋深 | 容重 | 粘聚力 | 内摩擦角 |
|---|---|--------------|------|------|--------|---------|
| 4.0 | 3.0 | 1.0 | 200 | 18.0 | 0.5 | 30.0 |
| 5.0 | 3.5 | 1.2 | 250 | 20.0 | 0.6 | 32.0 |
| 4.5 | 3.2 | 1.1 | 220 | 19.0 | 0.55 | 31.0 |

### API 快速测试

```bash
# Windows PowerShell
$params = '{"B":4.0,"H":3.0,"K":1.0,"depth":200,"gamma":18.0,"C":0.5,"phi":30.0}'
Invoke-RestMethod -Uri "http://localhost:8000/api/tunnel-support/calculate" `
  -Method Post -Body $params -ContentType "application/json"
```

### Python 脚本调用

```python
from backend.tunnel_support import TunnelSupportCalculator

calc = TunnelSupportCalculator()
result = calc.calculate_complete({
    'B': 4.0, 'H': 3.0, 'K': 1.0, 
    'depth': 200, 'gamma': 18.0, 
    'C': 0.5, 'phi': 30.0
})

print(f"R = {result['basic']['R']} m")
print(f"锚索长度 = {result['anchor']['L_total']} m")
```

### 预期输出

单次计算结果示例：

```json
{
  "basic": {
    "R": 91.191,
    "hct": 89.691,
    "hcs": 89.191,
    "hat": 89.191
  },
  "anchor": {
    "Nt": 349.31,
    "L_total": 96.641,
    "spacing_area": 0.001
  },
  "rod": {
    "Nt": 86.58,
    "L_top": 89.861,
    "L_side": 89.861
  }
}
```

### 下一步

- 📖 查看完整文档：[TUNNEL_SUPPORT_GUIDE.md](./TUNNEL_SUPPORT_GUIDE.md)
- 🔧 调整默认常量：点击"查看常量"按钮
- 📊 批量处理：使用 Excel 导入功能
- 🧪 运行测试：`python backend/verify_tunnel_support.py`

## 故障排查

**问题：后端启动失败**
```bash
# 安装依赖
pip install fastapi uvicorn pandas numpy scipy scikit-learn sqlalchemy
```

**问题：API 返回 404**
- 确认后端已启动（访问 http://localhost:8000/api/health）
- 检查路由是否正确注册

**问题：Excel 解析失败**
- 确认列名完全匹配（区分大小写）
- 确认文件格式为 .xlsx 或 .xls
- 确认数据为数值类型

---

完整API文档和更多示例请参考 [TUNNEL_SUPPORT_GUIDE.md](./TUNNEL_SUPPORT_GUIDE.md)
