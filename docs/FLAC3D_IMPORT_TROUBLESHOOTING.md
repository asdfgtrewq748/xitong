# FLAC3D分层导入问题修复指南

## 问题1：zone group 命令失败

### 错误信息
```
+++ No groups assigned to Zones.
```

### 原因
FISH脚本使用了错误的命令语法：
```fish
zone group 'L06_coal' range group 'geo_06'  ❌ 错误
```

### 修复
已更新为正确语法：
```fish
geometry import '06_coal.stl' set 'geo_06'
geometry set 'geo_06' triangulate
zone generate from-geometry set 'geo_06' maximum-edge @mesh_size group 'L06_coal'  ✅ 正确
```

**关键变化**：
- 添加了 `geometry set triangulate` 步骤
- 在`zone generate`命令中**直接指定group参数**
- **不需要**单独的`zone group`命令

---

## 问题2：几何体冲突错误

### 错误信息
```
*** [CM2_ERROR] A hard edge is cut by another hard edge or has a hard node inside it.
```

### 原因
多个封闭体（每层都是完整的六面体）在空间中重叠或相交，导致：
- 第n层的顶面与第n+1层的底面重叠
- Z坐标计算精度问题导致微小重叠
- FLAC3D的几何引擎检测到边相交

### 解决方案

#### 方案1：逐层调试（推荐用于定位问题）

```fish
; 1. 只导入前3层测试
geometry import '01_coal_6.stl' set 'geo_01'
geometry set 'geo_01' triangulate
zone generate from-geometry set 'geo_01' maximum-edge 50.0
zone group 'L01' range geometry-set 'geo_01'

geometry import '02_sandy_mudstone.stl' set 'geo_02'
geometry set 'geo_02' triangulate
zone generate from-geometry set 'geo_02' maximum-edge 50.0
zone group 'L02' range geometry-set 'geo_02'

; 如果这里成功，继续添加第3层
; 如果失败，说明第1-2层有问题
```

#### 方案2：增大网格尺寸

粗网格对几何误差的容忍度更高：
```fish
fish define mesh_size
    return 100.0   ; 增大到100米（原来是50米）
end
```

#### 方案3：分段导入

将23层分成几个段落：
```fish
; 段落1：第1-5层
; 导入并生成网格...
zone attach by-face
model save 'segment_01_05.sav'

; 段落2：第6-10层
; 导入并生成网格...
zone attach by-face
model save 'segment_06_10.sav'

; 最后合并所有段落
```

#### 方案4：检查数据质量

确认Z坐标的连续性：
```python
# 在Python中检查
for i in range(len(layers)-1):
    layer1 = layers[i]
    layer2 = layers[i+1]
    
    # 第i层的顶面应该等于第i+1层的底面
    top1 = layer1['top_surface_z']
    bottom2 = layer2['bottom_surface_z']
    
    diff = np.abs(top1 - bottom2)
    max_diff = np.max(diff)
    
    print(f"层{i+1}和层{i+2}之间的最大间隙: {max_diff:.6f}m")
    
    if max_diff > 0.01:  # 1厘米容差
        print(f"  ⚠️ 警告：间隙过大！")
```

---

## 立即可行的操作步骤

### Step 1: 使用修复后的FISH脚本

重新导出STL文件（已包含修复）：
1. 在前端点击"导出为STL（分层）"
2. 解压ZIP文件
3. 使用新的`import_to_flac3d.fish`脚本

### Step 2: 逐层测试导入

修改FISH脚本，先注释掉第8层之后的内容：
```fish
; --- Layer 08: 粗粒砂岩 ---
; geometry import '08_coarse_sandstone.stl' set 'geo_08'
; geometry set 'geo_08' triangulate
; zone generate from-geometry set 'geo_08' maximum-edge @mesh_size
; zone group 'L08_coarse_sandstone' range geometry-set 'geo_08'

; ; --- Layer 09: ... ---
; ; 暂时注释
```

### Step 3: 增大网格尺寸

如果仍有问题，修改mesh_size：
```fish
fish define mesh_size
    return 100.0   ; 从50增加到100
end
```

### Step 4: 检查导入结果

在每层导入后添加检查：
```fish
geometry import '06_coal.stl' set 'geo_06'
geometry set 'geo_06' triangulate
list geometry information  ; ← 检查几何信息
zone generate from-geometry set 'geo_06' maximum-edge @mesh_size
list zone information       ; ← 检查生成的网格
zone group 'L06_coal' range geometry-set 'geo_06'
list zone group             ; ← 检查组分配
```

---

## 根本解决方案（需要修改导出逻辑）

如果问题持续存在，可能需要改变STL导出策略：

### 选项A：只导出顶底面（无侧面）
每层只包含顶面和底面，不包含四个侧面。FLAC3D会自动连接相邻层。

### 选项B：层间共享节点
导出时确保相邻层的接触面使用完全相同的坐标。

### 选项C：统一导出（原来的方式）
将所有层合并为一个STL文件导出，避免多个几何集。

---

## 诊断命令

在FLAC3D中使用这些命令诊断问题：

```fish
; 查看所有几何集
list geometry sets

; 查看特定几何集的详情
list geometry set 'geo_08'

; 查看网格生成情况
list zone information

; 查看组分配
list zone group

; 删除问题几何集（重新来过）
geometry delete set 'geo_08'
```

---

## 总结

1. ✅ **zone group 命令已修复** - 使用`range geometry-set`
2. ⚠️ **几何冲突需要逐层调试** - 先找出是哪一层出问题
3. 💡 **建议**：先用粗网格(mesh_size=100)测试整个流程
4. 🔧 **如需根本解决**：可能要调整STL导出策略

---

**修复版本**: v1.2.1  
**修复日期**: 2024-11-21
