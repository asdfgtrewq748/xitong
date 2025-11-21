import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.ndimage import gaussian_filter


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
    
    # ⚠️ 关键修复: NaN/Inf不能转0,会导致厚度为0!
    # 用厚度数据的中位数填充
    invalid_mask = ~np.isfinite(values)
    if np.any(invalid_mask):
        fill_value = float(np.median(thickness)) if len(thickness) > 0 else 1.0
        values = np.where(np.isfinite(values), values, fill_value)
    
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
        
        # 🔍 诊断日志
        print(f"    [建模] {seam_name}: {num_valid}个有效厚度采样点")
        if num_valid > 0:
            print(f"           厚度范围: [{np.min(thickness_points):.2f}, {np.max(thickness_points):.2f}]m")
            print(f"           平均厚度: {np.mean(thickness_points):.2f}m")
            print(f"           中位数厚度: {np.median(thickness_points):.2f}m")
        
        # ⚠️ 最小点数要求提高到3,避免插值外推产生极端值
        if num_valid < 3:
            skipped.append(f"{seam_name} (有效点太少: {num_valid} < 3)")
            print(f"    [警告] {seam_name} 采样点不足3个,跳过建模")
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

            # ⚠️ 关键修复：厚度NaN不能转成0，会导致层间重叠！
            # 原因：厚度=0 → 顶面=底面 → 与下一层重合
            # 解决：用该层的平均厚度或最小有效厚度填充
            nan_count = np.isnan(thickness_grid).sum()
            if nan_count > 0:
                valid_thickness = thickness_grid[~np.isnan(thickness_grid)]
                if len(valid_thickness) > 0:
                    # 使用中位数填充（比平均值更稳健）
                    fill_value = float(np.median(valid_thickness))
                    # 确保填充值不小于最小有效厚度的一半
                    min_thickness = max(0.5, float(np.min(valid_thickness)) * 0.5)
                    fill_value = max(fill_value, min_thickness)
                else:
                    # 如果没有有效值，使用经验最小厚度
                    fill_value = 1.0  # 默认1米
                
                thickness_grid = np.nan_to_num(thickness_grid, nan=fill_value)
                print(f"    [建模] {seam_name}: {nan_count}个位置厚度缺失，用{fill_value:.2f}m填充")
            
            # ⚠️ 处理Inf和负值 - 不能转为0！转为NaN后用median填充
            inf_count = np.sum(np.isinf(thickness_grid)) + np.sum(thickness_grid < 0)
            if inf_count > 0:
                # 将Inf和负值标记为NaN
                thickness_grid = np.where(
                    np.isfinite(thickness_grid) & (thickness_grid >= 0),
                    thickness_grid,
                    np.nan
                )
                # 用中位数填充
                valid_thickness = thickness_grid[~np.isnan(thickness_grid)]
                if len(valid_thickness) > 0:
                    fill_value_inf = float(np.median(valid_thickness))
                else:
                    fill_value_inf = 1.0
                thickness_grid = np.nan_to_num(thickness_grid, nan=fill_value_inf)
                print(f"    [建模] {seam_name}: {inf_count}个无效值(Inf/负值)用{fill_value_inf:.2f}m填充")
            
            # 确保非负
            thickness_grid = np.clip(thickness_grid, 0.0, None)

            # 🔧 厚度变化限制: 防止网格扭曲
            # 如果厚度max/min > 2.0,会导致侧壁网格严重扭曲和边缘相交
            thickness_min_val = float(np.min(thickness_grid[thickness_grid > 0]))
            thickness_max_val = float(np.max(thickness_grid))
            thickness_avg = float(np.mean(thickness_grid[thickness_grid > 0]))
            thickness_ratio = thickness_max_val / thickness_min_val if thickness_min_val > 0 else 1.0
            
            if thickness_ratio > 2.0:
                print(f"    [警告] {seam_name} 厚度变化过大!")
                print(f"           厚度范围: [{thickness_min_val:.2f}, {thickness_max_val:.2f}]m")
                print(f"           变化比值: {thickness_ratio:.2f} (推荐 < 2.0)")
                print(f"           平均厚度: {thickness_avg:.2f}m")
                
                # 策略: 使用高斯平滑减少极端值,而非硬性截断
                # 保存原始范围
                original_range = thickness_max_val - thickness_min_val
                
                # 应用温和的高斯平滑 (sigma=1.0)
                thickness_grid_smoothed = gaussian_filter(thickness_grid, sigma=1.0, mode='nearest')
                
                # 如果平滑后比值仍>2.0,才使用软性限制
                new_min = float(np.min(thickness_grid_smoothed[thickness_grid_smoothed > 0]))
                new_max = float(np.max(thickness_grid_smoothed))
                new_ratio = new_max / new_min if new_min > 0 else 1.0
                
                if new_ratio > 2.0:
                    # 软性限制: 只裁剪极端5%的异常值
                    percentile_5 = np.percentile(thickness_grid_smoothed, 5)
                    percentile_95 = np.percentile(thickness_grid_smoothed, 95)
                    thickness_grid_smoothed = np.clip(thickness_grid_smoothed, percentile_5, percentile_95)
                    
                    new_min = float(np.min(thickness_grid_smoothed[thickness_grid_smoothed > 0]))
                    new_max = float(np.max(thickness_grid_smoothed))
                    new_ratio = new_max / new_min
                
                print(f"           → 平滑后: [{new_min:.2f}, {new_max:.2f}]m, 比值 {new_ratio:.2f}")
                thickness_grid = thickness_grid_smoothed

            bottom_surface = current_base_surface.copy()
            
            # 🔧 预防性检查: 底面起伏过大时,预先增加最小厚度
            bottom_min = float(np.min(bottom_surface))
            bottom_max = float(np.max(bottom_surface))
            bottom_range = bottom_max - bottom_min
            
            # 如果底面起伏 > 20m,预防性地增加最小厚度
            if bottom_range > 20.0:
                # 确保最小厚度至少是底面起伏的1.1倍 + 2m安全余量
                preventive_min_thickness = bottom_range * 1.1 + 2.0
                thickness_min_original = float(np.min(thickness_grid))
                
                if thickness_min_original < preventive_min_thickness:
                    print(f"    [预防] {seam_name} 底面起伏很大({bottom_range:.2f}m)")
                    print(f"           预防性增加最小厚度: {thickness_min_original:.2f}m → {preventive_min_thickness:.2f}m")
                    thickness_grid = np.maximum(thickness_grid, preventive_min_thickness)
            
            top_surface = bottom_surface + thickness_grid
            
            # 🔧 关键修复: 检查并修复自身交错
            # 问题: 如果 top_min < bottom_max,顶面和底面在空间上会交错
            top_min = float(np.min(top_surface))
            top_max = float(np.max(top_surface))
            
            if top_min < bottom_max:
                # 计算需要的最小厚度保证 top_min >= bottom_max
                # 使用更大的安全余量: max(2m, 底面起伏的5%)
                safety_margin = max(2.0, bottom_range * 0.05)
                required_min_thickness = bottom_max - bottom_min + safety_margin
                
                print(f"    [警告] {seam_name} 检测到自身交错风险!")
                print(f"           顶面范围: [{top_min:.2f}, {top_max:.2f}]m")
                print(f"           底面范围: [{bottom_min:.2f}, {bottom_max:.2f}]m")
                print(f"           问题: 顶面最小值({top_min:.2f}m) < 底面最大值({bottom_max:.2f}m)")
                print(f"           差值: {bottom_max - top_min:.2f}m")
                print(f"    [修复] 将所有厚度增加到最小 {required_min_thickness:.2f}m (安全余量: {safety_margin:.2f}m)")
                
                # 方案: 确保每个位置的厚度至少等于 (底面最大值 - 底面最小值 + 安全余量)
                # 这样即使底面起伏很大,顶面也能完全覆盖底面
                thickness_grid = np.maximum(thickness_grid, required_min_thickness)
                top_surface = bottom_surface + thickness_grid
                
                # 验证修复
                new_top_min = float(np.min(top_surface))
                new_top_max = float(np.max(top_surface))
                print(f"    [验证] 修复后顶面: [{new_top_min:.2f}, {new_top_max:.2f}]m")
                print(f"           修复后厚度: [{np.min(thickness_grid):.2f}, {np.max(thickness_grid):.2f}]m")
                
                if new_top_min >= bottom_max:
                    margin_achieved = new_top_min - bottom_max
                    print(f"    [OK] 自身交错已修复 ✅ (实际余量: {margin_achieved:.2f}m)")
                else:
                    print(f"    [失败] 修复无效! ❌")
                    print(f"           仍有差值: {bottom_max - new_top_min:.2f}m")
                    # 强制修复: 使用更激进的策略
                    required_min_thickness = bottom_max - bottom_min + 5.0  # 强制5m余量
                    print(f"    [强制] 使用激进修复: 最小厚度 {required_min_thickness:.2f}m")
                    thickness_grid = np.maximum(thickness_grid, required_min_thickness)
                    top_surface = bottom_surface + thickness_grid
                    final_top_min = float(np.min(top_surface))
                    if final_top_min >= bottom_max:
                        print(f"    [OK] 强制修复成功 ✅")
                    else:
                        print(f"    [错误] 强制修复仍失败,数据可能有严重问题 ⚠️")
            
            # 最终验证并记录
            final_top_min = float(np.min(top_surface))
            final_top_max = float(np.max(top_surface))
            final_bottom_min = float(np.min(bottom_surface))
            final_bottom_max = float(np.max(bottom_surface))
            final_thickness_min = float(np.min(thickness_grid))
            final_thickness_max = float(np.max(thickness_grid))
            
            print(f"    [最终] {seam_name} 建模完成")
            print(f"           底面: [{final_bottom_min:.2f}, {final_bottom_max:.2f}]m (极差: {final_bottom_max - final_bottom_min:.2f}m)")
            print(f"           厚度: [{final_thickness_min:.2f}, {final_thickness_max:.2f}]m (极差: {final_thickness_max - final_thickness_min:.2f}m)")
            print(f"           顶面: [{final_top_min:.2f}, {final_top_max:.2f}]m (极差: {final_top_max - final_top_min:.2f}m)")
            
            # 最终安全检查
            if final_top_min < final_bottom_max:
                print(f"    ⚠️⚠️⚠️  严重警告: 仍存在交错! 差值: {final_bottom_max - final_top_min:.2f}m")
            else:
                safety_gap = final_top_min - final_bottom_max
                print(f"           ✅ 安全间隙: {safety_gap:.2f}m")
            
            block_models.append(BlockModel(
                name=str(seam_name),
                points=num_valid,
                top_surface=top_surface,
                bottom_surface=bottom_surface
            ))

            current_base_surface = top_surface
            if gap_value:
                current_base_surface = current_base_surface + float(gap_value)
                print(f"           [层间] 添加间隙 {float(gap_value):.2f}m,下一层底面将从 {np.mean(current_base_surface):.2f}m 开始")
        
        except Exception as e:
            skipped.append(f"{seam_name} (插值失败: {str(e)[:30]}, {num_valid}个点)")
            continue

    if not block_models:
        raise RuntimeError("选定的岩层数据不足以生成模型")

    return block_models, skipped, (XI, YI)
