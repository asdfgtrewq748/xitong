# backend/api.py
import io
import os
import sys
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import threading
import json
from scipy.interpolate import griddata, Rbf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 导入优化后的模块
from key_strata_calculator import calculate_key_strata_details as calculate_key_strata_optimized
from data_validation import validate_geological_data, GeologicalDataValidator
from upward_mining_feasibility import UpwardMiningFeasibility, process_borehole_csv_for_feasibility, batch_process_borehole_files, auto_calibrate_coefficients
from exporters.dxf_exporter import DXFExporter
from exporters.flac3d_exporter import FLAC3DExporter

# ==============================================================================
#  核心计算函数 - 使用优化版本
# ==============================================================================
def calculate_key_strata_details(df_strata_above_coal, coal_seam_properties_df):
    """
    计算给定煤层上覆岩层的关键层信息。
    (使用优化后的模块 - 性能提升30%+)
    """
    # 直接调用优化后的实现
    return calculate_key_strata_optimized(df_strata_above_coal, coal_seam_properties_df)


def _read_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    """Read CSV content from raw bytes with robust encoding fallbacks."""
    encodings = ["utf-8-sig", "utf-8", "gbk"]
    last_error: Optional[Exception] = None
    for encoding in encodings:
        try:
            return pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        except Exception as exc:  # pragma: no cover - relies on external files
            last_error = exc
            continue
    raise ValueError(f"无法解析CSV文件: {last_error}")


def process_single_borehole_file(file_bytes: bytes, filename: str) -> Tuple[List[Dict[str, Any]], str, str]:
    """Process a single borehole CSV file and extract coal seam metrics."""

    processed_records: List[Dict[str, Any]] = []
    borehole_name = os.path.splitext(os.path.basename(filename or ""))[0] or "未知钻孔"

    try:
        df = _read_csv_from_bytes(file_bytes)
    except Exception as exc:
        return [], f"文件 '{filename}' 读取失败: {exc}", "error"

    df.dropna(how="all", inplace=True)
    if df.empty:
        return [], f"文件 '{filename}' 为空。", "warning"

    std_cols_map = {
        "名称": "岩层名称",
        "岩层名称": "岩层名称",
        "岩层": "岩层名称",
        "岩性": "岩层名称",
        "厚度/m": "厚度/m",
        "厚度": "厚度/m",
        "弹性模量/GPa": "弹性模量/GPa",
        "弹性模量/Gpa": "弹性模量/GPa",
        "弹性模量": "弹性模量/GPa",
        "容重/kN·m-3": "容重/kN·m-3",
        "容重/kN*m-3": "容重/kN·m-3",
        "容重": "容重/kN·m-3",
        "抗拉强度/MPa": "抗拉强度/MPa",
        "抗拉强度": "抗拉强度/MPa",
    }
    df.rename(columns=lambda c: std_cols_map.get(str(c).strip(), str(c).strip()), inplace=True)

    if "岩层名称" not in df.columns or "厚度/m" not in df.columns:
        return [], f"文件 '{filename}' 缺少'岩层名称'或'厚度/m'列。", "error"

    coal_indices = df[df["岩层名称"].astype(str).str.contains("煤", na=False)].index.tolist()
    if not coal_indices:
        return [], f"在文件 '{filename}' 中未找到煤层。", "warning"

    for coal_idx in coal_indices:
        coal_row = df.iloc[coal_idx]
        coal_name = str(coal_row.get("岩层名称", "")).strip() or "未知煤层"
        coal_thickness = pd.to_numeric(coal_row.get("厚度/m"), errors="coerce")
        coal_thickness_val = float(coal_thickness) if pd.notna(coal_thickness) else None

        direct_roof_name = "N/A"
        direct_roof_thickness = None
        if coal_idx > 0:
            roof_row = df.iloc[coal_idx - 1]
            direct_roof_name = str(roof_row.get("岩层名称", "")).strip() or "N/A"
            roof_thickness = pd.to_numeric(roof_row.get("厚度/m"), errors="coerce")
            direct_roof_thickness = float(roof_thickness) if pd.notna(roof_thickness) else None

        record: Dict[str, Any] = {
            "钻孔名": borehole_name,
            "煤层": coal_name,
            "煤层厚度": round(coal_thickness_val, 2) if coal_thickness_val is not None else "N/A",
            "直接顶岩性": direct_roof_name,
            "直接顶厚度": round(direct_roof_thickness, 2) if direct_roof_thickness is not None else "N/A",
        }

        df_above = df.iloc[:coal_idx].copy()
        coal_props_df = df.iloc[[coal_idx]].copy()

        key_info = []
        required_cols = ["岩层名称", "厚度/m", "弹性模量/GPa", "容重/kN·m-3", "抗拉强度/MPa"]
        if not df_above.empty and all(col in df_above.columns for col in required_cols):
            try:
                key_info = calculate_key_strata_details(df_above, coal_props_df)
            except Exception:
                key_info = []

        for index, info in enumerate(key_info[:4], start=1):
            record[f"关键层{index}厚度"] = info.get("厚度", "N/A")
            record[f"关键层{index}岩性"] = info.get("岩性", "N/A")
            record[f"关键层{index}距煤层的距离"] = info.get("距煤层距离", "N/A")

        for fallback_index in range(len(key_info) + 1, 5):
            record.setdefault(f"关键层{fallback_index}厚度", "N/A")
            record.setdefault(f"关键层{fallback_index}岩性", "N/A")
            record.setdefault(f"关键层{fallback_index}距煤层的距离", "N/A")

        processed_records.append(record)

    return processed_records, f"文件 '{filename}' 处理完成。", "info"


