"""
内存优化工具
针对4GB服务器的DataFrame和文件处理优化
"""
import gc
import sys
from typing import Iterator, Optional, Callable, Any
from functools import wraps
import pandas as pd
import numpy as np
from contextlib import contextmanager


def get_object_size_mb(obj: Any) -> float:
    """获取对象占用内存大小 (MB)"""
    size_bytes = sys.getsizeof(obj)
    if isinstance(obj, pd.DataFrame):
        size_bytes = obj.memory_usage(deep=True).sum()
    elif isinstance(obj, np.ndarray):
        size_bytes = obj.nbytes
    return round(size_bytes / (1024 * 1024), 2)


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """优化DataFrame内存占用

    通过降低数值类型精度来减少内存使用
    对于4GB服务器,这可以节省50%以上的内存
    """
    df = df.copy()

    for col in df.columns:
        col_type = df[col].dtype

        # 优化整数类型
        if col_type == 'int64':
            c_min = df[col].min()
            c_max = df[col].max()

            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                df[col] = df[col].astype(np.int8)
            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                df[col] = df[col].astype(np.int16)
            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)

        # 优化浮点数类型
        elif col_type == 'float64':
            df[col] = df[col].astype(np.float32)

        # 优化对象类型
        elif col_type == 'object':
            # 尝试转换为category (对于重复值多的列很有效)
            num_unique = df[col].nunique()
            num_total = len(df[col])
            if num_unique / num_total < 0.5:  # 唯一值少于50%时使用category
                df[col] = df[col].astype('category')

    return df


def read_csv_in_chunks(
    file_path: str,
    chunk_size: int = 5000,
    encoding: str = "utf-8-sig"
) -> Iterator[pd.DataFrame]:
    """分块读取CSV文件,避免大文件占满内存

    Args:
        file_path: CSV文件路径
        chunk_size: 每块行数
        encoding: 文件编码

    Yields:
        DataFrame块
    """
    encodings = [encoding, "utf-8", "gbk"]

    for enc in encodings:
        try:
            reader = pd.read_csv(
                file_path,
                encoding=enc,
                chunksize=chunk_size,
                low_memory=True
            )
            for chunk in reader:
                yield optimize_dataframe_memory(chunk)
            return
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    raise ValueError(f"无法读取CSV文件: {file_path}")


def process_large_dataframe(
    df: pd.DataFrame,
    process_func: Callable[[pd.DataFrame], pd.DataFrame],
    chunk_size: int = 5000
) -> pd.DataFrame:
    """分块处理大DataFrame

    Args:
        df: 源DataFrame
        process_func: 处理函数
        chunk_size: 块大小

    Returns:
        处理后的DataFrame
    """
    if len(df) <= chunk_size:
        return process_func(df)

    chunks = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        processed_chunk = process_func(chunk)
        chunks.append(processed_chunk)

        # 每处理10个块强制回收内存
        if len(chunks) % 10 == 0:
            gc.collect()

    result = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()

    return result


@contextmanager
def memory_efficient_operation():
    """内存高效操作的上下文管理器

    自动在操作前后执行垃圾回收
    """
    gc.collect()  # 操作前回收
    try:
        yield
    finally:
        gc.collect()  # 操作后回收


