try:
    import ezdxf
except ImportError:
    ezdxf = None

import numpy as np
from typing import Any, Dict, List, Optional
from .base_exporter import BaseExporter

class DXFExporter(BaseExporter):
    """
    导出地质模型为 DXF 格式 (SketchUp/CAD)
    """
    
    def export(self, data: Dict[str, Any], output_path: str, options: Optional[Dict[str, Any]] = None) -> str:
        if ezdxf is None:
            raise ImportError("ezdxf library is not installed. Please install it to use DXF export feature.")
            
        """
        导出 DXF 文件
        
        Args:
            data: 包含地层数据的字典，格式如下:
                  {
                      "layers": [
                          {
                              "name": "LayerName",
                              "grid_x": np.ndarray, # 2D array
                              "grid_y": np.ndarray, # 2D array
                              "grid_z": np.ndarray  # 2D array
                          },
                          ...
                      ]
                  }
            output_path: 输出文件路径 (.dxf)
            options: 导出选项
            
        Returns:
            str: 导出文件的路径
        """
        doc = ezdxf.new()
        msp = doc.modelspace()
        
        layers = data.get("layers", [])
        
        for layer_data in layers:
            layer_name = layer_data.get("name", "Default")
            # 替换非法字符
            safe_layer_name = "".join(c for c in layer_name if c.isalnum() or c in "_- ")
            
            grid_x = layer_data.get("grid_x")
            grid_y = layer_data.get("grid_y")
            grid_z = layer_data.get("grid_z")
            
            if grid_x is None or grid_y is None or grid_z is None:
                continue
                
            # 确保图层存在
            if safe_layer_name not in doc.layers:
                doc.layers.add(name=safe_layer_name)
            
            # 确保是 numpy 数组
            grid_x = np.array(grid_x)
            grid_y = np.array(grid_y)
            grid_z = np.array(grid_z)
            
            if grid_z.ndim != 2:
                # 如果不是2D数组，尝试reshape或者跳过
                # 这里假设输入已经是网格化的数据
                continue

            rows, cols = grid_z.shape
            
            # 如果 grid_x/y 是 1D，扩展为 2D
            if grid_x.ndim == 1 and grid_y.ndim == 1:
                 grid_x, grid_y = np.meshgrid(grid_x, grid_y)
            
            # 生成 3DFACE
            for r in range(rows - 1):
                for c in range(cols - 1):
                    # 获取四个顶点的坐标
                    try:
                        p1 = (float(grid_x[r, c]), float(grid_y[r, c]), float(grid_z[r, c]))
                        p2 = (float(grid_x[r, c+1]), float(grid_y[r, c+1]), float(grid_z[r, c+1]))
                        p3 = (float(grid_x[r+1, c+1]), float(grid_y[r+1, c+1]), float(grid_z[r+1, c+1]))
                        p4 = (float(grid_x[r+1, c]), float(grid_y[r+1, c]), float(grid_z[r+1, c]))
                        
                        # 检查是否有 NaN
                        if any(np.isnan(val) for p in [p1, p2, p3, p4] for val in p):
                            continue
                            
                        msp.add_3dface([p1, p2, p3, p4], dxfattribs={'layer': safe_layer_name})
                    except IndexError:
                        continue
                    except Exception as e:
                        print(f"Error creating face at {r},{c}: {e}")
                        continue
                        
        doc.saveas(output_path)
        return output_path
