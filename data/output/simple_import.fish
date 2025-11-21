; simple_import.fish - 简化版导入脚本
; 使用方法: program call 'e:/xiangmu/xitong/data/output/simple_import.fish'

; 清空并导入
model new
program call 'e:/xiangmu/xitong/data/output/地质3D模型_2025-11-20T10-40-10.f3grid'

; 显示结果
fish define show_result
  io.out('')
  io.out('===== Import Complete =====')
  io.out('Gridpoints: ' + string(gp.num))
  io.out('Zones: ' + string(zone.num))
  io.out('')
  
  if zone.num > 0 then
    io.out('Groups:')
    loop foreach local g zone.group.list
      io.out('  ' + g + ': ' + string(zone.group.count(g)))
    end_loop
  end_if
  io.out('')
end
@show_result

; 创建显示
plot create
plot item create zones
plot item zones color-by group
plot view auto
plot update

; 提示信息
fish define tips
  io.out('Model displayed successfully!')
  io.out('Use mouse to rotate/zoom/pan the view.')
  io.out('')
end
@tips
