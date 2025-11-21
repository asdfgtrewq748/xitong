# FLAC3D 导入网格完整指南

## 🎯 问题诊断

您的文件 `地质3D模型_2025-11-20T10-40-10.f3grid` **包含完整数据**：
- ✅ 节点数：153,600
- ✅ 单元数：143,543
- ✅ 文件大小：15.11 MB

如果在 FLAC3D 中"什么都没有"，通常是**导入方式或显示设置**的问题。

---

## 📖 正确的 FLAC3D 导入步骤

### 方法一：使用 PROGRAM CALL 命令（推荐）

1. **启动 FLAC3D**

2. **在命令行输入**：
   ```flac
   program call 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'
   ```
   
   ⚠️ **注意**：
   - 路径必须使用 **正斜杠 `/`** 或 **双反斜杠 `\\`**
   - 不要用单反斜杠 `\`
   - 路径用单引号包裹

3. **等待加载**（大约10-30秒）

4. **检查导入结果**：
   ```flac
   ; 查看节点数
   print zone.num
   
   ; 查看单元数
   print gp.num
   
   ; 查看分组
   print zone.group.list
   ```

5. **如果看不到模型，检查显示设置**：
   ```flac
   ; 打开图形窗口
   plot create
   
   ; 显示网格
   plot item create zones
   
   ; 自动调整视角
   plot view auto
   
   ; 刷新显示
   plot update
   ```

---

### 方法二：使用 GUI 导入

#### Step 1: 导入文件

1. 打开 FLAC3D
2. 菜单：**Tools → Import → Grid**
3. 选择文件类型：**FLAC3D Grid (*.f3grid)**
4. 浏览到：`e:\xiangmu\xitong\data\output\`
5. 选择文件：`地质3D模型_2025-11-20T10-40-10.f3grid`
6. 点击 **Open**

#### Step 2: 等待加载

- 进度条显示导入进度
- 大约需要 10-30 秒（取决于电脑性能）

#### Step 3: 显示模型

如果导入后看不到模型：

1. **打开 Plot 窗口**：
   - View → New Plot View
   
2. **添加 Zone 显示**：
   - 在 Plot Items 面板
   - 右键 → Add → Zones
   
3. **调整视角**：
   - 点击工具栏的 **Fit to Window** 按钮（放大镜图标）
   - 或使用鼠标：
     - 左键拖动：旋转
     - 滚轮：缩放
     - 中键拖动：平移

4. **检查模型范围**：
   ```flac
   ; 获取模型边界
   print zone.pos.min
   print zone.pos.max
   ```

---

### 方法三：通过 FISH 脚本导入

创建文件 `import_model.fish`：

```fish
; import_model.fish - 导入并显示地质模型

def import_and_show
  ; 清空当前模型
  model new
  
  ; 导入网格
  program call 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'
  
  ; 等待导入完成
  command
    program log on
  endcommand
  
  ; 检查导入结果
  local num_zones = zone.num
  local num_gps = gp.num
  io.out('导入完成:')
  io.out('  节点数: ' + string(num_gps))
  io.out('  单元数: ' + string(num_zones))
  
  ; 如果导入成功，显示模型
  if num_zones > 0 then
    command
      ; 创建图形窗口
      plot create
      plot item create zones
      plot view auto
      plot update
    endcommand
    io.out('✅ 模型已显示')
  else
    io.out('❌ 导入失败，请检查文件路径')
  endif
end

; 执行导入
import_and_show
```

在 FLAC3D 中运行：
```flac
program call 'import_model.fish'
```

---

## 🔍 故障排查

### 问题 1: 提示"文件未找到"

**原因**：路径格式错误

**解决**：
```flac
; ❌ 错误（单反斜杠）
program call 'e:\xiangmu\xitong\data\output\model.f3grid'

; ✅ 正确（正斜杠）
program call 'e:/xiangmu/xitong/data/output/model.f3grid'

; ✅ 正确（双反斜杠）
program call 'e:\\xiangmu\\xitong\\data\\output\\model.f3grid'
```

### 问题 2: 导入后显示"0 zones"

**检查步骤**：

1. **确认文件完整性**：
   ```powershell
   # 在 PowerShell 中运行
   python e:\xiangmu\xitong\backend\check_flac3d_export.py
   ```

2. **查看 FLAC3D 日志**：
   ```flac
   ; 开启详细日志
   program log on
   program log-file 'import_debug.log'
   program call 'model.f3grid'
   ```
   
3. **检查日志文件** `import_debug.log` 查找错误信息

### 问题 3: 模型太小或太大看不见

**原因**：坐标范围问题或视角未调整

**解决**：

```flac
; 1. 查看模型范围
print zone.pos.min
print zone.pos.max

; 2. 手动设置视角范围
plot view auto

; 3. 或指定视角中心
plot view center (0, 0, 0)
plot view distance 1000

; 4. 重置视角
plot view reset
```

### 问题 4: 只显示部分模型

**原因**：剪切面或范围过滤

**解决**：
```flac
; 移除所有剪切面
plot item clip remove

; 显示所有单元
plot item zones color by group
plot item zones transparency 0.3
```

### 问题 5: 模型是空心的

**原因**：只显示了外表面

**解决**：
```flac
; 显示剖面
plot item create zone-slice position (0,0,0) normal (0,0,1)

