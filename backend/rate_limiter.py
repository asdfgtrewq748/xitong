"""
请求限流中间件
轻量级实现,无需Redis
"""
import time
from collections import defaultdict, deque
from threading import RLock
from typing import Callable, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimiter:
    """基于滑动窗口的请求限流器"""

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小 (秒)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: defaultdict[str, deque] = defaultdict(deque)
        self._lock = RLock()

    def is_allowed(self, key: str) -> bool:
        """检查请求是否允许

        Args:
            key: 限流键 (通常是IP地址)

        Returns:
            True if allowed, False otherwise
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # 移除窗口外的请求
            requests = self._requests[key]
            while requests and requests[0] < window_start:
                requests.popleft()

            # 检查是否超过限制
            if len(requests) >= self.max_requests:
                return False

            # 记录当前请求
            requests.append(now)
            return True

    def get_retry_after(self, key: str) -> Optional[int]:
        """获取需要等待的秒数

        Args:
            key: 限流键

        Returns:
            需要等待的秒数,如果未超限则返回None
        """
        with self._lock:
            now = time.time()
            requests = self._requests[key]

            if len(requests) < self.max_requests:
                return None

            # 计算最早的请求何时超出窗口
            oldest_request = requests[0]
            window_start = now - self.window_seconds
            retry_after = int(oldest_request - window_start) + 1
            return max(retry_after, 1)

    def cleanup(self):
        """清理过期的限流记录"""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # 清理空的或过期的记录
            keys_to_remove = []
            for key, requests in self._requests.items():
                while requests and requests[0] < window_start:
                    requests.popleft()
                if not requests:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._requests[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI限流中间件"""

    def __init__(self, app, rate_per_minute: int = 60):
        """
        Args:
            app: FastAPI应用
            rate_per_minute: 每分钟最大请求数
        """
        super().__init__(app)
        self.limiter = RateLimiter(
            max_requests=rate_per_minute,
            window_seconds=60
        )

        # 上传接口单独限流
        self.upload_limiter = RateLimiter(
            max_requests=20,  # 每小时20次上传
            window_seconds=3600
        )

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 优先从X-Forwarded-For获取真实IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # 其次从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 最后从连接信息获取
        if request.client:
            return request.client.host

        return "unknown"

    def _is_upload_endpoint(self, path: str) -> bool:
        """判断是否为上传接口"""
        upload_patterns = [
            "/api/modeling/columns",
            "/api/borehole/analyze",
            "/api/keystratum/files",
            "/api/raw/import",
        ]
        return any(path.startswith(pattern) for pattern in upload_patterns)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        from performance_config import RATE_LIMIT_ENABLED

        # 限流未启用时直接通过
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)

        # 健康检查接口不限流
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # 上传接口使用单独的限流器
        if self._is_upload_endpoint(request.url.path):
            if not self.upload_limiter.is_allowed(client_ip):
                retry_after = self.upload_limiter.get_retry_after(client_ip)
                raise HTTPException(
                    status_code=429,
                    detail=f"上传频率过高，请{retry_after}秒后重试",
                    headers={"Retry-After": str(retry_after)}
                )
        else:
            # 普通请求限流
            if not self.limiter.is_allowed(client_ip):
                retry_after = self.limiter.get_retry_after(client_ip)
                raise HTTPException(
                    status_code=429,
                    detail=f"请求过于频繁，请{retry_after}秒后重试",
                    headers={"Retry-After": str(retry_after)}
                )

        response = await call_next(request)
        return response


# ============================================================================
# 装饰器方式的限流 (用于特定路由)
# ============================================================================

_route_limiters = {}


def rate_limit(max_requests: int, window_seconds: int):
    """路由级别的限流装饰器

    Args:
        max_requests: 时间窗口内最大请求数
        window_seconds: 时间窗口大小 (秒)

    Example:
        @app.get("/api/expensive-operation")
        @rate_limit(max_requests=10, window_seconds=60)
        async def expensive_operation():
            ...
    """
    def decorator(func):
        # 为每个函数创建独立的限流器
        limiter_key = f"{func.__module__}.{func.__name__}"
        if limiter_key not in _route_limiters:
            _route_limiters[limiter_key] = RateLimiter(max_requests, window_seconds)

        async def wrapper(*args, **kwargs):
            # 获取Request对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                # 如果没有Request对象,直接执行
                return await func(*args, **kwargs)

            # 获取客户端IP
            client_ip = request.client.host if request.client else "unknown"

            # 检查限流
            limiter = _route_limiters[limiter_key]
            if not limiter.is_allowed(client_ip):
                retry_after = limiter.get_retry_after(client_ip)
                raise HTTPException(
                    status_code=429,
                    detail=f"请求过于频繁，请{retry_after}秒后重试",
                    headers={"Retry-After": str(retry_after)}
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# 后台清理任务
# ============================================================================

_cleanup_task = None


def start_rate_limit_cleanup_task(middleware: RateLimitMiddleware):
    """启动后台清理任务"""
    import threading

    global _cleanup_task

    def cleanup_loop():
        while True:
            time.sleep(300)  # 每5分钟清理一次
            middleware.limiter.cleanup()
            middleware.upload_limiter.cleanup()

    if _cleanup_task is None:
        _cleanup_task = threading.Thread(target=cleanup_loop, daemon=True)
        _cleanup_task.start()
        print("[限流] 后台清理任务已启动")
