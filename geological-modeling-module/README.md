# 地质建模功能模块

这是一个独立的地质建模功能模块，可以从钻孔数据生成3D地质模型，并导出为多种格式（STL、DXF、FLAC3D等）。

## 目录结构

```
geological-modeling-module/
├── frontend/                          # 前端代码
│   ├── components/
│   │   └── GeologicalModelingView.vue # 主建模页面组件
│   ├── stores/
│   │   └── globalData.js              # Pinia全局数据存储
│   ├── utils/
│   │   ├── api.js                     # API调用工具
│   │   ├── lod3DManager.js            # 3D LOD管理器
│   │   └── dataNormalizer.js          # 数据规范化工具
│   └── data/
│       └── boreholes.json             # 演示数据
│
└── backend/                           # 后端代码
    ├── interpolation.py               # 插值算法模块
    ├── coal_seam_blocks/
    │   ├── __init__.py
    │   ├── modeling.py                # 建模核心逻辑
    │   └── aggregator.py              # 钻孔数据聚合
    └── exporters/
        ├── __init__.py
        ├── base_exporter.py           # 导出器基类
        ├── stl_exporter.py            # STL格式导出
        ├── dxf_exporter.py            # DXF格式导出
        ├── flac3d_exporter.py         # FLAC3D格式导出
        ├── f3grid_exporter.py         # F3GRID格式导出
        ├── obj_exporter.py            # OBJ格式导出
        ├── layered_stl_exporter.py    # 分层STL导出
        └── tetra_f3grid_exporter.py   # 四面体F3GRID导出
```

## 功能特性

### 1. 数据导入
- 支持CSV/Excel格式的钻孔数据
- 自动合并钻孔数据与坐标数据
- 数据验证和归一化处理

### 2. 插值算法
- **线性插值 (linear)**: 快速、稳定
- **最近邻插值 (nearest)**: 适用于稀疏数据
- **三次插值 (cubic)**: 平滑曲面
- **克里金插值 (kriging)**: 地质统计学方法
- **径向基函数 (RBF)**: 多种核函数支持
- **反距离加权 (IDW)**: 可调权重指数
- **各向异性插值**: 考虑地质构造方向性

### 3. 3D建模
- 基于钻孔数据生成三维地质模型
- 支持多层地层自下而上堆叠
- 自动处理层间间隙和重叠
- 垂向顺序验证和修复

### 4. 模型导出
- **STL**: 三角网格格式，用于FLAC3D、3D打印
- **DXF**: CAD格式，用于AutoCAD
- **OBJ**: 通用3D格式，用于Blender、3ds Max
- **FLAC3D DAT**: FLAC3D脚本格式
- **F3GRID**: FLAC3D原生网格格式

## 依赖要求

### 前端
```json
{
  "vue": "^3.0.0",
  "pinia": "^2.0.0",
  "element-plus": "^2.0.0",
  "echarts": "^5.0.0",
  "echarts-gl": "^2.0.0"
}
```

### 后端
```
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=0.24.0
ezdxf>=0.18.0  # DXF导出
pykrige>=1.5.0  # 克里金插值（可选）
```

## 集成指南

### 前端集成

1. **复制文件到项目**
```bash
# 复制组件
cp -r frontend/components/GeologicalModelingView.vue your-project/src/components/

# 复制工具函数
cp -r frontend/utils/* your-project/src/utils/

# 复制store
cp -r frontend/stores/globalData.js your-project/src/stores/

# 复制演示数据（可选）
cp -r frontend/data/boreholes.json your-project/src/data/
```

2. **配置路由**
```javascript
// router/index.js
import GeologicalModelingView from '@/components/GeologicalModelingView.vue'

const routes = [
  {
    path: '/modeling',
    name: 'GeologicalModeling',
    component: GeologicalModelingView
  }
]
```

3. **配置Pinia Store**
```javascript
// main.js
import { createPinia } from 'pinia'
import { useGlobalDataStore } from '@/stores/globalData'

const app = createApp(App)
app.use(createPinia())
```

### 后端集成

1. **复制后端模块**
```bash
# 复制核心模块
cp -r backend/coal_seam_blocks your-project/
cp backend/interpolation.py your-project/

# 复制导出器
cp -r backend/exporters your-project/
```

2. **添加API端点**
```python
# api.py
from coal_seam_blocks.modeling import build_block_models
from coal_seam_blocks.aggregator import aggregate_boreholes
from interpolation import interpolate
from exporters import STLExporter, DXFExporter, F3GridExporter

@app.post('/api/modeling/generate')
def generate_model(params: dict):
    """生成3D地质模型"""
    # 实现建模逻辑
    pass

@app.post('/api/modeling/export')
def export_model(params: dict):
    """导出模型到指定格式"""
    # 实现导出逻辑
    pass
```

3. **配置CORS（如果前后端分离）**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API接口说明

### 前端API调用

```javascript
// 获取API基础URL
import { getApiBase } from '@/utils/api'

// 生成块体模型
const response = await fetch(`${getApiBase()}/modeling/generate_block_model`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    seam_col: '煤层',
    x_col: 'X坐标',
    y_col: 'Y坐标',
    thickness_col: '厚度',
    selected_seams: ['煤层1', '煤层2'],
    resolution: 50,
    base_level: 0,
    gap: 0.5,
    interpolation_method: 'linear'
  })
})

// 导出模型
const exportResponse = await fetch(`${getApiBase()}/modeling/export`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    export_type: 'stl',  // 或 'dxf', 'f3grid'
    layers: modelData.layers
  })
})
```

### 后端API示例

```python
# 生成块体模型
@app.post('/api/modeling/generate_block_model')
def generate_block_model(params: ModelingParams):
    block_models, skipped, (XI, YI) = build_block_models(
        merged_df=params.merged_df,
        seam_column=params.seam_col,
        x_col=params.x_col,
        y_col=params.y_col,
        thickness_col=params.thickness_col,
        selected_seams=params.selected_seams,
        method_callable=lambda x,y,z,xi,yi: interpolate(x,y,z,xi,yi,params.method),
        resolution=params.resolution,
        base_level=params.base_level,
        gap_value=params.gap
    )

    return {
        'status': 'success',
        'layers': [
            {
                'name': m.name,
                'grid_x': XI.tolist(),
                'grid_y': YI.tolist(),
                'top_surface_z': m.top_surface.tolist(),
                'bottom_surface_z': m.bottom_surface.tolist()
            }
            for m in block_models
        ]
    }
```

## 使用示例

### 数据格式要求

**钻孔数据 (CSV)**
```csv
钻孔名,岩层,厚度,X坐标,Y坐标
ZK001,煤层1,2.5,100.0,200.0
ZK001,砂岩,5.0,100.0,200.0
ZK002,煤层1,3.0,150.0,250.0
```

**坐标文件 (CSV)**
```csv
钻孔名,X坐标,Y坐标
ZK001,100.0,200.0
ZK002,150.0,250.0
```

### 建模流程

1. **加载数据**: 上传钻孔文件和坐标文件
2. **选择参数**: 选择岩层、坐标列、插值方法
3. **生成模型**: 点击建模按钮生成3D模型
4. **导出模型**: 选择格式导出到本地

## 注意事项

1. **数据质量**: 建模结果质量取决于钻孔数据的密度和分布
2. **插值方法**: 建议先用线性插值快速验证，再用克里金优化
3. **导出格式**: FLAC3D推荐使用F3GRID格式，STL用于可视化
4. **性能**: 大数据量时建议降低分辨率或使用降采样

## 许可证

本模块从原项目中提取，请遵守原项目的许可证规定。
