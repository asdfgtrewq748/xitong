# backend/user_feedback.py
"""
用户反馈和错误提示优化模块
提供友好的错误信息、建议和帮助
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ErrorLevel(Enum):
    """错误级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(Enum):
    """错误代码"""
    # 数据相关
    INSUFFICIENT_DATA_POINTS = "E1001"
    INVALID_DATA_FORMAT = "E1002"
    MISSING_REQUIRED_COLUMNS = "E1003"
    DATA_OUT_OF_RANGE = "E1004"
    DUPLICATE_DATA = "E1005"

    # 插值相关
    INTERPOLATION_FAILED = "E2001"
    METHOD_NOT_SUPPORTED = "E2002"
    POINTS_COLLINEAR = "E2003"

    # 文件相关
    FILE_TOO_LARGE = "E3001"
    FILE_FORMAT_ERROR = "E3002"
    FILE_READ_ERROR = "E3003"

    # 计算相关
    CALCULATION_ERROR = "E4001"
    TIMEOUT = "E4002"
    MEMORY_ERROR = "E4003"

    # 系统相关
    DATABASE_ERROR = "E5001"
    NETWORK_ERROR = "E5002"
    PERMISSION_DENIED = "E5003"


@dataclass
class UserMessage:
    """用户消息"""
    level: ErrorLevel
    code: str
    title: str
    message: str
    suggestions: List[str]
    details: Optional[Dict[str, Any]] = None
    help_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "level": self.level.value,
            "code": self.code,
            "title": self.title,
            "message": self.message,
            "suggestions": self.suggestions,
            "details": self.details or {},
            "help_url": self.help_url
        }


