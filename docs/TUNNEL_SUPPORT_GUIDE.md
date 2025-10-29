# 巷道支护计算模块使用指南

## 概述

巷道支护计算模块基于《巷道支护理论公式.docx》实现，提供完整的巷道支护参数计算功能，包括：
- 等效圆塑性区半径计算
- 松动圈和压力拱高度计算
- 锚索和锚杆设计参数计算
- 间排距计算

## 功能特性

✅ **单次计算** - 输入参数即时计算，查看详细结果  
✅ **批量计算** - 支持 Excel 批量导入，一次计算多组参数  
✅ **结果导出** - 支持 CSV 格式导出，含 UTF-8 BOM 确保中文正常显示  
✅ **常量查看** - 可查看和了解所有默认计算常量  
✅ **参数验证** - 自动验证输入参数合法性

## 前端使用

### 访问页面

启动前端后，访问：`http://localhost:8080/#/tunnel-support`

或在系统主菜单中：**分析计算 → 巷道支护计算**

### 单次计算流程

1. 在左侧输入参数表单中填写：
   - 巷道宽度 B (m)
   - 巷道高度 H (m)
   - 应力集中系数 K
   - 埋深 (m)
   - 容重 (kN/m³)
   - 粘聚力 C (MPa)
   - 内摩擦角 φ (°)

2. 点击"计算"按钮

3. 右侧显示计算结果，包括：
   - **基础参数**：R, hct, hcs, hat
   - **锚索设计**：承载力、直径、锚固长度、总长度、间排距
   - **锚杆设计**：承载力、直径、锚固长度、顶/侧长度、间排距

4. 可选操作：
   - 点击"导出 CSV"保存单次结果
   - 点击"复制结果"将 JSON 格式结果复制到剪贴板

### 批量计算流程

1. 准备 Excel 文件，包含以下列：
   ```
   B, H, 应力集中系数K, 埋深, 容重, 粘聚力, 内摩擦角
   ```

   **示例数据：**
   | B | H | 应力集中系数K | 埋深 | 容重 | 粘聚力 | 内摩擦角 |
   |---|---|--------------|------|------|--------|---------|
   | 4.0 | 3.0 | 1.0 | 200 | 18.0 | 0.5 | 30.0 |
   | 5.0 | 3.5 | 1.2 | 250 | 20.0 | 0.6 | 32.0 |
   | 4.5 | 3.2 | 1.1 | 220 | 19.0 | 0.55 | 31.0 |

2. 点击页面右上角"导入参数 Excel"

3. 选择 Excel 文件，系统自动：
   - 解析文件内容
   - 批量计算所有参数
   - 在表格中显示结果

4. 点击"导出批量结果 CSV"保存所有计算结果

## 后端 API

### 1. 单次计算

**接口：** `POST /api/tunnel-support/calculate`

**请求体：**
```json
{
  "B": 4.0,
  "H": 3.0,
  "K": 1.0,
  "depth": 200,
  "gamma": 18.0,
  "C": 0.5,
  "phi": 30.0
}
```

**响应：**
```json
{
  "status": "success",
  "result": {
    "input": { "B": 4.0, "H": 3.0, ... },
    "basic": {
      "R": 91.191,
      "hct": 89.691,
      "hcs": 89.191,
      "hat": 89.191
    },
    "anchor": {
      "Nt": 349.31,
      "diameter": 17.62,
      "Lm": 7.451,
      "L_total": 96.641,
      "spacing_area": 0.001
    },
    "rod": {
      "Nt": 86.58,
      "diameter": 17.62,
      "La": 0.455,
      "L_top": 89.861,
      "L_side": 89.861,
      "spacing_area_top": 0.003,
      "spacing_area_side": 0.003
    }
  }
}
```

### 2. 批量计算

**接口：** `POST /api/tunnel-support/batch-calculate`

**请求体：**
```json
{
  "data": [
    { "B": 4.0, "H": 3.0, "K": 1.0, "depth": 200, "gamma": 18.0, "C": 0.5, "phi": 30.0 },
    { "B": 5.0, "H": 3.5, "K": 1.2, "depth": 250, "gamma": 20.0, "C": 0.6, "phi": 32.0 }
  ],
  "constants": null
}
```

**响应：**
```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "B": 4.0,
      "H": 3.0,
      "埋深": 200,
      "R(m)": 91.191,
      "hct(m)": 89.691,
      ...
    },
    ...
  ]
}
```

### 3. Excel 解析

**接口：** `POST /api/tunnel-support/parse-excel`

**请求：** `multipart/form-data` 上传 Excel 文件

**响应：**
```json
{
  "status": "success",
  "count": 3,
  "columns": ["B", "H", "K", "depth", "gamma", "C", "phi"],
  "data": [
    { "B": 4.0, "H": 3.0, ... },
    ...
  ]
}
```

### 4. 获取默认常量

**接口：** `GET /api/tunnel-support/default-constants`

