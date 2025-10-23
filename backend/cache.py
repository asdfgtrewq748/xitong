"""
轻量级内存缓存实现
无需Redis，使用Python内置数据结构实现缓存
"""
import time
import hashlib
import json
from typing import Any, Dict, Optional, Callable
from functools import wraps
from threading import RLock
from collections import OrderedDict


class MemoryCache:
    """线程安全的内存缓存实现"""

    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL (秒)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            # 检查是否过期
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                self._misses += 1
                return None

            # 移到末尾 (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }
            self._cache.move_to_end(key)

            # 超过最大大小时，删除最旧的条目
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def delete(self, key: str):
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def cleanup_expired(self):
        """清理过期缓存"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total
            }


# 全局缓存实例
_global_cache = None


def get_cache() -> MemoryCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        from performance_config import CACHE_MAX_SIZE, CACHE_TTL_SECONDS
        _global_cache = MemoryCache(
            max_size=CACHE_MAX_SIZE,
            default_ttl=CACHE_TTL_SECONDS
        )
    return _global_cache


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """缓存装饰器

    Args:
        ttl: 缓存时间 (秒), None使用默认值
        key_prefix: 缓存键前缀

    Example:
        @cached(ttl=300, key_prefix="stats")
        def get_dashboard_stats():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from performance_config import CACHE_ENABLED

            # 缓存未启用时直接调用
            if not CACHE_ENABLED:
                return func(*args, **kwargs)

            cache = get_cache()

            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:"
            cache_key += cache._generate_key(*args, **kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 调用函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        return wrapper
    return decorator


def cache_clear_pattern(pattern: str):
    """清除匹配模式的缓存 (简化版，清除所有缓存)"""
    cache = get_cache()
    cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    cache = get_cache()
    return cache.get_stats()


# ============================================================================
# 后台清理任务
# ============================================================================

_cleanup_task = None


def start_cache_cleanup_task():
    """启动后台缓存清理任务"""
    import threading
    global _cleanup_task

    def cleanup_loop():
        while True:
            time.sleep(300)  # 每5分钟清理一次
            cache = get_cache()
            expired = cache.cleanup_expired()
            if expired > 0:
                print(f"[缓存清理] 清除了 {expired} 个过期缓存条目")

    if _cleanup_task is None:
        _cleanup_task = threading.Thread(target=cleanup_loop, daemon=True)
        _cleanup_task.start()
        print("[缓存] 后台清理任务已启动")


# ============================================================================
# 专用缓存函数
# ============================================================================

def cache_database_query(query_key: str, query_func: Callable, ttl: int = 180) -> Any:
    """缓存数据库查询结果

    Args:
        query_key: 查询键
        query_func: 查询函数
        ttl: 缓存时间

    Returns:
        查询结果
    """
    from performance_config import CACHE_ENABLED

    if not CACHE_ENABLED:
        return query_func()

    cache = get_cache()
    cache_key = f"db:{query_key}"

    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    result = query_func()
    cache.set(cache_key, result, ttl=ttl)
    return result
