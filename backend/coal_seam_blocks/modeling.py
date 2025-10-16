import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


class BlockModel:
    def __init__(self,
                 name: str,
                 points: int,
                 top_surface: np.ndarray,
                 bottom_surface: np.ndarray):
        self.name = name
        self.points = points
        self.top_surface = np.asarray(top_surface, dtype=float)
        self.bottom_surface = np.asarray(bottom_surface, dtype=float)

        # 计算厚度网格及统计信息
        thickness = self.top_surface - self.bottom_surface
        thickness = np.clip(thickness, 0.0, None)
        self.thickness_grid = thickness

        def _safe_stat(func, array, default=0.0):
            try:
                value = func(array)
                if np.isfinite(value):
                    return float(value)
            except ValueError:
                pass
            return float(default)

        self.avg_thickness = _safe_stat(np.nanmean, thickness)
        self.max_thickness = _safe_stat(np.nanmax, thickness)
        self.avg_height = _safe_stat(np.nanmean, self.top_surface)
        self.max_height = _safe_stat(np.nanmax, self.top_surface)
        self.min_height = _safe_stat(np.nanmin, self.top_surface)
        self.avg_bottom = _safe_stat(np.nanmean, self.bottom_surface)
        self.min_bottom = _safe_stat(np.nanmin, self.bottom_surface)
        # 兼容早期版本仍读取 base 属性的场景
        self.base = self.avg_bottom


def build_grids(x_values: np.ndarray, y_values: np.ndarray, resolution: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    xi = np.linspace(x_values.min(), x_values.max(), resolution)
    yi = np.linspace(y_values.min(), y_values.max(), resolution)
    XI, YI = np.meshgrid(xi, yi)
    xi_flat = XI.flatten()
    yi_flat = YI.flatten()
    return XI, YI, xi_flat, yi_flat


def interpolate_seam(x_points: np.ndarray, y_points: np.ndarray, thickness: np.ndarray,
                      xi: np.ndarray, yi: np.ndarray, method_callable) -> np.ndarray:
    values = method_callable(x_points, y_points, thickness, xi, yi)
    values = values.reshape((int(np.sqrt(len(xi))), int(np.sqrt(len(xi)))))
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(values, 0.0, None)


def build_block_models(merged_df: pd.DataFrame,
                       seam_column: str,
                       x_col: str,
                       y_col: str,
                       thickness_col: str,
                       selected_seams: List[str],
                       method_callable,
                       resolution: int,
                       base_level: float,
                       gap_value: float) -> Tuple[List[BlockModel], List[str], Tuple[np.ndarray, np.ndarray]]:
    if merged_df.empty:
        raise ValueError("合并数据为空，无法建模")

    required_cols = [x_col, y_col, thickness_col, seam_column]
    valid_data = merged_df.dropna(subset=required_cols).copy()
    if len(valid_data) < 8:
        raise ValueError("生成块体至少需要8个有效数据点")

    valid_data[seam_column] = valid_data[seam_column].astype(str)
    x_vals = valid_data[x_col].astype(float)
    y_vals = valid_data[y_col].astype(float)

    if x_vals.nunique() < 2 or y_vals.nunique() < 2:
        raise ValueError("X 或 Y 坐标取值过少，无法构建网格")

    XI, YI, xi_flat, yi_flat = build_grids(x_vals.values, y_vals.values, resolution)

    block_models: List[BlockModel] = []
    skipped: List[str] = []
    current_base_surface = np.full((XI.shape[0], XI.shape[1]), float(base_level), dtype=float)

    for seam_name in selected_seams:
        seam_df = valid_data[valid_data[seam_column] == str(seam_name)]
        if seam_df.empty:
            skipped.append(f"{seam_name} (无数据点)")
            continue
        
        # 降低最小点数要求: 1个点也可以建模(使用最近邻插值)
        num_points = len(seam_df)
        if num_points < 1:
            skipped.append(f"{seam_name} (有效点 0)")
            continue

        x_points = seam_df[x_col].astype(float).values
        y_points = seam_df[y_col].astype(float).values
        thickness_points = pd.to_numeric(seam_df[thickness_col], errors='coerce').values
        
        # 过滤掉NaN值
        valid_mask = ~np.isnan(thickness_points)
        if not np.any(valid_mask):
            skipped.append(f"{seam_name} (厚度数据全部无效)")
            continue
        
        x_points = x_points[valid_mask]
        y_points = y_points[valid_mask]
        thickness_points = thickness_points[valid_mask]
        num_valid = len(thickness_points)
        
        if num_valid < 1:
            skipped.append(f"{seam_name} (有效点 0)")
            continue

        try:
            interpolated = method_callable(x_points, y_points, thickness_points, xi_flat, yi_flat)
            if interpolated is None:
                skipped.append(f"{seam_name} (插值无结果, {num_valid}个点)")
                continue

            thickness_grid = interpolated.reshape(XI.shape)
            thickness_grid = np.asarray(thickness_grid, dtype=float)
            if not np.isfinite(thickness_grid).any():
                skipped.append(f"{seam_name} (插值结果全为无效值, {num_valid}个点)")
                continue

            thickness_grid = np.nan_to_num(thickness_grid, nan=0.0, posinf=0.0, neginf=0.0)
            thickness_grid = np.clip(thickness_grid, 0.0, None)

            bottom_surface = current_base_surface.copy()
            top_surface = bottom_surface + thickness_grid
            block_models.append(BlockModel(
                name=str(seam_name),
                points=num_valid,
                top_surface=top_surface,
                bottom_surface=bottom_surface
            ))

            current_base_surface = top_surface
            if gap_value:
                current_base_surface = current_base_surface + float(gap_value)
        
        except Exception as e:
            skipped.append(f"{seam_name} (插值失败: {str(e)[:30]}, {num_valid}个点)")
            continue

    if not block_models:
        raise RuntimeError("选定的岩层数据不足以生成模型")

    return block_models, skipped, (XI, YI)