def auto_gc(threshold_mb: float = 100):
    """自动垃圾回收装饰器

    当函数分配的内存超过阈值时,自动触发GC

    Args:
        threshold_mb: 内存阈值 (MB)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import psutil
            try:
                process = psutil.Process()
                mem_before = process.memory_info().rss / (1024 * 1024)
            except ImportError:
                mem_before = 0

            result = func(*args, **kwargs)

            try:
                mem_after = process.memory_info().rss / (1024 * 1024)
                mem_increase = mem_after - mem_before

                if mem_increase > threshold_mb:
                    gc.collect()
                    print(f"[内存优化] {func.__name__} 分配了 {mem_increase:.1f}MB, 已触发GC")
            except (ImportError, NameError):
                pass

            return result

        return wrapper
    return decorator


def clear_dataframe_cache(state_objects: list):
    """清除DataFrame缓存

    Args:
        state_objects: 包含DataFrame的状态对象列表
    """
    for state in state_objects:
        if hasattr(state, 'merged_df') and state.merged_df is not None:
            del state.merged_df
            state.merged_df = None

        if hasattr(state, 'coords_df') and state.coords_df is not None:
            del state.coords_df
            state.coords_df = None

        if hasattr(state, 'files'):
            state.files.clear()

        if hasattr(state, 'last_result') and state.last_result is not None:
            del state.last_result
            state.last_result = None

    gc.collect()
    print("[内存优化] 已清除DataFrame缓存")


def check_memory_usage() -> dict:
    """检查当前内存使用情况"""
    try:
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()

        vm = psutil.virtual_memory()

        return {
            "process_mb": round(mem_info.rss / (1024 * 1024), 2),
            "system_total_mb": round(vm.total / (1024 * 1024), 2),
            "system_available_mb": round(vm.available / (1024 * 1024), 2),
            "system_used_percent": vm.percent
        }
    except ImportError:
        return {
            "process_mb": 0,
            "system_total_mb": 0,
            "system_available_mb": 0,
            "system_used_percent": 0,
            "error": "psutil未安装"
        }


def limit_dataframe_size(df: pd.DataFrame, max_rows: int = 50000) -> pd.DataFrame:
    """限制DataFrame大小

    对于超大数据集,自动采样以避免内存溢出

    Args:
        df: 源DataFrame
        max_rows: 最大行数

    Returns:
        限制后的DataFrame
    """
    if len(df) <= max_rows:
        return df

    print(f"[内存优化] DataFrame过大({len(df)}行), 采样为{max_rows}行")

    # 使用分层采样保持数据分布
    sample_ratio = max_rows / len(df)
    sampled_df = df.sample(frac=sample_ratio, random_state=42)

    return sampled_df.reset_index(drop=True)


def optimize_numpy_array(arr: np.ndarray) -> np.ndarray:
    """优化NumPy数组内存占用"""
    if arr.dtype == np.float64:
        # 转为float32可以减少50%内存
        return arr.astype(np.float32)
    elif arr.dtype == np.int64:
        # 根据数值范围选择合适的整数类型
        if arr.min() >= -128 and arr.max() <= 127:
            return arr.astype(np.int8)
        elif arr.min() >= -32768 and arr.max() <= 32767:
            return arr.astype(np.int16)
        elif arr.min() >= -2147483648 and arr.max() <= 2147483647:
            return arr.astype(np.int32)

    return arr


def memory_monitor(func: Callable) -> Callable:
    """内存监控装饰器

    记录函数执行前后的内存变化
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        mem_before = check_memory_usage()

        result = func(*args, **kwargs)

        mem_after = check_memory_usage()

        if "error" not in mem_before:
            mem_increase = mem_after["process_mb"] - mem_before["process_mb"]
            print(
                f"[内存监控] {func.__name__}: "
                f"前={mem_before['process_mb']}MB, "
                f"后={mem_after['process_mb']}MB, "
                f"增长={mem_increase:.1f}MB"
            )

        return result

    return wrapper


# ============================================================================
# 智能内存管理
# ============================================================================

class MemoryManager:
    """智能内存管理器"""

    def __init__(self, max_memory_mb: int = 3000):
        """
        Args:
            max_memory_mb: 最大允许内存 (MB), 默认3GB (为4GB服务器留1GB余量)
        """
        self.max_memory_mb = max_memory_mb
        self._watchers = []

    def register_watcher(self, obj: Any, name: str = ""):
        """注册监控对象"""
        self._watchers.append({"obj": obj, "name": name or str(type(obj))})

    def check_and_cleanup(self):
        """检查内存并自动清理"""
        mem_usage = check_memory_usage()

        if "error" in mem_usage:
            return

        if mem_usage["process_mb"] > self.max_memory_mb:
            print(f"[内存管理] 警告: 内存使用超限 ({mem_usage['process_mb']:.1f}MB > {self.max_memory_mb}MB)")
            gc.collect()

            # 再次检查
            mem_after_gc = check_memory_usage()
            print(f"[内存管理] GC后内存: {mem_after_gc['process_mb']:.1f}MB")

    def get_report(self) -> dict:
        """获取内存使用报告"""
        report = check_memory_usage()

        report["watchers"] = []
        for watcher in self._watchers:
            obj = watcher["obj"]
            size_mb = get_object_size_mb(obj)
            report["watchers"].append({
                "name": watcher["name"],
                "size_mb": size_mb
            })

        return report
