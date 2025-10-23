# backend/interpolation.py
"""
增强的插值算法模块 - 支持多种插值方法及智能选择
包含真正的克里金插值、各向异性插值、交叉验证等功能
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional, List
from scipy.interpolate import griddata, Rbf
from functools import lru_cache
import warnings


class InterpolationValidator:
    """插值结果验证器"""

    @staticmethod
    def cross_validate(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                       method_func, k_folds: int = 5) -> Dict[str, float]:
        """
        K折交叉验证

        Args:
            x, y, z: 输入数据点
            method_func: 插值方法函数
            k_folds: 折数

        Returns:
            包含MAE, RMSE, R2的字典
        """
        from sklearn.model_selection import KFold
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        n_samples = len(x)
        if n_samples < k_folds:
            k_folds = max(2, n_samples // 2)

        kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

        mae_scores = []
        rmse_scores = []
        r2_scores = []

        for train_idx, test_idx in kf.split(x):
            X_train_x, X_test_x = x[train_idx], x[test_idx]
            X_train_y, X_test_y = y[train_idx], y[test_idx]
            z_train, z_test = z[train_idx], z[test_idx]

            try:
                # 预测测试集
                z_pred = method_func(X_train_x, X_train_y, z_train, X_test_x, X_test_y)

                # 过滤NaN值
                valid_mask = ~np.isnan(z_pred) & ~np.isnan(z_test)
                if np.sum(valid_mask) < 2:
                    continue

                z_pred_valid = z_pred[valid_mask]
                z_test_valid = z_test[valid_mask]

                # 计算指标
                mae_scores.append(mean_absolute_error(z_test_valid, z_pred_valid))
                rmse_scores.append(np.sqrt(mean_squared_error(z_test_valid, z_pred_valid)))
                r2_scores.append(r2_score(z_test_valid, z_pred_valid))
            except Exception as e:
                warnings.warn(f"交叉验证折叠失败: {e}")
                continue

        if not mae_scores:
            return {"mae": float('inf'), "rmse": float('inf'), "r2": -float('inf'),
                    "confidence_low": 0, "confidence_high": 0}

        # 计算置信区间 (95%)
        z_std = np.std(z)
        confidence_interval = 1.96 * z_std / np.sqrt(len(z))

        return {
            "mae": float(np.mean(mae_scores)),
            "rmse": float(np.mean(rmse_scores)),
            "r2": float(np.mean(r2_scores)),
            "confidence_low": float(np.mean(z) - confidence_interval),
            "confidence_high": float(np.mean(z) + confidence_interval)
        }

    @staticmethod
    def detect_outliers(z: np.ndarray, method: str = "zscore", threshold: float = 3.0) -> np.ndarray:
        """
        检测异常值

        Args:
            z: 数据数组
            method: 检测方法 ('zscore' 或 'iqr')
            threshold: 阈值

        Returns:
            布尔数组,True表示异常值
        """
        if method == "zscore":
            # 3-sigma原则
            z_mean = np.mean(z)
            z_std = np.std(z)
            if z_std == 0:
                return np.zeros(len(z), dtype=bool)
            z_scores = np.abs((z - z_mean) / z_std)
            return z_scores > threshold

        elif method == "iqr":
            # 四分位距方法
            q1 = np.percentile(z, 25)
            q3 = np.percentile(z, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            return (z < lower_bound) | (z > upper_bound)

        return np.zeros(len(z), dtype=bool)


class EnhancedInterpolation:
    """增强的插值类 - 支持多种高级插值方法"""

    def __init__(self):
        self.validator = InterpolationValidator()
        self._check_pykrige()

    def _check_pykrige(self):
        """检查是否安装了pykrige库"""
        try:
            import pykrige
            self.has_pykrige = True
        except ImportError:
            self.has_pykrige = False
            warnings.warn("未安装pykrige库,克里金插值将使用高斯RBF近似。"
                         "建议安装: pip install pykrige")

    def ordinary_kriging(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                         xi: np.ndarray, yi: np.ndarray,
                         variogram_model: str = 'spherical') -> np.ndarray:
        """
        普通克里金插值 (真实实现)

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            variogram_model: 变差函数模型 ('spherical', 'exponential', 'gaussian', 'linear')

        Returns:
            插值结果
        """
        if not self.has_pykrige:
            # 回退到高斯RBF近似
            warnings.warn("使用高斯RBF近似克里金插值")
            return self._kriging_rbf_fallback(x, y, z, xi, yi)

        try:
            from pykrige.ok import OrdinaryKriging

            # 创建克里金对象
            OK = OrdinaryKriging(
                x, y, z,
                variogram_model=variogram_model,
                verbose=False,
                enable_plotting=False
            )

            # 执行插值
            # 判断xi, yi是网格还是点
            if len(xi.shape) == 1:
                # 扁平化的点
                z_pred, ss = OK.execute('points', xi, yi)
            else:
                # 网格
                z_pred, ss = OK.execute('grid', xi, yi)

            return z_pred

        except Exception as e:
            warnings.warn(f"克里金插值失败: {e}, 回退到RBF")
            return self._kriging_rbf_fallback(x, y, z, xi, yi)

    def _kriging_rbf_fallback(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                               xi: np.ndarray, yi: np.ndarray) -> np.ndarray:
        """克里金的RBF回退方案"""
        try:
            rbf = Rbf(x, y, z, function='gaussian')
            return rbf(xi, yi)
        except Exception:
            # 最终回退到线性插值
            return griddata((x, y), z, (xi, yi), method='linear')

    def anisotropic_interpolation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                                   xi: np.ndarray, yi: np.ndarray,
                                   angle: float = 0.0, ratio: float = 2.0) -> np.ndarray:
        """
        各向异性插值 - 考虑地质构造的方向性

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            angle: 主方向角度 (度)
            ratio: 主方向/次方向的比例

        Returns:
            插值结果
        """
        # 坐标变换矩阵
        theta = np.radians(angle)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # 变换已知点
        x_transformed = x * cos_theta + y * sin_theta
        y_transformed = (-x * sin_theta + y * cos_theta) / ratio

        # 变换插值点
        xi_transformed = xi * cos_theta + yi * sin_theta
        yi_transformed = (-xi * sin_theta + yi * cos_theta) / ratio

        # 在变换空间中插值
        try:
            rbf = Rbf(x_transformed, y_transformed, z, function='thin_plate')
            z_pred = rbf(xi_transformed, yi_transformed)
            return z_pred
        except Exception as e:
            warnings.warn(f"各向异性插值失败: {e}, 回退到各向同性")
            return griddata((x, y), z, (xi, yi), method='linear')

    def inverse_distance_weighting(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                                    xi: np.ndarray, yi: np.ndarray,
                                    power: float = 2.0, radius: Optional[float] = None) -> np.ndarray:
        """
        改进的反距离加权插值 (IDW)

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            power: 距离权重指数 (通常为2)
            radius: 搜索半径 (None表示使用所有点)

        Returns:
            插值结果
        """
        xi_flat = xi.flatten() if len(xi.shape) > 1 else xi
        yi_flat = yi.flatten() if len(yi.shape) > 1 else yi

        result = np.zeros(len(xi_flat))

        for i, (xi_val, yi_val) in enumerate(zip(xi_flat, yi_flat)):
            # 计算距离
            distances = np.sqrt((x - xi_val) ** 2 + (y - yi_val) ** 2)

            # 处理零距离
            if np.any(distances == 0):
                zero_idx = np.where(distances == 0)[0][0]
                result[i] = z[zero_idx]
                continue

            # 应用搜索半径
            if radius is not None:
                mask = distances <= radius
                if not np.any(mask):
                    # 如果半径内没有点,使用最近的点
                    result[i] = z[np.argmin(distances)]
                    continue
                distances = distances[mask]
                z_subset = z[mask]
            else:
                z_subset = z

            # 计算权重
            weights = 1.0 / (distances ** power)
            weights = weights / np.sum(weights)

            # 加权平均
            result[i] = np.sum(weights * z_subset)

        return result.reshape(xi.shape) if len(xi.shape) > 1 else result

    def smart_interpolation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                            xi: np.ndarray, yi: np.ndarray,
                            method: str = 'auto') -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        智能插值 - 根据数据特征自动选择最佳方法

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            method: 插值方法 ('auto' 自动选择)

        Returns:
            (插值结果, 元数据字典)
        """
        n_points = len(x)
        metadata = {
            "n_points": n_points,
            "method_used": method,
            "outliers_removed": 0,
            "data_quality": "unknown"
        }

        # 检测并移除异常值
        outliers = self.validator.detect_outliers(z, method='zscore', threshold=3.0)
        if np.any(outliers):
            n_outliers = np.sum(outliers)
            if n_outliers < n_points * 0.1:  # 异常值少于10%才移除
                x = x[~outliers]
                y = y[~outliers]
                z = z[~outliers]
                metadata["outliers_removed"] = int(n_outliers)
                n_points = len(x)

        # 根据点数量选择方法
        if method == 'auto':
            if n_points <= 3:
                method = 'nearest'
                metadata["data_quality"] = "poor"
            elif n_points <= 10:
                method = 'linear'
                metadata["data_quality"] = "fair"
            elif n_points <= 50:
                method = 'cubic'
                metadata["data_quality"] = "good"
            else:
                method = 'kriging'
                metadata["data_quality"] = "excellent"

            metadata["method_used"] = method

        # 检查点的空间分布
        x_range = np.max(x) - np.min(x)
        y_range = np.max(y) - np.min(y)

        if x_range < 1e-6 or y_range < 1e-6:
            # 点几乎在一条线上
            method = 'nearest'
            metadata["method_used"] = 'nearest'
            metadata["warning"] = "数据点接近共线,使用最近邻插值"

        # 执行插值
        try:
            if method == 'nearest':
                z_interp = griddata((x, y), z, (xi, yi), method='nearest')
            elif method == 'linear':
                z_interp = griddata((x, y), z, (xi, yi), method='linear')
            elif method == 'cubic':
                if n_points >= 16:
                    z_interp = griddata((x, y), z, (xi, yi), method='cubic')
                else:
                    z_interp = griddata((x, y), z, (xi, yi), method='linear')
                    metadata["method_used"] = 'linear'
                    metadata["warning"] = "点数不足16个,降级为线性插值"
            elif method == 'kriging':
                z_interp = self.ordinary_kriging(x, y, z, xi, yi)
            elif method == 'anisotropic':
                z_interp = self.anisotropic_interpolation(x, y, z, xi, yi)
            elif method == 'idw':
                z_interp = self.inverse_distance_weighting(x, y, z, xi, yi)
            else:
                # 未知方法,使用线性
                z_interp = griddata((x, y), z, (xi, yi), method='linear')
                metadata["method_used"] = 'linear'
                metadata["warning"] = f"未知方法 '{method}',使用线性插值"

            # 处理NaN
            z_interp = np.nan_to_num(z_interp, nan=0.0, posinf=0.0, neginf=0.0)

            return z_interp, metadata

        except Exception as e:
            warnings.warn(f"插值失败: {e}, 使用最近邻回退")
            z_interp = griddata((x, y), z, (xi, yi), method='nearest')
            z_interp = np.nan_to_num(z_interp, nan=0.0)
            metadata["method_used"] = 'nearest'
            metadata["error"] = str(e)
            return z_interp, metadata


