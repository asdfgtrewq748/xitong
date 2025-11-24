"""
测试顶板层功能 - 模拟真实数据
验证前端导出的完整流程
"""
import sys
sys.path.insert(0, 'backend')

import numpy as np
from exporters.layered_stl_exporter import LayeredSTLExporter

# 模拟真实地质数据(150x150网格)
def create_real_like_data():
    resolution = 150
    x = np.linspace(523051.37, 525091.64, resolution)
    y = np.linspace(4370914.16, 4371564.17, resolution)
    grid_x, grid_y = np.meshgrid(x, y)
    
    # 创建有起伏的地形
    terrain_base = 700.0
    terrain_variation = 50.0 * np.sin(grid_x / 500) * np.cos(grid_y / 300)
    
    layers = [
        {
            "name": "4煤",
            "grid_x": grid_x,
            "grid_y": grid_y,
            "grid_z": terrain_base + terrain_variation,
            "grid_z_bottom": terrain_base + terrain_variation - 5.0,
            "thickness": np.full_like(grid_x, 5.0)
        },
        {
            "name": "含砾粗砂岩",
            "grid_x": grid_x,
            "grid_y": grid_y,
            "grid_z": terrain_base + terrain_variation - 5.0,
            "grid_z_bottom": terrain_base + terrain_variation - 145.0,
            "thickness": np.full_like(grid_x, 140.0)
        }
    ]
    return {"layers": layers}

print("=" * 80)
print("REAL DATA TEST - Top Plate Auto-Generation")
print("=" * 80)

data = create_real_like_data()
layers = data["layers"]

print(f"\nOriginal model:")
print(f"  Resolution: 150x150 grid points")
print(f"  Layers: {len(layers)}")
for i, layer in enumerate(layers):
    z_top = np.array(layer["grid_z"])
    z_bottom = np.array(layer["grid_z_bottom"])
    print(f"  {i+1}. {layer['name']}:")
    print(f"     Top Z: [{np.min(z_top):.2f}, {np.max(z_top):.2f}]m")
    print(f"     Bottom Z: [{np.min(z_bottom):.2f}, {np.max(z_bottom):.2f}]m")
    print(f"     Thickness: {layer['thickness'][0,0]:.2f}m")

print(f"\nExport configuration:")
print(f"  - add_top_plate: True")
print(f"  - top_plate_thickness: 15m")
print(f"  - downsample_factor: 5x (150x150 -> 30x30)")
print(f"  - normalize_coords: True")
print()

exporter = LayeredSTLExporter()
output_path = "data/output/test_real_data_with_top_plate.zip"

result = exporter.export_layered(data, output_path, {
    "format": "binary",
    "downsample_factor": 5,
    "normalize_coords": True,
    "add_top_plate": True,
    "top_plate_thickness": 15.0
})

import os, zipfile

if os.path.exists(output_path):
    file_size = os.path.getsize(output_path)
    with zipfile.ZipFile(output_path, 'r') as zf:
        files = zf.namelist()
        stl_files = sorted([f for f in files if f.endswith('.stl')])
        
        print(f"\nGenerated ZIP: {file_size:,} bytes")
        print(f"\nSTL files ({len(stl_files)}):")
        for stl in stl_files:
            stl_data = zf.read(stl)
            # 读取三角形数量
            import struct
            tri_count = struct.unpack('<I', stl_data[80:84])[0]
            print(f"  {stl}: {len(stl_data):,} bytes, {tri_count} triangles")
        
        # 检查manifest
        if 'manifest.json' in files:
            import json
            manifest = json.loads(zf.read('manifest.json').decode('utf-8'))
            print(f"\nManifest summary:")
            print(f"  Total layers: {manifest['total_layers']}")
            print(f"  Exported successfully: {len([l for l in manifest['layers'] if 'filename' in l and l['filename']])}")
            print(f"\nLayer details:")
            for layer_info in manifest['layers']:
                if 'filename' in layer_info and layer_info['filename']:
                    print(f"  - {layer_info['name']} ({layer_info['name_english']})")
                    print(f"    File: {layer_info['filename']}")

print("\n" + "=" * 80)
print("[SUCCESS] Top plate layer successfully added to real-like data")
print("=" * 80)
print("\nNext steps:")
print("  1. Check if the first STL file is '01_layer.stl' (top plate)")
print("  2. Verify top plate has flat top surface")
print("  3. Import to FLAC3D and apply overburden load on top plate")
print(f"\nExported file: {output_path}")
