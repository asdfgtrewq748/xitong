# backend/api.py
import os
import sys
import webview
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import threading
import json
from scipy.interpolate import griddata, Rbf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==============================================================================
#  核心计算函数
# ==============================================================================
def calculate_key_strata_details(df_strata_above_coal, coal_seam_properties_df):
    """
    计算给定煤层上覆岩层的关键层信息。
    (此函数代码从 zongchengxuv3.0.3.py 完整迁移)
    """
    key_strata_output_list = []
    if df_strata_above_coal.empty or coal_seam_properties_df.empty:
        return key_strata_output_list

    df_strata_above_coal = df_strata_above_coal.copy()

    try:
        required_cols = ['厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
        for col in required_cols:
            if col not in df_strata_above_coal.columns:
                 df_strata_above_coal[col] = 0
        
        for col in required_cols:
            df_strata_above_coal[col] = pd.to_numeric(df_strata_above_coal[col], errors='coerce')
        
        df_strata_above_coal.fillna(0, inplace=True)

        mining_height_val = pd.to_numeric(coal_seam_properties_df['厚度/m'].iloc[0], errors='coerce')
        mining_height = round(float(mining_height_val), 2) if pd.notna(mining_height_val) else 0.0
        mining_height_factor = mining_height * 1.4

        column2 = df_strata_above_coal['岩层名称'].values
        column3 = df_strata_above_coal['厚度/m'].values
        column4 = df_strata_above_coal['弹性模量/GPa'].values
        column5 = df_strata_above_coal['容重/kN·m-3'].values
        column6 = df_strata_above_coal['抗拉强度/MPa'].values

        rh_orig = column5 * column3
        eh_orig = column4 * (column3 ** 3)

        eh_flipped = np.flipud(eh_orig)
        rh_flipped = np.flipud(rh_orig)
        column2_flipped_names = np.flipud(column2)
        column3_flipped_thickness = np.flipud(column3)
        column6_flipped_tensile = np.flipud(column6)

        key_flags_flipped = np.zeros(len(rh_flipped), dtype=int)
        number_deleted_rows_agg = 0
        
        temp_rh = rh_flipped.copy()
        temp_eh = eh_flipped.copy()

        max_iterations = 500
        for _ in range(max_iterations):
            if len(temp_rh) == 0 or len(temp_eh) == 0:
                break

            q_x = np.zeros(len(temp_rh))
            for i in range(len(temp_rh)):
                sum_rh_slice = np.sum(temp_rh[:i+1])
                sum_eh_slice = np.sum(temp_eh[:i+1])
                if sum_eh_slice != 0:
                    q_x[i] = temp_eh[0] * sum_rh_slice / sum_eh_slice
                else:
                    q_x[i] = 0
            
            found_key = False
            for i in range(1, len(q_x)):
                if q_x[i] < q_x[i-1]:
                    key_idx_in_temp = i
                    original_flipped_idx_to_mark = key_idx_in_temp -1 + number_deleted_rows_agg
                    if original_flipped_idx_to_mark < len(key_flags_flipped):
                         key_flags_flipped[original_flipped_idx_to_mark] = 1

                    temp_rh = temp_rh[i:]
                    temp_eh = temp_eh[i:]
                    number_deleted_rows_agg += i
                    found_key = True
                    break
            
            if not found_key:
                if len(temp_rh) > 0 and not np.any(key_flags_flipped):
                    key_flags_flipped[number_deleted_rows_agg] = 1
                break
        
        first_key_idx_array = np.where(key_flags_flipped == 1)[0]
        if len(first_key_idx_array) > 0:
            first_key_idx = first_key_idx_array[0]
            if first_key_idx > 0:
                immediate_roof_thickness = column3_flipped_thickness[0]
                if immediate_roof_thickness > mining_height_factor:
                    sum_thick_to_first_key = np.sum(column3_flipped_thickness[:first_key_idx+1])
                    if sum_thick_to_first_key > 10:
                        key_flags_flipped[0] = 1

        for i, name in enumerate(column2_flipped_names):
            if '泥岩' in str(name):
                key_flags_flipped[i] = 0
        
        sk_labels_flipped = ['-'] * len(key_flags_flipped)
        sk_count = 1
        key_indices_in_flipped_array = np.where(key_flags_flipped == 1)[0]

        for _, actual_flipped_idx in enumerate(key_indices_in_flipped_array):
            sk_labels_flipped[actual_flipped_idx] = f'SK{sk_count}'
            sk_count += 1
        
        if len(key_indices_in_flipped_array) > 0:
            q_z_values = np.zeros(len(key_indices_in_flipped_array))
            information = np.column_stack((rh_flipped, eh_flipped))

            for i, current_key_idx_flipped in enumerate(key_indices_in_flipped_array):
                if i == 0:
                    gs_i = information[:current_key_idx_flipped + 1, :]
                    sum_gs_i_rh = np.sum(gs_i[:, 0])
                    sum_gs_i_eh = np.sum(gs_i[:, 1])
                    if sum_gs_i_eh != 0:
                        q_z_values[i] = gs_i[-1, 1] * sum_gs_i_rh / sum_gs_i_eh
                    else:
                        q_z_values[i] = 0
                else:
                    prev_key_idx_flipped = key_indices_in_flipped_array[i-1]
                    chazhi_start_idx = prev_key_idx_flipped + 1
                    gs_i = information[chazhi_start_idx : current_key_idx_flipped + 1, :]
                    sum_gs_i_rh = np.sum(gs_i[:, 0])
                    sum_gs_i_eh = np.sum(gs_i[:, 1])
                    if sum_gs_i_eh != 0:
                        q_z_values[i] = gs_i[-1, 1] * sum_gs_i_rh / sum_gs_i_eh
                    else:
                        q_z_values[i] = 0

            h_values_for_pks = column3_flipped_thickness[key_indices_in_flipped_array]
            rt_values_for_pks = column6_flipped_tensile[key_indices_in_flipped_array]
            q_z_mpa = q_z_values / 1000.0
            l_x = np.zeros_like(h_values_for_pks, dtype=float)
            
            valid_q_z_indices_mask = (q_z_mpa > 0)
            if np.any(valid_q_z_indices_mask):
                h_subset = h_values_for_pks[valid_q_z_indices_mask]
                rt_subset = rt_values_for_pks[valid_q_z_indices_mask]
                q_z_mpa_subset = q_z_mpa[valid_q_z_indices_mask]
                term_in_sqrt = (2 * rt_subset) / q_z_mpa_subset
                safe_term_in_sqrt = np.where(term_in_sqrt >= 0, term_in_sqrt, 0)
                l_x_subset = h_subset * np.sqrt(safe_term_in_sqrt)
                l_x[valid_q_z_indices_mask] = l_x_subset
            
            if len(l_x) > 0 and np.any(np.isfinite(l_x)) and np.count_nonzero(np.isfinite(l_x) & (l_x > 0)) > 0:
                pks_idx_in_lx_array = np.nanargmax(l_x)
                pks_original_flipped_idx = key_indices_in_flipped_array[pks_idx_in_lx_array]
                if pks_original_flipped_idx < len(sk_labels_flipped) and sk_labels_flipped[pks_original_flipped_idx] != '-':
                    sk_labels_flipped[pks_original_flipped_idx] += '(PKS)'
        
        cumulative_thickness_from_coal_to_base = 0.0
        for i_flipped in range(len(sk_labels_flipped)):
            current_layer_thickness = float(column3_flipped_thickness[i_flipped])
            if sk_labels_flipped[i_flipped] != '-':
                lithology = column2_flipped_names[i_flipped]
                distance_from_coal = round(cumulative_thickness_from_coal_to_base + current_layer_thickness / 2, 2)
                
                key_strata_entry = {
                    '岩性': lithology,
                    '厚度': round(current_layer_thickness, 2),
                    '距煤层距离': distance_from_coal,
                    'SK_Label': sk_labels_flipped[i_flipped]
                }
                key_strata_output_list.append(key_strata_entry)
            
            cumulative_thickness_from_coal_to_base += current_layer_thickness

    except Exception as e:
        print(f"计算关键层时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []

    return key_strata_output_list


def process_single_borehole_file(input_csv_path):
    pass

def fill_missing_properties(df, rock_db, stat_preference: str = "median"):
    pass

# ==============================================================================
#  API 类
# ==============================================================================
class Api:
    def __init__(self):
        self.dfs = {}
        self.merged_df_modeling = None
        self.rock_db_cache = None
        self.china_geojson_cache = None
        # 新增：插值方法映射
        self.interpolation_methods = {
            "linear": "Linear (线性)", "cubic": "Cubic (三次样条)", "nearest": "Nearest (最近邻)",
            "multiquadric": "Multiquadric (多重二次)", "inverse": "Inverse (反距离)",
            "gaussian": "Gaussian (高斯)", "thin_plate": "Thin Plate (薄板样条)"
        }

    def _get_raw_db_path(self):
        # ... (代码与之前相同)
        pass

    def _read_raw_db(self):
        # ... (代码与之前相同)
        pass

    def _perform_interpolation(self, x_train, y_train, z_train, x_val, y_val, method_key):
        """[新增] 统一的插值执行函数"""
        if method_key in ["linear", "cubic", "nearest"]:
            # griddata对于点少的情况会自动降级，无需手动处理
            return griddata((x_train, y_train), z_train, (x_val, y_val), method=method_key)
        elif method_key in self.interpolation_methods:
            rbf = Rbf(x_train, y_train, z_train, function=method_key)
            return rbf(x_val, y_val)
        else:
            # 默认回退到线性插值
            return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')

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
        try:
            if self.merged_df_modeling is None:
                return {'status': 'error', 'message': '数据未加载，请先选择文件'}

            from coal_seam_blocks.modeling import build_block_models
            
            def interpolation_wrapper(x, y, z, xi_flat, yi_flat):
                return self._perform_interpolation(x, y, z, xi_flat, yi_flat, params['method'].lower())

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
            models_data = []
            for model in block_models_objs:
                models_data.append({
                    'name': model.name,
                    'points': model.points,
                    'top_surface': np.nan_to_num(model.top_surface).tolist(),
                    'bottom_surface': np.nan_to_num(model.bottom_surface).tolist(),
                    'avg_thickness': model.avg_thickness
                })
            return {
                'status': 'success',
                'grid': {'x': XI[0].tolist(), 'y': YI[:, 0].tolist()},
                'models': models_data, 'skipped': skipped
            }
        except Exception as e:
            return {'status': 'error', 'message': f'3D建模计算失败: {e}'}