# 全局插值器实例
_interpolator = None

def get_interpolator() -> EnhancedInterpolation:
    """获取全局插值器实例(单例模式)"""
    global _interpolator
    if _interpolator is None:
        _interpolator = EnhancedInterpolation()
    return _interpolator


# 便捷函数
    def modified_shepard(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                         xi: np.ndarray, yi: np.ndarray,
                         power: float = 2.0) -> np.ndarray:
        """
        修正谢泼德插值 (Modified Shepard)

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            power: 距离权重指数

        Returns:
            插值结果
        """
        xi_flat = xi.flatten() if len(xi.shape) > 1 else xi
        yi_flat = yi.flatten() if len(yi.shape) > 1 else yi

        result = np.zeros(len(xi_flat))

        for i, (xv, yv) in enumerate(zip(xi_flat, yi_flat)):
            distances = np.sqrt((x - xv) ** 2 + (y - yv) ** 2)
            # 避免除零错误
            distances = np.where(distances == 0, 1e-12, distances)
            weights = 1.0 / (distances ** power)
            weights = weights / np.sum(weights)
            result[i] = np.sum(weights * z)

        return result.reshape(xi.shape) if len(xi.shape) > 1 else result

    def natural_neighbor(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                         xi: np.ndarray, yi: np.ndarray) -> np.ndarray:
        """
        自然邻点插值 (Natural Neighbor)
        使用线性插值作为近似实现

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标

        Returns:
            插值结果
        """
        try:
            # 自然邻点的完整实现需要Voronoi图计算，这里使用线性插值近似
            return griddata((x, y), z, (xi, yi), method='linear')
        except Exception as e:
            warnings.warn(f"自然邻点插值失败: {e}, 使用最近邻")
            return griddata((x, y), z, (xi, yi), method='nearest')

    def radial_basis_function(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                               xi: np.ndarray, yi: np.ndarray,
                               function: str = 'multiquadric') -> np.ndarray:
        """
        径向基函数插值 (Radial Basis Function)

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            function: RBF函数类型

        Returns:
            插值结果
        """
        try:
            rbf = Rbf(x, y, z, function=function, smooth=0.1)
            return rbf(xi, yi)
        except Exception as e:
            warnings.warn(f"RBF插值失败: {e}, 回退到线性插值")
            return griddata((x, y), z, (xi, yi), method='linear')

    def universal_kriging(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                          xi: np.ndarray, yi: np.ndarray) -> np.ndarray:
        """
        通用克里金插值 (Universal Kriging)
        使用薄板样条近似

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标

        Returns:
            插值结果
        """
        if len(x) < 4:
            warnings.warn("数据点太少，使用最近邻插值")
            return griddata((x, y), z, (xi, yi), method='nearest')

        try:
            rbf = Rbf(x, y, z, function='thin_plate', smooth=0.5)
            return rbf(xi, yi)
        except Exception as e:
            warnings.warn(f"通用克里金插值失败: {e}, 回退到线性插值")
            return griddata((x, y), z, (xi, yi), method='linear')

    def bilinear_interpolation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                                xi: np.ndarray, yi: np.ndarray) -> np.ndarray:
        """
        双线性插值 (Bilinear)

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标

        Returns:
            插值结果
        """
        return griddata((x, y), z, (xi, yi), method='linear')

    def perform_interpolation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                               xi: np.ndarray, yi: np.ndarray,
                               method: str) -> np.ndarray:
        """
        统一的插值执行函数，支持所有插值方法

        Args:
            x, y, z: 已知数据点
            xi, yi: 插值点坐标
            method: 插值方法名称

        Returns:
            插值结果
        """
        method = method.lower()

        # 数据验证
        if len(x) < 3:
            warnings.warn(f"数据点太少 ({len(x)} 个)，使用最近邻插值")
            return griddata((x, y), z, (xi, yi), method='nearest')

        try:
            # 基础griddata方法
            if method in ['linear', 'nearest']:
                return griddata((x, y), z, (xi, yi), method=method)
            elif method == 'cubic':
                if len(x) >= 16:
                    return griddata((x, y), z, (xi, yi), method='cubic')
                else:
                    warnings.warn(f"数据点不足 ({len(x)} < 16)，从cubic降级为linear")
                    return griddata((x, y), z, (xi, yi), method='linear')

            # RBF方法
            elif method in ['multiquadric', 'inverse', 'gaussian', 'thin_plate']:
                return self.radial_basis_function(x, y, z, xi, yi, function=method)
            elif method == 'linear_rbf':
                return self.radial_basis_function(x, y, z, xi, yi, function='linear')
            elif method == 'cubic_rbf':
                return self.radial_basis_function(x, y, z, xi, yi, function='cubic')
            elif method == 'quintic_rbf':
                return self.radial_basis_function(x, y, z, xi, yi, function='quintic')

            # 高级方法
            elif method == 'modified_shepard':
                return self.modified_shepard(x, y, z, xi, yi)
            elif method == 'natural_neighbor':
                return self.natural_neighbor(x, y, z, xi, yi)
            elif method == 'radial_basis':
                return self.radial_basis_function(x, y, z, xi, yi, function='multiquadric')
            elif method == 'ordinary_kriging':
                return self.ordinary_kriging(x, y, z, xi, yi)
            elif method == 'universal_kriging':
                return self.universal_kriging(x, y, z, xi, yi)
            elif method == 'bilinear':
                return self.bilinear_interpolation(x, y, z, xi, yi)
            elif method == 'anisotropic':
                return self.anisotropic_interpolation(x, y, z, xi, yi)
            elif method == 'idw':
                return self.inverse_distance_weighting(x, y, z, xi, yi)

            # 未知方法，使用线性插值
            else:
                warnings.warn(f"未知插值方法 '{method}'，使用线性插值")
                return griddata((x, y), z, (xi, yi), method='linear')

        except Exception as e:
            warnings.warn(f"插值方法 '{method}' 失败: {e}, 回退到最近邻插值")
            return griddata((x, y), z, (xi, yi), method='nearest')


def interpolate_smart(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                      xi: np.ndarray, yi: np.ndarray,
                      method: str = 'auto') -> Tuple[np.ndarray, Dict[str, Any]]:
    """智能插值的便捷函数"""
    interpolator = get_interpolator()
    return interpolator.smart_interpolation(x, y, z, xi, yi, method)


def validate_interpolation(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                           method_func, k_folds: int = 5) -> Dict[str, float]:
    """交叉验证的便捷函数"""
    validator = InterpolationValidator()
    return validator.cross_validate(x, y, z, method_func, k_folds)


def interpolate(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                xi: np.ndarray, yi: np.ndarray,
                method: str = 'linear') -> np.ndarray:
    """
    统一的插值便捷函数

    Args:
        x, y, z: 已知数据点
        xi, yi: 插值点坐标
        method: 插值方法

    Returns:
        插值结果
    """
    interpolator = get_interpolator()
    return interpolator.perform_interpolation(x, y, z, xi, yi, method)
