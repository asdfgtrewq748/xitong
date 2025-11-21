; ==========================================
; FLAC3D 3层地质模型分步导入脚本
; 生成时间: 2025-11-21T19:11:04.088496
; 优势：线性执行，无复杂函数，易于调试
; ==========================================

; --- 1. 初始化 ---
model new
model deterministic on
model title "3-Layer Geological Model"

; --- 2. 定义全局网格尺寸 ---
; 修改这个数字可以控制所有层的网格疏密
fish define mesh_size
    return 50.0   ; 建议范围: 20.0 - 100.0 (单位：米)
end

; ==========================================
;   开始分层导入 (Layer 01 - 03)
; ==========================================

; --- Layer 01: 测试煤层1 ---
geometry import '01_coal_seam_1.stl' set 'geo_01'
zone generate from-geometry set 'geo_01' maximum-edge @mesh_size group 'L01_coal_seam_1'

; --- Layer 02: 测试煤层2 ---
geometry import '02_coal_seam_2.stl' set 'geo_02'
zone generate from-geometry set 'geo_02' maximum-edge @mesh_size group 'L02_coal_seam_2'

; --- Layer 03: 测试煤层3 ---
geometry import '03_coal_seam_3.stl' set 'geo_03'
zone generate from-geometry set 'geo_03' maximum-edge @mesh_size group 'L03_coal_seam_3'


; ==========================================
;   3. 关键步骤：全局网格缝合
; ==========================================
; 将所有独立生成的网格粘合在一起
zone attach by-face

; ==========================================
;   4. 保存模型
; ==========================================
model save 'Mesh_Generated_3Layers.sav'

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