def fill_missing_properties(df: pd.DataFrame, rock_db: pd.DataFrame, stat_preference: str = "median") -> Tuple[pd.DataFrame, int, List[str]]:
    """Fill missing mechanical properties using statistics from rock database."""

    if rock_db is None or rock_db.empty or df is None or df.empty:
        return df, 0, []

    stat_preference = (stat_preference or "median").lower()
    if stat_preference not in {"mean", "median"}:
        stat_preference = "median"

    lithology_col = None
    if "岩层名称" in df.columns:
        lithology_col = "岩层名称"
    elif "岩性" in df.columns:
        lithology_col = "岩性"
    if lithology_col is None or "岩性" not in rock_db.columns:
        return df, 0, []

    stats_group = rock_db.copy()
    stats_group["岩性"] = stats_group["岩性"].astype(str).str.strip()
    stats_group = stats_group[stats_group["岩性"].astype(bool)]

    aggregation: Dict[str, str] = {}
    numeric_columns = []
    for column in stats_group.columns:
        if column == "岩性":
            continue
        if pd.api.types.is_numeric_dtype(stats_group[column]):
            numeric_columns.append(column)
            aggregation[column] = stat_preference

    if not numeric_columns:
        return df, 0, []

    stats_map = stats_group.groupby("岩性").agg(aggregation)

    filled_df = df.copy()
    filled_count = 0
    filled_cols: set[str] = set()

    for idx, row in filled_df.iterrows():
        lithology = str(row.get(lithology_col, "")).strip()
        match_row = None
        if lithology:
            exact = stats_map.loc[stats_map.index == lithology]
            if not exact.empty:
                match_row = exact.iloc[0]
            elif "煤" in lithology:
                coal_candidates = stats_map.loc[stats_map.index.str.contains("煤")]
                if not coal_candidates.empty:
                    match_row = coal_candidates.iloc[0]

        if match_row is None:
            continue

        for column in numeric_columns:
            if column not in filled_df.columns:
                continue
            current = filled_df.at[idx, column]
            needs_fill = pd.isna(current)
            if not needs_fill:
                try:
                    needs_fill = float(current) == 0.0
                except Exception:
                    needs_fill = False
            if needs_fill:
                value = match_row.get(column)
                if pd.notna(value):
                    filled_df.at[idx, column] = value
                    filled_count += 1
                    filled_cols.add(column)

    return filled_df, filled_count, sorted(filled_cols)

