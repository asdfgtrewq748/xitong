# backend/progress_tracker_ws.py
"""
WebSocket进度跟踪模块
实时推送操作进度到前端
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any, Optional
import asyncio
import json
from datetime import datetime
from enum import Enum


class ProgressStatus(Enum):
    """进度状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 活跃连接: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 任务订阅: {task_id: set(client_ids)}
        self.task_subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """接受新连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # 清理订阅
        for task_id in list(self.task_subscriptions.keys()):
            if client_id in self.task_subscriptions[task_id]:
                self.task_subscriptions[task_id].remove(client_id)
            if not self.task_subscriptions[task_id]:
                del self.task_subscriptions[task_id]

    def subscribe_task(self, client_id: str, task_id: str):
        """订阅任务进度"""
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = set()
        self.task_subscriptions[task_id].add(client_id)

    def unsubscribe_task(self, client_id: str, task_id: str):
        """取消订阅"""
        if task_id in self.task_subscriptions:
            self.task_subscriptions[task_id].discard(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"发送消息失败 (client: {client_id}): {e}")
                self.disconnect(client_id)

    async def broadcast_task_progress(self, task_id: str, progress_data: dict):
        """广播任务进度到所有订阅者"""
        if task_id not in self.task_subscriptions:
            return

        subscribers = list(self.task_subscriptions[task_id])

        for client_id in subscribers:
            await self.send_personal_message(progress_data, client_id)


# 全局连接管理器实例
manager = ConnectionManager()


class TaskProgress:
    """任务进度"""

    def __init__(self,
                 task_id: str,
                 task_name: str,
                 total_steps: int = 100):
        self.task_id = task_id
        self.task_name = task_name
        self.total_steps = total_steps
        self.current_step = 0
        self.status = ProgressStatus.PENDING
        self.message = ""
        self.start_time = None
        self.end_time = None
        self.error = None
        self.result = None

    def start(self):
        """开始任务"""
        self.status = ProgressStatus.RUNNING
        self.start_time = datetime.now()
        self.message = f"开始执行: {self.task_name}"

    def update(self, current_step: int, message: str = ""):
        """更新进度"""
        self.current_step = min(current_step, self.total_steps)
        if message:
            self.message = message

    def complete(self, result: Any = None):
        """完成任务"""
        self.status = ProgressStatus.SUCCESS
        self.current_step = self.total_steps
        self.end_time = datetime.now()
        self.result = result
        self.message = f"完成: {self.task_name}"

    def fail(self, error: str):
        """任务失败"""
        self.status = ProgressStatus.FAILED
        self.end_time = datetime.now()
        self.error = error
        self.message = f"失败: {error}"

    def cancel(self):
        """取消任务"""
        self.status = ProgressStatus.CANCELLED
        self.end_time = datetime.now()
        self.message = "任务已取消"

    def get_percentage(self) -> float:
        """获取完成百分比"""
        if self.total_steps == 0:
            return 0.0
        return round((self.current_step / self.total_steps) * 100, 1)

    def get_elapsed_time(self) -> Optional[float]:
        """获取已用时间(秒)"""
        if not self.start_time:
            return None

        end = self.end_time or datetime.now()
        elapsed = (end - self.start_time).total_seconds()
        return round(elapsed, 2)

    def get_eta(self) -> Optional[float]:
        """估算剩余时间(秒)"""
        if not self.start_time or self.current_step == 0:
            return None

        elapsed = self.get_elapsed_time()
        if not elapsed:
            return None

        progress_rate = self.current_step / elapsed  # 步/秒
        remaining_steps = self.total_steps - self.current_step

        if progress_rate > 0:
            eta = remaining_steps / progress_rate
            return round(eta, 2)

        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": self.get_percentage(),
            "message": self.message,
            "elapsed_time": self.get_elapsed_time(),
            "eta": self.get_eta(),
            "error": self.error,
            "result": self.result
        }

    async def broadcast(self):
        """广播当前进度"""
        await manager.broadcast_task_progress(
            self.task_id,
            {
                "type": "progress",
                "data": self.to_dict()
            }
        )


class ProgressTracker:
    """进度跟踪器(支持WebSocket)"""

    def __init__(self):
        # 活跃任务: {task_id: TaskProgress}
        self.active_tasks: Dict[str, TaskProgress] = {}

    def create_task(self,
                   task_id: str,
                   task_name: str,
                   total_steps: int = 100) -> TaskProgress:
        """创建新任务"""
        task = TaskProgress(task_id, task_name, total_steps)
        self.active_tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[TaskProgress]:
        """获取任务"""
        return self.active_tasks.get(task_id)

    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务状态"""
        return {
            task_id: task.to_dict()
            for task_id, task in self.active_tasks.items()
        }

    async def update_and_broadcast(self,
                                   task_id: str,
                                   current_step: int,
                                   message: str = ""):
        """更新并广播进度"""
        task = self.get_task(task_id)
        if task:
            task.update(current_step, message)
            await task.broadcast()


# 全局进度跟踪器实例
tracker = ProgressTracker()


# WebSocket路由辅助函数
async def handle_websocket_progress(websocket: WebSocket, client_id: str):
    """
    处理WebSocket进度连接

    使用示例:
    @app.websocket("/ws/progress/{client_id}")
    async def websocket_progress(websocket: WebSocket, client_id: str):
        await handle_websocket_progress(websocket, client_id)
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action")

            if action == "subscribe":
                # 订阅任务
                task_id = message.get("task_id")
                if task_id:
                    manager.subscribe_task(client_id, task_id)

                    # 发送当前任务状态
                    task = tracker.get_task(task_id)
                    if task:
                        await manager.send_personal_message(
                            {
                                "type": "progress",
                                "data": task.to_dict()
                            },
                            client_id
                        )

            elif action == "unsubscribe":
                # 取消订阅
                task_id = message.get("task_id")
                if task_id:
                    manager.unsubscribe_task(client_id, task_id)

            elif action == "list_tasks":
                # 列出所有任务
                await manager.send_personal_message(
                    {
                        "type": "task_list",
                        "data": tracker.get_all_tasks()
                    },
                    client_id
                )

            elif action == "ping":
                # 心跳
                await manager.send_personal_message(
                    {"type": "pong"},
                    client_id
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket错误 (client: {client_id}): {e}")
        manager.disconnect(client_id)


# 便捷装饰器
def track_progress(task_name: str, total_steps: int = 100):
    """
    进度跟踪装饰器

    使用示例:
    @track_progress("数据导入", total_steps=100)
    async def import_data(task_id: str, ...):
        # 获取任务进度对象
        task = tracker.get_task(task_id)

        for i in range(100):
            # 更新进度
            await tracker.update_and_broadcast(task_id, i+1, f"处理第{i+1}项")

        return "导入完成"
    """
    def decorator(func):
        async def wrapper(task_id: str, *args, **kwargs):
            # 创建任务
            task = tracker.create_task(task_id, task_name, total_steps)
            task.start()
            await task.broadcast()

            try:
                # 执行函数
                result = await func(task_id, *args, **kwargs)

                # 完成任务
                task.complete(result)
                await task.broadcast()

                return result

            except Exception as e:
                # 任务失败
                task.fail(str(e))
                await task.broadcast()
                raise

        return wrapper
    return decorator
