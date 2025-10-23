"""
性能优化配置
针对4GB服务器优化的配置参数
"""
import os
from typing import Optional

# ============================================================================
# 内存控制配置
# ============================================================================

# 最大上传文件大小 (MB)
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "30"))

# DataFrame处理块大小 (行数)
DATAFRAME_CHUNK_SIZE = int(os.getenv("DATAFRAME_CHUNK_SIZE", "5000"))

# 最大并发请求数
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

# 建模状态内存限制 (MB) - 超过此值会自动清理旧数据
MODELING_STATE_MEMORY_LIMIT_MB = int(os.getenv("MODELING_STATE_MEMORY_LIMIT_MB", "200"))

# ============================================================================
# 缓存配置
# ============================================================================

# 缓存启用标志
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# 缓存TTL (秒)
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5分钟

# 最大缓存条目数
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))

# ============================================================================
# 数据库优化配置
# ============================================================================

# SQLite连接池大小 (SQLite不支持真正的连接池,但可以控制并发)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

# 查询结果缓存时间 (秒)
DB_QUERY_CACHE_TTL = int(os.getenv("DB_QUERY_CACHE_TTL", "180"))  # 3分钟

# 数据库查询超时 (秒)
DB_QUERY_TIMEOUT = int(os.getenv("DB_QUERY_TIMEOUT", "30"))

# ============================================================================
# 插值计算优化配置
# ============================================================================

# 最大分辨率限制 (防止内存溢出)
MAX_RESOLUTION = int(os.getenv("MAX_RESOLUTION", "150"))

# 低内存模式下的默认分辨率
LOW_MEMORY_RESOLUTION = int(os.getenv("LOW_MEMORY_RESOLUTION", "50"))

# 大网格分块计算阈值 (网格点数)
LARGE_GRID_THRESHOLD = int(os.getenv("LARGE_GRID_THRESHOLD", "10000"))

# 分块大小 (用于大网格计算)
INTERPOLATION_CHUNK_SIZE = int(os.getenv("INTERPOLATION_CHUNK_SIZE", "2000"))

# ============================================================================
# 请求限流配置
# ============================================================================

# 限流启用标志
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

# 每分钟最大请求数
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# 上传接口专用限流 (每小时)
UPLOAD_RATE_LIMIT_PER_HOUR = int(os.getenv("UPLOAD_RATE_LIMIT_PER_HOUR", "100"))

# ============================================================================
# 临时文件清理配置
# ============================================================================

# 临时文件保留时间 (秒)
TEMP_FILE_RETENTION_SECONDS = int(os.getenv("TEMP_FILE_RETENTION_SECONDS", "3600"))

# 自动清理间隔 (秒)
TEMP_FILE_CLEANUP_INTERVAL = int(os.getenv("TEMP_FILE_CLEANUP_INTERVAL", "1800"))

# ============================================================================
# 日志配置
# ============================================================================

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 性能监控日志
PERFORMANCE_LOGGING_ENABLED = os.getenv("PERFORMANCE_LOGGING_ENABLED", "true").lower() == "true"

# ============================================================================
# 辅助函数
# ============================================================================

def get_memory_limit() -> Optional[int]:
    """获取系统内存限制 (MB)"""
    try:
        import psutil
        return int(psutil.virtual_memory().total / (1024 * 1024))
    except ImportError:
        return None


def is_low_memory_system() -> bool:
    """判断是否为低内存系统 (< 6GB)"""
    mem = get_memory_limit()
    if mem is None:
        return False
    return mem < 6144  # 6GB


def adjust_for_low_memory():
    """自动调整配置以适应低内存环境"""
    global MAX_RESOLUTION, CACHE_MAX_SIZE, DATAFRAME_CHUNK_SIZE

    if is_low_memory_system():
        MAX_RESOLUTION = min(MAX_RESOLUTION, 100)
        CACHE_MAX_SIZE = min(CACHE_MAX_SIZE, 50)
        DATAFRAME_CHUNK_SIZE = min(DATAFRAME_CHUNK_SIZE, 3000)
        print("[性能优化] 检测到低内存系统，已自动调整配置")


# 启动时自动调整
adjust_for_low_memory()


# ============================================================================
# 配置摘要
# ============================================================================

def print_config_summary():
    """打印配置摘要"""
    print("\n" + "=" * 60)
    print("后端性能优化配置摘要".center(60))
    print("=" * 60)
    print(f"系统内存: {get_memory_limit() or '未知'} MB")
    print(f"低内存模式: {'是' if is_low_memory_system() else '否'}")
    print(f"最大上传大小: {MAX_UPLOAD_SIZE_MB} MB")
    print(f"最大分辨率: {MAX_RESOLUTION}")
    print(f"缓存启用: {'是' if CACHE_ENABLED else '否'}")
    print(f"缓存TTL: {CACHE_TTL_SECONDS} 秒")
    print(f"限流启用: {'是' if RATE_LIMIT_ENABLED else '否'}")
    print(f"请求限流: {RATE_LIMIT_PER_MINUTE} 次/分钟")
    print("=" * 60 + "\n")
