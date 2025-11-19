import numpy as np
from typing import Any, Dict, List, Optional
from .base_exporter import BaseExporter

class FLAC3DExporter(BaseExporter):
    """
    导出地质模型为 FLAC3D 格式 (.f3grid)
    """
    
    def export(self, data: Dict[str, Any], output_path: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        导出 FLAC3D 网格文件
        
        Args:
            data: 包含地层数据的字典，格式如下:
                  {
                      "layers": [
                          {
                              "name": "LayerName",
                              "grid_x": np.ndarray,
                              "grid_y": np.ndarray,
                              "grid_z": np.ndarray,       # 顶板
                              "grid_z_bottom": np.ndarray # 底板 (可选，如果没有则尝试用 thickness)
                              "thickness": np.ndarray     # 厚度 (可选)
                          },
                          ...
                      ]
                  }
            output_path: 输出文件路径
            options: 导出选项
            
        Returns:
            str: 导出文件的路径
        """
        layers = data.get("layers", [])
        if not layers:
            return output_path
            
        # 收集所有节点和单元
        nodes = [] # (id, x, y, z)
        zones = [] # (type, id, [node_indices], group_name)
        
        node_map = {} # (x, y, z) -> node_id
        next_node_id = 1
        next_zone_id = 1
        
        for layer in layers:
            layer_name = layer.get("name", "Default")
            # 替换非法字符
            safe_layer_name = "".join(c for c in layer_name if c.isalnum() or c in "_-")
            
            grid_x = layer.get("grid_x")
            grid_y = layer.get("grid_y")
            grid_z_top = layer.get("grid_z")
            
            if grid_x is None or grid_y is None or grid_z_top is None:
                continue
                
            grid_x = np.array(grid_x)
            grid_y = np.array(grid_y)
            grid_z_top = np.array(grid_z_top)
            
            if grid_x.ndim == 1 and grid_y.ndim == 1:
                 grid_x, grid_y = np.meshgrid(grid_x, grid_y)
            
            grid_z_bottom = layer.get("grid_z_bottom")
            if grid_z_bottom is None:
                thickness = layer.get("thickness")
                if thickness is not None:
                    thickness = np.array(thickness)
                    grid_z_bottom = grid_z_top - thickness
                else:
                    # 无法生成体单元
                    continue
            else:
                grid_z_bottom = np.array(grid_z_bottom)
            
            rows, cols = grid_z_top.shape
            
            for r in range(rows - 1):
                for c in range(cols - 1):
                    # 8个顶点
                    # Top: (r,c), (r,c+1), (r+1,c+1), (r+1,c)
                    # Bottom: 同上
                    
                    indices = [
                        (r, c), (r, c+1), (r+1, c+1), (r+1, c)
                    ]
                    
                    cell_nodes = []
                    valid_cell = True
                    
                    # FLAC3D B8 顺序: 
                    # Bottom: 1, 2, 3, 4 (counter-clockwise looking from top)
                    # Top: 5, 6, 7, 8 (above 1, 2, 3, 4)
                    
                    # 先底面
                    for rr, cc in indices:
                        try:
                            x = float(grid_x[rr, cc])
                            y = float(grid_y[rr, cc])
                            z = float(grid_z_bottom[rr, cc])
                            if np.isnan(z) or np.isnan(x) or np.isnan(y): 
                                valid_cell = False; break
                            
                            # 简单的坐标 key，保留4位小数以合并节点
                            key = (round(x, 4), round(y, 4), round(z, 4))
                            if key not in node_map:
                                node_map[key] = next_node_id
                                nodes.append((next_node_id, x, y, z))
                                next_node_id += 1
                            cell_nodes.append(node_map[key])
                        except IndexError:
                            valid_cell = False; break
                        
                    if not valid_cell: continue
                        
                    # 后顶面
                    for rr, cc in indices:
                        try:
                            x = float(grid_x[rr, cc])
                            y = float(grid_y[rr, cc])
                            z = float(grid_z_top[rr, cc])
                            if np.isnan(z) or np.isnan(x) or np.isnan(y): 
                                valid_cell = False; break
                            
                            key = (round(x, 4), round(y, 4), round(z, 4))
                            if key not in node_map:
                                node_map[key] = next_node_id
                                nodes.append((next_node_id, x, y, z))
                                next_node_id += 1
                            cell_nodes.append(node_map[key])
                        except IndexError:
                            valid_cell = False; break
                        
                    if not valid_cell: continue
                    
                    zones.append(('B8', next_zone_id, cell_nodes, safe_layer_name))
                    next_zone_id += 1

        # 计算几何中心并归一化坐标
        if nodes:
            nodes_array = np.array([(n[1], n[2], n[3]) for n in nodes])
            centroid = np.mean(nodes_array, axis=0)
            print(f"Model Centroid: {centroid}")
        else:
            centroid = np.array([0.0, 0.0, 0.0])

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("* FLAC3D Grid Data Generated by System\n")
            f.write(f"* Original Center (Offset): X={centroid[0]:.4f}, Y={centroid[1]:.4f}, Z={centroid[2]:.4f}\n")
            f.write("* Nodes\n")
            for nid, x, y, z in nodes:
                # 减去中心坐标
                nx = x - centroid[0]
                ny = y - centroid[1]
                nz = z - centroid[2]
                f.write(f"G P {nid} {nx:.4f} {ny:.4f} {nz:.4f}\n")
            
            f.write("* Zones\n")
            for ztype, zid, nids, group in zones:
                # B8 is Z B8
                nids_str = " ".join(map(str, nids))
                f.write(f"Z {ztype} {zid} {nids_str}\n")
                
            f.write("* Groups\n")
            # 整理 Group
            groups = {}
            for ztype, zid, nids, group in zones:
                if group not in groups:
                    groups[group] = []
                groups[group].append(zid)
                
            for gname, zids in groups.items():
                f.write(f"Z GROUP \"{gname}\" SLOT 1 \n")
                # 分块写入 ID，每行最多20个ID
                chunk_size = 20
                for i in range(0, len(zids), chunk_size):
                    chunk = zids[i:i+chunk_size]
                    f.write("  " + " ".join(map(str, chunk)) + "\n")

        return output_path
