; ==========================================
; FLAC3D 23层地质模型分步导入脚本
; 生成时间: 2025-11-21T19:19:11.609240
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

; ==========================================
;   开始分层导入 (Layer 01 - 23)
; ==========================================

; --- Layer 01: 6煤 ---
geometry import '01_coal_6.stl' set 'geo_01'
zone generate from-geometry set 'geo_01' maximum-edge @mesh_size group 'L01_coal_6'

; --- Layer 02: 6-1煤 ---
geometry import '02_coal_6_1.stl' set 'geo_02'
zone generate from-geometry set 'geo_02' maximum-edge @mesh_size group 'L02_coal_6_1'

; --- Layer 03: 砂质泥岩 ---
geometry import '03_sandy_mudstone.stl' set 'geo_03'
zone generate from-geometry set 'geo_03' maximum-edge @mesh_size group 'L03_sandy_mudstone'

; --- Layer 04: 炭质泥岩 ---
geometry import '04_mudstone.stl' set 'geo_04'
zone generate from-geometry set 'geo_04' maximum-edge @mesh_size group 'L04_mudstone'

; --- Layer 05: 高岭质泥岩 ---
geometry import '05_mudstone.stl' set 'geo_05'
zone generate from-geometry set 'geo_05' maximum-edge @mesh_size group 'L05_mudstone'

; --- Layer 06: 风化煤 ---
geometry import '06_coal.stl' set 'geo_06'
zone generate from-geometry set 'geo_06' maximum-edge @mesh_size group 'L06_coal'

; --- Layer 07: 粉砂岩 ---
geometry import '07_siltstone.stl' set 'geo_07'
zone generate from-geometry set 'geo_07' maximum-edge @mesh_size group 'L07_siltstone'

; --- Layer 08: 粗粒砂岩 ---
geometry import '08_coarse_sandstone.stl' set 'geo_08'
zone generate from-geometry set 'geo_08' maximum-edge @mesh_size group 'L08_coarse_sandstone'

; --- Layer 09: 细粒砂岩 ---
geometry import '09_fine_sandstone.stl' set 'geo_09'
zone generate from-geometry set 'geo_09' maximum-edge @mesh_size group 'L09_fine_sandstone'

; --- Layer 10: 中粒砂岩 ---
geometry import '10_medium_sandstone.stl' set 'geo_10'
zone generate from-geometry set 'geo_10' maximum-edge @mesh_size group 'L10_medium_sandstone'

; --- Layer 11: 泥岩 ---
geometry import '11_mudstone.stl' set 'geo_11'
zone generate from-geometry set 'geo_11' maximum-edge @mesh_size group 'L11_mudstone'

; --- Layer 12: 含砾粗粒砂岩 ---
geometry import '12_coarse_sandstone.stl' set 'geo_12'
zone generate from-geometry set 'geo_12' maximum-edge @mesh_size group 'L12_coarse_sandstone'

; --- Layer 13: 含砾中砂岩 ---
geometry import '13_medium_sandstone.stl' set 'geo_13'
zone generate from-geometry set 'geo_13' maximum-edge @mesh_size group 'L13_medium_sandstone'

; --- Layer 14: 煤 ---
geometry import '14_coal.stl' set 'geo_14'
zone generate from-geometry set 'geo_14' maximum-edge @mesh_size group 'L14_coal'

; --- Layer 15: 5煤 ---
geometry import '15_coal_5.stl' set 'geo_15'
zone generate from-geometry set 'geo_15' maximum-edge @mesh_size group 'L15_coal_5'

; --- Layer 16: 黄土 ---
geometry import '16_loess.stl' set 'geo_16'
zone generate from-geometry set 'geo_16' maximum-edge @mesh_size group 'L16_loess'

; --- Layer 17: 高岭岩 ---
geometry import '17_layer.stl' set 'geo_17'
zone generate from-geometry set 'geo_17' maximum-edge @mesh_size group 'L17_layer'

; --- Layer 18: 砾岩 ---
geometry import '18_conglomerate.stl' set 'geo_18'
zone generate from-geometry set 'geo_18' maximum-edge @mesh_size group 'L18_conglomerate'

; --- Layer 19: 煤线 ---
geometry import '19_coal.stl' set 'geo_19'
zone generate from-geometry set 'geo_19' maximum-edge @mesh_size group 'L19_coal'

; --- Layer 20: 含砾粗砂岩 ---
geometry import '20_coarse_sandstone.stl' set 'geo_20'
zone generate from-geometry set 'geo_20' maximum-edge @mesh_size group 'L20_coarse_sandstone'

; --- Layer 21: 黄土、断层 ---
geometry import '21_loess.stl' set 'geo_21'
zone generate from-geometry set 'geo_21' maximum-edge @mesh_size group 'L21_loess'

; --- Layer 22: 4煤 ---
geometry import '22_coal_4.stl' set 'geo_22'
zone generate from-geometry set 'geo_22' maximum-edge @mesh_size group 'L22_coal_4'

; --- Layer 23: 4号风化煤 ---
geometry import '23_coal_4.stl' set 'geo_23'
zone generate from-geometry set 'geo_23' maximum-edge @mesh_size group 'L23_coal_4'


; ==========================================
;   3. 关键步骤：全局网格缝合
; ==========================================
; 将所有独立生成的网格粘合在一起
zone attach by-face

; ==========================================
;   4. 保存模型
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
