"""
测试新的流形网格生成算法

验证:
1. 顶点去重是否生效
2. 非流形边是否为0
3. 与旧算法对比三角形数量
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import struct
import numpy as np
from collections import defaultdict
from exporters.stl_exporter import STLExporter

def analyze_stl_manifold(filepath):
    """分析STL文件的流形性"""
    with open(filepath, 'rb') as f:
        f.read(80)  # header
        triangle_count = struct.unpack('<I', f.read(4))[0]
        
        edges = defaultdict(int)
        for i in range(triangle_count):
            f.read(12)  # normal
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))
            f.read(2)  # attribute
            
            edge1 = tuple(sorted([v1, v2]))
            edge2 = tuple(sorted([v2, v3]))
            edge3 = tuple(sorted([v3, v1]))
            edges[edge1] += 1
            edges[edge2] += 1
            edges[edge3] += 1
        
        # 统计边的共享情况
        edge_stats = defaultdict(int)
        for count in edges.values():
            edge_stats[count] += 1
        
        non_manifold = sum(cnt for share_count, cnt in edge_stats.items() if share_count != 2)
        
        return {
            'triangle_count': triangle_count,
            'edge_stats': dict(edge_stats),
            'non_manifold_edges': non_manifold,
            'is_manifold': non_manifold == 0
        }

def test_single_layer_export():
    """测试单层导出"""
    print("=" * 60)
    print("测试流形网格生成算法")
    print("=" * 60)
    
    # 创建简单的测试数据
    resolution = 10
    x = np.linspace(0, 100, resolution)
    y = np.linspace(0, 100, resolution)
    grid_x, grid_y = np.meshgrid(x, y)
    
    # 顶面: 平面在z=10
    grid_z_top = np.full_like(grid_x, 10.0)
    
    # 底面: 平面在z=0
    grid_z_bottom = np.zeros_like(grid_x)
    
    # 构造数据
    test_data = {
        "layers": [{
            "name": "测试层",
            "grid_x": grid_x,
            "grid_y": grid_y,
            "top_surface_z": grid_z_top,
            "bottom_surface_z": grid_z_bottom
        }]
    }
    
    # 导出STL
    exporter = STLExporter()
    output_path = "test_manifold_output.stl"
    
    print(f"\n测试参数:")
    print(f"  网格分辨率: {resolution}x{resolution}")
    print(f"  预期网格单元: {(resolution-1) * (resolution-1)}")
    print(f"  预期三角形(理论): {(resolution-1) * (resolution-1) * 12}")
    
    exporter.export(test_data, output_path, {
        "downsample_factor": 1,  # 不降采样
        "normalize_coords": False
    })
    
    # 分析生成的STL
    print(f"\n分析生成的STL文件...")
    result = analyze_stl_manifold(output_path)
    
    print(f"\n结果:")
    print(f"  三角形数量: {result['triangle_count']}")
    print(f"  边统计:")
    for share_count in sorted(result['edge_stats'].keys()):
        print(f"    被{share_count}个三角形共享的边: {result['edge_stats'][share_count]}")
    print(f"  非流形边: {result['non_manifold_edges']}")
    print(f"  是否流形: {'✓ 是' if result['is_manifold'] else '✗ 否'}")
    
    # 清理
    if os.path.exists(output_path):
        os.remove(output_path)
    
    return result['is_manifold']

def compare_old_new_exports():
    """对比新旧导出结果"""
    print("\n" + "=" * 60)
    print("对比新旧导出文件")
    print("=" * 60)
    
    old_file = r"e:\xiangmu\xitong\FLAC\geological_model_20251122_004539\01_coal_6.stl"
    new_file = r"e:\xiangmu\xitong\FLAC\geological_model_20251122_131001\01_coal_6.stl"
    
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        print("找不到对比文件,跳过对比")
        return
    
    print(f"\n旧导出 (成功): {os.path.basename(os.path.dirname(old_file))}")
    old_result = analyze_stl_manifold(old_file)
    print(f"  三角形: {old_result['triangle_count']}")
    print(f"  非流形边: {old_result['non_manifold_edges']} ({old_result['non_manifold_edges']/sum(old_result['edge_stats'].values())*100:.1f}%)")
    
    print(f"\n新导出 (失败): {os.path.basename(os.path.dirname(new_file))}")
    new_result = analyze_stl_manifold(new_file)
    print(f"  三角形: {new_result['triangle_count']}")
    print(f"  非流形边: {new_result['non_manifold_edges']} ({new_result['non_manifold_edges']/sum(new_result['edge_stats'].values())*100:.1f}%)")
    
    print(f"\n对比:")
    print(f"  三角形增加: {new_result['triangle_count']/old_result['triangle_count']:.2f}x")
    print(f"  非流形边增加: {new_result['non_manifold_edges']/max(old_result['non_manifold_edges'],1):.2f}x")

if __name__ == "__main__":
    # 测试新算法
    success = test_single_layer_export()
    
    # 对比旧导出
    compare_old_new_exports()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 测试通过: 新算法生成流形网格!")
        print("\n下一步: 使用前端重新导出STL,然后在FLAC3D中验证")
    else:
        print("✗ 测试失败: 仍存在非流形边")
    print("=" * 60)
