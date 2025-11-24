"""
诊断STL层间重叠的工具脚本
用于读取导出的STL文件并检查Z范围是否有重叠
"""

import struct
import numpy as np
from pathlib import Path


def read_stl_z_range(stl_path):
    """读取STL文件的Z坐标范围"""
    with open(stl_path, 'rb') as f:
        # 跳过80字节头
        header = f.read(80)
        
        # 读取三角形数量
        num_triangles = struct.unpack('<I', f.read(4))[0]
        
        z_values = []
        
        # 读取每个三角形
        for _ in range(num_triangles):
            # 跳过法向量(12字节)
            f.read(12)
            
            # 读取3个顶点(每个顶点12字节: 3个float)
            for _ in range(3):
                x, y, z = struct.unpack('<fff', f.read(12))
                z_values.append(z)
            
            # 跳过属性字节(2字节)
            f.read(2)
        
        z_array = np.array(z_values)
        return {
            'min': float(np.min(z_array)),
            'max': float(np.max(z_array)),
            'mean': float(np.mean(z_array)),
            'num_triangles': num_triangles,
            'num_vertices': len(z_values)
        }


def check_layer_overlap(stl_dir, pattern='*.stl'):
    """检查目录中所有STL文件的层间重叠情况"""
    stl_files = sorted(Path(stl_dir).glob(pattern))
    
    if not stl_files:
        print(f"未找到STL文件: {stl_dir}/{pattern}")
        return
    
    print(f"\n{'='*80}")
    print(f"STL文件Z范围检查")
    print(f"{'='*80}")
    print(f"目录: {stl_dir}")
    print(f"文件数: {len(stl_files)}")
    print(f"{'='*80}\n")
    
    layers_info = []
    
    # 读取所有文件
    for stl_file in stl_files:
        print(f"读取: {stl_file.name}...", end='')
        try:
            info = read_stl_z_range(stl_file)
            info['filename'] = stl_file.name
            layers_info.append(info)
            print(f" ✅ (Z: [{info['min']:.2f}, {info['max']:.2f}]m)")
        except Exception as e:
            print(f" ❌ 错误: {e}")
    
    if not layers_info:
        print("\n未能读取任何STL文件")
        return
    
    # 按最小Z值排序(从底到顶)
    layers_info.sort(key=lambda x: x['min'])
    
    # 输出详细表格
    print(f"\n{'='*80}")
    print(f"层序详细信息(按底面Z排序)")
    print(f"{'='*80}")
    print(f"{'序号':>4} {'文件名':^30} {'Z最小':>10} {'Z最大':>10} {'Z跨度':>10} {'三角形数':>10}")
    print(f"{'-'*80}")
    
    for i, info in enumerate(layers_info):
        z_span = info['max'] - info['min']
        print(f"{i+1:>4} {info['filename']:^30} {info['min']:>10.2f} {info['max']:>10.2f} {z_span:>10.2f} {info['num_triangles']:>10}")
    
    # 检查层间重叠
    print(f"\n{'='*80}")
    print(f"层间重叠检查")
    print(f"{'='*80}")
    print(f"{'层对':^40} {'下层顶面':>12} {'上层底面':>12} {'间隙/重叠':>12} {'状态':^10}")
    print(f"{'-'*80}")
    
    total_overlap = 0
    overlap_layers = []
    
    for i in range(len(layers_info) - 1):
        lower = layers_info[i]
        upper = layers_info[i + 1]
        
        lower_top = lower['max']
        upper_bottom = upper['min']
        gap = upper_bottom - lower_top
        
        layer_pair = f"{lower['filename'][:15]} → {upper['filename'][:15]}"
        
        if gap < 0:
            status = "❌ 重叠"
            total_overlap += 1
            overlap_layers.append((lower['filename'], upper['filename'], -gap))
        elif gap < 0.1:
            status = "⚠️ 过近"
        else:
            status = "✅ 正常"
        
        print(f"{layer_pair:^40} {lower_top:>12.2f} {upper_bottom:>12.2f} {gap:>12.2f} {status:^10}")
    
    # 总结
    print(f"\n{'='*80}")
    print(f"检查总结")
    print(f"{'='*80}")
    
    if total_overlap == 0:
        print(f"✅ 检查通过: 所有相邻层无重叠")
    else:
        print(f"❌ 检查失败: 发现 {total_overlap} 对相邻层存在重叠")
        print(f"\n重叠详情:")
        for lower_name, upper_name, overlap in overlap_layers:
            print(f"  • {lower_name} 与 {upper_name}: 重叠 {overlap:.2f}m")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        stl_dir = sys.argv[1]
    else:
        # 默认检查最近的导出目录
        import os
        # 查找最新的_temp_stl_export目录
        possible_dirs = [
            r"E:\xiangmu\xitong\output\_temp_stl_export",
            r"E:\xiangmu\xitong\backend\_temp_stl_export",
            "."
        ]
        
        stl_dir = None
        for d in possible_dirs:
            if os.path.exists(d):
                stl_dir = d
                break
        
        if stl_dir is None:
            print("请指定STL文件目录:")
            print("  python diagnose_layer_overlap.py <stl_directory>")
            sys.exit(1)
    
    check_layer_overlap(stl_dir)