; 或创建剪切视图
plot item clip create position (0,0,0) normal (1,0,0)
```

---

## 🎨 模型可视化建议

### 基础显示设置

```flac
; 创建新视图
model new
program call 'model.f3grid'

; 设置显示
plot create
plot item create zones
plot item zones color-by group
plot item zones edge show
plot view auto
plot lighting on
```

### 按煤层着色

```flac
; 为不同煤层设置颜色
plot item zones color-by group
plot item zones color '2煤' red
plot item zones color '3煤' blue
plot item zones color '顶板' gray
plot item zones color '底板' brown
```

### 显示网格线

```flac
plot item zones edge show
plot item zones edge color black
plot item zones transparency 0.3
```

### 创建剖面图

```flac
; XZ 平面剖面（沿 Y=0 切）
plot item create zone-slice position (0,0,0) normal (0,1,0)
plot item zone-slice color-by group

; YZ 平面剖面（沿 X=0 切）
plot item create zone-slice position (0,0,0) normal (1,0,0)
```

---

## 📝 完整建模流程示例

### 1. 导入和验证

```flac
; 新建模型
model new
model title '煤层地质模型'

; 导入网格
program call 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'

; 验证导入
print zone.num
print gp.num
print zone.group.list

; 显示模型
plot create
plot item create zones
plot item zones color-by group
plot view auto
```

### 2. 赋材料属性

```flac
; 定义本构模型
zone cmodel assign mohr-coulomb

; 2煤层属性
zone property density 1400 bulk 1.5e9 shear 0.9e9 cohesion 1.5e6 ...
  friction 28 dilation 5 range group '2煤'

; 顶板（砂岩）属性
zone property density 2600 bulk 5e9 shear 3e9 cohesion 5e6 ...
  friction 35 range group '顶板'

; 底板（泥岩）属性
zone property density 2500 bulk 3e9 shear 1.8e9 cohesion 3e6 ...
  friction 30 range group '底板'
```

### 3. 设置边界条件

```flac
; 底部固定
zone face apply velocity-normal 0 range position-z [zone.pos.min.z]

; 侧面法向约束
zone face apply velocity-normal 0 range ...
  position-x [zone.pos.min.x] [zone.pos.min.x + 10]
zone face apply velocity-normal 0 range ...
  position-x [zone.pos.max.x - 10] [zone.pos.max.x]
  
zone face apply velocity-normal 0 range ...
  position-y [zone.pos.min.y] [zone.pos.min.y + 10]
zone face apply velocity-normal 0 range ...
  position-y [zone.pos.max.y - 10] [zone.pos.max.y]

; 顶部应力
zone face apply stress-normal -10e6 range position-z [zone.pos.max.z]
```

### 4. 初始化和求解

```flac
; 设置重力
model gravity 9.81

; 初始平衡
model cycle 5000
model solve ratio 1e-5

; 保存初始状态
model save 'initial'

; 模拟开采（删除煤层的一部分）
zone delete range group '2煤' ...
  position-x -50 50 ...
  position-y -100 100

; 求解开采后状态
model cycle 10000
model solve ratio 1e-5

; 保存最终状态
model save 'after_mining'
```

### 5. 结果查看

```flac
; 位移云图
plot create
plot item create zone-contour quantity displacement-z
plot item zone-contour transparency 0
plot colormap rainbow
plot view auto

; 应力云图
plot create
plot item create zone-contour quantity stress-zz
plot colormap jet

; 塑性区分布
plot create
plot item create zones
plot item zones color-by state
plot view auto
```

---

## 🚀 快速测试脚本

创建 `test_import.fish` 快速测试：

```fish
def test_import
  model new
  
  ; 尝试导入
  command
    program log on
    program call 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'
  endcommand
  
  ; 检查结果
  local nz = zone.num
  local ngp = gp.num
  
  io.out('')
  io.out('=== 导入测试结果 ===')
  io.out('节点数: ' + string(ngp))
  io.out('单元数: ' + string(nz))
  
  if nz > 0 then
    io.out('✅ 导入成功！')
    
    ; 显示模型
    command
      plot create
      plot title 'Geological Model'
      plot item create zones
      plot item zones color-by group
      plot item zones edge show
      plot view auto
      plot update
    endcommand
    
    ; 输出分组信息
    io.out('')
    io.out('=== 煤层分组 ===')
    local glist = zone.group.list
    loop foreach local g glist
      local count = zone.group.count(g)
      io.out('  ' + g + ': ' + string(count) + ' 个单元')
    endloop
    
  else
    io.out('❌ 导入失败，请检查文件路径')
  endif
end

; 执行测试
test_import
```

运行：
```flac
program call 'test_import.fish'
```

---

## 📞 技术支持

如果以上方法仍然无法显示模型，请提供：

1. **FLAC3D 版本**
   ```flac
   print version
   ```

2. **错误日志**
   ```flac
   program log on
   program log-file 'error.log'
   program call 'model.f3grid'
   ```
   然后发送 `error.log` 内容

3. **模型信息**
   ```flac
   print zone.num
   print gp.num
   print zone.pos.min
   print zone.pos.max
   ```

---

**关键提示**：您的文件是完整的，包含 153,600 个节点和 143,543 个单元。如果看不到，99% 是导入命令或显示设置的问题，请严格按照上述步骤操作！
