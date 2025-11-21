; FLAC3D自动导入脚本
; 自动导入所有分层STL文件
; 生成时间: 2025-11-21T17:53:23.776715

; 设置导入选项
model new
model configure geometry

; 获取脚本所在目录
define get_script_dir
    global script_dir = string(command.path.source)
    local i = string.reverse.find(script_dir, '\')
    if i # 0 then
        script_dir = string.sub(script_dir, 1, i-1)
    end_if
end
@get_script_dir

; 打印信息
fish define print_info
    io.out('========================================')
    io.out('地质模型自动导入')
    io.out('地层总数: 23')
    io.out('========================================')
end
@print_info


; 导入第1层: 6煤
fish define import_layer_1
    local filepath = string.build(script_dir, '\\01_6煤.stl')
    io.out('导入: 6煤')
    command
        geometry import stl [filepath]
        geometry group '6煤' range id @last
    end_command
end
@import_layer_1


; 导入第2层: 6-1煤
fish define import_layer_2
    local filepath = string.build(script_dir, '\\02_6-1煤.stl')
    io.out('导入: 6-1煤')
    command
        geometry import stl [filepath]
        geometry group '6-1煤' range id @last
    end_command
end
@import_layer_2


; 导入第3层: 砂质泥岩
fish define import_layer_3
    local filepath = string.build(script_dir, '\\03_砂质泥岩.stl')
    io.out('导入: 砂质泥岩')
    command
        geometry import stl [filepath]
        geometry group '砂质泥岩' range id @last
    end_command
end
@import_layer_3


; 导入第4层: 炭质泥岩
fish define import_layer_4
    local filepath = string.build(script_dir, '\\04_炭质泥岩.stl')
    io.out('导入: 炭质泥岩')
    command
        geometry import stl [filepath]
        geometry group '炭质泥岩' range id @last
    end_command
end
@import_layer_4


; 导入第5层: 高岭质泥岩
fish define import_layer_5
    local filepath = string.build(script_dir, '\\05_高岭质泥岩.stl')
    io.out('导入: 高岭质泥岩')
    command
        geometry import stl [filepath]
        geometry group '高岭质泥岩' range id @last
    end_command
end
@import_layer_5


; 导入第6层: 风化煤
fish define import_layer_6
    local filepath = string.build(script_dir, '\\06_风化煤.stl')
    io.out('导入: 风化煤')
    command
        geometry import stl [filepath]
        geometry group '风化煤' range id @last
    end_command
end
@import_layer_6


; 导入第7层: 粉砂岩
fish define import_layer_7
    local filepath = string.build(script_dir, '\\07_粉砂岩.stl')
    io.out('导入: 粉砂岩')
    command
        geometry import stl [filepath]
        geometry group '粉砂岩' range id @last
    end_command
end
@import_layer_7


; 导入第8层: 粗粒砂岩
fish define import_layer_8
    local filepath = string.build(script_dir, '\\08_粗粒砂岩.stl')
    io.out('导入: 粗粒砂岩')
    command
        geometry import stl [filepath]
        geometry group '粗粒砂岩' range id @last
    end_command
end
@import_layer_8


; 导入第9层: 细粒砂岩
fish define import_layer_9
    local filepath = string.build(script_dir, '\\09_细粒砂岩.stl')
    io.out('导入: 细粒砂岩')
    command
        geometry import stl [filepath]
        geometry group '细粒砂岩' range id @last
    end_command
end
@import_layer_9


; 导入第10层: 中粒砂岩
fish define import_layer_10
    local filepath = string.build(script_dir, '\\10_中粒砂岩.stl')
    io.out('导入: 中粒砂岩')
    command
        geometry import stl [filepath]
        geometry group '中粒砂岩' range id @last
    end_command
end
@import_layer_10


; 导入第11层: 泥岩
fish define import_layer_11
    local filepath = string.build(script_dir, '\\11_泥岩.stl')
    io.out('导入: 泥岩')
    command
        geometry import stl [filepath]
        geometry group '泥岩' range id @last
    end_command
end
@import_layer_11


; 导入第12层: 含砾粗粒砂岩
fish define import_layer_12
    local filepath = string.build(script_dir, '\\12_含砾粗粒砂岩.stl')
    io.out('导入: 含砾粗粒砂岩')
    command
        geometry import stl [filepath]
        geometry group '含砾粗粒砂岩' range id @last
    end_command
end
@import_layer_12


; 导入第13层: 含砾中砂岩
fish define import_layer_13
    local filepath = string.build(script_dir, '\\13_含砾中砂岩.stl')
    io.out('导入: 含砾中砂岩')
    command
        geometry import stl [filepath]
        geometry group '含砾中砂岩' range id @last
    end_command
end
@import_layer_13


; 导入第14层: 煤
fish define import_layer_14
    local filepath = string.build(script_dir, '\\14_煤.stl')
    io.out('导入: 煤')
    command
        geometry import stl [filepath]
        geometry group '煤' range id @last
    end_command
end
@import_layer_14


; 导入第15层: 5煤
fish define import_layer_15
    local filepath = string.build(script_dir, '\\15_5煤.stl')
    io.out('导入: 5煤')
    command
        geometry import stl [filepath]
        geometry group '5煤' range id @last
    end_command
end
@import_layer_15


; 导入第16层: 黄土
fish define import_layer_16
    local filepath = string.build(script_dir, '\\16_黄土.stl')
    io.out('导入: 黄土')
    command
        geometry import stl [filepath]
        geometry group '黄土' range id @last
    end_command
end
@import_layer_16


; 导入第17层: 高岭岩
fish define import_layer_17
    local filepath = string.build(script_dir, '\\17_高岭岩.stl')
    io.out('导入: 高岭岩')
    command
        geometry import stl [filepath]
        geometry group '高岭岩' range id @last
    end_command
end
@import_layer_17


; 导入第18层: 砾岩
fish define import_layer_18
    local filepath = string.build(script_dir, '\\18_砾岩.stl')
    io.out('导入: 砾岩')
    command
        geometry import stl [filepath]
        geometry group '砾岩' range id @last
    end_command
end
@import_layer_18


; 导入第19层: 煤线
fish define import_layer_19
    local filepath = string.build(script_dir, '\\19_煤线.stl')
    io.out('导入: 煤线')
    command
        geometry import stl [filepath]
        geometry group '煤线' range id @last
    end_command
end
@import_layer_19


; 导入第20层: 含砾粗砂岩
fish define import_layer_20
    local filepath = string.build(script_dir, '\\20_含砾粗砂岩.stl')
    io.out('导入: 含砾粗砂岩')
    command
        geometry import stl [filepath]
        geometry group '含砾粗砂岩' range id @last
    end_command
end
@import_layer_20


; 导入第21层: 黄土、断层
fish define import_layer_21
    local filepath = string.build(script_dir, '\\21_黄土、断层.stl')
    io.out('导入: 黄土、断层')
    command
        geometry import stl [filepath]
        geometry group '黄土、断层' range id @last
    end_command
end
@import_layer_21


; 导入第22层: 4煤
fish define import_layer_22
    local filepath = string.build(script_dir, '\\22_4煤.stl')
    io.out('导入: 4煤')
    command
        geometry import stl [filepath]
        geometry group '4煤' range id @last
    end_command
end
@import_layer_22


; 导入第23层: 4号风化煤
fish define import_layer_23
    local filepath = string.build(script_dir, '\\23_4号风化煤.stl')
    io.out('导入: 4号风化煤')
    command
        geometry import stl [filepath]
        geometry group '4号风化煤' range id @last
    end_command
end
@import_layer_23


; 导入完成
fish define finish_import
    io.out('========================================')
    io.out('导入完成！')
    io.out('========================================')
    io.out(' ')
    io.out('下一步: 为每层生成网格并设置材料属性')
    io.out('示例:')
    io.out('  zone generate from-geometry group "岩层名" edge-length 10.0')
    io.out('  zone cmodel assign elastic group "岩层名"')
    io.out('  zone property bulk 5e9 shear 3e9 group "岩层名"')
end
@finish_import
