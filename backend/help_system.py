# backend/help_system.py
"""
帮助和引导系统
提供操作指引、提示和文档
"""

from typing import Dict, List, Optional
from enum import Enum


class TutorialStep(Enum):
    """教程步骤"""
    WELCOME = "welcome"
    UPLOAD_FILE = "upload_file"
    VIEW_DATA = "view_data"
    CREATE_MODEL = "create_model"
    EXPORT_RESULTS = "export_results"
    COMPLETED = "completed"


class HelpCategory(Enum):
    """帮助分类"""
    GETTING_STARTED = "getting_started"
    DATA_IMPORT = "data_import"
    MODELING = "modeling"
    ANALYSIS = "analysis"
    EXPORT = "export"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"


class HelpSystem:
    """帮助系统"""

    # 新手教程配置
    TUTORIAL_STEPS = {
        TutorialStep.WELCOME: {
            "title": "欢迎使用煤层地质建模系统",
            "content": "本系统用于煤层地质数据管理和3D建模可视化。\n\n让我们通过几个步骤快速上手!",
            "target": "#app",
            "position": "center",
            "actions": ["开始教程", "跳过"],
            "tips": [
                "系统支持CSV和Excel格式的钻孔数据",
                "可以进行多种插值方法的3D建模",
                "支持关键层分析和数据导出"
            ]
        },

        TutorialStep.UPLOAD_FILE: {
            "title": "第一步: 上传钻孔数据",
            "content": "点击'钻孔分析'菜单,然后上传您的钻孔数据文件。\n\n支持的格式: CSV, Excel (.xlsx, .xls)",
            "target": "#upload-button",
            "position": "bottom",
            "actions": ["下一步", "跳过"],
            "tips": [
                "确保文件包含必需列: 岩层名称、厚度",
                "建议包含完整的岩石力学参数",
                "可以同时上传多个文件"
            ]
        },

        TutorialStep.VIEW_DATA: {
            "title": "第二步: 查看和编辑数据",
            "content": "在数据库浏览器中,您可以查看、编辑和管理已导入的数据。\n\n支持搜索、过滤和排序功能。",
            "target": "#database-viewer",
            "position": "left",
            "actions": ["下一步", "跳过"],
            "tips": [
                "点击行可以编辑数据",
                "使用搜索框快速定位记录",
                "支持批量删除操作"
            ]
        },

        TutorialStep.CREATE_MODEL: {
            "title": "第三步: 创建3D模型",
            "content": "在'地质建模'模块,选择插值方法和参数,生成3D煤层模型。\n\n提供多种插值方法供选择。",
            "target": "#modeling-section",
            "position": "right",
            "actions": ["下一步", "跳过"],
            "tips": [
                "推荐使用'智能插值'自动选择最佳方法",
                "分辨率越高,模型越精细但计算越慢",
                "可以使用'插值对比'选择最佳方法"
            ]
        },

        TutorialStep.EXPORT_RESULTS: {
            "title": "第四步: 导出结果",
            "content": "完成建模后,可以导出数据、图表和报告。\n\n支持多种格式: CSV, Excel, PDF, 图片。",
            "target": "#export-button",
            "position": "top",
            "actions": ["完成教程"],
            "tips": [
                "PDF报告包含统计数据和可视化图表",
                "图表可以导出为高清PNG图片",
                "支持批量导出多个钻孔数据"
            ]
        },

        TutorialStep.COMPLETED: {
            "title": "教程完成!",
            "content": "恭喜您完成新手教程!\n\n现在可以开始使用系统进行地质建模了。\n\n如需帮助,随时点击右上角的'帮助'按钮。",
            "target": "#app",
            "position": "center",
            "actions": ["开始使用"],
            "tips": []
        }
    }

    # 帮助文档
    HELP_DOCS = {
        HelpCategory.GETTING_STARTED: {
            "title": "快速入门",
            "icon": "🚀",
            "sections": [
                {
                    "title": "系统概述",
                    "content": "煤层地质建模系统是一个用于煤层地质数据管理、分析和3D可视化的专业工具。\n\n主要功能:\n- 钻孔数据导入和管理\n- 多种插值方法的3D建模\n- 关键层分析\n- 数据可视化和导出"
                },
                {
                    "title": "系统要求",
                    "content": "浏览器: Chrome 90+, Firefox 88+, Edge 90+\n屏幕分辨率: 建议 1920x1080 或更高\n网络: 需要稳定的网络连接"
                },
                {
                    "title": "基本流程",
                    "content": "1. 准备钻孔数据文件 (CSV或Excel)\n2. 上传数据到系统\n3. 查看和验证数据\n4. 选择插值方法创建3D模型\n5. 导出结果和报告"
                }
            ]
        },

        HelpCategory.DATA_IMPORT: {
            "title": "数据导入",
            "icon": "📁",
            "sections": [
                {
                    "title": "文件格式要求",
                    "content": "支持格式: CSV (.csv), Excel (.xlsx, .xls)\n\n必需列:\n- 岩层名称\n- 厚度/m\n\n可选列:\n- 弹性模量/GPa\n- 容重/kN·m-3\n- 抗拉强度/MPa"
                },
                {
                    "title": "导入步骤",
                    "content": "1. 点击'钻孔分析'菜单\n2. 点击'上传文件'按钮\n3. 选择一个或多个文件\n4. 等待处理完成\n5. 查看导入结果"
                },
                {
                    "title": "常见问题",
                    "content": "Q: 文件上传失败?\nA: 检查文件格式、大小(限制50MB)和编码(推荐UTF-8)\n\nQ: 缺少必需列?\nA: 确保文件包含'岩层名称'和'厚度/m'列\n\nQ: 数据显示异常?\nA: 使用'数据验证'功能检查数据质量"
                }
            ]
        },

        HelpCategory.MODELING: {
            "title": "地质建模",
            "icon": "🏔️",
            "sections": [
                {
                    "title": "插值方法介绍",
                    "content": "系统提供多种插值方法:\n\n- 线性插值: 快速,适合数据点较少\n- 三次样条: 平滑,需要16个以上点\n- 克里金插值: 精确,考虑空间相关性\n- 智能插值: 自动选择最佳方法(推荐)"
                },
                {
                    "title": "参数说明",
                    "content": "分辨率: 网格密度,范围20-200\n- 低分辨率(20-50): 快速预览\n- 中分辨率(50-100): 平衡质量和速度\n- 高分辨率(100-200): 高质量,计算较慢\n\n基准高程: 模型底部高程\n煤层间隙: 相邻煤层间的间隔"
                },
                {
                    "title": "插值对比",
                    "content": "使用'插值对比'功能比较不同方法:\n\n1. 选择要对比的方法\n2. 系统自动计算各方法的精度指标\n3. 查看MAE, RMSE, R²等指标\n4. 选择最优方法进行建模"
                }
            ]
        },

        HelpCategory.ANALYSIS: {
            "title": "数据分析",
            "icon": "📊",
            "sections": [
                {
                    "title": "关键层分析",
                    "content": "关键层分析用于识别煤层上覆岩层中的关键控制层。\n\n必需数据:\n- 岩层厚度\n- 弹性模量\n- 容重\n- 抗拉强度\n\n结果包括:\n- 关键层位置(SK1, SK2, ...)\n- 主关键层(PKS)\n- 距煤层距离"
                },
                {
                    "title": "数据统计",
                    "content": "系统提供丰富的统计功能:\n\n- 基本统计: 总记录数、钻孔数、省份数\n- 岩性统计: 各类岩性分布和占比\n- 参数统计: 厚度、强度等参数的平均值、最大最小值\n- 省份分布: 各省份钻孔数量和分布"
                },
                {
                    "title": "可视化图表",
                    "content": "支持多种图表类型:\n\n- 柱状图: 岩性分布、省份统计\n- 饼图: 占比分析\n- 玫瑰图: 多维度分布\n- 雷达图: 参数对比\n- 热力图: 空间分布\n- 3D模型: 煤层立体展示"
                }
            ]
        },

        HelpCategory.EXPORT: {
            "title": "导出功能",
            "icon": "💾",
            "sections": [
                {
                    "title": "数据导出",
                    "content": "支持的格式:\n- CSV: 通用数据格式\n- Excel: 包含格式的电子表格\n- JSON: 程序化处理\n\n导出选项:\n- 导出全部数据\n- 导出筛选后的数据\n- 导出选中的记录"
                },
                {
                    "title": "图表导出",
                    "content": "图表可以导出为:\n- PNG: 高清图片(推荐)\n- JPG: 压缩图片\n- SVG: 矢量图(可缩放)\n\n导出设置:\n- 分辨率: 800x600 到 4K\n- 背景: 透明或白色\n- 包含标题和图例"
                },
                {
                    "title": "PDF报告",
                    "content": "自动生成专业报告:\n\n报告内容:\n- 封面: 项目信息和日期\n- 数据统计: 汇总表格\n- 可视化图表: 自动截图\n- 分析结论: 自动生成或手动编辑\n\n适用场景:\n- 项目汇报\n- 存档备份\n- 对外分享"
                }
            ]
        },

        HelpCategory.TROUBLESHOOTING: {
            "title": "故障排除",
            "icon": "🔧",
            "sections": [
                {
                    "title": "常见错误",
                    "content": "1. 插值失败\n原因: 数据点太少或分布不均\n解决: 增加数据点或使用更简单的插值方法\n\n2. 计算超时\n原因: 分辨率过高或数据量过大\n解决: 降低分辨率或分批处理\n\n3. 文件上传失败\n原因: 文件过大、格式错误或网络问题\n解决: 检查文件格式,压缩数据,重试"
                },
                {
                    "title": "性能优化",
                    "content": "提升系统性能的建议:\n\n1. 降低网格分辨率\n2. 关闭不必要的可视化\n3. 清理浏览器缓存\n4. 使用高性能电脑\n5. 避免同时打开多个标签页"
                },
                {
                    "title": "数据质量问题",
                    "content": "如何改善数据质量:\n\n1. 使用'数据验证'功能自动检查\n2. 删除或修正异常值\n3. 补充缺失的参数\n4. 确保坐标准确性\n5. 使用标准单位(米、GPa、kN/m³等)"
                }
            ]
        },

        HelpCategory.FAQ: {
            "title": "常见问题",
            "icon": "❓",
            "sections": [
                {
                    "title": "账号和权限",
                    "content": "Q: 需要注册账号吗?\nA: 目前系统开放使用,无需注册。未来版本将支持账号管理。\n\nQ: 数据会保存吗?\nA: 数据保存在浏览器本地存储和服务器数据库中。\n\nQ: 可以分享数据吗?\nA: 可以导出数据文件或PDF报告分享给他人。"
                },
                {
                    "title": "功能相关",
                    "content": "Q: 支持哪些地区的数据?\nA: 支持全国范围的煤层地质数据。\n\nQ: 可以导入多个钻孔吗?\nA: 可以,支持批量导入和合并分析。\n\nQ: 3D模型可以旋转查看吗?\nA: 可以,使用鼠标拖动旋转,滚轮缩放。"
                },
                {
                    "title": "技术支持",
                    "content": "Q: 遇到问题怎么办?\nA: 1. 查看本帮助文档\n2. 查看错误提示和建议\n3. 联系技术支持\n\nQ: 如何反馈建议?\nA: 欢迎通过邮件或GitHub提交反馈和建议。"
                }
            ]
        }
    }

    @classmethod
    def get_tutorial_step(cls, step: TutorialStep) -> Dict:
        """获取教程步骤"""
        return cls.TUTORIAL_STEPS.get(step, {})

    @classmethod
    def get_all_tutorial_steps(cls) -> List[Dict]:
        """获取所有教程步骤"""
        return [
            {
                "step": step.value,
                **data
            }
            for step, data in cls.TUTORIAL_STEPS.items()
        ]

    @classmethod
    def get_help_doc(cls, category: HelpCategory) -> Dict:
        """获取帮助文档"""
        return cls.HELP_DOCS.get(category, {})

    @classmethod
    def get_all_help_categories(cls) -> List[Dict]:
        """获取所有帮助分类"""
        return [
            {
                "category": category.value,
                **data
            }
            for category, data in cls.HELP_DOCS.items()
        ]

    @classmethod
    def search_help(cls, keyword: str) -> List[Dict]:
        """搜索帮助文档"""
        results = []
        keyword_lower = keyword.lower()

        for category, doc in cls.HELP_DOCS.items():
            if keyword_lower in doc["title"].lower():
                results.append({
                    "category": category.value,
                    "title": doc["title"],
                    "match_type": "title"
                })

            for section in doc["sections"]:
                if (keyword_lower in section["title"].lower() or
                    keyword_lower in section["content"].lower()):
                    results.append({
                        "category": category.value,
                        "title": doc["title"],
                        "section": section["title"],
                        "match_type": "content"
                    })

        return results


# 便捷函数
def get_tutorial() -> List[Dict]:
    """获取新手教程"""
    return HelpSystem.get_all_tutorial_steps()


def get_help_docs() -> List[Dict]:
    """获取所有帮助文档"""
    return HelpSystem.get_all_help_categories()


def search_help(keyword: str) -> List[Dict]:
    """搜索帮助"""
    return HelpSystem.search_help(keyword)