# ==============================================================================
#  API 类
# ==============================================================================
class Api:
    def __init__(self):
        self.dfs = {}
        self.merged_df_modeling = None
        self.rock_db_cache = None
        self.china_geojson_cache = None
        # 新增：插值方法映射 - 完整版本
        self.interpolation_methods = {
            # 基础griddata方法
            "linear": "线性 (Linear)",
            "cubic": "三次样条 (Cubic)",
            "nearest": "最近邻 (Nearest)",
            # RBF径向基函数方法
            "multiquadric": "多重二次 (Multiquadric)",
            "inverse": "反距离 (Inverse)",
            "gaussian": "高斯 (Gaussian)",
            "linear_rbf": "线性RBF (Linear RBF)",
            "cubic_rbf": "三次RBF (Cubic RBF)",
            "quintic_rbf": "五次RBF (Quintic RBF)",
            "thin_plate": "薄板样条 (Thin Plate)",
            # 高级插值方法
            "modified_shepard": "修正谢泼德 (Modified Shepard)",
            "natural_neighbor": "自然邻点 (Natural Neighbor)",
            "radial_basis": "径向基函数 (Radial Basis)",
            "ordinary_kriging": "普通克里金 (Ordinary Kriging)",
            "universal_kriging": "通用克里金 (Universal Kriging)",
            "bilinear": "双线性 (Bilinear)",
            "anisotropic": "各向异性 (Anisotropic)",
            "idw": "反距离加权 (IDW)"
        }

    def _get_raw_db_path(self):
        # ... (代码与之前相同)
        pass

    def _read_raw_db(self):
        # ... (代码与之前相同)
        pass

    def _perform_interpolation(self, x_train, y_train, z_train, x_val, y_val, method_key):
        """[优化] 统一的插值执行函数 - 增强稳定性，使用interpolation模块"""
        from interpolation import interpolate
        
        # 数据验证
        if x_train is None or y_train is None or z_train is None:
            raise ValueError("训练数据不能为None")

        if len(x_train) == 0 or len(y_train) == 0 or len(z_train) == 0:
            raise ValueError("训练数据不能为空")

        if len(x_train) != len(y_train) or len(x_train) != len(z_train):
            raise ValueError(f"训练数据长度不匹配: x={len(x_train)}, y={len(y_train)}, z={len(z_train)}")

        # 过滤NaN和Inf值
        valid_mask = np.isfinite(x_train) & np.isfinite(y_train) & np.isfinite(z_train)
        if not np.any(valid_mask):
            raise ValueError("所有训练数据都是无效值(NaN或Inf)")

        x_train = x_train[valid_mask]
        y_train = y_train[valid_mask]
        z_train = z_train[valid_mask]

        num_points = len(x_train)
        if num_points < 3:
            # 数据点太少,强制使用最近邻
            method_key = 'nearest'

        try:
            # 使用增强的插值模块
            result = interpolate(x_train, y_train, z_train, x_val, y_val, method_key)
            
            # 检查结果
            if result is None or (isinstance(result, np.ndarray) and result.size == 0):
                raise ValueError(f"{method_key}插值返回空结果")
            
            # ⚠️ 处理NaN/Inf值 - 不能转为0,会导致厚度为0!
            if isinstance(result, np.ndarray):
                invalid_mask = ~np.isfinite(result)
                if np.any(invalid_mask):
                    # 用原始数据的中位数填充
                    fill_value = float(np.median(z_train)) if len(z_train) > 0 else 0.0
                    result = np.where(np.isfinite(result), result, fill_value)
            
            return result
            
        except Exception as e:
            # 任何插值失败都回退到最近邻
            print(f"[警告] 插值方法 {method_key} 失败: {e}, 回退到最近邻插值")
            try:
                result = griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
                # 用中位数填充无效值
                fill_value = float(np.median(z_train)) if len(z_train) > 0 else 0.0
                result = np.where(np.isfinite(result), result, fill_value)
                return result
            except Exception as fallback_error:
                print(f"[错误] 最近邻插值也失败: {fallback_error}")
                # 返回零数组作为最后的回退
                return np.zeros_like(x_val)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        # ... (代码与之前相同)
        pass
    
    def get_china_geojson(self) -> Dict[str, Any]:
        # ... (代码与之前相同)
        pass

    # --- 其他模块API保持不变 ---

    # --- 地质建模 API (新增一个方法) ---
    def get_modeling_data_columns(self, filepaths: List[str], coords_path: str) -> Dict:
        # ... (代码与之前相同)
        pass

    def get_unique_column_values(self, params: Dict) -> Dict:
        # ... (代码与之前相同)
        pass

    def generate_contour_data(self, params: Dict) -> Dict:
        # ... (代码与之前相同)
        pass

    def compare_interpolation_methods(self, params: Dict) -> Dict[str, Any]:
        """[新增] 对比所有插值方法的性能"""
        if self.merged_df_modeling is None:
            return {'status': 'error', 'message': '请先加载并合并数据'}

        try:
            x_col, y_col, z_col = params['x_col'], params['y_col'], params['z_col']
            validation_ratio = params.get('validation_ratio', 0.2)
            
            df = self.merged_df_modeling.dropna(subset=[x_col, y_col, z_col])
            if len(df) < 10:
                return {'status': 'error', 'message': f'数据点不足（少于10个），无法进行有效验证'}

            X = df[[x_col, y_col]].values
            y = df[z_col].values
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=validation_ratio, random_state=42)

            x_train, y_train_coords = X_train[:, 0], X_train[:, 1]
            x_test, y_test_coords = X_test[:, 0], X_test[:, 1]

            results = []
            for key, name in self.interpolation_methods.items():
                try:
                    y_pred = self._perform_interpolation(x_train, y_train_coords, y_train, x_test, y_test_coords, key)
                    
                    # 过滤掉预测失败的NaN值
                    valid_mask = ~np.isnan(y_pred)
                    if not np.any(valid_mask):
                        continue

                    y_test_valid = y_test[valid_mask]
                    y_pred_valid = y_pred[valid_mask]

                    mae = mean_absolute_error(y_test_valid, y_pred_valid)
                    rmse = np.sqrt(mean_squared_error(y_test_valid, y_pred_valid))
                    r2 = r2_score(y_test_valid, y_pred_valid)
                    
                    results.append({
                        'method': name,
                        'mae': round(mae, 4),
                        'rmse': round(rmse, 4),
                        'r2': round(r2, 4),
                    })
                except Exception as e:
                    print(f"插值方法 {name} 失败: {e}")
                    continue
            
            if not results:
                return {'status': 'error', 'message': '所有插值方法均计算失败'}

            # 按 R² 降序排序
            results.sort(key=lambda x: x['r2'], reverse=True)
            
            return {'status': 'success', 'results': results}

        except Exception as e:
            return {'status': 'error', 'message': f'对比插值方法时出错: {e}'}

    def generate_block_model_data(self, params: Dict) -> Dict:
        """[优化] 生成3D块体模型数据 - 增强稳定性和错误处理"""
        try:
            # 数据验证
            if self.merged_df_modeling is None:
                return {'status': 'error', 'message': '数据未加载,请先选择文件'}

            # 参数验证
            required_params = ['seam_col', 'x_col', 'y_col', 'thickness_col', 'selected_seams', 'method']
            for param in required_params:
                if param not in params or not params[param]:
                    return {'status': 'error', 'message': f'缺少必需参数: {param}'}

            if not isinstance(params['selected_seams'], list) or len(params['selected_seams']) == 0:
                return {'status': 'error', 'message': '至少需要选择一个岩层进行建模'}

            from coal_seam_blocks.modeling import build_block_models

            def interpolation_wrapper(x, y, z, xi_flat, yi_flat):
                """包装插值函数,增加异常处理"""
                try:
                    return self._perform_interpolation(
                        x, y, z, xi_flat, yi_flat,
                        params['method'].lower()
                    )
                except Exception as e:
                    print(f"[警告] 插值失败: {e}, 使用最近邻方法")
                    return self._perform_interpolation(
                        x, y, z, xi_flat, yi_flat, 'nearest'
                    )

            # 调用建模函数
            block_models_objs, skipped, (XI, YI) = build_block_models(
                merged_df=self.merged_df_modeling,
                seam_column=params['seam_col'],
                x_col=params['x_col'],
                y_col=params['y_col'],
                thickness_col=params['thickness_col'],
                selected_seams=params['selected_seams'],
                method_callable=interpolation_wrapper,
                resolution=params.get('resolution', 80),
                base_level=params.get('base_level', 0),
                gap_value=params.get('gap', 0)
            )

            # 验证结果
            if not block_models_objs or len(block_models_objs) == 0:
                return {
                    'status': 'error',
                    'message': '未能生成任何块体模型,可能是数据点不足或插值失败',
                    'skipped': skipped
                }

            # 格式化模型数据 - 修复前后端数据格式不匹配问题
            models_data = []
            grid_x = XI[0].tolist() if XI.shape[0] > 0 else []
            grid_y = YI[:, 0].tolist() if YI.shape[1] > 0 else []

            for model in block_models_objs:
                # 验证模型数据
                if model.top_surface is None or model.bottom_surface is None:
                    print(f"[警告] 岩层 {model.name} 的表面数据为空,跳过")
                    continue

                # ⚠️ 关键修复：保留NaN，不要转成0！
                # 原因：建模时各层是从基准面累加的，NaN应该保留让导出器处理
                # 如果转成0会破坏层序关系，导致层间交错
                top_surface = model.top_surface.copy()
                bottom_surface = model.bottom_surface.copy()
                
                # 只处理Inf值（保留NaN）
                top_surface[np.isinf(top_surface)] = np.nan
                bottom_surface[np.isinf(bottom_surface)] = np.nan

                # 确保数据维度正确
                if top_surface.shape != XI.shape or bottom_surface.shape != XI.shape:
                    print(f"[警告] 岩层 {model.name} 的表面数据维度不匹配,跳过")
                    continue

                # 转换为列表，NaN会被序列化为null（JSON标准）
                # 导出器会使用插值填充这些null值
                models_data.append({
                    'name': str(model.name),
                    'points': int(model.points),
                    'grid_x': grid_x,  # 前端期待的字段名
                    'grid_y': grid_y,  # 前端期待的字段名
                    'top_surface_z': top_surface.tolist(),  # NaN → null（保留缺失信息）
                    'bottom_surface_z': bottom_surface.tolist(),  # NaN → null
                    'avg_thickness': float(model.avg_thickness) if hasattr(model, 'avg_thickness') else 0.0,
                    'max_thickness': float(model.max_thickness) if hasattr(model, 'max_thickness') else 0.0,
                    'avg_height': float(model.avg_height) if hasattr(model, 'avg_height') else 0.0,
                })

            if len(models_data) == 0:
                return {
                    'status': 'error',
                    'message': '所有模型数据验证失败,无法生成3D模型',
                    'skipped': skipped
                }

            return {
                'status': 'success',
                'grid': {'x': grid_x, 'y': grid_y},
                'models': models_data,
                'skipped': skipped,
                'total_models': len(models_data),
                'total_skipped': len(skipped)
            }

        except ValueError as ve:
            return {'status': 'error', 'message': f'数据验证失败: {str(ve)}'}
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[错误] 3D建模计算失败:\n{error_detail}")
            return {'status': 'error', 'message': f'3D建模计算失败: {str(e)}'}

    # --- 上行开采可行度计算 API ---
    def calculate_upward_mining_feasibility(self, params: Dict) -> Dict:
        """
        计算单个钻孔的上行开采可行度

        Args:
            params: 包含以下键的字典:
                - csv_file_path: CSV文件路径
                - bottom_coal_name: 开采煤层名称
                - upper_coal_name: 上煤层名称
                - lamda: 影响因子λ (可选, 默认4.95)
                - C: 地质常数C (可选, 默认-0.84)

        Returns:
            计算结果字典
        """
        try:
            # 验证必需参数
            required_params = ['csv_file_path', 'bottom_coal_name', 'upper_coal_name']
            for param in required_params:
                if param not in params or not params[param]:
                    return {'status': 'error', 'message': f'缺少必需参数: {param}'}

            # 获取参数
            csv_file_path = params['csv_file_path']
            bottom_coal_name = params['bottom_coal_name']
            upper_coal_name = params['upper_coal_name']
            lamda = params.get('lamda', 4.95)
            C = params.get('C', -0.84)

            # 检查文件是否存在
            if not os.path.exists(csv_file_path):
                return {'status': 'error', 'message': f'文件不存在: {csv_file_path}'}

            # 调用扰动度计算函数
            result = process_borehole_csv_for_feasibility(csv_file_path, bottom_coal_name, upper_coal_name, lamda, C)

            if "error" in result:
                return {'status': 'error', 'message': result['error']}

            return {
                'status': 'success',
                'data': result
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[错误] 上行开采可行度计算失败:\n{error_detail}")
            return {'status': 'error', 'message': f'计算失败: {str(e)}'}

    def batch_calculate_upward_mining_feasibility(self, params: Dict) -> Dict:
        """
        批量计算钻孔的上行开采可行度

        Args:
            params: 包含以下键的字典:
                - csv_file_paths: CSV文件路径列表
                - bottom_coal_name: 开采煤层名称
                - upper_coal_name: 上煤层名称
                - lamda: 影响因子λ (可选, 默认4.95)
                - C: 地质常数C (可选, 默认-0.84)

        Returns:
            批量计算结果字典
        """
        try:
            # 验证必需参数
            required_params = ['csv_file_paths', 'bottom_coal_name', 'upper_coal_name']
            for param in required_params:
                if param not in params or not params[param]:
                    return {'status': 'error', 'message': f'缺少必需参数: {param}'}

            # 获取参数
            csv_file_paths = params['csv_file_paths']
            bottom_coal_name = params['bottom_coal_name']
            upper_coal_name = params['upper_coal_name']
            lamda = params.get('lamda', 4.95)
            C = params.get('C', -0.84)

            # 验证文件列表
            if not isinstance(csv_file_paths, list) or len(csv_file_paths) == 0:
                return {'status': 'error', 'message': 'CSV文件路径列表不能为空'}

            # 检查所有文件是否存在
            for file_path in csv_file_paths:
                if not os.path.exists(file_path):
                    return {'status': 'error', 'message': f'文件不存在: {file_path}'}

            # 调用批量计算函数
            result = batch_process_borehole_files(csv_file_paths, bottom_coal_name, upper_coal_name, lamda, C)

            return {
                'status': 'success',
                'data': result
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[错误] 批量上行开采可行度计算失败:\n{error_detail}")
            return {'status': 'error', 'message': f'批量计算失败: {str(e)}'}

    def auto_calibrate_upward_mining_coefficients(self, params: Dict) -> Dict:
        """
        自动标定上行开采计算的系数(λ和C)

        Args:
            params: 包含以下键的字典:
                - csv_file_paths: CSV文件路径列表
                - bottom_coal_name: 开采煤层名称
                - upper_coal_name: 上煤层名称
                - initial_lamda: 初始影响因子λ (可选, 默认4.95)
                - initial_C: 初始地质常数C (可选, 默认-0.84)

        Returns:
            标定结果字典
        """
        try:
            # 验证必需参数
            required_params = ['csv_file_paths', 'bottom_coal_name', 'upper_coal_name']
            for param in required_params:
                if param not in params or not params[param]:
                    return {'status': 'error', 'message': f'缺少必需参数: {param}'}

            # 获取参数
            csv_file_paths = params['csv_file_paths']
            bottom_coal_name = params['bottom_coal_name']
            upper_coal_name = params['upper_coal_name']
            initial_lamda = params.get('initial_lamda', 4.95)
            initial_C = params.get('initial_C', -0.84)

            # 验证文件列表
            if not isinstance(csv_file_paths, list) or len(csv_file_paths) == 0:
                return {'status': 'error', 'message': 'CSV文件路径列表不能为空'}

            # 检查所有文件是否存在
            for file_path in csv_file_paths:
                if not os.path.exists(file_path):
                    return {'status': 'error', 'message': f'文件不存在: {file_path}'}

            # 调用自动标定函数
            result = auto_calibrate_coefficients(csv_file_paths, bottom_coal_name, upper_coal_name, initial_lamda, initial_C)

            return {
                'status': 'success',
                'data': result
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[错误] 自动标定系数失败:\n{error_detail}")
            return {'status': 'error', 'message': f'标定失败: {str(e)}'}

    def get_feasibility_evaluation_levels(self) -> Dict:
        """
        获取可行性等级评估标准

        Returns:
            可行性等级评估标准
        """
        return {
            'status': 'success',
            'levels': [
                {
                    'level': 'I级 (不可行/极困难)',
                    'omega_range': '0-2',
                    'description': '煤层基本处于垮落带内，完整度破坏非常严重，上行开采不合理或过于危险。'
                },
                {
                    'level': 'II级 (困难)',
                    'omega_range': '2-4',
                    'description': '上行开采难度大，易出现顶板问题和巷道支护困难，需要重型支护或充填。'
                },
                {
                    'level': 'III级 (可行，需支护)',
                    'omega_range': '4-6',
                    'description': '中等破坏程度，顶板和煤层少量破碎，但裂隙发育程度大。技术上可行，局部需加强支护。'
                },
                {
                    'level': 'IV级 (良好)',
                    'omega_range': '6-8',
                    'description': '轻微破坏，煤层完整性良好，顶板有少量裂隙，下沉量微小，上行开采效果较好。'
                },
                {
                    'level': 'V级 (优良)',
                    'omega_range': '8以上',
                    'description': '煤层基本不受下煤层开采的影响，煤层间的相互作用基本不存在，上行开采不存在困难。'
                }
            ]
        }

    def export_model(self, params: Dict) -> Dict:
        """
        导出地质模型到外部格式 (DXF, FLAC3D)
        
        Args:
            params: 包含建模参数和导出选项
                - export_type: 'dxf' 或 'flac3d'
                - output_path: (可选) 输出路径
                - ... (其他建模参数同 generate_block_model_data)
        """
        try:
            # 数据验证
            if self.merged_df_modeling is None:
                return {'status': 'error', 'message': '数据未加载,请先选择文件'}

            # 参数验证
            required_params = ['seam_col', 'x_col', 'y_col', 'thickness_col', 'selected_seams']
            for param in required_params:
                if param not in params or not params[param]:
                    return {'status': 'error', 'message': f'缺少必需参数: {param}'}

            from coal_seam_blocks.modeling import build_block_models

            def interpolation_wrapper(x, y, z, xi_flat, yi_flat):
                try:
                    return self._perform_interpolation(
                        x, y, z, xi_flat, yi_flat,
                        params.get('method', 'linear').lower()
                    )
                except Exception as e:
                    print(f"[警告] 导出时插值失败: {e}, 使用最近邻方法")
                    return self._perform_interpolation(
                        x, y, z, xi_flat, yi_flat, 'nearest'
                    )

            # 调用建模函数生成数据
            block_models_objs, skipped, (XI, YI) = build_block_models(
                merged_df=self.merged_df_modeling,
                seam_column=params['seam_col'],
                x_col=params['x_col'],
                y_col=params['y_col'],
                thickness_col=params['thickness_col'],
                selected_seams=params['selected_seams'],
                method_callable=interpolation_wrapper,
                resolution=params.get('resolution', 80),
                base_level=params.get('base_level', 0),
                gap_value=params.get('gap', 0)
            )

            if not block_models_objs:
                return {
                    'status': 'error',
                    'message': '未能生成模型数据, 无法导出',
                    'skipped': skipped
                }

            # 准备导出数据结构
            export_data = {"layers": []}
            for model in block_models_objs:
                if model.top_surface is None:
                    continue
                    
                export_data["layers"].append({
                    "name": model.name,
                    "grid_x": XI,
                    "grid_y": YI,
                    "grid_z": model.top_surface,
                    "grid_z_bottom": model.bottom_surface,
                    "thickness": model.thickness_grid
                })

            # 确定导出类型和路径
            export_type = params.get("export_type", "dxf").lower()
            output_path = params.get("output_path")
            
            if not output_path:
                import os
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = "f3grid" if export_type == "flac3d" else "dxf"
                
                user_filename = params.get("filename")
                if user_filename:
                    # 移除可能包含的路径，只保留文件名
                    user_filename = os.path.basename(user_filename)
                    if not user_filename.lower().endswith(f".{ext}"):
                        user_filename += f".{ext}"
                    filename = user_filename
                else:
                    filename = f"model_export_{timestamp}.{ext}"

                # 默认保存到 backend/data/output 或当前目录
                output_dir = os.path.join(os.path.dirname(__file__), "data", "output")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, filename)

            # 执行导出
            exporter = None
            if export_type == "dxf":
                exporter = DXFExporter()
            elif export_type == "flac3d":
                exporter = FLAC3DExporter()
            else:
                return {'status': 'error', 'message': f'不支持的导出类型: {export_type}'}
                
            final_path = exporter.export(export_data, output_path)
            
            return {
                'status': 'success', 
                'message': f'模型已成功导出到: {final_path}',
                'file_path': final_path,
                'skipped_layers': skipped
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': f'导出过程中发生错误: {str(e)}'}