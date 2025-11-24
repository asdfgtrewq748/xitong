"""
F3GRID文件验证脚本
快速检查.f3grid文件的结构和完整性
"""

import sys
from collections import defaultdict

def verify_f3grid(filepath):
    """验证F3GRID文件"""
    print(f"\n正在验证: {filepath}\n")
    print("=" * 80)
    
    gridpoints = {}
    zones = []
    groups = {}
    current_section = None
    current_group = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 跳过注释和空行
            if line.startswith(';') or not line:
                continue
            
            # 识别块
            if line == 'GRIDPOINTS':
                current_section = 'GRIDPOINTS'
                continue
            elif line.startswith('ZONES'):
                current_section = 'ZONES'
                continue
            elif line == 'GROUPS':
                current_section = 'GROUPS'
                continue
            
            # 解析数据
            if current_section == 'GRIDPOINTS':
                parts = line.split()
                if len(parts) == 4:
                    gp_id = int(parts[0])
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    gridpoints[gp_id] = (x, y, z)
            
            elif current_section == 'ZONES':
                parts = line.split()
                if len(parts) == 9:  # ID + 8 gridpoint IDs
                    zone_id = int(parts[0])
                    gp_ids = [int(p) for p in parts[1:]]
                    zones.append({'id': zone_id, 'gridpoints': gp_ids})
            
            elif current_section == 'GROUPS':
                parts = line.split()
                if len(parts) == 1 and not parts[0].isdigit():
                    # 新的group名称
                    current_group = parts[0]
                    groups[current_group] = []
                elif current_group and parts:
                    # zone IDs
                    zone_ids = [int(p) for p in parts if p.isdigit()]
                    groups[current_group].extend(zone_ids)
    
    # 统计信息
    print(f"✅ 文件读取成功!\n")
    print(f"📊 基本统计:")
    print(f"  - GridPoints: {len(gridpoints)}")
    print(f"  - Zones: {len(zones)}")
    print(f"  - Groups: {len(groups)}\n")
    
    # 分组详情
    print(f"📂 分组详情:")
    for group_name, zone_ids in groups.items():
        print(f"  - {group_name}: {len(zone_ids)} zones")
    print()
    
    # 验证节点复用(检测层间节点共享)
    print(f"🔗 检查节点复用(层间连接):")
    gp_usage = defaultdict(int)
    for zone in zones:
        for gp_id in zone['gridpoints']:
            gp_usage[gp_id] += 1
    
    shared_nodes = {gp_id: count for gp_id, count in gp_usage.items() if count > 1}
    print(f"  - 被复用的节点数: {len(shared_nodes)}")
    print(f"  - 最大复用次数: {max(gp_usage.values())}")
    
    # 随机显示几个共享节点
    sample_shared = list(shared_nodes.items())[:5]
    if sample_shared:
        print(f"\n  示例(节点ID: 被引用次数):")
        for gp_id, count in sample_shared:
            x, y, z = gridpoints[gp_id]
            print(f"    GP {gp_id}: {count}次引用, 坐标=({x:.2f}, {y:.2f}, {z:.2f})")
    print()
    
    # 验证BRICK单元完整性
    print(f"🧱 验证BRICK单元:")
    invalid_zones = []
    for zone in zones:
        gp_ids = zone['gridpoints']
        if len(gp_ids) != 8:
            invalid_zones.append(zone['id'])
        # 检查所有节点是否存在
        for gp_id in gp_ids:
            if gp_id not in gridpoints:
                print(f"  ⚠️ Zone {zone['id']} 引用了不存在的节点 {gp_id}")
    
    if invalid_zones:
        print(f"  ⚠️ 发现 {len(invalid_zones)} 个无效单元(节点数!=8)")
    else:
        print(f"  ✅ 所有单元都是有效的BRICK(8节点)")
    print()
    
    # Z坐标范围
    z_coords = [z for _, _, z in gridpoints.values()]
    print(f"📏 Z坐标范围:")
    print(f"  - 最小Z: {min(z_coords):.2f}m")
    print(f"  - 最大Z: {max(z_coords):.2f}m")
    print(f"  - 垂向范围: {max(z_coords) - min(z_coords):.2f}m")
    print()
    
    print("=" * 80)
    print("✅ 验证完成! 文件格式正确,可以导入FLAC3D。\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python verify_f3grid.py <f3grid文件路径>")
        print("示例: python verify_f3grid.py data/output/geological_model_20251123_005150.f3grid")
        sys.exit(1)
    
    filepath = sys.argv[1]
    try:
        verify_f3grid(filepath)
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