class FriendlyErrorHandler:
    """友好的错误处理器"""

    # 错误消息模板
    ERROR_TEMPLATES = {
        ErrorCode.INSUFFICIENT_DATA_POINTS: {
            "title": "数据点不足",
            "message": "数据点太少，无法进行{method}插值\n当前数据点: {current}个\n最少需要: {required}个",
            "suggestions": [
                "补充更多钻孔数据",
                "或使用'{fallback_method}'方法 (需要{fallback_required}个点即可)",
                "检查数据是否有重复或无效记录"
            ]
        },

        ErrorCode.INVALID_DATA_FORMAT: {
            "title": "数据格式错误",
            "message": "文件'{filename}'的数据格式不正确\n错误详情: {error_detail}",
            "suggestions": [
                "确保文件是有效的CSV或Excel格式",
                "检查文件编码 (推荐使用UTF-8)",
                "参考示例文件格式",
                "联系技术支持获取帮助"
            ]
        },

        ErrorCode.MISSING_REQUIRED_COLUMNS: {
            "title": "缺少必需列",
            "message": "数据文件缺少必需的列\n缺少的列: {missing_columns}\n当前列: {current_columns}",
            "suggestions": [
                "添加缺少的列: {missing_columns}",
                "检查列名拼写是否正确",
                "参考数据模板",
                "尝试使用'列映射'功能重新映射列名"
            ]
        },

        ErrorCode.DATA_OUT_OF_RANGE: {
            "title": "数据超出范围",
            "message": "检测到数据超出合理范围\n字段: {field}\n有效范围: {min_val} - {max_val}\n发现值: {found_values}",
            "suggestions": [
                "检查数据输入是否正确",
                "确认数据单位是否匹配 (如厚度单位为米)",
                "使用'数据验证'功能自动修正",
                "删除或修改异常数据"
            ]
        },

        ErrorCode.INTERPOLATION_FAILED: {
            "title": "插值计算失败",
            "message": "'{method}'插值方法执行失败\n原因: {reason}",
            "suggestions": [
                "尝试使用更简单的插值方法 (如'线性插值')",
                "检查数据点是否分布合理",
                "降低网格分辨率",
                "使用'智能插值'让系统自动选择最佳方法"
            ]
        },

        ErrorCode.POINTS_COLLINEAR: {
            "title": "数据点共线",
            "message": "数据点几乎在一条直线上,无法进行{method}插值",
            "suggestions": [
                "补充更多空间分布均匀的数据点",
                "使用'最近邻插值'方法",
                "检查坐标数据是否正确"
            ]
        },

        ErrorCode.FILE_TOO_LARGE: {
            "title": "文件过大",
            "message": "文件'{filename}'超过大小限制\n文件大小: {file_size} MB\n最大允许: {max_size} MB",
            "suggestions": [
                "分割文件为多个小文件",
                "压缩数据 (删除不必要的列)",
                "联系管理员增加文件大小限制",
                "使用批量导入功能"
            ]
        },

        ErrorCode.FILE_FORMAT_ERROR: {
            "title": "文件格式错误",
            "message": "无法识别文件'{filename}'的格式\n支持的格式: {supported_formats}",
            "suggestions": [
                "确保文件扩展名正确 (.csv, .xlsx)",
                "尝试将文件另存为CSV格式",
                "检查文件是否损坏",
                "使用文本编辑器查看文件内容"
            ]
        },

        ErrorCode.CALCULATION_ERROR: {
            "title": "计算出错",
            "message": "关键层计算过程中发生错误\n错误信息: {error_message}",
            "suggestions": [
                "检查输入数据是否完整",
                "确认所有必需参数已填写",
                "尝试减少数据量",
                "查看详细日志获取更多信息"
            ]
        },

        ErrorCode.TIMEOUT: {
            "title": "操作超时",
            "message": "操作执行时间过长,已超时\n超时时间: {timeout}秒",
            "suggestions": [
                "降低数据规模或网格分辨率",
                "简化计算参数",
                "稍后重试",
                "联系管理员优化系统性能"
            ]
        },

        ErrorCode.DATABASE_ERROR: {
            "title": "数据库错误",
            "message": "数据库操作失败\n错误详情: {error_detail}",
            "suggestions": [
                "检查数据库连接是否正常",
                "刷新页面重试",
                "联系系统管理员",
                "查看系统日志获取详细信息"
            ]
        }
    }

    @classmethod
    def create_message(cls,
                      error_code: ErrorCode,
                      level: ErrorLevel = ErrorLevel.ERROR,
                      **kwargs) -> UserMessage:
        """
        创建用户友好的错误消息

        Args:
            error_code: 错误代码
            level: 错误级别
            **kwargs: 模板变量

        Returns:
            用户消息对象
        """
        template = cls.ERROR_TEMPLATES.get(error_code)

        if not template:
            # 默认消息
            return UserMessage(
                level=level,
                code=error_code.value,
                title="发生错误",
                message=kwargs.get("message", "操作失败,请稍后重试"),
                suggestions=["刷新页面重试", "联系技术支持"],
                details=kwargs
            )

        # 格式化消息
        try:
            message = template["message"].format(**kwargs)
        except KeyError:
            message = template["message"]

        # 格式化建议
        suggestions = []
        for suggestion in template["suggestions"]:
            try:
                suggestions.append(suggestion.format(**kwargs))
            except KeyError:
                suggestions.append(suggestion)

        return UserMessage(
            level=level,
            code=error_code.value,
            title=template["title"],
            message=message,
            suggestions=suggestions,
            details=kwargs,
            help_url=kwargs.get("help_url")
        )

    @classmethod
    def create_success_message(cls, title: str, message: str,
                               details: Optional[Dict] = None) -> UserMessage:
        """创建成功消息"""
        return UserMessage(
            level=ErrorLevel.INFO,
            code="S0000",
            title=title,
            message=message,
            suggestions=[],
            details=details
        )

    @classmethod
    def create_warning_message(cls, title: str, message: str,
                               suggestions: List[str],
                               details: Optional[Dict] = None) -> UserMessage:
        """创建警告消息"""
        return UserMessage(
            level=ErrorLevel.WARNING,
            code="W0000",
            title=title,
            message=message,
            suggestions=suggestions,
            details=details
        )


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total_steps: int, description: str = ""):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.step_descriptions = []
        self.errors = []
        self.warnings = []

    def update(self, step: int, step_description: str = ""):
        """更新进度"""
        self.current_step = step
        if step_description:
            self.step_descriptions.append(step_description)

    def add_error(self, error: str):
        """添加错误"""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)

    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        percentage = (self.current_step / self.total_steps * 100) if self.total_steps > 0 else 0

        return {
            "percentage": round(percentage, 1),
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "description": self.description,
            "current_step_description": self.step_descriptions[-1] if self.step_descriptions else "",
            "errors": self.errors,
            "warnings": self.warnings,
            "is_complete": self.current_step >= self.total_steps
        }


def create_interpolation_error(method: str, current_points: int,
                               required_points: int,
                               fallback_method: str = "线性插值",
                               fallback_required: int = 3) -> UserMessage:
    """创建插值错误消息的便捷函数"""
    return FriendlyErrorHandler.create_message(
        ErrorCode.INSUFFICIENT_DATA_POINTS,
        method=method,
        current=current_points,
        required=required_points,
        fallback_method=fallback_method,
        fallback_required=fallback_required
    )


def create_validation_warning(field: str, min_val: float, max_val: float,
                             found_values: List[float]) -> UserMessage:
    """创建数据验证警告的便捷函数"""
    return FriendlyErrorHandler.create_message(
        ErrorCode.DATA_OUT_OF_RANGE,
        level=ErrorLevel.WARNING,
        field=field,
        min_val=min_val,
        max_val=max_val,
        found_values=", ".join([f"{v:.2f}" for v in found_values[:5]]) +
                     ("..." if len(found_values) > 5 else "")
    )


def create_file_error(filename: str, error_detail: str) -> UserMessage:
    """创建文件错误消息的便捷函数"""
    return FriendlyErrorHandler.create_message(
        ErrorCode.FILE_FORMAT_ERROR,
        filename=filename,
        supported_formats="CSV (.csv), Excel (.xlsx, .xls)",
        error_detail=error_detail
    )
