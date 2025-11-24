# backend/z_section_slicer.py
"""
Z轴剖面切片功能 - 从3D地质模型中提取水平剖面
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from coal_seam_blocks.modeling import BlockModel


def extract_z_section(
    block_models: List[BlockModel],
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    z_coordinate: float,
    sampling_step: int = 3
) -> Dict:
    """
    根据指定 z 坐标提取水平剖面
    
    Args:
        block_models: BlockModel 列表 (从底到顶排序)
        grid_x: X 轴网格坐标 (1D 数组)
        grid_y: Y 轴网格坐标 (1D 数组)
        z_coordinate: 剖面的 z 坐标值
        sampling_step: 采样步长 (默认3,即每3个点采样1个,减少数据量)
        
    Returns:
        包含剖面数据的字典:
        {
            'z_coordinate': float,
            'x_coords': List[float],  # 网格展开后的 x 坐标
            'y_coords': List[float],  # 网格展开后的 y 坐标
            'lithology': List[str],   # 每个点的岩性名称
            'lithology_index': List[int],  # 岩性索引 (用于着色)
            'z_values': List[float],  # 实际 z 值 (用于验证)
            'legend': List[Dict],  # 图例信息
            'z_range': Tuple[float, float]  # 模型的 z 范围
        }
    """
    if not block_models:
        raise ValueError("block_models 为空")
    
    if len(grid_x) == 0 or len(grid_y) == 0:
        raise ValueError("grid_x 或 grid_y 为空")
    
    # 应用降采样减少数据量
    if sampling_step > 1:
        grid_x_sampled = grid_x[::sampling_step]
        grid_y_sampled = grid_y[::sampling_step]
        print(f"[Z剖面] 降采样: {len(grid_x)}x{len(grid_y)} -> {len(grid_x_sampled)}x{len(grid_y_sampled)} (步长={sampling_step})")
    else:
        grid_x_sampled = grid_x
        grid_y_sampled = grid_y
    
    # 创建网格
    XI, YI = np.meshgrid(grid_x_sampled, grid_y_sampled)
    ny, nx = XI.shape
    
    # 展平坐标
    x_flat = XI.flatten()
    y_flat = YI.flatten()
    total_points = len(x_flat)
    
    # 初始化结果数组
    lithology_names = np.full(total_points, "", dtype=object)
    lithology_indices = np.full(total_points, -1, dtype=int)
    z_values = np.full(total_points, np.nan, dtype=float)
    
    # 计算模型的 z 范围
    all_tops = np.concatenate([bm.top_surface.flatten() for bm in block_models])
    all_bottoms = np.concatenate([bm.bottom_surface.flatten() for bm in block_models])
    z_min = float(np.nanmin(all_bottoms))
    z_max = float(np.nanmax(all_tops))
    
    print(f"\n[Z剖面] 提取 z={z_coordinate} 的剖面")
    print(f"[Z剖面] 模型范围: z_min={z_min:.2f}, z_max={z_max:.2f}")
    print(f"[Z剖面] 网格尺寸: {ny} x {nx} = {total_points} 点")
    
    # 检查 z_coordinate 是否在合理范围内
    if z_coordinate < z_min or z_coordinate > z_max:
        print(f"⚠️ [Z剖面] 警告: z={z_coordinate} 超出模型范围 [{z_min:.2f}, {z_max:.2f}]")
    
    # 为每个网格点确定所在岩层
    # 从下到上遍历岩层,找到包含 z_coordinate 的岩层
    for layer_idx, model in enumerate(block_models):
        # 对模型表面数据也进行降采样
        if sampling_step > 1:
            # model.top_surface 和 model.bottom_surface 是 2D 数组 (ny_orig, nx_orig)
            top_sampled = model.top_surface[::sampling_step, ::sampling_step]
            bottom_sampled = model.bottom_surface[::sampling_step, ::sampling_step]
        else:
            top_sampled = model.top_surface
            bottom_sampled = model.bottom_surface
        
        top_flat = top_sampled.flatten()
        bottom_flat = bottom_sampled.flatten()
        
        # 确保尺寸匹配
        if len(top_flat) != total_points:
            print(f"⚠️ [Z剖面] 尺寸不匹配: top_flat={len(top_flat)}, total_points={total_points}")
            continue
        
        # 找到 z_coordinate 位于该岩层内的点
        # bottom <= z_coordinate < top
        mask = (bottom_flat <= z_coordinate) & (z_coordinate < top_flat)
        
        # 标记这些点的岩性
        lithology_names[mask] = model.name
        lithology_indices[mask] = layer_idx
        z_values[mask] = z_coordinate
        
        n_hits = np.sum(mask)
        if n_hits > 0:
            print(f"[Z剖面] 岩层 '{model.name}' (索引={layer_idx}): {n_hits} 点")
    
    # 统计未分配岩性的点
    unassigned_mask = lithology_indices == -1
    n_unassigned = np.sum(unassigned_mask)
    
    if n_unassigned > 0:
        # 对于未分配的点,标记为"无数据"
        lithology_names[unassigned_mask] = "无数据"
        lithology_indices[unassigned_mask] = len(block_models)  # 使用特殊索引
        print(f"[Z剖面] 未分配岩性: {n_unassigned} 点 (可能在模型外)")
    
    # 构建图例
    legend = []
    unique_layers = {}
    
    for idx, model in enumerate(block_models):
        if np.any(lithology_indices == idx):
            unique_layers[idx] = model.name
            legend.append({
                'index': idx,
                'name': model.name,
                'color': _get_layer_color(model.name, idx)
            })
    
    # 添加"无数据"图例
    if n_unassigned > 0:
        legend.append({
            'index': len(block_models),
            'name': '无数据',
            'color': '#CCCCCC'
        })
    
    print(f"[Z剖面] 图例包含 {len(legend)} 种岩性")
    
    return {
        'z_coordinate': float(z_coordinate),
        'x_coords': x_flat.tolist(),
        'y_coords': y_flat.tolist(),
        'lithology': lithology_names.tolist(),
        'lithology_index': lithology_indices.tolist(),
        'z_values': z_values.tolist(),
        'legend': legend,
        'z_range': (z_min, z_max),
        'grid_shape': (int(ny), int(nx))
    }


def get_z_range_from_models(block_models: List[BlockModel]) -> Tuple[float, float]:
    """
    获取模型的 z 范围
    
    Args:
        block_models: BlockModel 列表
        
    Returns:
        (z_min, z_max)
    """
    if not block_models:
        return (0.0, 0.0)
    
    all_tops = np.concatenate([bm.top_surface.flatten() for bm in block_models])
    all_bottoms = np.concatenate([bm.bottom_surface.flatten() for bm in block_models])
    
    z_min = float(np.nanmin(all_bottoms))
    z_max = float(np.nanmax(all_tops))
    
    return (z_min, z_max)


def _get_layer_color(layer_name: str, layer_index: int) -> str:
    """
    根据岩层名称和索引返回颜色
    
    优先根据岩性关键词匹配颜色,否则使用索引循环
    """
    name_lower = layer_name.lower()
    
    # 煤层 - 黑色系
    if '煤' in layer_name or 'coal' in name_lower:
        return '#1a1a1a'
    
    # 砂岩 - 黄色系
    if '砂' in layer_name or 'sand' in name_lower:
        return '#f4a460'
    
    # 泥岩 - 棕色系
    if '泥' in layer_name or 'mud' in name_lower or '页' in layer_name:
        return '#8b7355'
    
    # 灰岩 - 灰色系
    if '灰' in layer_name or 'lime' in name_lower:
        return '#a9a9a9'
    
    # 粉砂 - 浅黄色
    if '粉' in layer_name or 'silt' in name_lower:
        return '#deb887'
    
    # 页岩 - 深棕色
    if '页' in layer_name or 'shale' in name_lower:
        return '#654321'
    
    # 默认调色板 (使用索引循环)
    default_palette = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#546570'
    ]
    
    return default_palette[layer_index % len(default_palette)]