**响应：**
```json
{
  "status": "success",
  "constants": {
    "Sn": 313,
    "Rm_anchor": 1860,
    "Rm_rod": 460,
    "Q_anchor": 350,
    "Q_rod": 105,
    "c0": 3.0,
    "tau_rod": 2.0,
    "R_mm": 15,
    "D_mm": 30,
    "safety_K": 2.0,
    "m": 0.6,
    "n": 1
  },
  "descriptions": {
    "Sn": "锚索截面积 (mm²)",
    "Rm_anchor": "锚索抗拉强度 (MPa)",
    ...
  }
}
```

## Python 模块使用

### 单次计算

```python
from backend.tunnel_support import TunnelSupportCalculator

# 创建计算器
calc = TunnelSupportCalculator()

# 输入参数
params = {
    'B': 4.0,
    'H': 3.0,
    'K': 1.0,
    'depth': 200,
    'gamma': 18.0,
    'C': 0.5,
    'phi': 30.0
}

# 计算
result = calc.calculate_complete(params)

# 访问结果
print(f"R = {result['basic']['R']} m")
print(f"锚索承载力 = {result['anchor']['Nt']} kN")
```

### 批量计算

```python
from backend.tunnel_support import batch_calculate_tunnel_support

# 准备数据列表
data_list = [
    {'B': 4.0, 'H': 3.0, 'K': 1.0, 'depth': 200, 'gamma': 18.0, 'C': 0.5, 'phi': 30.0},
    {'B': 5.0, 'H': 3.5, 'K': 1.2, 'depth': 250, 'gamma': 20.0, 'C': 0.6, 'phi': 32.0}
]

# 批量计算
df_results = batch_calculate_tunnel_support(data_list)

# 保存结果
df_results.to_excel('results.xlsx', index=False)
```

### 自定义常量

```python
# 使用自定义常量
custom_constants = {
    'safety_K': 2.5,  # 提高安全系数
    'Q_anchor': 400   # 增大锚索设计荷载
}

calc = TunnelSupportCalculator(constants=custom_constants)
result = calc.calculate_complete(params)
```

## 计算公式说明

### 主要公式

1. **等效圆塑性区半径 R** (式 5.1)
   ```
   R = r × [((K×γ×H + C×cotφ)×(1-sinφ)) / (C×cotφ)]^((1-sinφ)/(2×sinφ))
   ```

2. **松动圈高度**
   - 顶板松动圈：hct = R - b (式 5.2)
   - 帮部松动圈：hcs = R - a (式 5.3)
   - 压力拱高度：hat = R - a (式 5.4，临时经验式)

3. **设计承载力** (式 5.6/5.11)
   ```
   Nt = m × n × Sn × Rm
   ```

4. **锚固长度** (式 5.8)
   ```
   Lm = Q / (π × R × c0)
   ```

5. **间排距** (式 5.17)
   ```
   a×b = Nt / (K × L × r)
   ```

## 测试示例

### 命令行测试

```bash
# 后端验证测试
cd backend
python verify_tunnel_support.py

# API 集成测试（需要后端运行）
python test_api_integration.py
```

### PowerShell 测试

```powershell
# 测试单次计算 API
$params = '{"B":4.0,"H":3.0,"K":1.0,"depth":200,"gamma":18.0,"C":0.5,"phi":30.0}'
$result = Invoke-RestMethod -Uri "http://localhost:8000/api/tunnel-support/calculate" `
  -Method Post -Body $params -ContentType "application/json"
$result.result.basic
```

## 常见问题

### Q: Excel 文件列名格式要求？
A: 必须包含以下列名（完全匹配）：
- B
- H
- 应力集中系数K
- 埋深
- 容重
- 粘聚力
- 内摩擦角

### Q: 如何修改默认计算常量？
A: 在批量计算时传入 `constants` 参数，或在 Python 中创建 `TunnelSupportCalculator` 时传入。

### Q: 导出的 CSV 文件中文乱码怎么办？
A: 系统已自动添加 UTF-8 BOM，用 Excel 打开应正常显示。如仍有问题，请用记事本打开并另存为 UTF-8 编码。

### Q: 单位是什么？
A: 
- 长度：m (米)
- 应力/强度：MPa
- 容重：kN/m³
- 荷载：kN
- 直径/半径（常量）：mm

## 更新日志

**v1.0.0** (2025-10-29)
- ✅ 实现基于理论公式的完整计算流程
- ✅ 支持单次和批量计算
- ✅ 提供 Web 界面和 REST API
- ✅ 支持 Excel 导入导出
- ✅ 添加默认常量查看功能

## 技术栈

- **后端**: FastAPI, pandas, numpy
- **前端**: Vue 3, Element Plus
- **计算**: 基于《巷道支护理论公式.docx》

## 相关文件

- `backend/tunnel_support.py` - 核心计算模块
- `backend/server.py` - API 路由定义
- `frontend/src/components/TunnelSupportView.vue` - 前端界面
- `backend/verify_tunnel_support.py` - 验证测试脚本
- `hangdaojisuangongshi.py` - 原始计算脚本参考

---

如有问题或建议，请联系开发团队。
