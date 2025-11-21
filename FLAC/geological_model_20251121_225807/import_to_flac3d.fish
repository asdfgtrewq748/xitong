; ==========================================
; FLAC3D 23层地质模型分步导入脚本
; 生成时间: 2025-11-21T22:58:07.302571
; 优势：线性执行，无复杂函数，易于调试
; ==========================================

; --- 1. 初始化 ---
model new
model deterministic on
model title "23-Layer Geological Model"

; --- 2. 定义全局网格尺寸 ---
; 修改这个数字可以控制所有层的网格疏密
fish define mesh_size
    return 50.0   ; 建议范围: 20.0 - 100.0 (单位：米)
end

; --- 3. 层间间隙配置 ---
; 自动层间间隙: 0.5m
; 坐标归一化: 是
;
; 说明：层间间隙不会影响建模，反而有以下好处：
;   1. 避免浮点误差导致的几何冲突
;   2. 提高接触面网格质量
;   3. 便于建立zone attach或zone interface
;   4. 使用zone attach可以刚性连接各层（无变形）
;
; 建立层间连接的方法（在所有层导入后执行）：
;   ; 方法1：刚性连接（假设完整接触）
;   zone attach by-face range geometry 'geo_01' range geometry 'geo_02'
;   
;   ; 方法2：接触单元（考虑滑移/分离）
;   zone interface create by-face range z [间隙中点Z值]
;   zone interface property stiffness-normal=1e10 stiffness-shear=1e9

; ==========================================
;   开始分层导入 (Layer 01 - 23)
; ==========================================
; 
; 重要提示：
; 如果遇到 "A hard edge is cut by another hard edge" 错误，
; 说明相邻层几何体有重叠或网格不闭合（已自动修复）。解决方法：
; 
; 方法1：逐层调试（推荐）
;   - 先注释掉所有层，只导入第1层
;   - 确认成功后，逐层添加，找出问题层
;   - 对问题层单独处理
; 
; 方法2：增大网格尺寸
;   - 将 mesh_size 改为 100.0 或更大
;   - 粗网格更容易生成，适合初步测试
; 
; 方法3：删除几何集后重新导入
;   - 如果某层失败，使用: geometry delete set 'geo_XX'
;   - 然后重新导入该层
; 
; ==========================================

; --- Layer 01: 6煤 ---
geometry import '01_coal_6.stl' set 'geo_01'
geometry set 'geo_01' triangulate
zone generate from-geometry set 'geo_01' maximum-edge @mesh_size
zone group 'L01_coal_6'

; --- Layer 02: 6-1煤 ---
geometry import '02_coal_6_1.stl' set 'geo_02'
geometry set 'geo_02' triangulate
zone generate from-geometry set 'geo_02' maximum-edge @mesh_size
zone group 'L02_coal_6_1'

; --- Layer 03: 砂质泥岩 ---
geometry import '03_sandy_mudstone.stl' set 'geo_03'
geometry set 'geo_03' triangulate
zone generate from-geometry set 'geo_03' maximum-edge @mesh_size
zone group 'L03_sandy_mudstone'

; --- Layer 04: 炭质泥岩 ---
geometry import '04_mudstone.stl' set 'geo_04'
geometry set 'geo_04' triangulate
zone generate from-geometry set 'geo_04' maximum-edge @mesh_size
zone group 'L04_mudstone'

; --- Layer 05: 高岭质泥岩 ---
geometry import '05_mudstone.stl' set 'geo_05'
geometry set 'geo_05' triangulate
zone generate from-geometry set 'geo_05' maximum-edge @mesh_size
zone group 'L05_mudstone'

; --- Layer 06: 风化煤 ---
geometry import '06_coal.stl' set 'geo_06'
geometry set 'geo_06' triangulate
zone generate from-geometry set 'geo_06' maximum-edge @mesh_size
zone group 'L06_coal'

; --- Layer 07: 粉砂岩 ---
geometry import '07_siltstone.stl' set 'geo_07'
geometry set 'geo_07' triangulate
zone generate from-geometry set 'geo_07' maximum-edge @mesh_size
zone group 'L07_siltstone'

; --- Layer 08: 粗粒砂岩 ---
geometry import '08_coarse_sandstone.stl' set 'geo_08'
geometry set 'geo_08' triangulate
zone generate from-geometry set 'geo_08' maximum-edge @mesh_size
zone group 'L08_coarse_sandstone'

; --- Layer 09: 细粒砂岩 ---
geometry import '09_fine_sandstone.stl' set 'geo_09'
geometry set 'geo_09' triangulate
zone generate from-geometry set 'geo_09' maximum-edge @mesh_size
zone group 'L09_fine_sandstone'

; --- Layer 10: 中粒砂岩 ---
geometry import '10_medium_sandstone.stl' set 'geo_10'
geometry set 'geo_10' triangulate
zone generate from-geometry set 'geo_10' maximum-edge @mesh_size
zone group 'L10_medium_sandstone'

