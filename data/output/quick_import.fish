; quick_import.fish - 快速导入和显示地质模型
; 使用方法：在 FLAC3D 中执行 program call 'quick_import.fish'

; 清空当前模型
model new
model title 'Geological Model Import Test'

; 显示信息
fish define show_info
  io.out('')
  io.out('==============================================')
  io.out('     FLAC3D Geological Model Import Tool')
  io.out('==============================================')
  io.out('')
end
@show_info

; 设置文件路径
fish define setup
  global fpath = 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'
  io.out('Importing file:')
  io.out('  ' + fpath)
  io.out('')
  io.out('Please wait...')
end
@setup

; 开启日志
program log on

; 导入网格文件
program call [fpath]

; 检查导入结果
fish define check_import
  io.out('')
  io.out('=== Import Result ===')
  io.out('  Number of gridpoints: ' + string(gp.num))
  io.out('  Number of zones: ' + string(zone.num))
  
  if zone.num = 0 then
    io.out('')
    io.out('ERROR: No zones imported!')
    io.out('Please check the file path above.')
    exit
  end_if
  
  io.out('  Status: SUCCESS')
  io.out('')
  
  ; Model bounds
  io.out('=== Model Bounds ===')
  io.out('  X: ' + string(zone.pos.min.x) + ' to ' + string(zone.pos.max.x))
  io.out('  Y: ' + string(zone.pos.min.y) + ' to ' + string(zone.pos.max.y))
  io.out('  Z: ' + string(zone.pos.min.z) + ' to ' + string(zone.pos.max.z))
  io.out('')
  
  ; Group info
  io.out('=== Groups ===')
  loop foreach local grp zone.group.list
    io.out('  ' + grp + ': ' + string(zone.group.count(grp)) + ' zones')
  end_loop
  io.out('')
end
@check_import

; Create visualization
io.out('Creating 3D visualization...')

plot create
plot title 'Geological Model'
plot item create zones
plot item zones color-by group
plot item zones edge show on
plot item zones edge color black
plot item zones transparency 0.3
plot view auto
plot lighting on
plot update

io.out('Visualization complete!')
io.out('')
io.out('==============================================')
io.out('  Tips:')
io.out('  - Left mouse: Rotate view')
io.out('  - Mouse wheel: Zoom')
io.out('  - Middle mouse: Pan')
io.out('  - Click Fit icon to auto-adjust view')
io.out('==============================================')
io.out('')