; --- Layer 11: 泥岩 ---
geometry import '11_mudstone.stl' set 'geo_11'
geometry set 'geo_11' triangulate
zone generate from-geometry set 'geo_11' maximum-edge @mesh_size
zone group 'L11_mudstone'

; --- Layer 12: 含砾粗粒砂岩 ---
geometry import '12_coarse_sandstone.stl' set 'geo_12'
geometry set 'geo_12' triangulate
zone generate from-geometry set 'geo_12' maximum-edge @mesh_size
zone group 'L12_coarse_sandstone'

; --- Layer 13: 含砾中砂岩 ---
geometry import '13_medium_sandstone.stl' set 'geo_13'
geometry set 'geo_13' triangulate
zone generate from-geometry set 'geo_13' maximum-edge @mesh_size
zone group 'L13_medium_sandstone'

; --- Layer 14: 煤 ---
geometry import '14_coal.stl' set 'geo_14'
geometry set 'geo_14' triangulate
zone generate from-geometry set 'geo_14' maximum-edge @mesh_size
zone group 'L14_coal'

; --- Layer 15: 5煤 ---
geometry import '15_coal_5.stl' set 'geo_15'
geometry set 'geo_15' triangulate
zone generate from-geometry set 'geo_15' maximum-edge @mesh_size
zone group 'L15_coal_5'

; --- Layer 16: 黄土 ---
geometry import '16_loess.stl' set 'geo_16'
geometry set 'geo_16' triangulate
zone generate from-geometry set 'geo_16' maximum-edge @mesh_size
zone group 'L16_loess'

; --- Layer 17: 高岭岩 ---
geometry import '17_layer.stl' set 'geo_17'
geometry set 'geo_17' triangulate
zone generate from-geometry set 'geo_17' maximum-edge @mesh_size
zone group 'L17_layer'

; --- Layer 18: 砾岩 ---
geometry import '18_conglomerate.stl' set 'geo_18'
geometry set 'geo_18' triangulate
zone generate from-geometry set 'geo_18' maximum-edge @mesh_size
zone group 'L18_conglomerate'

; --- Layer 19: 煤线 ---
geometry import '19_coal.stl' set 'geo_19'
geometry set 'geo_19' triangulate
zone generate from-geometry set 'geo_19' maximum-edge @mesh_size
zone group 'L19_coal'

; --- Layer 20: 含砾粗砂岩 ---
geometry import '20_coarse_sandstone.stl' set 'geo_20'
geometry set 'geo_20' triangulate
zone generate from-geometry set 'geo_20' maximum-edge @mesh_size
zone group 'L20_coarse_sandstone'

; --- Layer 21: 黄土、断层 ---
geometry import '21_loess.stl' set 'geo_21'
geometry set 'geo_21' triangulate
zone generate from-geometry set 'geo_21' maximum-edge @mesh_size
zone group 'L21_loess'

; --- Layer 22: 4煤 ---
geometry import '22_coal_4.stl' set 'geo_22'
geometry set 'geo_22' triangulate
zone generate from-geometry set 'geo_22' maximum-edge @mesh_size
zone group 'L22_coal_4'

; --- Layer 23: 4号风化煤 ---
geometry import '23_coal_4.stl' set 'geo_23'
geometry set 'geo_23' triangulate
zone generate from-geometry set 'geo_23' maximum-edge @mesh_size
zone group 'L23_coal_4'


; ==========================================
;   3. 建立层间连接（关键步骤）
; ==========================================
; 虽然各层有物理间隙，但需要建立力学连接
; 选择以下方法之一：

; --- 方法A：刚性连接（推荐，假设完整接触）---
; 将所有相邻层的接触面粘合在一起
; 优点：简单、稳定，适合大多数情况
zone attach by-face

; --- 方法B：柔性接触（可选，适合软弱夹层）---
; 如果需要模拟层间滑移或分离，使用接触单元
; 注释掉上面的 zone attach，改用以下代码：
;
; fish define setup_interfaces
;   ; 为每对相邻层创建接触界面
;   zone interface create by-face
;   ; 设置接触刚度（根据实际地质条件调整）
;   zone interface property stiffness-normal=1e10 stiffness-shear=1e9
;   zone interface property friction=30.0 cohesion=0.5e6
; end
; [@setup_interfaces]

; ==========================================
;   4. 检查并显示结果
; ==========================================
; 显示各层的网格数量
list zone group

; ==========================================
;   5. 保存模型
; ==========================================
model save 'Mesh_Generated_23Layers.sav'

; 输出结果信息
list zone information

; ==========================================
;   导入完成！
; ==========================================
; 下一步：
; 1. 为各层分配材料属性
;    例如: zone cmodel assign elastic range group 'L01_coal_6'
;         zone property bulk 5e9 shear 3e9 density 2500 range group 'L01_coal_6'
;
; 2. 设置边界条件
;    例如: zone face apply velocity-normal 0 range position-z 0
;
; 3. 运行模拟
;    例如: model solve
;
; 注意：
; - 如果导入过程中出错，可以注释掉已成功导入的层继续调试
; - mesh_size 值越小网格越密集，计算量越大
; - 确保所有STL文件与此脚本在同一目录下
