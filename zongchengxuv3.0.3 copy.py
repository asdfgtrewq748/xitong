import sys
import os
import re
import logging
import traceback
import importlib
import json
from functools import partial
from typing import List, Tuple, Optional, Dict, Any, Set
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import time  # 添加time模块导入
import threading  # 如果使用多线程超时保护，请添加此行
import warnings  # 如果使用warnings.catch_warnings()，请添加此行
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use('QtAgg')
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, 使Matplotlib注册3D投影
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from coal_seam_blocks.aggregator import aggregate_boreholes
from coal_seam_blocks.modeling import build_block_models

from app import load_app_config
from app.core import configure_logging
from app.services.lithology_colors import LithologyColorManager
from app.workers import FunctionWorker, TaskHandle

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTabWidget, QFileDialog, QMessageBox,
    QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QSlider,
    QGroupBox, QFormLayout, QGridLayout, QStackedWidget, QProgressBar,
    QSizePolicy, QProgressDialog, QAbstractItemView, QDoubleSpinBox,
    QSpinBox, QListWidget, QListWidgetItem, QCheckBox, QDialog,
    QDialogButtonBox, QTextBrowser, QRadioButton, QButtonGroup,
    QGraphicsDropShadowEffect
)

try:  # pragma: no cover - optional dependency
    qt_webengine = importlib.import_module("PyQt6.QtWebEngineWidgets")
    QWebEngineView = getattr(qt_webengine, "QWebEngineView", None)
except Exception:
    QWebEngineView = None


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def resolve_app_icon_path() -> str:
    candidates = [
        "Gemini_Generated_Image_3yuo953yuo953yuo.png",
        "icons/geology_shield.png",
        "icons/app_icon.png",
    ]
    for candidate in candidates:
        path = resource_path(candidate)
        if os.path.exists(path):
            return path
    return ""


def _resolve_local_asset_url(relative_path: str) -> Optional[str]:
    path = resource_path(relative_path)
    if os.path.exists(path):
        try:
            return QUrl.fromLocalFile(path).toString()
        except Exception:
            return None
    return None


_local_echarts = _resolve_local_asset_url("static/echarts/echarts.min.js")

def _load_china_geojson() -> Optional[Dict[str, Any]]:
    try:
        from pyecharts.datasets import map_file_reader  # type: ignore

        content = map_file_reader("china.json")
        if content:
            try:
                return json.loads(content)
            except Exception:
                pass
    except Exception:
        pass

    candidate_paths = [
        "static/echarts/china.json",
        os.path.join("data", "china.json"),
        os.path.join("data", "china_geo.json"),
    ]

    for relative in candidate_paths:
        try_path = resource_path(relative)
        if os.path.exists(try_path):
            try:
                with open(try_path, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except Exception:
                continue

    return None


CHINA_GEOJSON_DATA: Optional[Dict[str, Any]] = _load_china_geojson()
_local_china = _resolve_local_asset_url("static/echarts/china.js") if CHINA_GEOJSON_DATA is None else None

ECHARTS_JS_CDN_LIST = [
    src for src in [
        _local_echarts,
        "https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js",
        "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js",
        "https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/echarts/5.5.1/echarts.min.js",
        "https://registry.npmmirror.com/echarts/latest/files/dist/echarts.min.js",
    ]
    if src
]

if CHINA_GEOJSON_DATA is None:
    ECHARTS_CHINA_CDN_LIST = [
        src for src in [
            _local_china,
            "https://fastly.jsdelivr.net/npm/echarts@5/map/js/china.js",
            "https://cdn.jsdelivr.net/npm/echarts@5/map/js/china.js",
            "https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/echarts/5.5.1/map/js/china.js",
            "https://registry.npmmirror.com/echarts/latest/files/map/js/china.js",
        ]
        if src
    ]
else:
    ECHARTS_CHINA_CDN_LIST = []


def _build_simplified_china_geojson() -> Dict[str, Any]:
    layout = [
        {"name": "北京市", "lon": 116.40, "lat": 39.90, "width": 1.6, "height": 1.6},
        {"name": "天津市", "lon": 117.36, "lat": 39.34, "width": 1.4, "height": 1.4},
        {"name": "上海市", "lon": 121.47, "lat": 31.23, "width": 1.6, "height": 1.2},
        {"name": "重庆市", "lon": 106.55, "lat": 29.56, "width": 2.8, "height": 2.4},
        {"name": "河北省", "lon": 114.50, "lat": 38.00, "width": 6.4, "height": 5.2},
        {"name": "山西省", "lon": 112.55, "lat": 37.86, "width": 5.4, "height": 4.2},
        {"name": "辽宁省", "lon": 123.43, "lat": 41.80, "width": 4.2, "height": 3.4},
        {"name": "吉林省", "lon": 125.32, "lat": 43.90, "width": 4.6, "height": 4.6},
        {"name": "黑龙江省", "lon": 128.03, "lat": 47.36, "width": 6.8, "height": 6.4},
        {"name": "江苏省", "lon": 119.37, "lat": 32.97, "width": 4.4, "height": 3.6},
        {"name": "浙江省", "lon": 120.09, "lat": 29.18, "width": 3.8, "height": 3.2},
        {"name": "安徽省", "lon": 117.28, "lat": 31.86, "width": 4.8, "height": 4.2},
        {"name": "福建省", "lon": 118.70, "lat": 26.08, "width": 4.4, "height": 4.2},
        {"name": "江西省", "lon": 115.85, "lat": 27.64, "width": 4.4, "height": 4.2},
        {"name": "山东省", "lon": 117.00, "lat": 36.67, "width": 4.8, "height": 4.2},
        {"name": "河南省", "lon": 113.73, "lat": 34.76, "width": 4.8, "height": 4.2},
        {"name": "湖北省", "lon": 114.27, "lat": 30.98, "width": 4.8, "height": 4.4},
        {"name": "湖南省", "lon": 112.98, "lat": 27.90, "width": 4.8, "height": 4.4},
        {"name": "广东省", "lon": 113.26, "lat": 23.12, "width": 5.4, "height": 4.6},
        {"name": "海南省", "lon": 109.84, "lat": 19.03, "width": 3.6, "height": 2.6},
        {"name": "四川省", "lon": 103.99, "lat": 30.57, "width": 7.4, "height": 6.4},
        {"name": "贵州省", "lon": 106.71, "lat": 26.84, "width": 4.8, "height": 4.4},
        {"name": "云南省", "lon": 101.54, "lat": 25.04, "width": 5.8, "height": 5.4},
        {"name": "陕西省", "lon": 108.95, "lat": 34.27, "width": 4.8, "height": 4.4},
        {"name": "甘肃省", "lon": 103.84, "lat": 36.06, "width": 7.6, "height": 5.6},
        {"name": "青海省", "lon": 101.78, "lat": 36.62, "width": 6.8, "height": 5.6},
        {"name": "台湾省", "lon": 120.96, "lat": 23.80, "width": 2.8, "height": 3.6},
        {"name": "内蒙古自治区", "lon": 113.60, "lat": 44.00, "width": 12.4, "height": 5.4},
        {"name": "广西壮族自治区", "lon": 108.32, "lat": 23.83, "width": 5.4, "height": 4.8},
        {"name": "宁夏回族自治区", "lon": 106.27, "lat": 38.47, "width": 3.4, "height": 2.8},
        {"name": "新疆维吾尔自治区", "lon": 85.20, "lat": 41.10, "width": 10.8, "height": 7.6},
        {"name": "西藏自治区", "lon": 88.14, "lat": 31.10, "width": 9.6, "height": 6.6},
        {"name": "香港特别行政区", "lon": 114.17, "lat": 22.32, "width": 0.8, "height": 0.6},
        {"name": "澳门特别行政区", "lon": 113.55, "lat": 22.19, "width": 0.6, "height": 0.5},
        {"name": "南海诸岛", "lon": 112.00, "lat": 15.00, "width": 7.0, "height": 4.0},
    ]

    features: List[Dict[str, Any]] = []
    for entry in layout:
        half_w = entry["width"] / 2.0
        half_h = entry["height"] / 2.0
        coordinates = [
            [entry["lon"] - half_w, entry["lat"] - half_h],
            [entry["lon"] + half_w, entry["lat"] - half_h],
            [entry["lon"] + half_w, entry["lat"] + half_h],
            [entry["lon"] - half_w, entry["lat"] + half_h],
            [entry["lon"] - half_w, entry["lat"] - half_h],
        ]

        features.append({
            "type": "Feature",
            "id": entry["name"],
            "properties": {"name": entry["name"]},
            "geometry": {"type": "Polygon", "coordinates": [coordinates]},
        })

    return {"type": "FeatureCollection", "features": features}


if CHINA_GEOJSON_DATA is None:
    CHINA_GEOJSON_DATA = _build_simplified_china_geojson()
    ECHARTS_CHINA_CDN_LIST = []


def build_china_map_html(
    data_pairs: List[Tuple[str, float]],
    *,
    title: str,
    subtitle: str = "",
    tooltip_formatter: str = "{b}：{c}",
    value_unit: str = "",
    color_range: Optional[List[str]] = None,
    zoom: float = 1.05,
    center: Optional[Tuple[float, float]] = None,
    hide_south_china_sea: bool = True,
    enable_bridge: bool = False,
    empty_message: str = "暂无数据可用于绘制地图。",
) -> str:
    """构建中国省份地图的 HTML 字符串，兼容 Qt WebEngine 嵌入。"""

    sanitized: List[Dict[str, Any]] = []
    for name, value in data_pairs:
        if not name:
            continue
        if hide_south_china_sea and name == "南海诸岛":
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        sanitized.append({"name": name, "value": numeric_value})

    if not sanitized:
        return f"""
<!DOCTYPE html>
<html lang='zh-CN'>
<head><meta charset='utf-8'></head>
<body style='margin:0;padding:0;display:flex;align-items:center;justify-content:center;min-height:100%;background:#ffffff;color:#94a3b8;font-family: \"Microsoft YaHei\", system-ui, sans-serif;'>
    <div style='text-align:center;font-size:14px;line-height:1.6;'>{empty_message}</div>
</body>
</html>
"""

    max_value = max(item["value"] for item in sanitized)
    min_value = min(item["value"] for item in sanitized)
    if max_value <= 0:
        max_value = 1
    color_range = color_range or ["#f0f9ff", "#0f766e"]

    regions: List[Dict[str, Any]] = []
    if hide_south_china_sea:
        regions.append({
            "name": "南海诸岛",
            "itemStyle": {"opacity": 0},
            "label": {"show": False},
        })

    option = {
        "backgroundColor": "transparent",
        "title": {
            "text": title,
            "subtext": subtitle,
            "left": "center",
            "top": 8,
            "textStyle": {"fontSize": 18, "color": "#0f172a"},
            "subtextStyle": {"fontSize": 12, "color": "#64748b"},
        },
        "tooltip": {
            "trigger": "item",
            "formatter": tooltip_formatter + (value_unit if value_unit else ""),
        },
        "visualMap": {
            "min": 0 if min_value >= 0 else float(min_value),
            "max": float(max_value),
            "left": "left",
            "bottom": 20,
            "text": ["高", "低"],
            "calculable": True,
            "inRange": {"color": color_range},
        },
        "series": [
            {
                "name": title,
                "type": "map",
                "map": "china",
                "roam": True,
                "zoom": zoom,
                "center": list(center or (104.0, 35.2)),
                "label": {"show": False, "color": "#334155"},
                "emphasis": {
                    "label": {"show": True, "color": "#0f172a"},
                    "itemStyle": {"areaColor": "#22d3ee"},
                },
                "itemStyle": {
                    "borderColor": "#cbd5f5",
                    "borderWidth": 1,
                    "areaColor": "#f5fbff",
                },
                "data": sanitized,
                "regions": regions,
            }
        ],
    }

    option_json = json.dumps(option, ensure_ascii=False)

    bridge_setup = ""
    if enable_bridge:
        bridge_setup = """
    window.__chinaMapSetupBridge = function () {
        if (!window.__chinaMapInstance) { return; }
        window.__chinaMapInstance.off('click');
        if (window.bridge && window.bridge.onProvinceClicked) {
            window.__chinaMapInstance.on('click', function (params) {
                if (params && params.name) {
                    window.bridge.onProvinceClicked(params.name);
                }
            });
        }
    };
"""
    else:
        bridge_setup = "window.__chinaMapSetupBridge = function () {};"

    html = f"""
<!DOCTYPE html>
<html lang='zh-CN'>
<head>
    <meta charset='utf-8'>
    <style>
        html, body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            background: #ffffff;
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
        }}
        #main {{
            width: 100%;
            height: 100%;
        }}
    </style>
    <script type='text/javascript' src='qrc:///qtwebchannel/qwebchannel.js'></script>
</head>
<body>
    <div id='main'></div>
    <script type='text/javascript'>
        var chartOption = {option_json};
        var echartsSources = {json.dumps(ECHARTS_JS_CDN_LIST, ensure_ascii=False)};
        var chinaSources = {json.dumps(ECHARTS_CHINA_CDN_LIST, ensure_ascii=False)};
        var inlineChinaGeo = {json.dumps(CHINA_GEOJSON_DATA, ensure_ascii=False)};
        window.__chinaMapInstance = null;
        window.__chinaMapReadyPromise = null;
        window.__chinaMapRegistered = false;

        function loadScriptWithFallback(urls, onSuccess, onFailure) {{
            if (!urls || urls.length === 0) {{
                if (typeof onFailure === 'function') {{ onFailure(); }}
                return;
            }}
            var list = urls.slice();
            var current = list.shift();
            var script = document.createElement('script');
            script.async = true;
            script.onload = function () {{
                if (typeof onSuccess === 'function') {{ onSuccess(); }}
            }};
            script.onerror = function () {{
                script.remove();
                loadScriptWithFallback(list, onSuccess, onFailure);
            }};
            script.src = current;
            document.head.appendChild(script);
        }}

        function showFallback(message) {{
            var dom = document.getElementById('main');
            if (!dom) {{ return; }}
            dom.innerHTML = "<div style='display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;font-size:14px;padding:24px;text-align:center;line-height:1.6;'>" + message + "</div>";
        }}

        function registerInlineChinaGeo() {{
            if (!inlineChinaGeo || typeof echarts === 'undefined') {{
                return false;
            }}
            if (window.__chinaMapRegistered) {{
                return true;
            }}
            try {{
                echarts.registerMap('china', inlineChinaGeo);
                window.__chinaMapRegistered = true;
                return true;
            }} catch (err) {{
                console.error('注册中国地图失败', err);
                return false;
            }}
        }}

        function ensureChinaMapResources() {{
            if (window.__chinaMapReadyPromise) {{
                return window.__chinaMapReadyPromise;
            }}

            window.__chinaMapReadyPromise = new Promise(function (resolve, reject) {{
                function completeIfReady() {{
                    registerInlineChinaGeo();
                    if (typeof echarts !== 'undefined' && echarts.getMap && echarts.getMap('china')) {{
                        resolve();
                        return true;
                    }}
                    return false;
                }}

                function loadChinaMapData() {{
                    if (completeIfReady()) {{ return; }}

                    if (!chinaSources || chinaSources.length === 0) {{
                        if (inlineChinaGeo) {{
                            if (!completeIfReady()) {{
                                reject(new Error('内置中国地图数据注册失败'));
                            }}
                        }} else {{
                            reject(new Error('中国地图底图脚本加载失败'));
                        }}
                        return;
                    }}

                    loadScriptWithFallback(chinaSources, function () {{
                        if (!completeIfReady()) {{
                            reject(new Error('中国地图底图脚本加载后仍未就绪'));
                        }}
                    }}, function () {{
                        reject(new Error('中国地图底图脚本加载失败'));
                    }});
                }}

                if (typeof echarts !== 'undefined') {{
                    loadChinaMapData();
                    return;
                }}

                loadScriptWithFallback(echartsSources, function () {{
                    registerInlineChinaGeo();
                    loadChinaMapData();
                }}, function () {{
                    reject(new Error('ECharts 核心库加载失败'));
                }});
            }});

            window.__chinaMapReadyPromise.catch(function () {{
                window.__chinaMapReadyPromise = null;
            }});

            return window.__chinaMapReadyPromise;
        }}

        function initChinaMap() {{
            if (typeof echarts === 'undefined') {{ return; }}
            var dom = document.getElementById('main');
            if (!dom) {{ return; }}
            dom.innerHTML = '';
            window.__chinaMapInstance = echarts.init(dom, null, {{ renderer: 'canvas' }});
            window.__chinaMapInstance.setOption(chartOption);
            {bridge_setup}
            window.__chinaMapSetupBridge();
            window.addEventListener('resize', function () {{
                if (window.__chinaMapInstance) {{
                    window.__chinaMapInstance.resize();
                }}
            }});
        }}

        function connectQtBridge() {{
            if (typeof qt === 'undefined' || !qt.webChannelTransport || typeof QWebChannel === 'undefined') {{
                initChinaMap();
                return;
            }}
            new QWebChannel(qt.webChannelTransport, function (channel) {{
                window.bridge = channel.objects.bridge;
                initChinaMap();
                if (window.__chinaMapSetupBridge) {{
                    window.__chinaMapSetupBridge();
                }}
            }});
        }}

        function startChinaMap() {{
            ensureChinaMapResources().then(function () {{
                connectQtBridge();
            }}).catch(function (error) {{
                console.error(error);
                showFallback('地图资源加载失败：' + (error && error.message ? error.message : '未知错误') + '。\\n请检查网络连接或在 static/echarts 目录下放置离线资源。');
            }});
        }}

        document.addEventListener('DOMContentLoaded', startChinaMap);

        window.__chinaMapRefresh = function () {{
            ensureChinaMapResources().then(function () {{
                if (window.__chinaMapInstance) {{
                    window.__chinaMapInstance.setOption(chartOption, true);
                    if (window.__chinaMapSetupBridge) {{
                        window.__chinaMapSetupBridge();
                    }}
                }} else {{
                    connectQtBridge();
                }}
            }}).catch(function (error) {{
                console.error(error);
                showFallback('地图刷新失败：' + (error && error.message ? error.message : '未知错误'));
            }});
        }};
    </script>
</body>
</html>
"""

    return html

def perform_startup_checks(app_config) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    data_root = resource_path(app_config.data_root)
    try:
        os.makedirs(data_root, exist_ok=True)
    except OSError as exc:
        errors.append(f"无法创建数据目录: {data_root}\n→ {exc}")
        return errors, warnings

    for subdir in ("input", "output"):
        path = os.path.join(data_root, subdir)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc:
            warnings.append(f"无法创建子目录 {subdir}: {exc}")

    icon_path = resolve_app_icon_path()
    if not icon_path:
        warnings.append("未找到可用的应用图标，界面将使用系统默认图标。")

    required_modules = [
        ("coal_seam_blocks.aggregator", "钻孔数据合并模块"),
        ("coal_seam_blocks.modeling", "块体建模模块"),
    ]
    for module_name, description in required_modules:
        if module_name not in sys.modules:
            try:
                __import__(module_name)
            except Exception as exc:
                errors.append(f"缺少依赖 {description} ({module_name})\n→ {exc}")

    return errors, warnings


def install_exception_hook():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.exception("未处理的异常", exc_info=(exc_type, exc_value, exc_traceback))
        detail = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        QMessageBox.critical(
            None,
            "发生未处理的错误",
            "应用运行过程中出现严重错误，已记录到日志。\n\n" + detail,
        )

    sys.excepthook = handle_exception


class LoginWidget(QWidget):
    def __init__(self, app_config, on_login_success, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("矿山工程分析系统 - 登录")
        self.resize(420, 350)
        self.setMinimumSize(380, 320)
        self.setMaximumSize(500, 400)
        self.setStyleSheet("background-color: #f8fafc;")
        icon_path = resolve_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(0)

        layout.addStretch(1)

        title = QLabel("欢迎使用矿山工程分析系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 20px;
            letter-spacing: 1px;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(15)

        card = QFrame()
        card.setFixedWidth(300)
        card.setStyleSheet("""
            QFrame {
                background: linear-gradient(145deg, #ffffff 0%, #fafbfc 100%);
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)

        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(28)
        card_shadow.setOffset(0, 16)
        card_shadow.setColor(QColor(30, 64, 175, 35))
        card.setGraphicsEffect(card_shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(8)

        user_label = QLabel("账号")
        user_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #475569;
                font-weight: 600;
                margin-bottom: 4px;
                padding: 2px 0px;
                min-height: 20px;
            }
        """)
        card_layout.addWidget(user_label)
        card_layout.addSpacing(4)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("请输入账号")
        self.user_edit.setFixedHeight(40)
        self.user_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border-radius: 10px;
                border: 2px solid #e2e8f0;
                font-size: 14px;
                background: #ffffff;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #fafbfc;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #94a3b8;
            }
        """)
        card_layout.addWidget(self.user_edit)

        card_layout.addSpacing(12)

        pwd_label = QLabel("密码")
        pwd_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #475569;
                font-weight: 600;
                margin-bottom: 4px;
                padding: 2px 0px;
                min-height: 20px;
            }
        """)
        card_layout.addWidget(pwd_label)
        card_layout.addSpacing(4)

        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_edit.setPlaceholderText("请输入密码")
        self.pwd_edit.setFixedHeight(40)
        self.pwd_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border-radius: 10px;
                border: 2px solid #e2e8f0;
                font-size: 14px;
                background: #ffffff;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #fafbfc;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #94a3b8;
            }
        """)
        card_layout.addWidget(self.pwd_edit)

        card_layout.addSpacing(16)

        self.login_btn = QPushButton("登 录")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: #ffffff;
                font-size: 15px;
                border-radius: 12px;
                padding: 0;
                font-weight: 600;
                border: none;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e3a8a);
            }
        """)
        self.login_btn.clicked.connect(self.check_login)
        card_layout.addWidget(self.login_btn)

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(8)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setStyleSheet("color: #dc2626; font-size: 14px; font-weight: 500; margin-top: 0px;")
        layout.addWidget(self.msg_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        self.center_window()

    def center_window(self):
        screen_geometry = self.screen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2,
                  (screen_geometry.height() - self.height()) // 2)

    def check_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pwd_edit.text().strip()
        if self.app_config.verify_login(user, pwd):
            self.msg_label.setText("")
            self.on_login_success(user)
        else:
            self.msg_label.setText("账号或密码错误！")

from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QThread, QTimer, QDateTime, QUrl, QObject

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.interpolate import griddata, Rbf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:  # pragma: no cover - optional dependency for web channel bridge
    qt_webchannel = importlib.import_module("PyQt6.QtWebChannel")
    QWebChannel = getattr(qt_webchannel, "QWebChannel", None)
except Exception:
    QWebChannel = None

# --- 新增：增强的岩石属性数据库填充逻辑 ---
def fill_missing_properties(df, rock_db, stat_preference: str = "median"):
    """
    使用岩石属性数据库填充DataFrame中缺失的力学参数。
    增强版本：支持煤层智能匹配和密度/容重互转
    
    修改要点：
    1. 所有包含"煤"的岩性都使用煤的数据
    2. 支持密度和容重互转
    3. 优化匹配逻辑
    4. 支持按统计指标（平均值/中位数）优先填充
    """
    if rock_db is None or rock_db.empty:
        return df, 0, []

    stat_preference = (stat_preference or "median").lower()
    if stat_preference not in {"mean", "median"}:
        stat_preference = "median"

    stat_tokens = {
        "mean": ("平均", "mean", "avg", "average"),
        "median": ("中位", "median", "p50", "中值"),
    }

    def detect_stat_from_label(label: str) -> Optional[str]:
        lowered = str(label).lower()
        for key, tokens in stat_tokens.items():
            if any(token in lowered for token in tokens):
                return key
        return None

    # 查找岩性列 (兼容'岩层名称'和'岩性')
    lithology_col = None
    if '岩层名称' in df.columns:
        lithology_col = '岩层名称'
    elif '岩性' in df.columns:
        lithology_col = '岩性'
    else:
        return df, 0, [] # 没有岩性列，无法填充

    # 创建一个副本以避免SettingWithCopyWarning
    df_filled = df.copy()
    
    # 增强的参数映射字典 - 支持密度和容重互转
    parameter_mapping = {
        '弹性模量': ['弹性模量', '弹性模量/GPa', '弹性模量/Gpa', 'E', '杨氏模量'],
        '密度_容重': ['容重', '容重/kN·m-3', '容重/kN*m-3', '密度', '密度/g·cm-3', '密度/g/cm3', 'ρ', '密度（kg*m3）'],
        '抗拉强度': ['抗拉强度', '抗拉强度/MPa', '拉伸强度', 'σt'],
        '泊松比': ['泊松比', 'ν', 'nu', 'poisson'],
        '内摩擦角': ['内摩擦角', '内摩擦角/°', 'φ', 'phi'],
        '粘聚力': ['粘聚力', '粘聚力/MPa', 'c', 'cohesion']
    }
    
    filled_rows_count = 0
    filled_cols = set()

    for index, row in df_filled.iterrows():
        lithology = str(row[lithology_col]).strip()
        
        # 增强的岩性匹配逻辑
        db_row = None
        match_info = ""
        
        # 1. 精确匹配
        exact_match = rock_db[rock_db['岩性'].str.strip() == lithology]
        if not exact_match.empty:
            db_row = exact_match.iloc[0]
            match_info = f"精确匹配: '{lithology}'"
        
        # 2. 煤层智能匹配 - 修改：所有包含"煤"的都使用煤的数据
        elif '煤' in lithology:
            # 查找数据库中所有包含"煤"的记录
            coal_matches = rock_db[rock_db['岩性'].str.contains('煤', na=False)]
            if not coal_matches.empty:
                # 优先选择标准的煤层记录
                priority_order = ['煤层', '煤', '煤炭']
                db_row = None
                
                for priority_name in priority_order:
                    priority_match = coal_matches[coal_matches['岩性'] == priority_name]
                    if not priority_match.empty:
                        db_row = priority_match.iloc[0]
                        break
                
                # 如果没有找到优先级匹配，使用第一个煤层记录
                if db_row is None:
                    db_row = coal_matches.iloc[0]
                
                match_info = f"煤层匹配: '{lithology}' → '{db_row['岩性']}'"
        
        # 3. 模糊匹配（非煤层）
        else:
            best_match_score = 0
            best_match_row = None
            
            for db_lithology in rock_db['岩性'].unique():
                if pd.isna(db_lithology):
                    continue
                    
                db_lithology = str(db_lithology).strip()
                
                # 跳过煤层数据（煤层只能精确匹配或通过包含"煤"匹配）
                if '煤' in db_lithology:
                    continue
                
                # 计算匹配度
                if db_lithology in lithology:
                    score = len(db_lithology)
                    if score > best_match_score:
                        best_match_score = score
                        best_match_row = rock_db[rock_db['岩性'] == db_lithology].iloc[0]
                        match_info = f"模糊匹配: '{lithology}' → '{db_lithology}'"
            
            if best_match_row is not None:
                db_row = best_match_row
        
        # 如果找到匹配的岩性数据，进行参数填充
        if db_row is not None:
            row_filled = False
            
            # 遍历目标DataFrame中的列，寻找可以填充的参数
            for target_col in df_filled.columns:
                if target_col == lithology_col or pd.notna(row[target_col]):
                    continue  # 跳过岩性列和已有数据的列
                
                # 查找数据库中对应的参数
                fill_value = None
                source_col = None
                
                # 使用参数映射进行智能匹配
                for param_type, param_aliases in parameter_mapping.items():
                    # 检查目标列是否属于某个参数类型
                    target_matched = False
                    for alias in param_aliases:
                        if alias in target_col:
                            target_matched = True
                            break
                    
                    if target_matched:
                        # 在数据库中查找对应的参数列
                        fallback_value = None
                        alternative_value = None
                        for db_col in db_row.index:
                            col_label = str(db_col)
                            if not any(alias in col_label for alias in param_aliases):
                                continue

                            candidate_value = db_row[db_col]
                            if pd.isna(candidate_value):
                                continue

                            stat_tag = detect_stat_from_label(col_label)
                            if stat_tag == stat_preference:
                                fill_value = candidate_value
                                source_col = db_col
                                break
                            # 记录潜在的候选值（无统计标记或非首选统计标记）
                            if stat_tag is None and fallback_value is None:
                                fallback_value = (candidate_value, db_col)
                            elif stat_tag != stat_preference and alternative_value is None:
                                alternative_value = (candidate_value, db_col)

                        if fill_value is None and fallback_value is not None:
                            fill_value, source_col = fallback_value
                        if fill_value is None and alternative_value is not None:
                            fill_value, source_col = alternative_value
                        break
                
                # 如果找到了填充值，进行填充
                if fill_value is not None:
                    # 修改：处理密度和容重的单位转换
                    if _needs_unit_conversion(source_col, target_col):
                        fill_value = _convert_density_weight_units(fill_value, source_col, target_col)
                    
                    df_filled.at[index, target_col] = fill_value
                    filled_cols.add(target_col)
                    row_filled = True
            
            if row_filled:
                filled_rows_count += 1

    return df_filled, filled_rows_count, list(filled_cols)
def _needs_unit_conversion(source_col, target_col):
    """判断是否需要进行密度/容重单位转换"""
    density_keywords = ['密度', 'g/cm', 'g·cm', 'kg*m3', 'kg/m3']
    weight_keywords = ['容重', 'kN/m', 'kN·m']
    
    source_is_density = any(keyword in str(source_col) for keyword in density_keywords)
    source_is_weight = any(keyword in str(source_col) for keyword in weight_keywords)
    target_is_density = any(keyword in str(target_col) for keyword in density_keywords)
    target_is_weight = any(keyword in str(target_col) for keyword in weight_keywords)
    
    # 只有在源和目标列属于不同类型时才需要转换
    return (source_is_density and target_is_weight) or (source_is_weight and target_is_density)

def _convert_density_weight_units(value, source_col, target_col):
    """进行密度和容重的单位转换"""
    density_keywords = ['密度', 'g/cm', 'g·cm', 'kg*m3', 'kg/m3']
    weight_keywords = ['容重', 'kN/m', 'kN·m']
    
    source_is_density = any(keyword in str(source_col) for keyword in density_keywords)
    target_is_weight = any(keyword in str(target_col) for keyword in weight_keywords)
    
    if source_is_density and target_is_weight:
        # 检查密度单位并转换
        if 'kg*m3' in str(source_col) or 'kg/m3' in str(source_col):
            # 密度(kg/m³) 转 容重(kN/m³): 乘以 9.8/1000
            return value * 9.8 / 1000
        else:
            # 密度(g/cm³) 转 容重(kN/m³): 乘以 9.8
            return value * 9.8
    elif not source_is_density and not target_is_weight:
        # 容重(kN/m³) 转 密度
        if 'kg*m3' in str(target_col) or 'kg/m3' in str(target_col):
            # 容重(kN/m³) 转 密度(kg/m³): 乘以 1000/9.8
            return value * 1000 / 9.8
        else:
            # 容重(kN/m³) 转 密度(g/cm³): 除以 9.8
            return value / 9.8
    else:
        return value


class KeyStratumTab(QWidget):
    """批量钻孔关键层详细计算与分析的UI界面"""
    def __init__(self, main_win=None, parent=None):
        super().__init__(parent)
        self.dfs = {}  # 使用字典存储每个文件的DataFrame
        self.processed_df = None
        self.input_file_paths = []
        self.preview_df = None  # 添加预览数据框架
        self.main_win = main_win or self.window()
        self._current_task = None
        self.init_ui()
        # 获取主窗口引用以访问岩石数据库
        self.main_window = self.main_win

    def init_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        # --- 左侧控制面板 - 优化尺寸策略 ---
        control_panel = QFrame()
        # 移除 setFixedWidth(380)，改为设置最小宽度
        control_panel.setMinimumWidth(380)
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #fafbfc;
                border-right: 1px solid #e5e7eb;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
            }
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 24, 20, 24)
        control_layout.setSpacing(20)

        action_group = QGroupBox("文件与操作")
        action_layout = QVBoxLayout(action_group)
        action_layout.setSpacing(12)
        self.select_file_btn = ModernButton("1. 选择岩层数据文件(可多选)", icon_path="icons/folder.png")
        self.process_btn = ModernButton("2. 批量计算关键层", color="#059669", icon_path="icons/run.png")
        
        # 新增：一键从数据库导入按钮
        self.batch_import_btn = ModernButton("一键从数据库导入", color="#7c3aed", icon_path="icons/database.png")
        
        self.export_btn = ModernButton("3. 导出结果", color="#0891b2", icon_path="icons/export.png")
        self.clear_btn = ModernButton("清空", color="#dc2626", icon_path="icons/clear.png")
        self.file_label = QLabel("尚未选择文件")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("""
            QLabel {
                color: #6b7280; background-color: #ffffff; padding: 12px;
                border-radius: 8px; border: 1px solid #e5e7eb; font-size: 13px; line-height: 1.5;
            }
        """)
        self.select_file_btn.clicked.connect(self.select_files)
        self.process_btn.clicked.connect(self.process_data)
        self.batch_import_btn.clicked.connect(self.batch_import_from_database)  # 新增连接
        self.export_btn.clicked.connect(self.export_data)
        self.clear_btn.clicked.connect(self.clear_all)
        self.process_btn.setEnabled(False)
        self.batch_import_btn.setEnabled(False)  # 初始禁用
        self.export_btn.setEnabled(False)
        action_layout.addWidget(self.select_file_btn)
        action_layout.addWidget(self.process_btn)
        action_layout.addWidget(self.batch_import_btn)  # 新增按钮
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addWidget(self.file_label)
        control_layout.addWidget(action_group)

        # --- 岩层选择组 ---
        coal_selection_group = QGroupBox("目标岩层选择")
        coal_selection_layout = QVBoxLayout(coal_selection_group)
        coal_selection_layout.setSpacing(12)
        
        # 说明标签
        coal_info_label = QLabel("选择要计算关键层的目标岩层：")
        coal_info_label.setStyleSheet("color: #374151; font-size: 13px; margin-bottom: 8px;")
        coal_selection_layout.addWidget(coal_info_label)
        
        # 岩层选择下拉框
        self.coal_selection_combo = QComboBox()
        self.coal_selection_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px;
                background-color: #ffffff; font-size: 14px; min-height: 20px;
            }
            QComboBox:focus { border-color: #3b82f6; }
            QComboBox::drop-down {
                border: none; width: 30px; subcontrol-origin: padding;
                subcontrol-position: top right;
            }
            QComboBox::down-arrow {
                image: url(icons/dropdown.png); width: 12px; height: 12px;
            }
        """)
        self.coal_selection_combo.setEnabled(False)  # 初始禁用
        coal_selection_layout.addWidget(self.coal_selection_combo)
        
        # 自动检测按钮
        self.detect_coal_btn = ModernButton("检测可用岩层", color="#6366f1", icon_path="icons/search.png")
        self.detect_coal_btn.clicked.connect(self.detect_available_coals)
        self.detect_coal_btn.setEnabled(False)  # 初始禁用
        coal_selection_layout.addWidget(self.detect_coal_btn)
        
    # 岩层统计信息
        self.coal_stats_label = QLabel("请先选择数据文件")
        self.coal_stats_label.setStyleSheet("""
            QLabel {
                color: #6b7280; background-color: #f9fafb; padding: 10px;
                border-radius: 6px; border: 1px solid #e5e7eb; font-size: 12px;
            }
        """)
        self.coal_stats_label.setWordWrap(True)
        coal_selection_layout.addWidget(self.coal_stats_label)
        
        control_layout.addWidget(coal_selection_group)
        control_layout.addStretch()

        # --- 右侧结果面板 ---
        results_panel = QFrame()
        results_panel.setStyleSheet("background-color: #ffffff;")
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(24, 24, 24, 24)
        results_title = QLabel("分析结果")
        results_title.setStyleSheet("""
            QLabel {
                font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 16px;
            }
        """)
        results_layout.addWidget(results_title)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb; border-radius: 8px; gridline-color: #f3f4f6; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f9fafb; padding: 12px 16px; border-bottom: 2px solid #e5e7eb;
                font-weight: 600; color: #374151;
            }
            QTableWidget::item { padding: 12px 16px; border-bottom: 1px solid #f3f4f6; }
        """)
        results_layout.addWidget(self.table)

        main_splitter.addWidget(control_panel)
        main_splitter.addWidget(results_panel)
        
        # --- 优化比例 ---
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([400, 1200])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(main_splitter)

    def batch_import_from_database(self):
        """一键从数据库导入所有数据"""
        if not hasattr(self, 'preview_df') or self.preview_df is None or self.preview_df.empty:
            QMessageBox.warning(self, "状态错误", "请先选择文件并加载数据，然后再进行批量导入。")
            return

        # 获取主窗口的岩石数据库
        main_window = self.window()
        if not hasattr(main_window, 'rock_db') or main_window.rock_db is None or main_window.rock_db.empty:
            QMessageBox.warning(self, "数据库未加载", "岩石属性数据库未加载或为空。请检查数据库文件。")
            return

        # 确认操作
        reply = QMessageBox.question(self, "确认批量导入", 
                                   "确定要从数据库批量导入所有可填充的参数吗？\n\n"
                                   "此操作将：\n"
                                   "• 自动匹配所有岩性（包括5煤、6煤等所有含煤岩性）\n"
                                   "• 填充缺失的力学参数\n"
                                   "• 支持密度/容重自动转换\n"
                                   "• 一次性处理所有记录\n\n"
                                   "现有数据不会被覆盖。",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            total_filled_rows = 0
            total_filled_cols = set()
            file_results = []
            stat_preference = getattr(main_window, 'stat_preference', 'median')
            metric_label = '平均值' if stat_preference == 'mean' else '中位数'

            # 创建进度对话框
            progress_dialog = QProgressDialog("正在从数据库批量导入数据...", "取消", 0, len(self.dfs), self)
            progress_dialog.setWindowTitle("批量导入进行中")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(0)

            # 逐个处理每个文件
            for i, (filepath, df) in enumerate(self.dfs.items()):
                if progress_dialog.wasCanceled():
                    QMessageBox.information(self, "操作取消", "批量导入已取消。")
                    progress_dialog.close()
                    return

                progress_dialog.setValue(i)
                file_name = os.path.basename(filepath)
                progress_dialog.setLabelText(f"正在处理: {file_name}")
                QApplication.processEvents()

                # 对当前文件的数据进行填充
                filled_df, filled_count, filled_cols = fill_missing_properties(
                    df,
                    main_window.rock_db,
                    stat_preference=stat_preference,
                )
                
                if filled_count > 0:
                    # 更新源数据
                    self.dfs[filepath] = filled_df
                    total_filled_rows += filled_count
                    total_filled_cols.update(filled_cols)
                    
                    file_results.append({
                        'file': file_name,
                        'filled_rows': filled_count,
                        'filled_cols': filled_cols
                    })

            progress_dialog.close()

            # 如果有数据被填充，更新预览表
            if total_filled_rows > 0:
                # 重新生成预览数据
                all_preview_dfs = []
                for path, df_item in self.dfs.items():
                    df_copy = df_item.copy()
                    df_copy['_source_filepath'] = path
                    df_copy['_original_index'] = df_item.index
                    df_copy.insert(0, '钻孔名', os.path.basename(path).replace('.csv', ''))
                    all_preview_dfs.append(df_copy)
                
                if all_preview_dfs:
                    self.preview_df = pd.concat(all_preview_dfs, ignore_index=True)
                    self.display_in_table(self.preview_df, is_preview=True)

                # 生成详细的成功报告
                success_message = f"🎉 批量导入成功完成！\n\n"
                success_message += f"📊 总体统计：\n"
                success_message += f"• 填充记录数：{total_filled_rows} 条\n"
                success_message += f"• 填充参数列：{len(total_filled_cols)} 个\n"
                success_message += f"• 使用统计指标：{metric_label}\n"
                success_message += f"• 处理文件数：{len(file_results)} 个\n\n"
                
                success_message += f"📋 填充的参数：\n"
                for col in sorted(total_filled_cols):
                    success_message += f"  • {col}\n"
                
                # 统计煤层匹配情况
                coal_count = 0
                for _, df_item in self.dfs.items():
                    coal_count += df_item['岩层名称'].astype(str).str.contains('煤', na=False).sum()
                
                if coal_count > 0:
                    success_message += f"\n🔥 煤层处理：检测到 {coal_count} 条含煤记录，已统一使用煤层标准参数\n"
                
                success_message += f"\n✅ 数据已更新到表格中，可以继续进行关键层计算。"

                QMessageBox.information(self, "批量导入完成", success_message)

            else:
                QMessageBox.information(self, "导入完成", 
                                      "批量导入完成，但没有找到可以填充的数据。\n\n"
                                      "可能的原因：\n"
                                      "• 所有参数列都已有数据\n"
                                      "• 数据库中没有匹配的岩性\n"
                                      "• 列名格式不匹配")

        except Exception as e:
            QMessageBox.critical(self, "批量导入失败", f"批量导入过程中发生错误：\n\n{str(e)}")

    def clear_all(self):
        """清空所有数据和状态"""
        self.dfs = {}
        self.processed_df = None
        self.input_file_paths = []
        self.preview_df = None  # 清空预览数据
        self.file_label.setText("尚未选择文件")
        self.file_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                background-color: #ffffff;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        self.process_btn.setEnabled(False)
        self.batch_import_btn.setEnabled(False)  # 重置批量导入按钮状态
        self.export_btn.setEnabled(False)
        self.detect_coal_btn.setEnabled(False)  # 重置煤层检测按钮状态
        self.coal_selection_combo.setEnabled(False)  # 重置煤层选择下拉框状态
        self.coal_selection_combo.clear()  # 清空煤层选择项
        self.coal_stats_label.setText("请先选择数据文件")  # 重置煤层统计信息
        self.clear_table()

    def select_files(self):
        """选择多个岩层数据文件并使用健壮的读取和验证方法"""
        filepaths, _ = QFileDialog.getOpenFileNames(self, "选择一个或多个岩层数据文件", "", "CSV 文件 (*.csv)")
        if filepaths:
            self.clear_all()
            self.input_file_paths = filepaths
            
            valid_files_count = 0
            error_files = []
            
            for filepath in filepaths:
                try:
                    if not filepath.lower().endswith('.csv'):
                        error_files.append(f"{os.path.basename(filepath)} (非CSV文件)")
                        continue
                    
                    try:
                        df = pd.read_csv(filepath, encoding='utf-8-sig')
                    except UnicodeDecodeError:
                        df = pd.read_csv(filepath, encoding='gbk')
                    
                    df.dropna(how='all', inplace=True)
                    if df.empty:
                        error_files.append(f"{os.path.basename(filepath)} (文件为空)")
                        continue

                    validation_result, validated_df = self._validate_and_prepare_df(df)
                    if validation_result['is_valid']:
                        self.dfs[filepath] = validated_df
                        valid_files_count += 1
                    else:
                        error_files.append(f"{os.path.basename(filepath)} ({validation_result['message']})")
                        
                except Exception as e:
                    error_files.append(f"{os.path.basename(filepath)} (读取失败: {e})")

            if valid_files_count > 0:
                self.file_label.setText(f"已加载 {valid_files_count} / {len(filepaths)} 个有效文件。")
                self.file_label.setStyleSheet("color: #059669; background-color: #f0fdf4; border-color: #a7f3d0;")
                self.process_btn.setEnabled(True)
                self.batch_import_btn.setEnabled(True)  # 启用批量导入按钮
                self.detect_coal_btn.setEnabled(True)  # 启用煤层检测按钮
                
                # --- 修改部分：创建并显示可操作的预览表 ---
                all_preview_dfs = []
                for path, df_item in self.dfs.items():
                    df_copy = df_item.copy()
                    # 为预览表添加源文件路径和原始索引，用于后续数据回写
                    df_copy['_source_filepath'] = path
                    df_copy['_original_index'] = df_item.index
                    df_copy.insert(0, '钻孔名', os.path.basename(path).replace('.csv', ''))
                    all_preview_dfs.append(df_copy)
                
                if all_preview_dfs:
                    # 将合并后的预览数据存储在 self.preview_df 中
                    self.preview_df = pd.concat(all_preview_dfs, ignore_index=True)
                    # 在计算前，用预览数据填充表格
                    self.display_in_table(self.preview_df, is_preview=True)
                    
                    # 自动检测可用煤层
                    self.detect_available_coals()
                        
                if error_files:
                    QMessageBox.warning(self, "部分文件加载失败", f"以下文件未能成功加载:\n\n" + "\n".join(error_files))
            else:
                self.file_label.setText(f"加载失败: 所有 {len(filepaths)} 个文件均不符合要求。")
                self.file_label.setStyleSheet("color: #dc2626; background-color: #fef2f2; border-color: #fecaca;")
                self.process_btn.setEnabled(False)
                self.batch_import_btn.setEnabled(False)  # 禁用批量导入按钮
                self.clear_table()
                if error_files:
                    QMessageBox.critical(self, "文件加载失败", "所有选择的文件都无法处理，请检查文件内容和格式。\n\n" + "\n".join(error_files))

    # 修改 display_in_table 方法以支持批量导入按钮
    def display_in_table(self, df, is_preview=False):
        """在QTableWidget中显示DataFrame，并高亮关键层和钻孔，同时添加数据库填充按钮"""
        self.clear_table()
        if df is None or df.empty: return
        
        # 在预览模式下，不显示内部跟踪列
        display_df = df.drop(columns=['_source_filepath', '_original_index'], errors='ignore')
                
        # 增加一列用于放置按钮（只在预览模式下）
        button_col_count = 1 if is_preview else 0
        self.table.setRowCount(len(display_df))
        self.table.setColumnCount(len(display_df.columns) + button_col_count)
        
        # 设置表头
        headers = list(display_df.columns)
        if is_preview:
            headers.append("数据库填充")
        self.table.setHorizontalHeaderLabels(headers)
        
        # 定义颜色
        from PyQt6.QtGui import QColor
        color_key_stratum = QColor("#e6fffa")      # 浅青色 (SK)
        color_pks = QColor("#d1fae5")              # 浅绿色 (PKS)
        color_coal = QColor("#fee2e2")             # 浅红色 (煤层)
        color_borehole_name = QColor("#e0f7fa")    # 钻孔名背景色

        for i, row in enumerate(display_df.itertuples(index=False)):
            is_pks = False
            is_sk = False
            is_coal = False
            
            # 检查标记列
            if '关键层标记' in display_df.columns:
                marker_idx = list(display_df.columns).index('关键层标记')
                marker_val = str(row[marker_idx]) if marker_idx < len(row) else ""
                if "(PKS)" in marker_val: is_pks = True
                elif "SK" in marker_val: is_sk = True
                elif "煤层" in marker_val: is_coal = True

            # 填充数据列
            for j, value in enumerate(row):
                # 格式化数值显示 - 数值类型保留2位小数
                if pd.notna(value):
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        # 对于数值类型，保留2位小数
                        if abs(value - round(value)) < 1e-10:  # 接近整数的数
                            item_text = str(int(round(value)))
                        else:
                            item_text = f"{value:.2f}"
                    else:
                        item_text = str(value)
                else:
                    item_text = ""
                
                item = QTableWidgetItem(item_text)
                
                # 根据列名和标记设置单元格样式
                col_name = display_df.columns[j]
                if col_name == '钻孔名':
                    item.setBackground(color_borehole_name)
                elif is_pks:
                    item.setBackground(color_pks)
                elif is_sk:
                    item.setBackground(color_key_stratum)
                elif is_coal:
                    item.setBackground(color_coal)
                    
                self.table.setItem(i, j, item)
            
            # 添加数据库填充按钮（只在预览模式下且针对非煤层行）
            if is_preview and not is_coal:
                fill_btn = QPushButton("从数据库填充")
                fill_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                     stop:0 #4f46e5, stop:1 #3730a3);
                        color: white;
                        border: 1px solid #4338ca;
                        border-radius: 8px;
                        padding: 10px 16px;
                        font-size: 13px;
                        font-weight: 600;
                        min-height: 36px;
                        max-height: 40px;
                        min-width: 120px;
                        max-width: 140px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                     stop:0 #6366f1, stop:1 #4f46e5);
                        border: 1px solid #6366f1;
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                     stop:0 #3730a3, stop:1 #312e81);
                    }
                """)
                # 将当前行号传递给槽函数
                fill_btn.clicked.connect(lambda checked, row_idx=i: self.fill_from_database(row_idx))
                
                # 创建一个容器widget来居中对齐按钮
                button_widget = QWidget()
                button_widget.setStyleSheet("""
                    QWidget {
                        background: transparent;
                        border: none;
                    }
                """)
                button_layout = QHBoxLayout(button_widget)
                button_layout.setContentsMargins(8, 4, 8, 4)
                button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                button_layout.addWidget(fill_btn)
                
                self.table.setCellWidget(i, len(display_df.columns), button_widget)

        # 设置行高以适应按钮
        if is_preview:
            for i in range(self.table.rowCount()):
                self.table.setRowHeight(i, 50)  # 设置行高为50像素，适应按钮高度

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    # 修改 fill_from_database 方法以支持新的填充逻辑
    def fill_from_database(self, table_row_idx):
        """从岩石数据库填充当前行的参数（直接修改源数据）- 使用增强的填充逻辑"""
        # 检查是预览模式还是结果模式
        if not hasattr(self, 'preview_df') or self.preview_df is None or self.preview_df.empty:
            QMessageBox.warning(self, "状态错误", "只能在计算关键层之前进行数据填充。")
            return

        # --- 从预览DataFrame中获取必要信息 ---
        preview_row = self.preview_df.iloc[table_row_idx]
        source_filepath = preview_row['_source_filepath']
        original_index = preview_row['_original_index']
        lithology_name = str(preview_row['岩层名称']).strip()

        # 获取主窗口的岩石数据库
        main_window = self.window()
        if not hasattr(main_window, 'rock_db') or main_window.rock_db is None or main_window.rock_db.empty:
            QMessageBox.warning(self, "数据库未加载", "岩石属性数据库未加载或为空。")
            return

        # 使用增强的数据填充逻辑
        single_row_df = pd.DataFrame([preview_row])
        stat_preference = getattr(main_window, 'stat_preference', 'median')
        filled_df, filled_count, filled_cols = fill_missing_properties(
            single_row_df,
            main_window.rock_db,
            stat_preference=stat_preference,
        )
        
        if filled_count == 0:
            QMessageBox.information(self, "无需填充", 
                                  f"岩性 '{lithology_name}' 的所有参数都已存在，或在数据库中未找到匹配的数据。")
            return

        # 获取填充后的数据
        filled_row = filled_df.iloc[0]
        filled_values = {}
        
        # 找出哪些参数被填充了
        for col in filled_cols:
            if col in filled_row.index and pd.notna(filled_row[col]):
                filled_values[col] = filled_row[col]

        # --- 更新数据和UI ---
        # 1. 更新源DataFrame (self.dfs)
        for param, value in filled_values.items():
            if param in self.dfs[source_filepath].columns:
                self.dfs[source_filepath].loc[original_index, param] = value
        
        # 2. 更新预览DataFrame (self.preview_df)
        for param, value in filled_values.items():
            if param in self.preview_df.columns:
                self.preview_df.loc[table_row_idx, param] = value

        # 3. 更新表格UI
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount()-1)]
        for param, value in filled_values.items():
            if param in headers:
                col_idx = headers.index(param)
                # 格式化数值显示 - 保留2位小数
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if abs(value - round(value)) < 1e-10:  # 接近整数
                        formatted_value = str(int(round(value)))
                    else:
                        formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                self.table.setItem(table_row_idx, col_idx, QTableWidgetItem(formatted_value))

        # 显示成功消息
        metric_label = '平均值' if stat_preference == 'mean' else '中位数'
        success_message = (
            f"已从数据库为 '{lithology_name}' 成功填充参数（优先使用{metric_label}）。\n\n填充详情:\n"
        )
        success_message += "\n".join([f"• {k}: {v}" for k, v in filled_values.items()])
        
        # 如果是煤层，显示特殊提示
        if '煤' in lithology_name:
            success_message += f"\n\n💡 提示：检测到煤层岩性，已使用数据库中煤层的标准参数进行填充。"
        
        QMessageBox.information(self, "填充成功", success_message)
    def _validate_and_prepare_df(self, df):
        """验证CSV文件格式，重命名列，并返回验证结果和处理后的DataFrame"""
        df_copy = df.copy()
        
        column_mappings = {
            '名称': '岩层名称', '岩层名称': '岩层名称', '岩性': '岩层名称', '岩石名称': '岩层名称',
            '厚度/m': '厚度/m', '厚度': '厚度/m', 'thickness': '厚度/m',
            '弹性模量/GPa': '弹性模量/GPa', '弹性模量/Gpa': '弹性模量/GPa', '弹性模量': '弹性模量/GPa',
            '容重/kN·m-3': '容重/kN·m-3', '容重/kN*m-3': '容重/kN·m-3', '容重': '容重/kN·m-3',
            '抗拉强度/MPa': '抗拉强度/MPa', '抗拉强度': '抗拉强度/MPa'
        }
        df_copy.rename(columns=lambda c: column_mappings.get(str(c).strip(), str(c).strip()), inplace=True)

        required_cols = ['岩层名称', '厚度/m']
        optional_cols = ['弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
        
        missing_required = [col for col in required_cols if col not in df_copy.columns]
        if missing_required:
            return {'is_valid': False, 'message': f'缺少必需列: {", ".join(missing_required)}'}, df
        
        coal_found = df_copy['岩层名称'].astype(str).str.contains('煤', na=False).any()
        if not coal_found:
            return {'is_valid': False, 'message': '未在"岩层名称"列中找到含"煤"的记录。'}, df

        for col in required_cols + optional_cols:
            if col in df_copy.columns and col != '岩层名称':
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')

        missing_optional = [col for col in optional_cols if col not in df_copy.columns]
        message = f"✓ 必需列存在\n✓ 找到煤层记录"
        if missing_optional:
            message += f"\n⚠ 缺少可选列: {', '.join(missing_optional)}，计算精度可能受影响。"
        else:
            message += "\n✓ 可选列完整"
            
        return {'is_valid': True, 'message': message}, df_copy

    def detect_available_coals(self):
        """检测所有数据文件中可用的煤层"""
        if not self.dfs:
            QMessageBox.warning(self, "无数据", "请先选择并加载数据文件。")
            return
        
        all_coal_names = set()
        coal_distribution = {}  # 记录每个煤层在多少个钻孔中出现
        
        for filepath, df in self.dfs.items():
            borehole_name = os.path.basename(filepath).replace('.csv', '')
            
            # 查找含"煤"的岩层
            coal_mask = df['岩层名称'].astype(str).str.contains('煤', na=False)
            if coal_mask.any():
                coal_layers = df[coal_mask]['岩层名称'].tolist()
                
                for coal_name in coal_layers:
                    coal_name_clean = str(coal_name).strip()
                    all_coal_names.add(coal_name_clean)
                    
                    if coal_name_clean not in coal_distribution:
                        coal_distribution[coal_name_clean] = []
                    coal_distribution[coal_name_clean].append(borehole_name)
        
        # 更新下拉框
        self.coal_selection_combo.clear()
        if all_coal_names:
            # 按煤层在钻孔中的普遍程度排序，越普遍的越靠前
            sorted_coals = sorted(all_coal_names, 
                                key=lambda x: (-len(coal_distribution[x]), x))
            
            for coal_name in sorted_coals:
                count = len(coal_distribution[coal_name])
                total_holes = len(self.dfs)
                display_text = f"{coal_name} ({count}/{total_holes}个钻孔)"
                self.coal_selection_combo.addItem(display_text, coal_name)
            
            # 默认选择最普遍的煤层
            self.coal_selection_combo.setCurrentIndex(0)
            self.coal_selection_combo.setEnabled(True)
            
            # 更新统计信息
            stats_text = f"发现 {len(all_coal_names)} 种煤层类型，涉及 {len(self.dfs)} 个钻孔"
            most_common = sorted_coals[0]
            most_common_count = len(coal_distribution[most_common])
            stats_text += f"\n推荐: {most_common} (出现在{most_common_count}个钻孔中)"
            
            self.coal_stats_label.setText(stats_text)
            self.coal_stats_label.setStyleSheet("""
                QLabel {
                    color: #059669; background-color: #f0fdf4; padding: 10px;
                    border-radius: 6px; border: 1px solid #a7f3d0; font-size: 12px;
                }
            """)
        else:
            self.coal_selection_combo.setEnabled(False)
            self.coal_stats_label.setText("未在任何文件中发现煤层")
            self.coal_stats_label.setStyleSheet("""
                QLabel {
                    color: #dc2626; background-color: #fef2f2; padding: 10px;
                    border-radius: 6px; border: 1px solid #fecaca; font-size: 12px;
                }
            """)

    def process_data(self):
        """根据选择的目标煤层批量计算关键层"""
        if not self.dfs:
            QMessageBox.warning(self, "无数据", "请先选择并加载有效的数据文件。")
            return

        if self._current_task is not None:
            QMessageBox.information(self, "任务进行中", "已有关键层计算任务正在执行，请稍候完成后再试。")
            return

        if not self.coal_selection_combo.isEnabled() or self.coal_selection_combo.currentIndex() == -1:
            QMessageBox.warning(self, "未选择岩层", "请先检测并选择目标岩层。")
            return

        selected_coal = self.coal_selection_combo.currentData()
        if not selected_coal:
            QMessageBox.warning(self, "岩层选择错误", "未能获取选择的岩层信息。")
            return

        payload = [(path, df.copy(deep=True)) for path, df in self.dfs.items()]

        progress_dialog = QProgressDialog("正在批量计算关键层...", None, 0, 0, self)
        progress_dialog.setWindowTitle("处理中")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setCancelButton(None)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.show()

        worker = FunctionWorker(self._compute_key_stratum_task, payload, selected_coal)
        worker.signals.finished.connect(self._on_key_stratum_finished)
        worker.signals.error.connect(self._on_key_stratum_error)
        self._current_task = TaskHandle(worker=worker, progress_dialog=progress_dialog)
        worker.start()

    def _compute_key_stratum_task(self, payload, selected_coal):
        all_results = []
        processed_count = 0
        error_files = []

        for filepath, df_copy in payload:
            borehole_name = os.path.basename(filepath).replace('.csv', '')
            try:
                target_coal_mask = df_copy['岩层名称'].astype(str).str.strip() == selected_coal.strip()
                if not target_coal_mask.any():
                    error_files.append(f"{borehole_name} (未找到目标煤层: {selected_coal})")
                    continue

                coal_indices = df_copy[target_coal_mask].index.tolist()
                coal_idx = coal_indices[0]

                coal_seam_df = df_copy.loc[[coal_idx]]
                df_above_coal = df_copy.loc[:coal_idx-1].copy()

                if df_above_coal.empty:
                    error_files.append(f"{borehole_name} (目标煤层 {selected_coal} 上方无岩层)")
                    continue

                required_calc_cols = ['弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
                if any(col not in df_above_coal.columns for col in required_calc_cols):
                    error_files.append(f"{borehole_name} (缺少计算所需列)")
                    continue

                key_strata_info = calculate_key_strata_details(df_above_coal, coal_seam_df)

                result_df = df_copy.copy()
                result_df['关键层标记'] = '-'
                result_df['距煤层距离/m'] = 0.0
                result_df.loc[coal_idx, '关键层标记'] = '煤层'

                cumulative_thickness = 0
                for row_idx in range(len(df_above_coal) - 1, -1, -1):
                    actual_idx = df_above_coal.index[row_idx]
                    layer_thickness = df_above_coal.iloc[row_idx]['厚度/m']
                    layer_thickness = layer_thickness if pd.notna(layer_thickness) else 0
                    distance_to_center = round(cumulative_thickness + layer_thickness / 2, 2)
                    result_df.loc[actual_idx, '距煤层距离/m'] = distance_to_center
                    cumulative_thickness += layer_thickness

                if coal_idx < len(result_df) - 1:
                    cumulative_thickness_below = 0
                    for row_idx in range(coal_idx + 1, len(result_df)):
                        layer_thickness = result_df.iloc[row_idx]['厚度/m']
                        layer_thickness = layer_thickness if pd.notna(layer_thickness) else 0
                        cumulative_thickness_below += layer_thickness
                        result_df.iloc[row_idx, result_df.columns.get_loc('距煤层距离/m')] = round(-cumulative_thickness_below, 2)

                above_coal_mask = result_df.index < coal_idx
                for ks in key_strata_info:
                    lithology_name = ks['岩性'].replace('(PKS)', '')
                    lithology_match = result_df['岩层名称'].astype(str).str.strip() == lithology_name.strip()
                    distance_match = np.isclose(result_df['距煤层距离/m'], ks['距煤层距离'], atol=0.1)
                    match_mask = above_coal_mask & lithology_match & distance_match
                    if match_mask.any():
                        result_df.loc[match_mask, '关键层标记'] = ks['SK_Label']

                result_df.insert(0, '钻孔名', borehole_name)
                all_results.append(result_df)
                processed_count += 1
            except Exception as exc:  # pragma: no cover
                error_files.append(f"{borehole_name} (处理失败: {exc})")

        if all_results:
            processed_df = pd.concat(all_results, ignore_index=True, sort=False)
        else:
            def _render_map(self, df: Optional[pd.DataFrame]):
                if self.web_view is None or self.map_container is None:
                    if self.map_placeholder is not None:
                        self.map_placeholder.setText("当前环境缺少 Qt WebEngine 支持，无法显示地图。")
                    return

                if df is None or df.empty or '省份' not in df:
                    if self.map_placeholder is not None:
                        self.map_placeholder.setText("暂无可用数据绘制地图。")
                        self.map_container.setCurrentWidget(self.map_placeholder)
                    return

                province_counts = (
                    df['省份']
                    .astype(str)
                    .str.strip()
                    .replace(['', 'nan', 'None', 'NaN'], pd.NA)
                    .dropna()
                    .map(self._normalize_province_name)
                    .value_counts()
                )

                if province_counts.empty:
                    if self.map_placeholder is not None:
                        self.map_placeholder.setText("数据集中未找到省份信息，无法绘制地图。")
                        self.map_container.setCurrentWidget(self.map_placeholder)
                    return

                data_pairs = [
                    (province, int(count))
                    for province, count in province_counts.items()
                ]

                html = build_china_map_html(
                    data_pairs=data_pairs,
                    title="岩石样本省份分布",
                    subtitle="数值表示样本数量",
                    tooltip_formatter="{b}：{c}",
                    value_unit=" 条样本",
                    color_range=["#e0f2fe", "#0ea5e9"],
                    zoom=1.08,
                    center=(104.0, 35.6),
                    enable_bridge=False,
                )

                self.web_view.setHtml(html)
                self.map_container.setCurrentWidget(self.web_view)
    def _get_chinese_prefix(self, text):
        """辅助函数：从字符串中提取开头的连续汉字部分。"""
        import re
        match = re.match(r'[\u4e00-\u9fff]+', str(text))
        return match.group(0) if match else ''

    def export_data(self):
        """导出批量关键层计算结果，支持 Excel 与 CSV。"""
        if self.processed_df is None or self.processed_df.empty:
            QMessageBox.warning(self, "无数据", "当前没有可导出的计算结果，请先完成关键层计算。")
            return

        output_dir = os.path.join(os.getcwd(), "output", "key_stratum_analysis")
        os.makedirs(output_dir, exist_ok=True)

        suggested_name = "批量关键层分析结果.xlsx"
        default_path = os.path.join(output_dir, suggested_name)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存分析结果",
            default_path,
            "Excel 文件 (*.xlsx);;CSV 文件 (*.csv)",
        )

        if not save_path:
            return

        try:
            if save_path.lower().endswith(".xlsx"):
                with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                    self.processed_df.to_excel(writer, index=False, sheet_name="关键层分析结果")

                    if self.dfs:
                        for path, df in self.dfs.items():
                            sheet_name = os.path.basename(path).replace(".csv", "")[:30]
                            df.to_excel(writer, index=False, sheet_name=f"原始_{sheet_name}")
            else:
                self.processed_df.to_csv(save_path, index=False, encoding="utf-8-sig")

            QMessageBox.information(self, "导出成功", f"分析结果已保存到:\n{save_path}")

            if QMessageBox.question(self, "打开文件", "需要现在打开保存的文件吗？") == QMessageBox.StandardButton.Yes:
                open_file_auto(save_path)

        except Exception as exc:
            QMessageBox.critical(self, "导出失败", f"保存文件时出现错误：\n{exc}")

    def clear_table(self):
        """清空表格"""
        self.table.setRowCount(0)
        self.table.setColumnCount(0)



# 设置全局字体以支持中文和英文
# 汉字使用宋体，数字和英文使用Times New Roman
plt.rcParams['font.sans-serif'] = ['SimSun', 'Microsoft YaHei', 'DejaVu Sans']  # 宋体优先，微软雅黑备用
plt.rcParams['font.serif'] = ['SimSun', 'Microsoft YaHei', 'DejaVu Serif']       # 衬线字体设置
plt.rcParams['font.family'] = 'sans-serif'                       # 改为sans-serif，确保中文显示
plt.rcParams['axes.unicode_minus'] = False                       # 正确显示负号

# 为不同元素设置专用字体大小
plt.rcParams['font.size'] = 12                                   # 默认字体大小
plt.rcParams['axes.titlesize'] = 14                             # 标题字体大小
plt.rcParams['axes.labelsize'] = 12                             # 轴标签字体大小
plt.rcParams['xtick.labelsize'] = 10                            # X轴刻度标签字体大小
plt.rcParams['ytick.labelsize'] = 10                            # Y轴刻度标签字体大小
plt.rcParams['legend.fontsize'] = 10                            # 图例字体大小
plt.rcParams['figure.titlesize'] = 16                           # 图表标题字体大小

# 设置数学公式字体
plt.rcParams['mathtext.fontset'] = 'stix'                       # 数学公式使用STIX字体
plt.rcParams['mathtext.default'] = 'regular'                    # 数学文本默认样式

# 设置图表输出质量
plt.rcParams['figure.dpi'] = 100                                # 显示DPI
plt.rcParams['savefig.dpi'] = 300                               # 保存时DPI
plt.rcParams['savefig.format'] = 'png'                          # 默认保存格式
plt.rcParams['savefig.bbox'] = 'tight'                          # 紧凑边界
plt.rcParams['savefig.facecolor'] = 'white'                     # 背景色
plt.rcParams['savefig.edgecolor'] = 'none'                      # 边框色

# 设置PDF输出字体嵌入
plt.rcParams['pdf.fonttype'] = 42                               # TrueType字体嵌入
plt.rcParams['ps.fonttype'] = 42                                # PostScript字体嵌入
def open_file_auto(filepath):
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            os.system(f"open '{filepath}'")
        else:
            os.system(f"xdg-open '{filepath}'")
        return True
    except Exception as e:
        QMessageBox.critical(None, "打开文件错误", f"无法自动打开文件: {filepath}\n错误: {e}")
        return False

# --- 核心数据处理逻辑 (从 zongchengxuv2.4.py 迁移并优化) ---

def process_single_borehole_file(input_csv_path):
    """
    处理单个钻孔文件，提取煤层信息 - 使用健壮的编码处理
    """
    processed_data_for_file = []
    borehole_name = os.path.basename(input_csv_path).replace('.csv', '')
    try:
        try: 
            df = pd.read_csv(input_csv_path, encoding='utf-8-sig')
        except UnicodeDecodeError: 
            df = pd.read_csv(input_csv_path, encoding='gbk')
        except Exception as e: 
            return None, f"文件 '{os.path.basename(input_csv_path)}' 读取失败: {e}", "error"
        
        df.dropna(how='all', inplace=True)
        if df.empty: 
            return [], f"文件 '{os.path.basename(input_csv_path)}' 为空。", "warning"

        std_cols_map = {
            '名称': '岩层名称', '岩层名称': '岩层名称', '岩性': '岩层名称',
            '厚度/m': '厚度/m', '厚度': '厚度/m',
            '弹性模量/GPa': '弹性模量/GPa', '弹性模量/Gpa': '弹性模量/GPa', '弹性模量': '弹性模量/GPa',
            '容重/kN·m-3': '容重/kN·m-3', '容重/kN*m-3': '容重/kN·m-3', '容重': '容重/kN·m-3',
            '抗拉强度/MPa': '抗拉强度/MPa', '抗拉强度': '抗拉强度/MPa'
        }
        df.rename(columns=lambda c: std_cols_map.get(str(c).strip(), str(c).strip()), inplace=True)

        if "岩层名称" not in df.columns or "厚度/m" not in df.columns:
            return None, f"文件 '{os.path.basename(input_csv_path)}' 缺少'岩层名称'或'厚度/m'列。", "error"

        coal_seam_indices = df[df['岩层名称'].astype(str).str.contains('煤', na=False)].index.tolist()
        if not coal_seam_indices: 
            return [], f"在文件 '{os.path.basename(input_csv_path)}' 中未找到煤层。", "info"

        for coal_idx in coal_seam_indices:
            coal_row = df.iloc[coal_idx]
            coal_name = str(coal_row["岩层名称"]).strip()
            coal_thickness = round(pd.to_numeric(coal_row["厚度/m"], errors='coerce'), 2)

            direct_roof_name, direct_roof_thickness = "N/A", "N/A"
            if coal_idx > 0:
                roof_row = df.iloc[coal_idx - 1]
                direct_roof_name = str(roof_row["岩层名称"]).strip()
                direct_roof_thickness = round(pd.to_numeric(roof_row["厚度/m"], errors='coerce'), 2)
            
            feature_dict = {
                "钻孔名": borehole_name, "煤层": coal_name, "煤层厚度": coal_thickness,
                "直接顶厚度": direct_roof_thickness, "直接顶岩性": direct_roof_name,
            }

            df_above = df.iloc[:coal_idx].copy()
            coal_props_df = df.iloc[[coal_idx]].copy()
            
            key_strata_info = []
            required_ks_cols = ['岩层名称', '厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
            if not df_above.empty and all(col in df_above.columns for col in required_ks_cols):
                key_strata_info = calculate_key_strata_details(df_above, coal_props_df)
            
            for i in range(4): 
                if i < len(key_strata_info):
                    ks = key_strata_info[i] 
                    feature_dict[f'关键层{i+1}厚度'] = ks['厚度']
                    feature_dict[f'关键层{i+1}岩性'] = ks['岩性']
                    feature_dict[f'关键层{i+1}距煤层的距离'] = ks['距煤层距离']
                else:
                    feature_dict.update({f'关键层{i+1}厚度': "N/A", f'关键层{i+1}岩性': "N/A", f'关键层{i+1}距煤层的距离': "N/A"})
            processed_data_for_file.append(feature_dict)
        
        return processed_data_for_file, f"文件 '{os.path.basename(input_csv_path)}' 处理完成。", "info"
    except Exception as e:
        return [], f"文件读取失败: {str(e)}", "error"

def calculate_key_strata_details(df_strata_above_coal, coal_seam_properties_df):
    """
    计算给定煤层上覆岩层的关键层信息。
    数值结果（厚度、距离）会被四舍五入到两位小数。
    --- 2024/07/26 更新：与Matlab代码对齐 ---
    """
    key_strata_output_list = []
    if df_strata_above_coal.empty or coal_seam_properties_df.empty:
        return key_strata_output_list

    df_strata_above_coal = df_strata_above_coal.copy()

    try:
        required_cols = ['厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
        for col in required_cols:
            if col not in df_strata_above_coal.columns:
                return key_strata_output_list
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
        
        # --- Matlab逻辑对齐：循环判别 ---
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
                    # 在原始翻转数组中的索引是 i + number_deleted_rows_agg
                    # 但matlab代码是 key(i+number) = 1，这个i是2开始的，所以是i-1层。
                    # q_x(i) < q_x(i-1) 意味着第 i 层使得结构失稳，控制层是 i-1 层
                    # 所以标记的是第 i-1 层
                    key_idx_in_temp = i
                    original_flipped_idx_to_mark = key_idx_in_temp + number_deleted_rows_agg
                    if original_flipped_idx_to_mark < len(key_flags_flipped):
                         key_flags_flipped[original_flipped_idx_to_mark] = 1

                    # 删除前 i-1 行
                    temp_rh = temp_rh[i:]
                    temp_eh = temp_eh[i:]
                    number_deleted_rows_agg += i
                    found_key = True
                    break
            
            if not found_key:
                # 如果循环结束没有找到，说明第一层就是关键层
                if not np.any(key_flags_flipped):
                    key_flags_flipped[0] = 1
                break
        
        # --- Matlab逻辑对齐：特殊条件判断 ---
        # 这部分在matlab中很奇怪，似乎是 `key(i+number)=1` 之后，又有一个 `key(1)=1` 的判断
        # `num = find(key == 1, 1)` 找到第一个关键层的位置
        first_key_idx_array = np.where(key_flags_flipped == 1)[0]
        if len(first_key_idx_array) > 0:
            first_key_idx = first_key_idx_array[0]
            # `mining_h = thick_h(1,1)` 是紧邻煤层的顶板厚度
            # `thick_h` 是 `flipud(column3)`，所以 `thick_h(1)` 就是 `column3_flipped_thickness[0]`
            immediate_roof_thickness = column3_flipped_thickness[0]
            if immediate_roof_thickness > mining_height_factor:
                # `sum(thick_h(1:num))` 是从直接顶到第一个关键层的累计厚度
                sum_thick_to_first_key = np.sum(column3_flipped_thickness[:first_key_idx+1])
                if sum_thick_to_first_key > 10:
                    key_flags_flipped[0] = 1 # 将第一层标记为关键层

        # --- Matlab逻辑对齐：泥岩检查 ---
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
            # --- Matlab逻辑对齐：破断距计算 q_z ---
            q_z_values = np.zeros(len(key_indices_in_flipped_array))
            information = np.column_stack((rh_flipped, eh_flipped))

            for i, current_key_idx_flipped in enumerate(key_indices_in_flipped_array):
                if i == 0:
                    # gs_i = information(1:new(1), :)
                    gs_i = information[:current_key_idx_flipped + 1, :]
                    # resul = gs_i(new(1),2) * sum(gs_i(:,1)) / sum(gs_i(:,2))
                    sum_gs_i_rh = np.sum(gs_i[:, 0])
                    sum_gs_i_eh = np.sum(gs_i[:, 1])
                    if sum_gs_i_eh != 0:
                        q_z_values[i] = gs_i[current_key_idx_flipped, 1] * sum_gs_i_rh / sum_gs_i_eh
                    else:
                        q_z_values[i] = 0
                else:
                    prev_key_idx_flipped = key_indices_in_flipped_array[i-1]
                    chazhi = current_key_idx_flipped - prev_key_idx_flipped
                    if chazhi == 1:
                        # resul = information(new(i),1)
                        q_z_values[i] = information[current_key_idx_flipped, 0]
                    else:
                        # chazhi = new(i-1)+1; gs_i = information(chazhi:new(i), :);
                        chazhi_start_idx = prev_key_idx_flipped + 1
                        gs_i = information[chazhi_start_idx : current_key_idx_flipped + 1, :]
                        # for j = 1:length(gs_i)
                        #     resul = gs_i(j,2) * sum(gs_i(:,1)) / sum(gs_i(:,2));
                        # end
                        # q_z(i)=resul;
                        # Matlab的这个循环是错误的，最后resul只会是最后一次循环的值。这里我们按matlab的逻辑来
                        sum_gs_i_rh = np.sum(gs_i[:, 0])
                        sum_gs_i_eh = np.sum(gs_i[:, 1])
                        if sum_gs_i_eh != 0:
                            # 使用该段的最后一个岩层（也就是当前关键层）的eh来计算
                            resul = gs_i[-1, 1] * sum_gs_i_rh / sum_gs_i_eh
                        else:
                            resul = 0
                        q_z_values[i] = resul

            h_values_for_pks = column3_flipped_thickness[key_indices_in_flipped_array]
            rt_values_for_pks = column6_flipped_tensile[key_indices_in_flipped_array]
            q_z_mpa = q_z_values / 1000.0
            l_x = np.zeros_like(h_values_for_pks, dtype=float)
            
            valid_q_z_indices_mask = (q_z_mpa != 0)
            if np.any(valid_q_z_indices_mask):
                h_subset = h_values_for_pks[valid_q_z_indices_mask]
                rt_subset = rt_values_for_pks[valid_q_z_indices_mask]
                q_z_mpa_subset = q_z_mpa[valid_q_z_indices_mask]
                term_in_sqrt = (2 * rt_subset) / q_z_mpa_subset
                safe_term_in_sqrt = np.where(term_in_sqrt >= 0, term_in_sqrt, 0)
                l_x_subset = h_subset * np.sqrt(safe_term_in_sqrt)
                l_x[valid_q_z_indices_mask] = l_x_subset
            
            if len(l_x) > 0 and np.any(np.isfinite(l_x)) and np.count_nonzero(np.isfinite(l_x) & (l_x > 0)) > 0:
                # 使用nanargmax来安全地找到最大值的索引，忽略nan和inf
                pks_idx_in_lx_array = np.nanargmax(l_x)
                pks_original_flipped_idx = key_indices_in_flipped_array[pks_idx_in_lx_array]
                if pks_original_flipped_idx < len(sk_labels_flipped) and sk_labels_flipped[pks_original_flipped_idx] != '-':
                    sk_labels_flipped[pks_original_flipped_idx] += '(PKS)'
        
        # --- 结果整理和输出 ---
        cumulative_thickness_from_coal_to_base = 0.0
        for i_flipped in range(len(sk_labels_flipped)):
            current_layer_thickness = float(column3_flipped_thickness[i_flipped])
            if sk_labels_flipped[i_flipped] != '-':
                lithology = column2_flipped_names[i_flipped]
                # 距离是到岩层中心的距离
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

# --- 删除重复的函数定义 ---



class ModernButton(QPushButton):
    def __init__(self, text, color="#4f46e5", icon_path=None):
        super().__init__(text)
        self.setMinimumHeight(38)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 {color}, stop:1 {self.darken_color(color)});
                color: white;
                border: 1px solid {self.darken_color(color, 20)};
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 {self.lighten_color(color)}, stop:1 {color});
                border: 1px solid {color};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 {self.darken_color(color, 30)}, stop:1 {self.darken_color(color, 40)});
                padding-left: 20px;
                padding-top: 9px;
            }}
            QPushButton:disabled {{
                background: #d1d5db;
                color: #9ca3af;
                border: 1px solid #d1d5db;
            }}
        """)

    def darken_color(self, hex_color, percent=15):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (1 - percent/100))) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def lighten_color(self, hex_color, percent=10):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c + (255-c) * percent/100)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"


class DashboardPage(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.rock_summary_value = None
        self.key_summary_value = None
        self.model_summary_value = None
        self.data_summary_value = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 32)
        layout.setSpacing(24)

        hero = QFrame()
        hero.setObjectName("dashboardHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_layout.setSpacing(18)

        icon_label = QLabel()
        icon_label.setObjectName("dashboardHeroIcon")
        icon_label.setFixedSize(68, 68)
        pixmap_path = resolve_app_icon_path()
        pixmap = QPixmap(pixmap_path) if pixmap_path else QPixmap()
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(68, 68, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("🛠")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(6)

        title_label = QLabel("欢迎回来！")
        title_label.setObjectName("dashboardHeroTitle")
        title_box.addWidget(title_label)

        subtitle = QLabel("快速了解当前项目进展，并一键进入常用分析模块。")
        subtitle.setObjectName("dashboardHeroSubtitle")
        subtitle.setWordWrap(True)
        title_box.addWidget(subtitle)

        hero_layout.addLayout(title_box, 1)
        hero_layout.addStretch(1)

        layout.addWidget(hero)

        actions_frame = QFrame()
        actions_frame.setObjectName("dashboardActionBar")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(16, 12, 16, 12)
        actions_layout.setSpacing(12)

        quick_buttons = [
            ("打开关键层计算", lambda: self.main_win.navigate_to_module_feature("基础力学理论计算", "关键层计算")),
            ("进入地质建模", lambda: self.main_win.navigate_to_module_feature("地质建模", "煤层块体建模")),
            ("刷新岩石库", self.main_win._handle_reload_database),
            ("打开数据目录", self.main_win._handle_open_data_dir),
            ("查看操作指南", self.main_win._handle_open_manual),
        ]

        for text, handler in quick_buttons:
            btn = QPushButton(text)
            btn.setObjectName("dashboardAction")
            btn.clicked.connect(handler)
            actions_layout.addWidget(btn)

        actions_layout.addStretch(1)
        layout.addWidget(actions_frame)

        stats_frame = QFrame()
        stats_frame.setObjectName("dashboardStats")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(12, 12, 12, 12)
        stats_layout.setSpacing(16)

        rock_card, self.rock_summary_value = self._create_stat_card(
            "岩石属性库", "已加载的岩性记录数"
        )
        key_card, self.key_summary_value = self._create_stat_card(
            "关键层计算", "最新批次的数据行数"
        )
        model_card, self.model_summary_value = self._create_stat_card(
            "地质建模", "当前块体模型的岩层数量"
        )
        data_card, self.data_summary_value = self._create_stat_card(
            "钻孔数据", "当前已合并的钻孔记录"
        )

        stats_layout.addWidget(rock_card, 0, 0)
        stats_layout.addWidget(key_card, 0, 1)
        stats_layout.addWidget(model_card, 1, 0)
        stats_layout.addWidget(data_card, 1, 1)

        layout.addWidget(stats_frame)
        layout.addStretch(1)

        self.refresh_cards()

    def _create_stat_card(self, title: str, subtitle: str):
        frame = QFrame()
        frame.setObjectName("dashboardStatCard")
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(20, 18, 20, 18)
        inner.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("dashboardStatTitle")
        inner.addWidget(title_label)

        value_label = QLabel("--")
        value_label.setObjectName("dashboardStatValue")
        inner.addWidget(value_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("dashboardStatSubtitle")
        subtitle_label.setWordWrap(True)
        inner.addWidget(subtitle_label)

        return frame, value_label

    def refresh_cards(self):
        if self.rock_summary_value is None:
            return

        rock_count = 0
        rock_db = getattr(self.main_win, 'rock_db', None)
        if rock_db is not None:
            try:
                rock_count = len(rock_db)
            except Exception:
                rock_count = 0
        self.rock_summary_value.setText(f"{rock_count:,}" if rock_count else "--")

        key_tab = getattr(self.main_win, 'key_stratum_tab', None)
        processed_df = getattr(key_tab, 'processed_df', None) if key_tab is not None else None
        key_rows = 0
        if processed_df is not None:
            try:
                key_rows = int(getattr(processed_df, 'shape', (0,))[0])
            except Exception:
                key_rows = 0
        self.key_summary_value.setText(str(key_rows) if key_rows else "待计算")

        coal_tab = getattr(self.main_win, 'coal_block_tab', None)
        model_payload = getattr(coal_tab, 'last_plot_payload', None) if coal_tab is not None else None
        if model_payload and isinstance(model_payload, tuple) and len(model_payload) >= 3:
            block_models = model_payload[2]
            layer_count = len(block_models) if block_models else 0
            self.model_summary_value.setText(f"{layer_count} 层" if layer_count else "待生成")
        else:
            self.model_summary_value.setText("待生成")

        merged_df = getattr(coal_tab, 'merged_df', None) if coal_tab is not None else None
        borehole_rows = 0
        if merged_df is not None:
            try:
                borehole_rows = int(getattr(merged_df, 'shape', (0,))[0])
            except Exception:
                borehole_rows = 0
        self.data_summary_value.setText(str(borehole_rows) if borehole_rows else "未加载")


class AspectRatioContainer(QWidget):
    """保持内部控件固定宽高比的容器"""

    def __init__(self, ratio: float = 1.0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ratio = max(ratio, 0.01)
        self._widget: Optional[QWidget] = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setWidget(self, widget: Optional[QWidget]) -> None:
        if self._widget is widget:
            return
        if self._widget is not None:
            self._widget.setParent(None)
        self._widget = widget
        if widget is not None:
            widget.setParent(self)
            widget.show()
        self.updateGeometry()

    def widget(self) -> Optional[QWidget]:
        return self._widget

    def sizeHint(self) -> QSize:
        if self._widget is not None:
            base = self._widget.sizeHint()
            side = min(base.width(), base.height())
            return QSize(side, int(side / self.ratio))
        return super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        if self._widget is not None:
            base = self._widget.minimumSizeHint()
            side = min(base.width(), base.height())
            return QSize(side, int(side / self.ratio))
        return super().minimumSizeHint()

    def resizeEvent(self, event):  # type: ignore[override]
        super().resizeEvent(event)
        if self._widget is None:
            return

        available_width = self.width()
        available_height = self.height()

        target_width = available_width
        target_height = int(target_width / self.ratio)

        if target_height > available_height:
            target_height = available_height
            target_width = int(target_height * self.ratio)

        x = (available_width - target_width) // 2
        y = (available_height - target_height) // 2
        self._widget.setGeometry(x, y, target_width, target_height)


class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 创建Figure时就设置好布局参数和字体
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='#ffffff')
        
        # 设置图表专用字体 - 更可靠的中文字体设置
        import matplotlib.font_manager as fm
        import matplotlib
        
        # 强制设置matplotlib使用支持中文的字体
        try:
            # 尝试使用系统中的中文字体
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            # 优先使用的中文字体列表
            preferred_chinese_fonts = ['SimSun', '宋体', 'Microsoft YaHei', '微软雅黑', 'SimHei', '黑体']
            preferred_english_fonts = ['Times New Roman', 'Arial', 'DejaVu Sans']
            
            # 查找可用的中文字体
            chinese_font_name = None
            for font in preferred_chinese_fonts:
                if font in available_fonts:
                    chinese_font_name = font
                    break
            
            # 查找可用的英文字体
            english_font_name = None
            for font in preferred_english_fonts:
                if font in available_fonts:
                    english_font_name = font
                    break
            
            # 如果没找到，使用默认字体
            if not chinese_font_name:
                chinese_font_name = 'Microsoft YaHei'  # Windows默认字体
            if not english_font_name:
                english_font_name = 'Arial'
            
            # 创建字体属性
            self.chinese_font = fm.FontProperties(family=chinese_font_name, size=12)
            self.english_font = fm.FontProperties(family=english_font_name, size=12)
            self.title_chinese_font = fm.FontProperties(family=chinese_font_name, size=14, weight='bold')
            self.title_english_font = fm.FontProperties(family=english_font_name, size=14, weight='bold')
            
            print(f"✓ 中文字体: {chinese_font_name}, 英文字体: {english_font_name}")
            
        except Exception as e:
            print(f"字体设置警告: {e}")
            # 使用更简单但更可靠的字体设置
            self.chinese_font = fm.FontProperties(size=12)
            self.english_font = fm.FontProperties(size=12)
            self.title_chinese_font = fm.FontProperties(size=14, weight='bold')
            self.title_english_font = fm.FontProperties(size=14, weight='bold')
        
        # 针对2:1比例优化布局参数
        ratio = width / height
        if ratio >= 1.8:  # 宽屏比例 (2:1 = 2.0)
            self.figure.subplots_adjust(
                left=0.15,    # 减小左边距
                bottom=0.15,  # 适中下边距  
                right=1.00,   # 增加右边距
                top=0.85,     # 适中上边距，为标题留空间
                wspace=0.2,   # 子图间水平间距
                hspace=0.2    # 子图间垂直间距
            )
        else:  # 普通比例
            self.figure.subplots_adjust(
                left=0.15,    # 左边距
                bottom=0.15,  # 下边距  
                right=1.00,   # 右边距
                top=0.85,     # 上边距，为标题留空间
                wspace=0.2,   # 子图间水平间距
                hspace=0.2    # 子图间垂直间距
            )
        
        super().__init__(self.figure)
        self.setParent(parent)
        # 设置尺寸策略，确保画布能够正确缩放
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        
        # 设置最小尺寸，保证2:1比例
        if ratio >= 1.8:  # 宽屏比例
            self.setMinimumSize(600, 300)  # 2:1的最小尺寸
        else:
            self.setMinimumSize(400, 300)  # 4:3的最小尺寸
        
        # 设置图表样式
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        
        # 连接画布调整事件
        self.mpl_connect('resize_event', self.on_resize)
    
    def apply_mixed_fonts(self, ax):
        """为图表元素应用混合字体设置 - 简化版本，更可靠"""
        try:
            # 获取当前的标题、标签文本
            title_text = ax.get_title()
            xlabel_text = ax.get_xlabel()
            ylabel_text = ax.get_ylabel()
            
            # 应用字体到标题（通常包含中文）
            if title_text:
                # 优先使用中文字体显示标题
                ax.set_title(title_text, fontproperties=self.title_chinese_font)
            
            # 应用字体到轴标签
            if xlabel_text:
                if self._contains_chinese(xlabel_text):
                    ax.set_xlabel(xlabel_text, fontproperties=self.chinese_font)
                else:
                    ax.set_xlabel(xlabel_text, fontproperties=self.english_font)
            
            if ylabel_text:
                if self._contains_chinese(ylabel_text):
                    ax.set_ylabel(ylabel_text, fontproperties=self.chinese_font)
                else:
                    ax.set_ylabel(ylabel_text, fontproperties=self.english_font)
            
            # 设置刻度标签字体（数字使用英文字体）
            for tick in ax.get_xticklabels():
                tick.set_fontproperties(self.english_font)
            for tick in ax.get_yticklabels():
                tick.set_fontproperties(self.english_font)
            
            # 设置图例字体
            legend = ax.get_legend()
            if legend:
                for text in legend.get_texts():
                    legend_text = text.get_text()
                    if self._contains_chinese(legend_text):
                        text.set_fontproperties(self.chinese_font)
                    else:
                        text.set_fontproperties(self.english_font)
            
        except Exception as e:
            print(f"字体应用警告: {e}")
    
    def _contains_chinese(self, text):
        """检查文本是否包含中文字符 - 更准确的检测"""
        if not text:
            return False
        # 检查是否包含中文字符（Unicode范围）
        for char in str(text):
            if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                return True
        return False
    
    def on_resize(self, event):
        """处理画布大小调整事件 - 保持指定边距"""
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                # 保持指定的边距设置，不使用 tight_layout
                if hasattr(self, 'figure') and self.figure.get_axes():
                    # 强制使用指定边距
                    self.figure.subplots_adjust(
                        left=0.15,    # 左边距
                        bottom=0.15,  # 下边距
                        right=1.00,   # 右边距
                        top=0.85      # 上边距
                    )
                    
                    # 重新应用字体设置
                    for ax in self.figure.get_axes():
                        self.apply_mixed_fonts(ax)
                        
                self.draw()
        except:
            # 如果调整失败，保持原有布局
            pass

class CSVFormatterTab(QWidget):
    # ... (此部分代码与之前相同，为简洁省略) ...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_df = None
        self.input_file_path = None
        self.target_columns = ['序号', '岩层名称', '厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa']
        self.column_mapping_combos = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        input_group = QGroupBox("源文件选择与加载")
        input_layout = QGridLayout(input_group)
        self.select_file_btn = ModernButton("1. 选择源CSV文件", icon_path="icons/folder.png")
        self.load_cols_btn = ModernButton("2. 加载列名", color="#1cc88a", icon_path="icons/load.png")
        self.selected_file_label = QLabel("尚未选择源文件")
        self.selected_file_label.setStyleSheet("color: #858796; padding-top: 5px;")
        self.selected_file_label.setWordWrap(True)
        self.select_file_btn.clicked.connect(self.select_input_file)
        self.load_cols_btn.clicked.connect(self.load_source_columns)
        self.load_cols_btn.setEnabled(False)
        input_layout.addWidget(self.select_file_btn, 0, 0)
        input_layout.addWidget(self.load_cols_btn, 0, 1)
        input_layout.addWidget(self.selected_file_label, 1, 0, 1, 2)
        layout.addWidget(input_group)
        mapping_group = QGroupBox("列映射 (将源列映射到目标标准列)")
        mapping_layout = QFormLayout(mapping_group)
        mapping_layout.setSpacing(10)
        for target_col in self.target_columns:
            combo = QComboBox()
            combo.setMinimumWidth(300)
            combo.addItem("<请先加载源文件列名>")
            self.column_mapping_combos[target_col] = combo
            mapping_layout.addRow(f"目标列 '{target_col}':", combo)
        layout.addWidget(mapping_group)
        action_group = QGroupBox("转换与保存")
        action_layout = QHBoxLayout(action_group)
        self.transform_btn = ModernButton("3. 转换并另存为", color="#36b9cc", icon_path="icons/save.png")
        self.clear_btn = ModernButton("清空设置", color="#f6c23e", icon_path="icons/clear.png")
        self.transform_btn.clicked.connect(self.transform_and_save)
        self.clear_btn.clicked.connect(self.clear_formatter_settings)
        self.transform_btn.setEnabled(False)
        action_layout.addWidget(self.transform_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addStretch()
        layout.addWidget(action_group)
        layout.addStretch()

    def select_input_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择一个CSV数据文件", "", "CSV 文件 (*.csv)")
        if filepath:
            self.input_file_path = filepath
            self.selected_file_label.setText(f"<b>已选择:</b> {os.path.basename(filepath)}")
            self.load_cols_btn.setEnabled(True)
            self.transform_btn.setEnabled(False)
            self.clear_formatter_settings(reset_path=False)
        else:
            self.selected_file_label.setText("未选择源文件。")

    def load_source_columns(self):
        if not self.input_file_path: return
        try:
            try: self.source_df = pd.read_csv(self.input_file_path, encoding='utf-8-sig')
            except UnicodeDecodeError: self.source_df = pd.read_csv(self.input_file_path, encoding='gbk')
            self.source_df.dropna(how='all', inplace=True)
            if self.source_df.empty:
                QMessageBox.critical(self, "文件错误", "源CSV文件为空或无法解析。")
                return
            source_columns = [""] + list(self.source_df.columns)
            for target_col, combo in self.column_mapping_combos.items():
                combo.clear()
                combo.addItems(source_columns)
            self.transform_btn.setEnabled(True)
            QMessageBox.information(self, "加载成功", f"源文件列名已加载。共 {len(self.source_df)} 行数据。")
        except Exception as e:
            QMessageBox.critical(self, "文件读取错误", f"加载源文件失败: {e}")
            self.clear_formatter_settings()

    def transform_and_save(self):
        if self.source_df is None: return
        transformed_data = {}
        for target_col, combo in self.column_mapping_combos.items():
            source_col_name = combo.currentText()
            if source_col_name and source_col_name in self.source_df.columns:
                transformed_data[target_col] = self.source_df[source_col_name]
            else:
                transformed_data[target_col] = pd.Series([pd.NA] * len(self.source_df), name=target_col)
        transformed_df = pd.DataFrame(transformed_data)[self.target_columns]
        output_dir = os.path.join(os.getcwd(), "output", "csv_formatted")
        os.makedirs(output_dir, exist_ok=True)
        initial_filename = f"{os.path.splitext(os.path.basename(self.input_file_path))[0]}_formatted.csv"
        save_path, _ = QFileDialog.getSaveFileName(self, "保存转换后的标准CSV文件", os.path.join(output_dir, initial_filename), "CSV 文件 (*.csv)")
        if save_path:
            try:
                transformed_df.to_csv(save_path, index=False, encoding='utf-8-sig')
                reply = QMessageBox.information(self, "转换成功", f"标准格式的CSV文件已保存到:\n{save_path}", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open)
                if reply == QMessageBox.StandardButton.Open:
                    open_file_auto(save_path)
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存文件失败: {e}")

    def clear_formatter_settings(self, reset_path=True):
        self.source_df = None
        if reset_path:
            self.input_file_path = None
            self.selected_file_label.setText("尚未选择源文件")
        self.load_cols_btn.setEnabled(bool(self.input_file_path))
        self.transform_btn.setEnabled(False)
        for combo in self.column_mapping_combos.values():
            combo.clear()
            combo.addItem("<请先加载源文件列名>")

class BoreholeTab(QWidget):
    """钻孔数据批量处理与分析 - 现代化设计"""
    def __init__(self, main_win=None, parent=None):
        super().__init__(parent)
        self.main_win = main_win or self.window()
        self.all_processed_data = []
        self.filtered_df = pd.DataFrame()
        self.input_files = []
        self.processing_summary = {}
        self._current_task = None
        self.init_ui()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        # --- 左侧控制面板 - 添加滚动功能和紧凑设计 ---
        control_panel = QFrame()
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #fafbfc;
                border-right: 1px solid #e5e7eb;
            }
        """)
        
        # 使用 QScrollArea 使控制面板在内容过多时可以滚动
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(control_panel)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 20, 15, 20)  # 减小左右边距
        control_layout.setSpacing(15)  # 减小组件间距

        # 1. 文件选择与处理组 - 紧凑设计
        process_group = QGroupBox("文件处理")
        process_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        process_layout = QVBoxLayout(process_group)
        process_layout.setSpacing(8)
        
        # 创建紧凑的按钮
        button_style = "QPushButton { padding: 8px 12px; font-size: 12px; min-height: 16px; max-height: 32px; }"
        
        self.select_files_btn = ModernButton("选择钻孔文件", color="#2563eb")
        self.select_files_btn.setStyleSheet(self.select_files_btn.styleSheet() + button_style)
        self.process_files_btn = ModernButton("开始批量处理", color="#059669")
        self.process_files_btn.setStyleSheet(self.process_files_btn.styleSheet() + button_style)
        
        self.file_status_label = QLabel("请先选择一个或多个钻孔CSV文件。")
        self.file_status_label.setWordWrap(True)
        self.file_status_label.setStyleSheet("""
            QLabel {
                color: #6b7280; background-color: #ffffff; padding: 12px;
                border-radius: 8px; border: 1px solid #e5e7eb; font-size: 12px; line-height: 1.4;
                max-height: 120px;
            }
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(8)  # 减小进度条高度
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none; border-radius: 4px; background-color: #f3f4f6;
                height: 6px; text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 4px;
            }
        """)
        
        self.processing_status_label = QLabel("")
        self.processing_status_label.setWordWrap(True)
        self.processing_status_label.setStyleSheet("QLabel { color: #374151; font-size: 12px; font-weight: 500; padding: 6px 0; }")
        
        self.summary_text = QLabel("")
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet("""
            QLabel {
                background-color: #ffffff; padding: 12px; border-radius: 8px;
                border: 1px solid #e5e7eb; font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                font-size: 11px; color: #374151; line-height: 1.4; max-height: 200px;
            }
        """)
        self.summary_text.setVisible(False)
        
        self.select_files_btn.clicked.connect(self.select_input_files)
        self.process_files_btn.clicked.connect(self.process_selected_files)
        self.process_files_btn.setEnabled(False)
        
        process_layout.addWidget(self.select_files_btn)
        process_layout.addWidget(self.process_files_btn)
        process_layout.addWidget(self.file_status_label)
        process_layout.addWidget(self.progress_bar)
        process_layout.addWidget(self.processing_status_label)
        process_layout.addWidget(self.summary_text)
        control_layout.addWidget(process_group)

        # 2. 数据筛选组 - 紧凑设计
        filter_group = QGroupBox("数据筛选")
        filter_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        filter_layout = QFormLayout(filter_group)
        filter_layout.setVerticalSpacing(6)  # 减小垂直间距
        filter_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 设置下拉框样式，减小高度
        combo_style = """
            QComboBox {
                border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px;
                background-color: #ffffff; color: #374151; font-size: 13px; 
                min-height: 16px; max-height: 24px;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox:focus { border-color: #2563eb; outline: none; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none; border-left: 4px solid transparent; border-right: 4px solid transparent;
                border-top: 5px solid #6b7280; margin-right: 6px;
            }
        """
        
        self.coal_seam_filter_combo = QComboBox()
        self.coal_seam_filter_combo.addItem("显示所有煤层")
        self.coal_seam_filter_combo.setStyleSheet(combo_style)
        self.coal_seam_filter_combo.currentIndexChanged.connect(self.apply_coal_seam_filter)
        
        self.borehole_filter_combo = QComboBox()
        self.borehole_filter_combo.addItem("显示所有钻孔")
        self.borehole_filter_combo.setStyleSheet(combo_style)
        self.borehole_filter_combo.currentIndexChanged.connect(self.apply_borehole_filter)
        
        filter_layout.addRow("煤层筛选:", self.coal_seam_filter_combo)
        filter_layout.addRow("钻孔筛选:", self.borehole_filter_combo)
        
        self.stats_label = QLabel("数据统计：\n• 处理的文件数: 0\n• 煤层记录数: 0\n• 钻孔数量: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #6b7280; font-size: 12px; padding: 10px; background-color: #f9fafb;
                border-radius: 6px; border: 1px solid #f3f4f6; line-height: 1.4;
            }
        """)
        filter_layout.addRow("", self.stats_label)
        control_layout.addWidget(filter_group)

        # 3. 数据导出组 - 紧凑设计
        export_group = QGroupBox("数据操作")
        export_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(8)
        
        self.export_btn = ModernButton("导出筛选结果", color="#0891b2")
        self.export_btn.setStyleSheet(self.export_btn.styleSheet() + button_style)
        self.export_summary_btn = ModernButton("导出处理摘要", color="#7c3aed")
        self.export_summary_btn.setStyleSheet(self.export_summary_btn.styleSheet() + button_style)
        self.clear_data_btn = ModernButton("清空所有数据", color="#dc2626")
        self.clear_data_btn.setStyleSheet(self.clear_data_btn.styleSheet() + button_style)
        
        self.export_btn.clicked.connect(self.export_filtered_data)
        self.export_summary_btn.clicked.connect(self.export_processing_summary)
        self.clear_data_btn.clicked.connect(self.clear_all_data)
        
        export_layout.addWidget(self.export_btn)
        export_layout.addWidget(self.export_summary_btn)
        export_layout.addWidget(self.clear_data_btn)
        control_layout.addWidget(export_group)
        control_layout.addStretch()  # 添加弹性空间

        # --- 右侧结果展示面板 ---
        results_panel = QFrame()
        results_panel.setStyleSheet("QFrame { background-color: #ffffff; }")
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(24, 24, 24, 24)
        
        results_title = QLabel("钻孔数据处理结果")
        results_title.setStyleSheet("""
            QLabel {
                font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 16px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
        """)
        results_layout.addWidget(results_title)
        
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb; border-radius: 8px; gridline-color: #f3f4f6;
                background-color: #ffffff; alternate-background-color: #f9fafb;
                selection-background-color: #eff6ff; font-size: 14px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8fafc, stop:1 #f1f5f9);
                padding: 12px 16px; border: none; border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb; font-weight: 600; color: #374151;
                text-align: left; font-size: 13px;
            }
            QHeaderView::section:first { border-top-left-radius: 8px; }
            QHeaderView::section:last { border-top-right-radius: 8px; border-right: none; }
            QTableWidget::item { padding: 12px 16px; border-bottom: 1px solid #f3f4f6; color: #374151; }
            QTableWidget::item:selected { background-color: #dbeafe; color: #1e40af; }
            QTableWidget::item:hover { background-color: #f8fafc; }
        """)
        results_layout.addWidget(self.results_table)

        # --- 添加到主分割器 ---
        # 使用带滚动条的 scroll_area 替代原来的 control_panel
        main_splitter.addWidget(scroll_area)
        main_splitter.addWidget(results_panel)
        
        # --- 优化比例 ---
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([420, 960])  # 减小左侧面板宽度
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
    def select_input_files(self):
        """选择输入文件并显示详细信息"""
        files, _ = QFileDialog.getOpenFileNames(self, "选择一个或多个钻孔CSV文件", "", "CSV 文件 (*.csv)")
        if files:
            self.input_files = files
            
            # 计算文件大小统计
            total_size = 0
            file_info = []
            for file in files:
                try:
                    size = os.path.getsize(file) / 1024  # KB
                    total_size += size
                    file_info.append(f"• {os.path.basename(file)} ({size:.1f} KB)")
                except:
                    file_info.append(f"• {os.path.basename(file)} (大小未知)")
            
            # 更新文件状态显示
            status_text = f"""📁 已选择 {len(files)} 个文件 (总大小: {total_size:.1f} KB)

文件列表:
{chr(10).join(file_info[:10])}"""
            
            if len(file_info) > 10:
                status_text += f"\n... 还有 {len(file_info) - 10} 个文件"
            
            self.file_status_label.setText(status_text)
            self.process_files_btn.setEnabled(True)
            self.clear_preview()
            
            # 重置处理摘要
            self.processing_summary = {}
            self.summary_text.setVisible(False)

    def process_selected_files(self):
        """批量处理选中的文件，提供详细的进度反馈"""
        if not self.input_files:
            return

        if self._current_task is not None:
            QMessageBox.information(self, "任务进行中", "当前已有处理任务在执行，请稍后再试。")
            return

        self.all_processed_data.clear()
        self.processing_summary = {}
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.input_files))
        self.progress_bar.setValue(0)
        self.processing_status_label.setText("正在准备批处理任务...")
        self.summary_text.setVisible(False)

        self.process_files_btn.setEnabled(False)
        self.process_files_btn.setText("处理中...")

        worker = FunctionWorker(self._process_files_task, list(self.input_files))
        worker.signals.progress.connect(self._on_processing_progress)
        worker.signals.message.connect(self._on_processing_message)
        worker.signals.finished.connect(self._on_processing_finished)
        worker.signals.error.connect(self._on_processing_error)
        self._current_task = TaskHandle(worker=worker)
        worker.start()

    def _process_files_task(self, files, progress_callback=None, message_callback=None):
        import time

        summary = {
            'total_files': len(files),
            'successful_files': 0,
            'failed_files': 0,
            'warning_files': 0,
            'total_coal_records': 0,
            'error_details': [],
            'warning_details': [],
            'processing_time': 0,
            'file_details': []
        }
        all_processed = []

        start_time = time.time()
        for index, file_path in enumerate(files):
            file_name = os.path.basename(file_path)
            if message_callback:
                message_callback(f"正在处理: {file_name} ({index + 1}/{len(files)})")

            try:
                processed_data, msg, level = process_single_borehole_file(file_path)
                file_detail = {
                    'file_name': file_name,
                    'status': level,
                    'message': msg,
                    'coal_records': len(processed_data) if processed_data else 0
                }

                if level == "error":
                    summary['failed_files'] += 1
                    summary['error_details'].append(f"{file_name}: {msg}")
                elif level == "warning":
                    summary['warning_files'] += 1
                    summary['warning_details'].append(f"{file_name}: {msg}")
                    if processed_data:
                        all_processed.extend(processed_data)
                        summary['total_coal_records'] += len(processed_data)
                else:
                    summary['successful_files'] += 1
                    if processed_data:
                        all_processed.extend(processed_data)
                        summary['total_coal_records'] += len(processed_data)

                summary['file_details'].append(file_detail)
            except Exception as exc:  # pragma: no cover
                error_msg = f"处理文件时发生意外错误: {exc}"
                summary['failed_files'] += 1
                summary['error_details'].append(f"{file_name}: {error_msg}")
                summary['file_details'].append({
                    'file_name': file_name,
                    'status': 'error',
                    'message': error_msg,
                    'coal_records': 0
                })

            if progress_callback:
                progress_callback(index + 1)

        summary['processing_time'] = time.time() - start_time

        return {
            'all_processed_data': all_processed,
            'processing_summary': summary,
        }

    def _on_processing_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _on_processing_message(self, message: str):
        self.processing_status_label.setText(message)

    def _on_processing_finished(self, result):
        self._current_task = None
        self.process_files_btn.setEnabled(True)
        self.process_files_btn.setText("2. 开始批量处理")
        self.progress_bar.setVisible(False)

        self.all_processed_data = result['all_processed_data']
        self.processing_summary = result['processing_summary']

        if not self.all_processed_data:
            self._show_processing_summary()
            self.processing_status_label.setText("❌ 处理完成，但未提取到有效数据")
            self.processing_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.warning(self, "处理完成", "未从所选文件中提取到有效的煤层数据。\n\n请检查文件格式和内容。")
            return

        self.processing_status_label.setStyleSheet("color: #374151; font-size: 12px; font-weight: 500; padding: 6px 0;")
        self.update_filter_options()
        self.apply_filters()
        self._update_statistics()
        self._show_processing_summary()

    def _on_processing_error(self, exc):
        self._current_task = None
        self.progress_bar.setVisible(False)
        self.process_files_btn.setEnabled(True)
        self.process_files_btn.setText("2. 开始批量处理")
        self.processing_status_label.setText("❌ 处理失败")
        self.processing_status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        QMessageBox.critical(self, "处理失败", f"批量处理过程中出现错误：\n{exc}")

    def _show_processing_summary(self):
        """显示详细的处理摘要"""
        summary = self.processing_summary
        
        # 计算成功率
        success_rate = (summary['successful_files'] / summary['total_files'] * 100) if summary['total_files'] > 0 else 0
        
        # 计算平均每文件记录数 - 修复除零错误
        avg_records_per_file = 0
        if summary['successful_files'] > 0:
            avg_records_per_file = summary['total_coal_records'] / summary['successful_files']
        
        # 生成摘要文本
        summary_text = f"""📊 批量处理完成摘要

⏱️ 处理时间: {summary['processing_time']:.2f} 秒
📁 文件统计:
  • 总文件数: {summary['total_files']}
  • 成功处理: {summary['successful_files']} ({success_rate:.1f}%)
  • 处理失败: {summary['failed_files']}
  • 警告信息: {summary['warning_files']}

📋 数据统计:
  • 提取煤层记录: {summary['total_coal_records']} 条
  • 平均每文件: {avg_records_per_file:.1f} 条 (基于成功文件)

"""
        
        # 添加错误详情
        if summary['error_details']:
            summary_text += f"❌ 错误详情 ({len(summary['error_details'])} 个):\n"
            for error in summary['error_details'][:5]:  # 只显示前5个错误
                summary_text += f"  • {error}\n"
            if len(summary['error_details']) > 5:
                summary_text += f"  ... 还有 {len(summary['error_details']) - 5} 个错误\n"
        
        # 添加警告详情
        if summary['warning_details']:
            summary_text += f"\n⚠️ 警告详情 ({len(summary['warning_details'])} 个):\n"
            for warning in summary['warning_details'][:3]:  # 只显示前3个警告
                summary_text += f"  • {warning}\n"
            if len(summary['warning_details']) > 3:
                summary_text += f"  ... 还有 {len(summary['warning_details']) - 3} 个警告\n"
        
        # 显示摘要
        self.summary_text.setText(summary_text)
        self.summary_text.setVisible(True)
        
        # 更新处理状态标签
        if summary['successful_files'] > 0:
            self.processing_status_label.setText(f"✅ 处理完成！成功提取 {summary['total_coal_records']} 条煤层记录")
            self.processing_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.processing_status_label.setText("❌ 处理完成，但未提取到有效数据")
            self.processing_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")

    def update_filter_options(self):
        """更新筛选选项"""
        if not self.all_processed_data:
            return
        
        df = pd.DataFrame(self.all_processed_data)
        
        # 更新煤层筛选选项
        self.coal_seam_filter_combo.blockSignals(True)
        current_coal = self.coal_seam_filter_combo.currentText()
        self.coal_seam_filter_combo.clear()
        self.coal_seam_filter_combo.addItem("显示所有煤层")
        unique_coals = sorted(df['煤层'].unique())
        self.coal_seam_filter_combo.addItems(unique_coals)
        if current_coal in unique_coals:
            self.coal_seam_filter_combo.setCurrentText(current_coal)
        self.coal_seam_filter_combo.blockSignals(False)
        
        # 更新钻孔筛选选项
        self.borehole_filter_combo.blockSignals(True)
        current_borehole = self.borehole_filter_combo.currentText()
        self.borehole_filter_combo.clear()
        self.borehole_filter_combo.addItem("显示所有钻孔")
        unique_boreholes = sorted(df['钻孔名'].unique())
        self.borehole_filter_combo.addItems(unique_boreholes)
        if current_borehole in unique_boreholes:
            self.borehole_filter_combo.setCurrentText(current_borehole)
        self.borehole_filter_combo.blockSignals(False)

    def apply_coal_seam_filter(self):
        """应用煤层筛选"""
        self.apply_filters()

    def apply_borehole_filter(self):
        """应用钻孔筛选"""
        self.apply_filters()

    def apply_filters(self):
        """应用所有筛选条件"""
        if not self.all_processed_data:
            self.clear_preview()
            return
        
        full_df = pd.DataFrame(self.all_processed_data)
        
        # 应用煤层筛选
        selected_coal = self.coal_seam_filter_combo.currentText()
        if selected_coal != "显示所有煤层":
            full_df = full_df[full_df['煤层'] == selected_coal]
        
        # 应用钻孔筛选
        selected_borehole = self.borehole_filter_combo.currentText()
        if selected_borehole != "显示所有钻孔":
            full_df = full_df[full_df['钻孔名'] == selected_borehole]
        
        self.filtered_df = full_df
        self.display_dataframe_in_table(self.filtered_df)
        self._update_statistics()

    def _update_statistics(self):
        """更新统计信息显示"""
        if self.all_processed_data:
            full_df = pd.DataFrame(self.all_processed_data)
            total_records = len(full_df)
            unique_boreholes = full_df['钻孔名'].nunique()
            unique_coals = full_df['煤层'].nunique()
            filtered_records = len(self.filtered_df)
            
            stats_text = f"""数据统计：
• 处理的文件数: {self.processing_summary.get('total_files', 0)}
• 总煤层记录: {total_records}
• 当前显示: {filtered_records}
• 钻孔数量: {unique_boreholes}
• 煤层种类: {unique_coals}"""
        else:
            stats_text = "数据统计：\n• 处理的文件数: 0\n• 煤层记录数: 0\n• 钻孔数量: 0"
        
        self.stats_label.setText(stats_text)

    def display_dataframe_in_table(self, df):
        """在表格中显示数据框，支持更好的格式化"""
        self.results_table.clear()
        if df.empty:
            # 如果df为空，也设置表头
            self.results_table.setColumnCount(1)
            self.results_table.setHorizontalHeaderLabels(["无数据"])
            self.results_table.setRowCount(0)
            return
        
        # 导入QColor
        from PyQt6.QtGui import QColor
        # 定义自定义颜色
        color_borehole = QColor("#e0f7fa")  # 浅蓝色
        color_key_stratum = QColor("#f0fdf4")  # 浅绿色

        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        
        for i, row in enumerate(df.itertuples(index=False)):
            for j, value in enumerate(row):
                # 格式化数值显示 - 数值类型保留2位小数
                if pd.notna(value):
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        # 对于数值类型，保留2位小数
                        if abs(value - round(value)) < 1e-10:  # 接近整数的数
                            item_text = str(int(round(value)))
                        else:
                            item_text = f"{value:.2f}"
                    else:
                        item_text = str(value)
                else:
                    item_text = ""
                
                item = QTableWidgetItem(item_text)
                
                # 为特定列添加样式
                if df.columns[j] == '钻孔名':
                    item.setBackground(color_borehole)
                elif '关键层' in df.columns[j] and str(value) != 'N/A':
                    item.setBackground(color_key_stratum)
                
                self.results_table.setItem(i, j, item)
        
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)


    def export_filtered_data(self):
        """导出当前筛选的数据"""
        if self.filtered_df.empty:
            QMessageBox.warning(self, "无数据", "没有数据可导出。请先处理一些文件。")
            return
        
        output_dir = os.path.join(os.getcwd(), "output", "borehole_analysis")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        filter_info = []
        if self.coal_seam_filter_combo.currentText() != "显示所有煤层":
            filter_info.append(f"煤层_{self.coal_seam_filter_combo.currentText()}")
        if self.borehole_filter_combo.currentText() != "显示所有钻孔":
            filter_info.append(f"钻孔_{self.borehole_filter_combo.currentText()}")
        
        if filter_info:
            filename = f"钻孔分析结果_{'_'.join(filter_info)}.xlsx"
        else:
            filename = "钻孔分析结果_全部数据.xlsx"
        
        save_path, _ = QFileDialog.getSaveFileName(self, "导出筛选数据", 
                                                 os.path.join(output_dir, filename), 
                                                 "Excel 文件 (*.xlsx);;CSV 文件 (*.csv)")
        
        if save_path:
            try:
                if save_path.endswith('.xlsx'):
                    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                        # 导出筛选数据
                        self.filtered_df.to_excel(writer, sheet_name='钻孔分析结果', index=False)
                        
                        # 导出统计摘要
                        if self.all_processed_data:
                            full_df = pd.DataFrame(self.all_processed_data)
                            summary_stats = {
                                '统计项目': ['总记录数', '钻孔数量', '煤层种类', '平均煤层厚度', '最大煤层厚度', '最小煤层厚度'],
                                '数值': [
                                    len(full_df),
                                    full_df['钻孔名'].nunique(),
                                    full_df['煤层'].nunique(),
                                    f"{full_df['煤层厚度'].mean():.2f} m",
                                    f"{full_df['煤层厚度'].max():.2f} m",
                                    f"{full_df['煤层厚度'].min():.2f} m"
                                ]
                            }
                            pd.DataFrame(summary_stats).to_excel(writer, sheet_name='数据统计', index=False)
                else:
                    self.filtered_df.to_csv(save_path, index=False, encoding='utf-8-sig')
                
                QMessageBox.information(self, "导出成功", f"数据已成功导出到:\n{save_path}")
                
                if QMessageBox.question(self, "打开文件", "是否要打开导出的文件？") == QMessageBox.StandardButton.Yes:
                    open_file_auto(save_path)
                    
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出文件时发生错误: {e}")

    def export_processing_summary(self):
        """导出处理摘要报告"""
        if not self.processing_summary:
            QMessageBox.warning(self, "无摘要", "没有处理摘要可导出。请先处理一些文件。")
            return
        
        output_dir = os.path.join(os.getcwd(), "output", "borehole_analysis")
        os.makedirs(output_dir, exist_ok=True)
        
        save_path, _ = QFileDialog.getSaveFileName(self, "导出处理摘要", 
                                                 os.path.join(output_dir, "钻孔处理摘要报告.xlsx"), 
                                                 "Excel 文件 (*.xlsx)")
        
        if save_path:
            try:
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    # 处理摘要
                    summary_data = {
                        '项目': ['总文件数', '成功处理', '处理失败', '警告信息', '提取煤层记录', '处理时间(秒)'],
                        '数值': [
                            self.processing_summary['total_files'],
                            self.processing_summary['successful_files'],
                            self.processing_summary['failed_files'],
                            self.processing_summary['warning_files'],
                            self.processing_summary['total_coal_records'],
                            f"{self.processing_summary['processing_time']:.2f}"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='处理摘要', index=False)
                    
                    # 文件详情
                    if self.processing_summary['file_details']:
                        file_details_df = pd.DataFrame(self.processing_summary['file_details'])
                        file_details_df.to_excel(writer, sheet_name='文件处理详情', index=False)
                    
                    # 错误详情
                    if self.processing_summary['error_details']:
                        error_df = pd.DataFrame({'错误信息': self.processing_summary['error_details']})
                        error_df.to_excel(writer, sheet_name='错误详情', index=False)
                
                QMessageBox.information(self, "导出成功", f"处理摘要报告已保存到:\n{save_path}")
                
                if QMessageBox.question(self, "打开文件", "是否要打开导出的文件？") == QMessageBox.StandardButton.Yes:
                    open_file_auto(save_path)
                    
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出摘要时发生错误: {e}")

    def clear_all_data(self):
        """清空所有数据和状态"""
        reply = QMessageBox.question(self, "确认清空", 
                                   "确定要清空所有处理数据和结果吗？\n\n此操作不可撤销。",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.all_processed_data.clear()
            self.filtered_df = pd.DataFrame()
            self.input_files = []
            self.processing_summary = {}
            
            # 重置界面
            self.clear_preview()
            self.file_status_label.setText("请先选择一个或多个钻孔CSV文件。")
            self.processing_status_label.setText("")
            self.processing_status_label.setStyleSheet("color: #5a5c69; font-size: 12px;")
            self.summary_text.setVisible(False)
            self.progress_bar.setVisible(False)
            self.process_files_btn.setEnabled(False)
            
            # 重置筛选选项
            self.coal_seam_filter_combo.clear()
            self.coal_seam_filter_combo.addItem("显示所有煤层")
            self.borehole_filter_combo.clear()
            self.borehole_filter_combo.addItem("显示所有钻孔")
            
            self._update_statistics()
            
            QMessageBox.information(self, "清空完成", "所有数据和状态已清空。")

    def clear_preview(self):
        """清空预览表格"""
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)

class DatabaseOverviewPage(QWidget):
    """数据库模块首页：展示地图、统计及快速入口"""

    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.data_df = pd.DataFrame()
        self.source_path: Optional[str] = None
        self.web_view = QWebEngineView() if QWebEngineView is not None else None
        self.map_container: Optional[QStackedWidget] = None
        self.map_placeholder: Optional[QLabel] = None
        self.map_hint_label: Optional[QLabel] = None
        self.status_label: Optional[QLabel] = None
        self.stat_labels: Dict[str, QLabel] = {}
        self.province_table: Optional[QTableWidget] = None
        self.sample_table: Optional[QTableWidget] = None
        self.refresh_btn: Optional[ModernButton] = None
        self._init_ui()
        self.refresh_content()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("dbOverviewScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        outer_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        title_label = QLabel("岩石数据库全景概览")
        title_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch(1)

        self.refresh_btn = ModernButton("刷新数据", color="#0ea5e9", icon_path="icons/refresh.png")
        self.refresh_btn.clicked.connect(self.refresh_content)
        header_layout.addWidget(self.refresh_btn)

        manage_btn = ModernButton("打开可编辑数据库", color="#2563eb", icon_path="icons/database.png")
        manage_btn.clicked.connect(lambda: self.main_win.navigate_to_module_feature("煤岩层力学参数数据库", "岩石属性数据库"))
        header_layout.addWidget(manage_btn)

        content_layout.addLayout(header_layout)
        content_layout.addSpacing(6)

        self.status_label = QLabel("正在载入数据…")
        self.status_label.setStyleSheet("color: #475569; font-size: 13px;")
        self.status_label.setWordWrap(True)
        content_layout.addWidget(self.status_label)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.setChildrenCollapsible(False)
        top_splitter.setHandleWidth(12)

        map_card = QFrame()
        map_card.setObjectName("dbMapCard")
        map_card.setStyleSheet("QFrame#dbMapCard { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 18px; }")
        map_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        map_card.setMinimumHeight(420)
        map_layout = QVBoxLayout(map_card)
        map_layout.setContentsMargins(18, 18, 18, 18)
        map_layout.setSpacing(12)

        map_title = QLabel("全国省份覆盖情况")
        map_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        map_header = QHBoxLayout()
        map_header.setContentsMargins(0, 0, 0, 0)
        map_header.setSpacing(8)
        map_header.addWidget(map_title)

        map_header.addStretch(1)

        self.map_refresh_hint = QLabel("数据实时更新 · 支持缩放与拖拽")
        self.map_refresh_hint.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.map_refresh_hint.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        map_header.addWidget(self.map_refresh_hint)

        map_layout.addLayout(map_header)

        self.map_container = QStackedWidget()
        self.map_container.setContentsMargins(0, 0, 0, 0)
        self.map_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.map_container.setMinimumSize(300, 300)

        self.map_placeholder = QLabel("正在生成地图…")
        self.map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_placeholder.setStyleSheet("color: #64748b; font-size: 14px; border-radius: 12px; padding: 24px;")
        self.map_placeholder.setWordWrap(True)

        if self.web_view is not None:
            self.web_view.setMinimumSize(560, 400)
            self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.map_container.addWidget(self.web_view)
        self.map_container.addWidget(self.map_placeholder)

        map_layout.addWidget(self.map_container, 1)

        self.map_hint_label = QLabel("提示：鼠标滚轮缩放，右键拖拽可平移，双击可重新居中视图。")
        self.map_hint_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.map_hint_label.setWordWrap(True)
        map_layout.addWidget(self.map_hint_label)
        top_splitter.addWidget(map_card)

        stats_card = QFrame()
        stats_card.setObjectName("dbStatsCard")
        stats_card.setStyleSheet("QFrame#dbStatsCard { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 18px; }")
        stats_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        stats_card.setMinimumWidth(300)
        stats_card.setMaximumWidth(360)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(18, 18, 18, 18)
        stats_layout.setSpacing(14)

        stats_title = QLabel("核心统计")
        stats_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        stats_layout.addWidget(stats_title)

        metrics_grid = QGridLayout()
        metrics_grid.setContentsMargins(0, 0, 0, 0)
        metrics_grid.setHorizontalSpacing(12)
        metrics_grid.setVerticalSpacing(12)
        metrics_grid.setColumnStretch(0, 1)
        metrics_grid.setColumnStretch(1, 1)
        metrics_grid.setColumnStretch(2, 1)

        metric_defs = [
            ("总样本", "records"),
            ("覆盖省份", "provinces"),
            ("矿山数量", "mines"),
            ("岩性类型", "lithologies"),
            ("文献来源", "references"),
        ]

        for idx, (title, key) in enumerate(metric_defs):
            card, value_label = self._create_stat_chip(title)
            self.stat_labels[key] = value_label
            row, col = divmod(idx, 3)
            metrics_grid.addWidget(card, row, col)

        stats_layout.addLayout(metrics_grid)
        stats_layout.addSpacing(8)

        province_label = QLabel("省份样本占比 Top 8")
        province_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #1f2937;")
        stats_layout.addSpacing(4)
        stats_layout.addWidget(province_label)

        self.province_table = QTableWidget()
        self.province_table.setColumnCount(3)
        self.province_table.setHorizontalHeaderLabels(["省份", "样本数", "占比%"])
        self.province_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.province_table.verticalHeader().setVisible(False)
        self.province_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.province_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.province_table.setAlternatingRowColors(True)
        self.province_table.setStyleSheet("QTableWidget { border: 1px solid #e2e8f0; border-radius: 12px; }")
        self.province_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.province_table.setMinimumHeight(300)
        stats_layout.addWidget(self.province_table, 1)
        stats_layout.addStretch(1)

        top_splitter.addWidget(stats_card)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 1)
        top_splitter.setSizes([940, 320])

        table_card = QFrame()
        table_card.setObjectName("dbSampleCard")
        table_card.setStyleSheet("QFrame#dbSampleCard { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 18px; }")
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_card.setMinimumHeight(320)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(22, 20, 22, 22)
        table_layout.setSpacing(12)

        table_title = QLabel("省份统计摘要")
        table_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        table_layout.addWidget(table_title)

        subtitle = QLabel("展示样本量排名靠前省份的文献、矿井、煤岩层数量，双击行可复制数据。")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.5;")
        subtitle.setWordWrap(True)
        table_layout.addWidget(subtitle)
        table_layout.addSpacing(6)

        self.sample_table = QTableWidget()
        self.sample_table.setAlternatingRowColors(True)
        self.sample_table.verticalHeader().setVisible(False)
        self.sample_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sample_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.sample_table.setStyleSheet("QTableWidget { border: 1px solid #e2e8f0; border-radius: 12px; }")
        self.sample_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sample_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.sample_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sample_table.setWordWrap(False)
        self.sample_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sample_table.setMinimumHeight(280)
        self.sample_table.verticalHeader().setDefaultSectionSize(36)
        self.sample_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(self.sample_table, 1)
        table_layout.addStretch(1)

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(12)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(table_card)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setSizes([660, 360])

        content_layout.addWidget(main_splitter)
        content_layout.setStretch(content_layout.count() - 1, 1)

    def _create_stat_chip(self, title: str):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(0, 4, 0, 4)
        vbox.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #475569; font-size: 13px; font-weight: 600;")
        vbox.addWidget(title_label)

        value_label = QLabel("--")
        value_label.setStyleSheet("color: #1e3a8a; font-size: 22px; font-weight: 700;")
        vbox.addWidget(value_label)

        return frame, value_label

    def refresh_content(self):
        df, source_path, error_msg = self._load_dataset()
        self.data_df = df
        self.source_path = source_path

        if df is None or df.empty:
            message = error_msg or "未找到可用的数据源，请放置 \"汇总表.csv\" 于 data/input/ 目录。"
            if self.status_label is not None:
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: #dc2626; font-size: 13px;")
            self._clear_tables()
            self._render_map(None)
            return

        rel_path = os.path.relpath(source_path, resource_path("")) if source_path else ""
        if self.status_label is not None:
            self.status_label.setText(f"数据源：{rel_path} · 记录数 {len(df)} · 更新时间 {pd.Timestamp.now():%Y-%m-%d %H:%M}")
            self.status_label.setStyleSheet("color: #1e3a8a; font-size: 13px;")

        self._update_stat_cards(df)
        self._update_province_table(df)
        self._update_sample_table(df)
        self._render_map(df)

    def _load_dataset(self):
        candidates = [
            '汇总表.csv',
            os.path.join('data', 'input', '汇总表.csv'),
            os.path.join('data', 'input', 'huizongbiao.csv'),
        ]
        last_error = ""

        for relative in candidates:
            path = resource_path(relative)
            if not os.path.exists(path):
                continue
            df = self._read_csv(path)
            if df is not None:
                return df, path, ""
            last_error = f"无法读取文件：{path}"

        return pd.DataFrame(), None, last_error or "未找到汇总表数据文件。"

    def _read_csv(self, path: str) -> Optional[pd.DataFrame]:
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
        last_error = None
        for encoding in encodings:
            try:
                df = pd.read_csv(path, encoding=encoding)
                break
            except Exception as exc:  # pragma: no cover - 容错处理
                last_error = exc
                df = None
        if df is None:
            print(f"读取 {path} 失败: {last_error}")
            return None

        df.columns = [str(col).strip() for col in df.columns]
        df = df.loc[:, [col for col in df.columns if col and not str(col).startswith('Unnamed')]]

        rename_map = {}
        for col in df.columns:
            if col == '份':
                rename_map[col] = '省份'
            elif col.lower() in {'sheng', 'province'}:
                rename_map[col] = '省份'
            elif col in {'市/县', '市县', '地市'}:
                rename_map[col] = '地市'
            elif '弹性模量' in col or '体积模量' in col or '剪切模量' in col:
                rename_map[col] = (
                    col.replace('（', '(')
                    .replace('）', ')')
                    .replace(' ', '')
                )
            elif '密度' in col or '泊松比' in col or '内摩擦角' in col or '抗压强度' in col or '抗拉强度' in col or '内聚力' in col:
                rename_map[col] = (
                    col.replace('（', '(')
                    .replace('）', ')')
                    .replace(' ', '')
                )
        df = df.rename(columns=rename_map)

        if '省份' not in df.columns:
            df['省份'] = pd.NA

        df['省份'] = df['省份'].apply(self._normalize_province_name)
        df['省份'] = df['省份'].fillna('')

        for text_col in ['矿名', '文献', '岩性', '地市']:
            if text_col in df.columns:
                df[text_col] = (
                    df[text_col]
                    .astype(str)
                    .str.strip()
                    .replace({'nan': '', 'NaN': '', 'None': '', 'NULL': '', 'null': ''})
                )
            else:
                df[text_col] = ''

        numeric_keywords = ['模量', '强度', '角', '厚度', '密度', '埋深', '泊松', '体积']
        for col in df.columns:
            if any(keyword in col for keyword in numeric_keywords):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def _normalize_province_name(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, float) and pd.isna(value):
            return None

        name = str(value).strip()
        if not name:
            return None

        normalized = name
        for token in [' ', '　']:
            normalized = normalized.replace(token, '')

        lower = normalized.lower()
        if lower in {'nan', 'none', 'null', '无', '未标注', 'n/a', 'na'}:
            return None

        replacements = {
            '北京': '北京市',
            '北京市': '北京市',
            '天津': '天津市',
            '天津市': '天津市',
            '上海': '上海市',
            '上海市': '上海市',
            '重庆': '重庆市',
            '重庆市': '重庆市',
            '河北': '河北省',
            '河北省': '河北省',
            '山西': '山西省',
            '山西省': '山西省',
            '辽宁': '辽宁省',
            '辽宁省': '辽宁省',
            '吉林': '吉林省',
            '吉林省': '吉林省',
            '黑龙江': '黑龙江省',
            '黑龙江省': '黑龙江省',
            '江苏': '江苏省',
            '江苏省': '江苏省',
            '浙江': '浙江省',
            '浙江省': '浙江省',
            '安徽': '安徽省',
            '安徽省': '安徽省',
            '福建': '福建省',
            '福建省': '福建省',
            '江西': '江西省',
            '江西省': '江西省',
            '山东': '山东省',
            '山东省': '山东省',
            '河南': '河南省',
            '河南省': '河南省',
            '湖北': '湖北省',
            '湖北省': '湖北省',
            '湖南': '湖南省',
            '湖南省': '湖南省',
            '广东': '广东省',
            '广东省': '广东省',
            '海南': '海南省',
            '海南省': '海南省',
            '四川': '四川省',
            '四川省': '四川省',
            '贵州': '贵州省',
            '贵州省': '贵州省',
            '云南': '云南省',
            '云南省': '云南省',
            '陕西': '陕西省',
            '陕西省': '陕西省',
            '甘肃': '甘肃省',
            '甘肃省': '甘肃省',
            '青海': '青海省',
            '青海省': '青海省',
            '台湾': '台湾省',
            '台湾省': '台湾省',
            '内蒙古': '内蒙古自治区',
            '内蒙古自治区': '内蒙古自治区',
            '广西': '广西壮族自治区',
            '广西壮族自治区': '广西壮族自治区',
            '宁夏': '宁夏回族自治区',
            '宁夏回族自治区': '宁夏回族自治区',
            '新疆': '新疆维吾尔自治区',
            '新疆维吾尔自治区': '新疆维吾尔自治区',
            '西藏': '西藏自治区',
            '西藏自治区': '西藏自治区',
            '香港': '香港特别行政区',
            '香港特别行政区': '香港特别行政区',
            '澳门': '澳门特别行政区',
            '澳门特别行政区': '澳门特别行政区',
        }

        normalized = replacements.get(normalized, normalized)

        return normalized

    def _province_display_name(self, normalized: str) -> str:
        display = normalized
        for token in ['省', '市', '自治区', '特别行政区', '壮族', '回族', '维吾尔']:
            display = display.replace(token, '')
        return display

    def _update_stat_cards(self, df: pd.DataFrame):
        total = len(df)
        province_count = df['省份'].replace('', pd.NA).dropna().nunique() if '省份' in df else 0
        mine_count = df['矿名'].replace('', pd.NA).dropna().nunique() if '矿名' in df else 0
        lithology_count = df['岩性'].replace('', pd.NA).dropna().nunique() if '岩性' in df else 0
        reference_count = df['文献'].replace('', pd.NA).dropna().nunique() if '文献' in df else 0

        stats = {
            'records': f"{total:,}",
            'provinces': str(province_count) if province_count else '—',
            'mines': str(mine_count) if mine_count else '—',
            'lithologies': str(lithology_count) if lithology_count else '—',
            'references': str(reference_count) if reference_count else '—',
        }

        for key, label in self.stat_labels.items():
            label.setText(stats.get(key, '--'))

    def _update_province_table(self, df: pd.DataFrame):
        if self.province_table is None:
            return

        if '省份' not in df:
            self.province_table.setRowCount(0)
            return

        province_series = df['省份'].replace('', pd.NA).dropna()
        if province_series.empty:
            self.province_table.setRowCount(0)
            return

        summary = province_series.value_counts().reset_index()
        summary.columns = ['省份', '样本数']
        summary['占比'] = summary['样本数'] / summary['样本数'].sum() * 100
        top_summary = summary.head(8)

        self.province_table.setRowCount(len(top_summary))
        for row, record in top_summary.iterrows():
            display_name = self._province_display_name(str(record['省份']))
            self.province_table.setItem(row, 0, QTableWidgetItem(display_name))
            self.province_table.setItem(row, 1, QTableWidgetItem(f"{int(record['样本数'])}"))
            self.province_table.setItem(row, 2, QTableWidgetItem(f"{record['占比']:.1f}"))

        self.province_table.resizeColumnsToContents()

        if self.map_hint_label is not None:
            self.map_hint_label.setText(
                f"覆盖 {summary['省份'].nunique()} 个省份 · 当前展示前 {len(top_summary)} 位"
            )

    def _update_sample_table(self, df: pd.DataFrame):
        if self.sample_table is None:
            return

        if '省份' not in df.columns:
            self.sample_table.clear()
            self.sample_table.setRowCount(0)
            self.sample_table.setColumnCount(0)
            return

        province_series = df['省份'].replace('', pd.NA).dropna()
        if province_series.empty:
            self.sample_table.clear()
            self.sample_table.setRowCount(0)
            self.sample_table.setColumnCount(0)
            return

        top_provinces = province_series.value_counts().head(12)
        province_keys = top_provinces.index.tolist()
        province_headers = [self._province_display_name(name) for name in province_keys]

        metrics = [
            ("统计文献数", '文献'),
            ("统计矿井数", '矿名'),
            ("统计煤岩层数", '岩性'),
        ]

        self.sample_table.clear()
        self.sample_table.setRowCount(len(metrics))
        self.sample_table.setColumnCount(len(province_keys) + 1)
        self.sample_table.setHorizontalHeaderLabels(['指标'] + province_headers)

        for row_idx, (label, column_name) in enumerate(metrics):
            label_item = QTableWidgetItem(label)
            label_item.setForeground(Qt.GlobalColor.black)
            self.sample_table.setItem(row_idx, 0, label_item)

            if column_name not in df.columns:
                for col_idx in range(1, len(province_keys) + 1):
                    self.sample_table.setItem(row_idx, col_idx, QTableWidgetItem("0"))
                continue

            for col_idx, province_key in enumerate(province_keys, start=1):
                province_df = df[df['省份'] == province_key]
                unique_count = (
                    province_df[column_name]
                    .replace('', pd.NA)
                    .dropna()
                    .nunique()
                )
                self.sample_table.setItem(row_idx, col_idx, QTableWidgetItem(str(unique_count)))

        self.sample_table.resizeColumnsToContents()
        self.sample_table.horizontalHeader().setMinimumSectionSize(80)

    # Stretch mode keeps columns evenly distributed; no need to auto-size each time.

    def _render_map(self, df: Optional[pd.DataFrame]):
        if self.map_container is None or self.map_placeholder is None:
            return

        if self.web_view is None:
            self.map_placeholder.setText("当前环境缺少 Qt WebEngine 支持，无法显示地图。")
            self.map_container.setCurrentWidget(self.map_placeholder)
            return

        if df is None or df.empty or '省份' not in df:
            self.map_placeholder.setText("暂无可用数据绘制地图。")
            self.map_container.setCurrentWidget(self.map_placeholder)
            return

        province_counts = (
            df['省份']
            .astype(str)
            .str.strip()
            .replace(['', 'nan', 'None', 'NaN'], pd.NA)
            .dropna()
            .map(self._normalize_province_name)
            .value_counts()
        )

        if province_counts.empty:
            self.map_placeholder.setText("数据集中未找到省份信息，无法绘制地图。")
            self.map_container.setCurrentWidget(self.map_placeholder)
            return

        data_pairs = [
            (province, int(count))
            for province, count in province_counts.items()
            if count is not None
        ]

        html = build_china_map_html(
            data_pairs=data_pairs,
            title="岩石样本省份分布",
            subtitle="数值表示样本数量",
            tooltip_formatter="{b}：{c}",
            value_unit=" 条样本",
            color_range=["#e0f2fe", "#0ea5e9"],
            zoom=1.08,
            center=(104.0, 35.6),
            enable_bridge=False,
        )

        self.web_view.setHtml(html)
        self.map_container.setCurrentWidget(self.web_view)

    def _clear_tables(self):
        if self.province_table is not None:
            self.province_table.setRowCount(0)
        if self.sample_table is not None:
            self.sample_table.setRowCount(0)


class ViolinChartCanvas(FigureCanvas):
    """用于展示按岩性统计的小提琴图画布"""

    GROUP_CONFIG: List[Tuple[str, List[str]]] = [
        ("模量参数 (GPa)", ["体积模量", "剪切模量", "弹性模量"]),
        ("强度参数 (MPa)", ["内聚力", "抗拉强度", "抗剪强度"]),
    ]

    PARAM_COLORS: Dict[str, str] = {
        "体积模量": "#be123c",
        "剪切模量": "#f97316",
        "弹性模量": "#2563eb",
        "内聚力": "#a16207",
        "抗拉强度": "#16a34a",
        "抗剪强度": "#0891b2",
        "抗压强度": "#7c3aed",
        "内摩擦角": "#fb7185",
        "密度": "#0284c7",
        "泊松比": "#0d9488",
    }

    AUTO_PALETTE: Tuple[str, ...] = (
        "#0ea5e9", "#6366f1", "#f97316", "#22c55e", "#8b5cf6",
        "#ec4899", "#14b8a6", "#facc15", "#ef4444",
    )

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 4), dpi=100)
        super().__init__(self.figure)
        self.setParent(parent)
        self._apply_theme()

    def _apply_theme(self):
        self.figure.set_facecolor("#f8fafc")
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#ffffff")
        self.figure.clear()

    def show_message(self, message: str):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis('off')
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=13, color="#94a3b8")
        self.figure.tight_layout()
        self.draw()

    def render_violin(self, data_series: List[Tuple[str, pd.Series]], stats_map: Dict[str, Dict[str, float]]):
        if not data_series:
            self.show_message("当前筛选条件下没有可用数据")
            return

        series_map: Dict[str, pd.Series] = {}
        for name, series in data_series:
            cleaned = series.dropna()
            if cleaned.empty:
                continue
            series_map[name] = cleaned

        if not series_map:
            self.show_message("当前岩性缺少有效的参数数值")
            return

        groups: List[Tuple[str, List[Tuple[str, pd.Series]]]] = []
        consumed: Set[str] = set()

        for title, members in self.GROUP_CONFIG:
            subset = [(name, series_map[name]) for name in members if name in series_map]
            if subset:
                groups.append((title, subset))
                consumed.update(name for name, _ in subset)

        for name, series in series_map.items():
            if name in consumed:
                continue
            groups.append((name, [(name, series)]))

        if not groups:
            self.show_message("当前岩性缺少有效的参数数值")
            return

        self.figure.clear()
        axes: List[Axes] = []
        total = len(groups)
        for idx in range(total):
            if total == 1:
                axes.append(self.figure.add_subplot(111))
            else:
                axes.append(self.figure.add_subplot(total, 1, idx + 1))

        for idx, (ax, (title, subset)) in enumerate(zip(axes, groups)):
            show_legend = idx == 0
            self._render_group(ax, subset, stats_map, show_legend=show_legend)
            ax.set_title(title, fontsize=14, fontweight='bold', color="#0f172a", pad=10)
            if idx < total - 1:
                ax.set_xlabel("")
                ax.tick_params(axis='x', labelbottom=False)
            else:
                ax.set_xlabel("参数取值", fontsize=12, color="#334155")
                ax.tick_params(axis='x', colors="#475569", labelsize=10)

        self.figure.tight_layout()
        self.draw()

    def _render_group(
        self,
        ax: Axes,
        subset: List[Tuple[str, pd.Series]],
        stats_map: Dict[str, Dict[str, float]],
        *,
        show_legend: bool,
    ) -> None:
        cleaned_series = [(name, series) for name, series in subset if not series.empty]
        if not cleaned_series:
            ax.clear()
            ax.axis('off')
            ax.text(0.5, 0.5, "缺少有效数据", ha='center', va='center', fontsize=12, color="#94a3b8")
            return

        # 统一水平方向范围，增加观感一致性
        all_values: List[float] = []
        for name, series in cleaned_series:
            all_values.extend(series.tolist())
            stats = stats_map.get(name, {})
            for key in ("max", "min", "mean", "median"):
                value = stats.get(key)
                if value is not None and not pd.isna(value):
                    all_values.append(float(value))

        if all_values:
            finite_values = [v for v in all_values if np.isfinite(v)]
        else:
            finite_values = []

        if finite_values:
            lower = min(finite_values)
            upper = max(finite_values)
            span = upper - lower
            if span <= 0:
                span = abs(upper) if upper != 0 else 1.0
            padding = span * 0.12
            ax.set_xlim(lower - padding, upper + padding)

        max_samples = max(len(series) for _, series in cleaned_series)
        if max_samples <= 3:
            self._render_strip_plot(ax, cleaned_series, stats_map, show_legend=show_legend)
        else:
            self._render_violin_plot(ax, cleaned_series, stats_map, show_legend=show_legend)

    def _render_violin_plot(
        self,
        ax: Axes,
        cleaned_series: List[Tuple[str, pd.Series]],
        stats_map: Dict[str, Dict[str, float]],
        *,
        show_legend: bool,
    ) -> None:
        stat_styles = [
            ("最大值", "max", "o", "#ef4444"),
            ("最小值", "min", "s", "#0ea5e9"),
            ("平均值", "mean", "D", "#22c55e"),
            ("中位数", "median", "^", "#f97316"),
        ]

        ax.set_facecolor("#ffffff")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color("#cbd5f5")
        ax.spines['bottom'].set_color("#cbd5f5")
        ax.grid(axis='x', linestyle='--', linewidth=0.6, alpha=0.3)
        ax.grid(axis='y', linestyle=':', linewidth=0.4, alpha=0.2)

        values = [series.values for _, series in cleaned_series]
        positions = np.arange(1, len(cleaned_series) + 1)
        parts = ax.violinplot(
            values,
            positions=positions,
            showmeans=False,
            showmedians=False,
            showextrema=False,
            vert=False,
        )

        for idx, body in enumerate(parts['bodies']):
            name = cleaned_series[idx][0]
            color = self._parameter_color(name, idx)
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.8)
            ax.axhspan(positions[idx] - 0.42, positions[idx] + 0.42, color=self._shade_color(color, 0.08), zorder=0)

        labels = [name for name, _ in cleaned_series]
        ax.set_yticks(positions)
        ax.set_yticklabels(labels, fontsize=11, color="#1f2937")
        ax.set_ylim(0.5, len(cleaned_series) + 0.5)
        ax.set_ylabel("参数项", fontsize=12, color="#334155")
        ax.tick_params(axis='y', colors="#1f2937")
        ax.tick_params(axis='x', colors="#475569")
        self._colorize_ticklabels(ax)

        for stat_label, stat_key, marker, color in stat_styles:
            xs, ys = [], []
            for pos, (name, _) in enumerate(cleaned_series, start=1):
                stat_values = stats_map.get(name, {})
                value = stat_values.get(stat_key)
                if value is None or pd.isna(value):
                    continue
                xs.append(value)
                ys.append(pos)
            if xs:
                ax.scatter(
                    xs,
                    ys,
                    marker=marker,
                    color=color,
                    s=60,
                    label=stat_label,
                    edgecolors="#ffffff",
                    linewidths=0.6,
                    zorder=3,
                )

        if show_legend and ax.get_legend_handles_labels()[0]:
            ax.legend(loc='lower right', frameon=False, fontsize=10)

        # 标注中位数/平均值，靠右对齐
        x_min, x_max = ax.get_xlim()
        anchor_x = x_max - (x_max - x_min) * 0.02
        for pos, (name, _) in enumerate(cleaned_series, start=1):
            stats = stats_map.get(name, {})
            median = stats.get("median")
            mean = stats.get("mean")
            if median is None or pd.isna(median):
                continue
            text = f"中位数 {median:.2f}"
            if mean is not None and not pd.isna(mean):
                text += f"\n平均值 {mean:.2f}"
            ax.text(
                anchor_x,
                pos,
                text,
                ha='right',
                va='center',
                fontsize=10,
                color="#1f2937",
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor=self._shade_color(self._parameter_color(name, pos), 0.2), linewidth=0.6, alpha=0.9),
                zorder=5,
            )

    def _render_strip_plot(
        self,
        ax: Axes,
        cleaned_series: List[Tuple[str, pd.Series]],
        stats_map: Dict[str, Dict[str, float]],
        *,
        show_legend: bool,
    ) -> None:
        stat_styles = [
            ("最大值", "max", "o", "#ef4444"),
            ("最小值", "min", "s", "#0ea5e9"),
            ("平均值", "mean", "D", "#22c55e"),
            ("中位数", "median", "^", "#f97316"),
        ]

        ax.set_facecolor("#ffffff")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color("#cbd5f5")
        ax.spines['bottom'].set_color("#cbd5f5")
        ax.grid(axis='x', linestyle='--', linewidth=0.6, alpha=0.3)
        ax.grid(axis='y', linestyle=':', linewidth=0.4, alpha=0.2)

        labels = []
        for idx, (name, series) in enumerate(cleaned_series, start=1):
            labels.append(name)
            values = series.values
            if len(values) == 1:
                offsets = np.array([0.0])
            else:
                offsets = np.linspace(-0.18, 0.18, len(values))
            ys = idx + offsets
            base_color = self._parameter_color(name, idx)
            ax.axhspan(idx - 0.42, idx + 0.42, color=self._shade_color(base_color, 0.08), zorder=0)
            ax.scatter(
                values,
                ys,
                color=base_color,
                alpha=0.85,
                s=70,
                edgecolors="#ffffff",
                linewidths=0.6,
                zorder=2,
            )
            text_x = float(np.nanmean(values)) if len(values) else 0.0
            ax.text(
                text_x,
                idx + 0.32,
                f"n={len(values)}",
                color="#64748b",
                fontsize=10,
                va='bottom',
                ha='center',
            )

        for stat_label, stat_key, marker, color in stat_styles:
            xs, ys = [], []
            for pos, (name, _) in enumerate(cleaned_series, start=1):
                stat_values = stats_map.get(name, {})
                value = stat_values.get(stat_key)
                if value is None or pd.isna(value):
                    continue
                xs.append(value)
                ys.append(pos)
            if xs:
                ax.scatter(
                    xs,
                    ys,
                    marker=marker,
                    color=color,
                    s=60,
                    label=stat_label,
                    edgecolors="#ffffff",
                    linewidths=0.6,
                    zorder=3,
                )

        if show_legend and ax.get_legend_handles_labels()[0]:
            ax.legend(loc='lower right', frameon=False, fontsize=10)

        ax.set_yticks(range(1, len(labels) + 1))
        ax.set_yticklabels(labels, fontsize=11, color="#1f2937")
        ax.set_ylim(0.5, len(labels) + 0.5)
        ax.set_ylabel("参数项", fontsize=12, color="#334155")
        ax.tick_params(axis='y', colors="#1f2937")
        ax.tick_params(axis='x', colors="#475569")
        self._colorize_ticklabels(ax)

    def _parameter_color(self, name: str, idx: int) -> str:
        base = self.PARAM_COLORS.get(name)
        if base:
            return base
        return self.AUTO_PALETTE[idx % len(self.AUTO_PALETTE)]

    def _shade_color(self, color: str, alpha: float) -> Tuple[float, float, float, float]:
        rgba = mcolors.to_rgba(color)
        return rgba[0], rgba[1], rgba[2], alpha

    def _colorize_ticklabels(self, ax: Axes) -> None:
        for tick in ax.get_yticklabels():
            name = tick.get_text()
            if not name:
                continue
            tick.set_color(self.PARAM_COLORS.get(name, "#1f2937"))


class RegionMapBridge(QObject):
    provinceClicked = pyqtSignal(str)

    @pyqtSlot(str)
    def onProvinceClicked(self, province: str):
        if province:
            self.provinceClicked.emit(province)


class RockParameterLookupPage(QWidget):
    """煤岩层力学参数取值查询模块"""

    PARAMETER_CONFIG = [
        ("密度", ["密度", "密度/g·cm-3", "密度(g/cm3)", "密度kg/m3", "密度（kg*m3）", "ρ"]),
        ("体积模量", ["体积模量", "体积模量/GPa", "体积模量(GPa)", "Bulk Modulus"]),
        ("剪切模量", ["剪切模量", "剪切模量/GPa", "Shear Modulus", "G"]),
        ("内聚力", ["内聚力", "内聚力/MPa", "粘聚力", "粘聚力/MPa", "Cohesion", "c"]),
        ("内摩擦角", ["内摩擦角", "内摩擦角/°", "摩擦角", "φ", "phi"]),
        ("抗拉强度", ["抗拉强度", "抗拉强度/MPa", "拉伸强度", "σt", "抗拉强度(MPa)"]),
        ("抗剪强度", ["抗剪强度", "抗剪强度/MPa", "剪切强度", "Shear Strength", "τf"]),
        ("抗压强度", ["抗压强度", "抗压强度/MPa", "抗压强度(MPa)", "σc"]),
        ("弹性模量", ["弹性模量", "弹性模量/GPa", "杨氏模量", "E"]),
        ("泊松比", ["泊松比", "ν", "nu", "poisson", "泊松比(ν)"]),
    ]

    STAT_ORDER = [
        ("最大值", "max"),
        ("最小值", "min"),
        ("平均值", "mean"),
        ("中位数", "median"),
    ]

    LITHOLOGY_COLUMNS = ["岩性", "岩层名称", "岩石名称", "岩石", "岩石类型", "岩性名称"]
    PROVINCE_COLUMNS = ["省份", "所在省份", "所属省份", "省", "省市", "省份名称", "所在省"]

    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self._dataset: Optional[pd.DataFrame] = None
        self._lithology_column: Optional[str] = None
        self._normalized_lithology_column: str = "__lookup_lithology__"
        self._province_column: Optional[str] = None
        self._normalized_province_column: str = "__lookup_province__"
        self._coal_region_groups: Dict[str, pd.DataFrame] = {}
        self._province_display_map: Dict[str, str] = {}
        self._display_to_province_map: Dict[str, str] = {}
        self._current_province: Optional[str] = None
        self._region_bridge: Optional[RegionMapBridge] = None
        self._region_channel: Optional[Any] = None
        self._dataset_sources: Dict[str, pd.DataFrame] = {}
        self._dataset_labels: Dict[str, str] = {}
        self._active_dataset_key: Optional[str] = None
        self._active_dataset_label: str = ""
        self._processed_dataset_cache: Dict[str, Dict[str, Any]] = {}
        self._stat_preference = getattr(self.main_win, 'stat_preference', 'median')

        self._init_ui()
        self.refresh_data()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("lookupScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        outer_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title_label = QLabel("煤岩层力学参数取值查询")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)

        subtitle = QLabel("参考数据库概览样式，展示按岩性汇总的参数分布与关键统计，支持小提琴图与表格双视角对比。")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #475569; font-size: 14px; line-height: 1.6;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        control_card = QFrame()
        control_card.setObjectName("lookupControlCard")
        control_card.setStyleSheet(
            "QFrame#lookupControlCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; }"
        )
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(18, 18, 18, 18)
        control_layout.setSpacing(12)

        mode_title = QLabel("查询窗口")
        mode_title.setStyleSheet("color: #0f172a; font-size: 15px; font-weight: 600;")
        control_layout.addWidget(mode_title)

        self.radio_region = QRadioButton("按地区")
        self.radio_region.setToolTip("仅统计数据库中含“煤”字岩性的省份")
        self.radio_lithology = QRadioButton("按岩性")
        self.radio_lithology.setChecked(True)

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_region, 0)
        self.mode_group.addButton(self.radio_lithology, 1)
        self.radio_region.toggled.connect(self._on_mode_changed)
        self.radio_lithology.toggled.connect(self._on_mode_changed)

        control_layout.addWidget(self.radio_region)
        control_layout.addWidget(self.radio_lithology)

        control_layout.addSpacing(10)

        dataset_label = QLabel("数据源：")
        dataset_label.setStyleSheet("color: #334155; font-size: 14px; font-weight: 600;")
        control_layout.addWidget(dataset_label)

        self.dataset_selector = QComboBox()
        self.dataset_selector.setEditable(False)
        self.dataset_selector.setMinimumWidth(180)
        self.dataset_selector.setStyleSheet(
            "QComboBox { padding: 6px 12px; border-radius: 10px; border: 1px solid #cbd5f5; }"
            "QComboBox:hover { border-color: #6366f1; }"
        )
        self.dataset_selector.currentIndexChanged.connect(self._on_dataset_changed)
        control_layout.addWidget(self.dataset_selector)

        control_layout.addSpacing(10)

        lithology_label = QLabel("岩性：")
        lithology_label.setStyleSheet("color: #334155; font-size: 14px; font-weight: 600;")
        control_layout.addWidget(lithology_label)

        self.lithology_combo = QComboBox()
        self.lithology_combo.setEditable(False)
        self.lithology_combo.setMinimumWidth(200)
        self.lithology_combo.setStyleSheet(
            "QComboBox { padding: 6px 12px; border-radius: 10px; border: 1px solid #cbd5f5; }"
            "QComboBox:hover { border-color: #6366f1; }"
        )
        self.lithology_combo.currentTextChanged.connect(self._on_lithology_changed)
        control_layout.addWidget(self.lithology_combo)

        control_layout.addSpacing(10)

        stat_label = QLabel("统计指标：")
        stat_label.setStyleSheet("color: #334155; font-size: 14px; font-weight: 600;")
        control_layout.addWidget(stat_label)

        self.stat_selector = QComboBox()
        self.stat_selector.setEditable(False)
        self.stat_selector.setMinimumWidth(120)
        self.stat_selector.setStyleSheet(
            "QComboBox { padding: 6px 12px; border-radius: 10px; border: 1px solid #cbd5f5; }"
            "QComboBox:hover { border-color: #6366f1; }"
        )
        self.stat_selector.addItems(["中位数", "平均值"])
        initial_label = "平均值" if self._stat_preference == "mean" else "中位数"
        self.stat_selector.setCurrentText(initial_label)
        self.stat_selector.currentTextChanged.connect(self._on_stat_preference_changed)
        control_layout.addWidget(self.stat_selector)

        control_layout.addStretch(1)

        self.sample_hint_label = QLabel("请选择岩性以查看参数分布。")
        self.sample_hint_label.setStyleSheet("color: #64748b; font-size: 13px;")
        control_layout.addWidget(self.sample_hint_label)

        layout.addWidget(control_card)

        self.mode_stack = QStackedWidget()
        layout.addWidget(self.mode_stack)
        layout.setStretch(layout.count() - 1, 1)

        region_frame = QFrame()
        region_frame.setObjectName("regionLookupFrame")
        region_layout = QVBoxLayout(region_frame)
        region_layout.setContentsMargins(0, 0, 0, 0)
        region_layout.setSpacing(16)

        self.region_status_label = QLabel("煤层省份：未选择")
        self.region_status_label.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        region_layout.addWidget(self.region_status_label)

        self.region_hint_label = QLabel("默认仅统计岩性中包含“煤”字的样本，请点击地图上的省份以查看详细分布。")
        self.region_hint_label.setWordWrap(True)
        self.region_hint_label.setStyleSheet("color: #64748b; font-size: 13px;")
        region_layout.addWidget(self.region_hint_label)

        region_splitter = QSplitter(Qt.Orientation.Horizontal)
        region_splitter.setChildrenCollapsible(False)
        region_splitter.setHandleWidth(12)
        region_splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; margin: 4px 0; border-radius: 4px; }")
        region_layout.addWidget(region_splitter, 1)

        map_card = QFrame()
        map_card.setObjectName("regionMapCard")
        map_card.setMinimumWidth(420)
        map_card.setStyleSheet("QFrame#regionMapCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; }")
        map_layout = QVBoxLayout(map_card)
        map_layout.setContentsMargins(22, 20, 22, 22)
        map_layout.setSpacing(12)

        map_title = QLabel("省份分布图（煤类岩性）")
        map_title.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        map_layout.addWidget(map_title)

        if QWebEngineView is not None:
            self.region_map_view = QWebEngineView()
            self.region_map_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            self.region_map_view.setMinimumHeight(480)
            map_layout.addWidget(self.region_map_view, 1)
            self.region_map_placeholder = None
        else:
            self.region_map_view = None
            self.region_map_placeholder = QLabel("缺少 Qt WebEngine 依赖，无法渲染交互式地图。")
            self.region_map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.region_map_placeholder.setStyleSheet("color: #94a3b8; font-size: 14px; border: 1px dashed #cbd5f5; border-radius: 12px;")
            self.region_map_placeholder.setMinimumHeight(360)
            map_layout.addWidget(self.region_map_placeholder, 1)

        region_splitter.addWidget(map_card)

        region_preview_card = QFrame()
        region_preview_card.setObjectName("regionPreviewCard")
        region_preview_card.setStyleSheet("QFrame#regionPreviewCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; }")
        region_preview_layout = QVBoxLayout(region_preview_card)
        region_preview_layout.setContentsMargins(22, 22, 22, 22)
        region_preview_layout.setSpacing(14)

        preview_title = QLabel("参数分布预览")
        preview_title.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        region_preview_layout.addWidget(preview_title)

        self.region_sample_hint = QLabel("请选择省份查看煤层样本。")
        self.region_sample_hint.setStyleSheet("color: #64748b; font-size: 13px;")
        region_preview_layout.addWidget(self.region_sample_hint)

        self.region_violin_canvas = ViolinChartCanvas()
        self.region_violin_canvas.setMinimumHeight(360)
        region_preview_layout.addWidget(self.region_violin_canvas, 1)

        region_table_card = QFrame()
        region_table_card.setObjectName("regionTableCard")
        region_table_card.setStyleSheet("QFrame#regionTableCard { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; }")
        region_table_layout = QVBoxLayout(region_table_card)
        region_table_layout.setContentsMargins(18, 16, 18, 18)
        region_table_layout.setSpacing(10)

        region_table_title = QLabel("统计指标（煤类样本）")
        region_table_title.setStyleSheet("color: #1f2937; font-size: 15px; font-weight: 600;")
        region_table_layout.addWidget(region_table_title)

        self.region_stats_table = QTableWidget(len(self.STAT_ORDER), len(self.PARAMETER_CONFIG))
        self.region_stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.region_stats_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.region_stats_table.verticalHeader().setVisible(True)
        self.region_stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.region_stats_table.setAlternatingRowColors(True)
        self.region_stats_table.setStyleSheet("QTableWidget { border: none; }")
        self.region_stats_table.setHorizontalHeaderLabels([name for name, _ in self.PARAMETER_CONFIG])
        self.region_stats_table.setVerticalHeaderLabels([label for label, _ in self.STAT_ORDER])
        region_table_layout.addWidget(self.region_stats_table)

        region_preview_layout.addWidget(region_table_card)

        region_splitter.addWidget(region_preview_card)
        region_splitter.setStretchFactor(0, 3)
        region_splitter.setStretchFactor(1, 4)
        region_splitter.setSizes([500, 620])

        self._clear_stats_table(table_widget=self.region_stats_table)

        self.mode_stack.addWidget(region_frame)

        lithology_frame = QFrame()
        lithology_layout = QVBoxLayout(lithology_frame)
        lithology_layout.setContentsMargins(0, 0, 0, 0)
        lithology_layout.setSpacing(16)

        self.preview_status = QLabel("未选择岩性")
        self.preview_status.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        lithology_layout.addWidget(self.preview_status)

        preview_splitter = QSplitter(Qt.Orientation.Vertical)
        preview_splitter.setChildrenCollapsible(False)
        preview_splitter.setHandleWidth(12)
        preview_splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; margin: 4px 0; border-radius: 4px; }")
        lithology_layout.addWidget(preview_splitter, 1)

        violin_card = QFrame()
        violin_card.setObjectName("violinCard")
        violin_card.setStyleSheet(
            "QFrame#violinCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; }"
        )
        violin_card.setMinimumHeight(460)
        violin_layout = QVBoxLayout(violin_card)
        violin_layout.setContentsMargins(22, 22, 22, 22)
        violin_layout.setSpacing(14)

        violin_title = QLabel("小提琴图预览")
        violin_title.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        violin_layout.addWidget(violin_title)

        self.violin_canvas = ViolinChartCanvas()
        self.violin_canvas.setMinimumHeight(400)
        violin_layout.addWidget(self.violin_canvas, 1)

        preview_splitter.addWidget(violin_card)

        table_card = QFrame()
        table_card.setObjectName("violinTableCard")
        table_card.setStyleSheet(
            "QFrame#violinTableCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; }"
        )
        table_card.setMinimumHeight(300)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(22, 20, 22, 22)
        table_layout.setSpacing(12)

        table_title = QLabel("统计指标")
        table_title.setStyleSheet("color: #1f2937; font-size: 16px; font-weight: 600;")
        table_layout.addWidget(table_title)

        self.stats_table = QTableWidget(len(self.STAT_ORDER), len(self.PARAMETER_CONFIG))
        self.stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stats_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.stats_table.verticalHeader().setVisible(True)
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("QTableWidget { border: 1px solid #e2e8f0; border-radius: 12px; }")

        self.stats_table.setHorizontalHeaderLabels([name for name, _ in self.PARAMETER_CONFIG])
        self.stats_table.setVerticalHeaderLabels([label for label, _ in self.STAT_ORDER])
        table_layout.addWidget(self.stats_table, 1)

        self._clear_stats_table()

        preview_splitter.addWidget(table_card)
        preview_splitter.setStretchFactor(0, 3)
        preview_splitter.setStretchFactor(1, 2)
        preview_splitter.setSizes([520, 320])

        self.mode_stack.addWidget(lithology_frame)
        self.mode_stack.setCurrentIndex(1)

    def refresh_data(self, retain_selection: bool = False, requested_dataset: Optional[str] = None):
        previous_lithology = self.lithology_combo.currentText() if retain_selection else ""
        previous_province = self._current_province if retain_selection else None
        previous_dataset = None
        if retain_selection:
            if requested_dataset is not None:
                previous_dataset = requested_dataset
            else:
                if self.dataset_selector is not None and self.dataset_selector.currentIndex() != -1:
                    previous_dataset = self.dataset_selector.currentData()

        dataset_candidates: List[Tuple[str, str, pd.DataFrame]] = []
        aggregated_df = getattr(self.main_win, 'rock_db', None)
        if aggregated_df is not None and not aggregated_df.empty:
            dataset_candidates.append(("aggregated", "汇总数据库", aggregated_df))
        raw_df = getattr(self.main_win, 'rock_db_raw', None)
        if raw_df is not None and not raw_df.empty:
            dataset_candidates.append(("raw", "原始样本", raw_df))
        custom_df = getattr(self.main_win, 'custom_rock_db', None)
        if custom_df is not None and not custom_df.empty:
            dataset_candidates.append(("custom", "自建库", custom_df))

        self._dataset_sources = {key: df for key, _, df in dataset_candidates}
        self._dataset_labels = {key: label for key, label, _ in dataset_candidates}
        self._processed_dataset_cache = {
            key: cache
            for key, cache in self._processed_dataset_cache.items()
            if key in self._dataset_sources
        }

        if self.dataset_selector is not None:
            self.dataset_selector.blockSignals(True)
            self.dataset_selector.clear()
            for key, label, _ in dataset_candidates:
                self.dataset_selector.addItem(label, key)
            self.dataset_selector.setEnabled(bool(dataset_candidates))
            self.dataset_selector.blockSignals(False)

        chosen_key: Optional[str] = None
        candidate_order: List[str] = []
        if retain_selection and previous_dataset:
            candidate_order.append(previous_dataset)
        candidate_order.extend([key for key, _, _ in dataset_candidates])
        for key in candidate_order:
            if key in self._dataset_sources:
                chosen_key = key
                break

        if chosen_key is None:
            if self.dataset_selector is not None:
                self.dataset_selector.blockSignals(True)
                self.dataset_selector.clear()
                self.dataset_selector.setEnabled(False)
                self.dataset_selector.blockSignals(False)

            self._dataset = None
            self._active_dataset_key = None
            self._active_dataset_label = ""
            self._lithology_column = None
            self._province_column = None
            self._coal_region_groups = {}
            self._province_display_map = {}

            self.lithology_combo.blockSignals(True)
            self.lithology_combo.clear()
            self.lithology_combo.setEnabled(False)
            self.lithology_combo.blockSignals(False)

            self.sample_hint_label.setText("尚未加载任何数据源，请先导入岩石数据库或自建库。")
            self.preview_status.setText("暂无数据可展示")
            self.violin_canvas.show_message("未加载到可用的岩石数据库")
            self._clear_stats_table()

            self._reset_region_preview(
                status="煤层省份：暂无数据",
                hint="尚未加载任何数据源，暂无法展示按地区信息。",
                message="未加载到含煤岩性数据"
            )
            self._render_region_map()
            return

        if self.dataset_selector is not None:
            index = self.dataset_selector.findData(chosen_key)
            if index != -1:
                self.dataset_selector.blockSignals(True)
                self.dataset_selector.setCurrentIndex(index)
                self.dataset_selector.blockSignals(False)

        self._active_dataset_key = chosen_key
        self._active_dataset_label = self._dataset_labels.get(chosen_key, "")
        source_df = self._dataset_sources.get(chosen_key)
        if source_df is None or source_df.empty:
            self._dataset = None
        else:
            self._dataset = self._get_processed_dataset(chosen_key, source_df)

        self._lithology_column = None
        self._province_column = None
        self._coal_region_groups = {}
        self._province_display_map = {}

        self.lithology_combo.blockSignals(True)
        self.lithology_combo.clear()

        if self._dataset is None or self._dataset.empty:
            self.lithology_combo.setEnabled(False)
            dataset_tip = self._active_dataset_label or "当前数据源"
            self.sample_hint_label.setText(f"{dataset_tip} 暂无有效记录，请检查数据内容。")
            self.preview_status.setText("暂无数据可展示")
            self.violin_canvas.show_message("未加载到可用的岩石数据库")
            self._clear_stats_table()

            self._reset_region_preview(
                status="煤层省份：暂无数据",
                hint="当前数据源缺少有效记录，暂无法展示按地区信息。",
                message="未加载到含煤岩性数据"
            )
            self._render_region_map()
            self.lithology_combo.blockSignals(False)
            return

        for candidate in self.LITHOLOGY_COLUMNS:
            if candidate in self._dataset.columns:
                self._lithology_column = candidate
                break

        for candidate in self.PROVINCE_COLUMNS:
            if candidate in self._dataset.columns:
                self._province_column = candidate
                break

        if self._lithology_column is None:
            self.lithology_combo.setEnabled(False)
            self.sample_hint_label.setText("数据集中缺少岩性字段，无法执行查询。")
            self.preview_status.setText("缺少岩性字段")
            self.violin_canvas.show_message("数据集中缺少岩性或岩层名称字段")
            self._clear_stats_table()

            self._reset_region_preview(
                status="煤层省份：缺少岩性字段",
                hint="由于缺少岩性字段，无法筛选含煤样本的省份。",
                message="请检查数据集中是否包含“岩性”或相关字段"
            )
            self._render_region_map()
            self.lithology_combo.blockSignals(False)
            return

        cleaned_lithology = (
            self._dataset[self._lithology_column]
            .astype(str)
            .str.strip()
            .replace(['', 'nan', 'None', 'NaN'], pd.NA)
        )
        normalized_series = cleaned_lithology.dropna().map(self._normalize_lithology_label)
        self._dataset[self._normalized_lithology_column] = cleaned_lithology.where(
            cleaned_lithology.isna(), normalized_series
        )

        lithologies = sorted(normalized_series.dropna().unique().tolist())
        for item in lithologies:
            self.lithology_combo.addItem(item)

        target_lithology = None
        if lithologies:
            if retain_selection and previous_lithology in lithologies:
                target_lithology = previous_lithology
            else:
                target_lithology = lithologies[0]
            self.lithology_combo.setCurrentIndex(lithologies.index(target_lithology))
            self.lithology_combo.setEnabled(True)
        else:
            self.lithology_combo.setEnabled(False)

        self.lithology_combo.blockSignals(False)

        if self._dataset is not None and not self._dataset.empty:
            self._refresh_sample_hint()

        if target_lithology:
            self._on_lithology_changed(target_lithology, force=True)
        else:
            self.sample_hint_label.setText("未检索到可用的岩性条目。")
            self.preview_status.setText("暂无岩性")
            self.violin_canvas.show_message("暂无有效岩性可供展示")
            self._clear_stats_table()

        self._prepare_region_data()
        self._render_region_map()

        if self._coal_region_groups:
            if retain_selection and previous_province and previous_province in self._coal_region_groups:
                target_province = previous_province
            else:
                target_province = max(self._coal_region_groups.items(), key=lambda item: len(item[1]))[0]
            self._update_region_preview(target_province)
        else:
            if self._province_column is None:
                status = "煤层省份：缺少省份字段"
                hint = "数据集中未找到省份相关字段，无法进行地区筛选。"
                message = "请为岩石数据库补充“省份”或类似字段"
            else:
                status = "煤层省份：暂无煤层数据"
                hint = "已加载数据，但未检索到岩性名称中包含“煤”的样本。"
                message = "暂未找到含煤岩性数据，可检查数据库是否完整"
            self._reset_region_preview(status=status, hint=hint, message=message)

    def _on_mode_changed(self):
        if self.radio_lithology.isChecked():
            self.mode_stack.setCurrentIndex(1)
            self.lithology_combo.setEnabled(self.lithology_combo.count() > 0)
            if self.lithology_combo.count() > 0:
                current = self.lithology_combo.currentText()
                if current:
                    self._on_lithology_changed(current, force=True)
            elif not self.lithology_combo.isEnabled():
                self.sample_hint_label.setText("未检索到可用的岩性条目。")
        else:
            self.mode_stack.setCurrentIndex(0)
            self.lithology_combo.setEnabled(False)
            self.sample_hint_label.setText("仅统计含“煤”的岩性，可在左侧地图选择省份。")
            if self._current_province and self._current_province in self._coal_region_groups:
                self._update_region_preview(self._current_province)

    def _on_dataset_changed(self, index: int):
        if index < 0 or self.dataset_selector is None:
            return
        dataset_key = self.dataset_selector.itemData(index)
        if not dataset_key or dataset_key == self._active_dataset_key:
            return
        self.refresh_data(retain_selection=True, requested_dataset=dataset_key)

    def _on_stat_preference_changed(self, text: str):
        preference = 'mean' if '均' in text else 'median'
        if preference == self._stat_preference:
            return
        self._stat_preference = preference
        if hasattr(self.main_win, 'stat_preference'):
            self.main_win.stat_preference = preference
        else:
            setattr(self.main_win, 'stat_preference', preference)
        self._highlight_stat_preference()
        # 更新提示文本以反映新的统计偏好
        self._refresh_sample_hint()

    def _get_processed_dataset(self, key: str, source_df: pd.DataFrame) -> pd.DataFrame:
        cache_entry = self._processed_dataset_cache.get(key)
        signature = (id(source_df), tuple(source_df.columns), source_df.shape)
        if cache_entry and cache_entry.get("signature") == signature:
            dataset = cache_entry.get("data")
            if dataset is not None:
                return dataset

        processed = source_df.copy()
        self._processed_dataset_cache[key] = {
            "signature": signature,
            "data": processed,
        }
        return processed
    def _highlight_stat_preference(self, table_widget: Optional[QTableWidget] = None):
        target_label = '平均值' if self._stat_preference == 'mean' else '中位数'
        highlight_color = QColor('#1d4ed8')
        default_color = QColor('#334155')
        tables = [table_widget] if table_widget else [self.stats_table, self.region_stats_table]
        for table in tables:
            if table is None:
                continue
            for row_index, (label, _) in enumerate(self.STAT_ORDER):
                for col in range(table.columnCount()):
                    item = table.item(row_index, col)
                    if item is None:
                        continue
                    font = item.font()
                    if label == target_label:
                        font.setBold(True)
                        item.setFont(font)
                        item.setForeground(highlight_color)
                    else:
                        font.setBold(False)
                        item.setFont(font)
                        item.setForeground(default_color)

    def _refresh_sample_hint(self):
        if self._dataset is None or self._dataset.empty:
            return
        dataset_label = self._active_dataset_label or "当前数据源"
        if self._active_dataset_key == "custom" and getattr(self.main_win, 'custom_rock_db_path', None):
            short_path = os.path.basename(getattr(self.main_win, 'custom_rock_db_path'))
            dataset_label = f"自建库 · {short_path}"
        stat_label = '平均值' if self._stat_preference == 'mean' else '中位数'
        self.sample_hint_label.setText(
            f"数据源：{dataset_label} · 共 {len(self._dataset)} 条记录（优先使用{stat_label}）。请选择岩性以查看参数分布。"
        )

    def _on_lithology_changed(self, lithology: str, force: bool = False):
        if not force and not self.radio_lithology.isChecked():
            return
        lithology = lithology.strip()
        if not lithology:
            self.preview_status.setText("请选择岩性")
            self.violin_canvas.show_message("请选择岩性以查看参数分布")
            self._clear_stats_table()
            return

        if self._dataset is None or self._dataset.empty or self._lithology_column is None:
            self.preview_status.setText("暂无数据")
            self.violin_canvas.show_message("未加载到可用的数据集")
            self._clear_stats_table()
            return

        if self._normalized_lithology_column in self._dataset.columns:
            filtered = self._dataset[
                self._dataset[self._normalized_lithology_column] == lithology
            ]
        else:
            filtered = self._dataset[
                self._dataset[self._lithology_column].astype(str).str.strip() == lithology
            ]

        sample_count = len(filtered)
        if sample_count == 0:
            self.preview_status.setText(f"岩性：{lithology} · 暂无数据")
            self.violin_canvas.show_message("该岩性暂无可用数据")
            self._clear_stats_table()
            return

        self.preview_status.setText(f"岩性：{lithology} · 样本数 {sample_count}")
        if self.radio_lithology.isChecked():
            stat_label = '平均值' if self._stat_preference == 'mean' else '中位数'
            self.sample_hint_label.setText(
                f"当前共收录 {sample_count} 条 {lithology} 样本记录（优先使用{stat_label}）。"
            )

        data_series, stats_map = self._extract_parameter_series(filtered)

        if not data_series:
            self.violin_canvas.show_message("该岩性缺少可用的力学参数数值")
        else:
            self.violin_canvas.render_violin(data_series, stats_map)

        self._populate_stats_table(stats_map)

    def _resolve_column(self, df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        for column in candidates:
            if column in df.columns:
                return column
            normalized = column.replace('（', '(').replace('）', ')').replace('·', '·')
            for df_col in df.columns:
                if df_col.replace('（', '(').replace('）', ')').strip().lower() == normalized.strip().lower():
                    return df_col
        return None

    def _extract_parameter_series(self, df: pd.DataFrame) -> Tuple[List[Tuple[str, pd.Series]], Dict[str, Dict[str, float]]]:
        data_series: List[Tuple[str, pd.Series]] = []
        stats_map: Dict[str, Dict[str, float]] = {}
        for display_name, candidates in self.PARAMETER_CONFIG:
            column_name = self._resolve_column(df, candidates)
            if column_name is None or column_name not in df.columns:
                continue
            series = pd.to_numeric(df[column_name], errors='coerce').dropna()
            if series.empty:
                continue
            data_series.append((display_name, series))
            stats_map[display_name] = {
                "max": series.max(),
                "min": series.min(),
                "mean": series.mean(),
                "median": series.median(),
            }
        return data_series, stats_map

    def _populate_stats_table(self, stats_map: Dict[str, Dict[str, float]], table_widget: Optional[QTableWidget] = None):
        table = table_widget or self.stats_table
        if table is None:
            return
        for col_index, (display_name, _) in enumerate(self.PARAMETER_CONFIG):
            stats = stats_map.get(display_name)
            for row_index, (label, key) in enumerate(self.STAT_ORDER):
                value = stats.get(key) if stats else None
                text = self._format_value(value)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_index, col_index, item)
        self._highlight_stat_preference(table)

    def _clear_stats_table(self, table_widget: Optional[QTableWidget] = None):
        table = table_widget or self.stats_table
        if table is None:
            return
        for col_index in range(len(self.PARAMETER_CONFIG)):
            for row_index in range(len(self.STAT_ORDER)):
                item = QTableWidgetItem("--")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_index, col_index, item)
        self._highlight_stat_preference(table)

    @staticmethod
    def _format_value(value: Optional[float]) -> str:
        if value is None or pd.isna(value):
            return "--"
        if isinstance(value, (int, float)):
            if abs(value) >= 1000:
                return f"{value:,.0f}"
            return f"{value:.2f}".rstrip('0').rstrip('.')
        return str(value)

    @staticmethod
    def _normalize_lithology_label(label: str) -> str:
        normalized = label.strip()
        if not normalized:
            return normalized
        if '煤' in normalized:
            return '煤类'
        if '土' in normalized:
            return '土类'
        return normalized

    def _prepare_region_data(self):
        self._coal_region_groups = {}
        self._province_display_map = {}
        self._display_to_province_map = {}
        self._current_province = None
        self._region_bridge = None
        self._region_channel = None

        if self._dataset is None or self._province_column is None:
            return

        province_series = (
            self._dataset[self._province_column]
            .astype(str)
            .str.strip()
            .replace(['', 'nan', 'None', 'NaN'], pd.NA)
            .dropna()
        )

        if province_series.empty:
            return

        normalized_provinces = province_series.map(self._normalize_province_name_from_lookup)
        self._dataset[self._normalized_province_column] = normalized_provinces

        coal_mask = self._dataset[self._normalized_lithology_column].fillna('').str.contains('煤')
        coal_df = self._dataset[coal_mask]

        if coal_df.empty:
            return

        grouped = coal_df.groupby(self._normalized_province_column)
        for province, group in grouped:
            if not province or group.empty:
                continue
            self._coal_region_groups[province] = group
            display = self._province_display_name(province)
            self._province_display_map[province] = display
            self._display_to_province_map[display] = province

    def _normalize_province_name_from_lookup(self, name: str) -> str:
        if name is None:
            return ''
        normalized = str(name).strip()
        if not normalized:
            return ''
        lower = normalized.lower()
        if lower in {'nan', 'none', 'null', '未标注', '无', 'n/a', 'na'}:
            return ''

        alias_map = {
            '北京': '北京市', '北京市': '北京市',
            '天津': '天津市', '天津市': '天津市',
            '上海': '上海市', '上海市': '上海市',
            '重庆': '重庆市', '重庆市': '重庆市',
            '河北': '河北省', '河北省': '河北省',
            '山西': '山西省', '山西省': '山西省',
            '辽宁': '辽宁省', '辽宁省': '辽宁省',
            '吉林': '吉林省', '吉林省': '吉林省',
            '黑龙江': '黑龙江省', '黑龙江省': '黑龙江省',
            '江苏': '江苏省', '江苏省': '江苏省',
            '浙江': '浙江省', '浙江省': '浙江省',
            '安徽': '安徽省', '安徽省': '安徽省',
            '福建': '福建省', '福建省': '福建省',
            '江西': '江西省', '江西省': '江西省',
            '山东': '山东省', '山东省': '山东省',
            '河南': '河南省', '河南省': '河南省',
            '湖北': '湖北省', '湖北省': '湖北省',
            '湖南': '湖南省', '湖南省': '湖南省',
            '广东': '广东省', '广东省': '广东省',
            '海南': '海南省', '海南省': '海南省',
            '四川': '四川省', '四川省': '四川省',
            '贵州': '贵州省', '贵州省': '贵州省',
            '云南': '云南省', '云南省': '云南省',
            '陕西': '陕西省', '陕西省': '陕西省',
            '甘肃': '甘肃省', '甘肃省': '甘肃省',
            '青海': '青海省', '青海省': '青海省',
            '台湾': '台湾省', '台湾省': '台湾省',
            '内蒙古': '内蒙古自治区', '内蒙古自治区': '内蒙古自治区',
            '广西': '广西壮族自治区', '广西壮族自治区': '广西壮族自治区',
            '宁夏': '宁夏回族自治区', '宁夏回族自治区': '宁夏回族自治区',
            '新疆': '新疆维吾尔自治区', '新疆维吾尔自治区': '新疆维吾尔自治区',
            '西藏': '西藏自治区', '西藏自治区': '西藏自治区',
            '香港': '香港特别行政区', '香港特别行政区': '香港特别行政区',
            '澳门': '澳门特别行政区', '澳门特别行政区': '澳门特别行政区',
        }

        if normalized in alias_map:
            return alias_map[normalized]

        simplified = normalized
        for token in ['省', '市', '自治区', '特别行政区', '壮族', '回族', '维吾尔']:
            simplified = simplified.replace(token, '')
        if simplified in alias_map:
            return alias_map[simplified]

        return normalized

    @staticmethod
    def _province_display_name(province: str) -> str:
        display = str(province)
        for token in ['省', '市', '自治区', '特别行政区', '壮族', '回族', '维吾尔']:
            display = display.replace(token, '')
        return display

    def _render_region_map(self):
        if self.region_map_view is None:
            if self.region_map_placeholder is not None:
                self.region_map_placeholder.setText("当前环境缺少 Qt WebEngine 支持，无法显示地图。")
            return

        if not self._coal_region_groups:
            empty_html = """<html><body style='display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;font-size:14px;'>暂无含煤样本可用于绘制地图。</body></html>"""
            self.region_map_view.setHtml(empty_html)
            return

        province_counts: Dict[str, int] = {}
        for province, group in self._coal_region_groups.items():
            display = self._province_display_map.get(province, self._province_display_name(province))
            province_counts[display] = province_counts.get(display, 0) + len(group)

        data_pairs = [(name, count) for name, count in province_counts.items() if count]

        if not data_pairs:
            empty_html = """<html><body style='display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;font-size:14px;'>暂无含煤样本可用于绘制地图。</body></html>"""
            self.region_map_view.setHtml(empty_html)
            return

        html = build_china_map_html(
            data_pairs=data_pairs,
            title="煤层样本省份分布",
            subtitle="点击省份查看详细参数",
            tooltip_formatter="{b}：{c}",
            value_unit=" 条样本",
            color_range=["#f0f9ff", "#0f766e"],
            zoom=1.08,
            center=(104.0, 35.6),
            enable_bridge=True,
        )

        self.region_map_view.setHtml(html)

        if QWebChannel is not None:
            channel = QWebChannel(self.region_map_view.page())
            bridge = RegionMapBridge()
            bridge.provinceClicked.connect(self._on_province_clicked)
            channel.registerObject("bridge", bridge)
            self.region_map_view.page().setWebChannel(channel)
            self._region_channel = channel
            self._region_bridge = bridge
            self.region_map_view.page().runJavaScript("if (window.__chinaMapRefresh) { window.__chinaMapRefresh(); }")

    def _on_province_clicked(self, display_name: str):
        normalized = self._display_to_province_map.get(display_name)
        if not normalized:
            normalized = self._normalize_province_name_from_lookup(display_name)
        if normalized in self._coal_region_groups:
            self._update_region_preview(normalized)

    def _update_region_preview(self, province: str):
        group = self._coal_region_groups.get(province)
        if group is None or group.empty:
            return

        self._current_province = province
        display_name = self._province_display_map.get(province, self._province_display_name(province))
        sample_count = len(group)
        self.region_status_label.setText(f"煤层省份：{display_name} · 样本数 {sample_count}")
        self.region_sample_hint.setText(f"当前共有 {sample_count} 条含“煤”岩性样本来自 {display_name}。")

        data_series, stats_map = self._extract_parameter_series(group)
        if not data_series:
            self.region_violin_canvas.show_message("该省份缺少可用的煤层力学参数数值")
            self._clear_stats_table(self.region_stats_table)
            return

        self.region_violin_canvas.render_violin(data_series, stats_map)
        self._populate_stats_table(stats_map, self.region_stats_table)

    def _reset_region_preview(self, status: str, hint: str, message: str):
        self._current_province = None
        self.region_status_label.setText(status)
        self.region_sample_hint.setText(hint)
        self.region_violin_canvas.show_message(message)
        self._clear_stats_table(self.region_stats_table)


class DatabaseViewerTab(QWidget):
    """用于显示、编辑和刷新岩石属性数据库的UI界面"""
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.is_modified = False  # 追踪是否有修改
        self.numeric_columns = set()
        self.column_order = []
        self.init_ui()
        self.populate_table() # 初始加载

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- 顶部控制栏 ---
        control_bar_layout = QHBoxLayout()
        
        title = QLabel("岩石物理力学性质数据库 (可编辑)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        
        self.refresh_btn = ModernButton("刷新数据库", color="#1cc88a", icon_path="icons/refresh.png")
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        self.save_btn = ModernButton("保存修改", color="#3b82f6", icon_path="icons/save.png")
        self.save_btn.clicked.connect(self.save_database)
        self.save_btn.setEnabled(False)  # 初始状态禁用
        
        self.status_label = QLabel("数据库状态：")
        self.status_label.setStyleSheet("color: #6b7280; font-size: 13px;")

        control_bar_layout.addWidget(title)
        control_bar_layout.addStretch()
        control_bar_layout.addWidget(self.status_label)
        control_bar_layout.addWidget(self.save_btn)
        control_bar_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(control_bar_layout)

        # --- 操作按钮栏 ---
        button_bar_layout = QHBoxLayout()
        
        self.add_row_btn = ModernButton("添加新行", color="#10b981", icon_path="icons/add.png")
        self.add_row_btn.clicked.connect(self.add_new_row)
        
        self.delete_row_btn = ModernButton("删除选中行", color="#ef4444", icon_path="icons/delete.png")
        self.delete_row_btn.clicked.connect(self.delete_selected_row)
        
        self.clear_changes_btn = ModernButton("撤销修改", color="#f59e0b", icon_path="icons/undo.png")
        self.clear_changes_btn.clicked.connect(self.clear_changes)
        self.clear_changes_btn.setEnabled(False)
        
        self.import_btn = ModernButton("导入CSV", color="#8b5cf6", icon_path="icons/import.png")
        self.import_btn.clicked.connect(self.import_csv)
        
        self.export_btn = ModernButton("导出CSV", color="#06b6d4", icon_path="icons/export.png")
        self.export_btn.clicked.connect(self.export_csv)
        
        button_bar_layout.addWidget(self.add_row_btn)
        button_bar_layout.addWidget(self.delete_row_btn)
        button_bar_layout.addWidget(self.clear_changes_btn)
        
        # 添加分隔线
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.VLine)
        separator_line.setFrameShadow(QFrame.Shadow.Sunken)
        button_bar_layout.addWidget(separator_line)
        
        button_bar_layout.addWidget(self.import_btn)
        button_bar_layout.addWidget(self.export_btn)
        button_bar_layout.addStretch()
        
        layout.addLayout(button_bar_layout)

        
        layout.addLayout(button_bar_layout)

        # --- 用于数据显示的表格 ---
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)  # 编辑模式下禁用排序
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb; border-radius: 8px; gridline-color: #f3f4f6; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f9fafb; padding: 12px 16px; border-bottom: 2px solid #e5e7eb;
                font-weight: 600; color: #374151;
            }
            QTableWidget::item { 
                padding: 10px 14px; border-bottom: 1px solid #f3f4f6; 
            }
            QTableWidget::item:selected {
                background-color: #dbeafe; color: #1e40af;
            }
        """)
        
        # 连接数据变化信号
        self.table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.table)

    def on_item_changed(self, item):
        """当表格项被修改时调用"""
        self.is_modified = True
        self.save_btn.setEnabled(True)
        self.clear_changes_btn.setEnabled(True)
        self.status_label.setText("数据库状态：已修改 (未保存)")
        self.status_label.setStyleSheet("color: #dc2626;")

    def add_new_row(self):
        """添加新行"""
        current_row_count = self.table.rowCount()
        self.table.insertRow(current_row_count)
        
        # 设置默认值为空
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("")
            header_item = self.table.horizontalHeaderItem(col)
            header_text = header_item.text() if header_item else ""
            if header_text in self.numeric_columns:
                alignment = Qt.AlignmentFlag.AlignRight
            else:
                alignment = Qt.AlignmentFlag.AlignLeft
            item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(current_row_count, col, item)
        
        self.on_item_changed(None)  # 标记为已修改
        
    def delete_selected_row(self):
        """删除选中的行"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除第 {current_row + 1} 行吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.table.removeRow(current_row)
                self.on_item_changed(None)  # 标记为已修改
        else:
            QMessageBox.information(self, "提示", "请先选择要删除的行。")

    def clear_changes(self):
        """撤销修改，重新加载数据"""
        if self.is_modified:
            reply = QMessageBox.question(self, "确认撤销", 
                                       "确定要撤销所有未保存的修改吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.populate_table()
                self.is_modified = False
                self.save_btn.setEnabled(False)
                self.clear_changes_btn.setEnabled(False)

    def save_database(self):
        """保存数据库修改"""
        try:
            headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
            if not headers:
                QMessageBox.warning(self, "保存失败", "没有可保存的数据。")
                return

            data = []
            for row in range(self.table.rowCount()):
                row_data = {}
                for col, header in enumerate(headers):
                    item = self.table.item(row, col)
                    value = item.text().strip() if item and item.text() else ""

                    if header in self.numeric_columns:
                        if value == "" or value.lower() in {"nan", "null", "none"}:
                            row_data[header] = np.nan
                        else:
                            try:
                                row_data[header] = float(value)
                            except ValueError:
                                QMessageBox.warning(
                                    self,
                                    "数据验证错误",
                                    f"第 {row + 1} 行的 {header} 不是有效数值: '{value}'",
                                )
                                return
                    else:
                        row_data[header] = value if value else pd.NA

                data.append(row_data)

            new_df = pd.DataFrame(data, columns=headers)

            # 基础校验：岩性字段不能全部为空
            if '岩性' in new_df.columns and new_df['岩性'].dropna().eq('').all():
                QMessageBox.warning(self, "数据验证错误", "岩性列不能为空，请至少填写一个岩性名称。")
                return

            # 保存原始数据库
            raw_path = getattr(self.main_win, 'rock_db_raw_path', None)
            if raw_path:
                try:
                    new_df.to_csv(raw_path, index=False, encoding='utf-8-sig')
                except Exception as io_err:
                    QMessageBox.warning(self, "保存警告", f"写入原始数据库文件时发生错误：{io_err}")

            self.main_win.rock_db_raw = new_df

            aggregated_view = self.main_win._aggregate_raw_database(new_df)
            if aggregated_view is not None and not aggregated_view.empty:
                self.main_win.rock_db = aggregated_view
                self.main_win._save_rock_database(aggregated_view)
            else:
                self.main_win.rock_db = new_df

            # 重置修改状态
            self.is_modified = False
            self.save_btn.setEnabled(False)
            self.clear_changes_btn.setEnabled(False)
            self.status_label.setText(f"数据库状态：已保存 ({len(new_df)} 条记录)")
            self.status_label.setStyleSheet("color: #059669;")

            QMessageBox.information(self, "保存成功", "数据库已成功保存并重新聚合。")

        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存数据库时发生错误：\n{str(e)}")

    def populate_table(self):
        """用主窗口加载的数据库填充表格"""
        self.table.clear()
        raw_df = getattr(self.main_win, "rock_db_raw", None)

        if raw_df is None or raw_df.empty:
            db_df = getattr(self.main_win, "rock_db", None)
        else:
            db_df = raw_df.copy()

        if db_df is None or db_df.empty:
            self.status_label.setText("数据库状态：未加载或为空")
            self.status_label.setStyleSheet("color: #dc2626;")
            # 创建默认的空表格结构
            default_columns = ["岩性", "密度", "弹性模量/GPa", "容重/kN·m-3", "抗拉强度/MPa", "泊松比", "内摩擦角", "粘聚力/MPa"]
            self.table.setColumnCount(len(default_columns))
            self.table.setHorizontalHeaderLabels(default_columns)
            self.table.setRowCount(0)
            self.column_order = default_columns
            self.numeric_columns = set(default_columns[1:])
            return

        # 确保存在省份列并将其提前展示
        if '省份' not in db_df.columns:
            db_df['省份'] = pd.NA

        preferred_order = ['省份', '地市', '矿名', '岩性']
        ordered_cols = [col for col in preferred_order if col in db_df.columns]
        ordered_cols.extend([col for col in db_df.columns if col not in ordered_cols])
        db_df = db_df.loc[:, ordered_cols]

        self.status_label.setText(f"数据库状态：已加载 ({len(db_df)} 条记录)")
        self.status_label.setStyleSheet("color: #059669;")

        self.column_order = list(db_df.columns)
        numeric_cols = []
        for col in self.column_order:
            series = db_df[col]
            if pd.api.types.is_numeric_dtype(series):
                numeric_cols.append(col)
        self.numeric_columns = set(numeric_cols)

        df_display = db_df.copy()
        
        self.table.setRowCount(len(df_display))
        self.table.setColumnCount(len(df_display.columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in df_display.columns])

        # 暂时禁用信号以避免在填充时触发修改事件
        self.table.blockSignals(True)
        
        for i, row in enumerate(df_display.itertuples(index=False)):
            for j, value in enumerate(row):
                # 格式化数值显示 - 数值类型保留2位小数
                if pd.notna(value):
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        # 对于数值类型，保留2位小数
                        if abs(value - round(value)) < 1e-10:  # 接近整数的数
                            item_text = str(int(round(value)))
                        else:
                            item_text = f"{value:.2f}"
                    else:
                        item_text = str(value)
                else:
                    item_text = ""
                
                item = QTableWidgetItem(item_text)
                header = self.column_order[j] if j < len(self.column_order) else ''
                if header in self.numeric_columns:
                    alignment = Qt.AlignmentFlag.AlignRight
                else:
                    alignment = Qt.AlignmentFlag.AlignLeft
                item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
                
                self.table.setItem(i, j, item)
        
        # 重新启用信号
        self.table.blockSignals(False)
        
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # 重置修改状态
        self.is_modified = False
        self.save_btn.setEnabled(False)
        self.clear_changes_btn.setEnabled(False)

    def refresh_data(self):
        """重新加载数据库并刷新表格"""
        if self.is_modified:
            reply = QMessageBox.question(self, "确认刷新", 
                                       "刷新将丢失所有未保存的修改，确定要继续吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.main_win._load_rock_database()
        self.populate_table()
        QMessageBox.information(self, "刷新完成", "数据库已刷新。")

    def import_csv(self):
        """从CSV文件导入数据"""
        if self.is_modified:
            reply = QMessageBox.question(self, "确认导入", 
                                       "导入将丢失所有未保存的修改，确定要继续吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 尝试不同编码读取文件
                encodings_to_try = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
                df = None
                
                for encoding in encodings_to_try:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        continue
                
                if df is None:
                    QMessageBox.critical(self, "导入失败", "无法读取CSV文件，请检查文件编码。")
                    return
                
                # 验证数据格式
                if len(df.columns) == 0:
                    QMessageBox.critical(self, "导入失败", "CSV文件为空或格式不正确。")
                    return
                
                # 检查是否有岩性名称列
                name_col_found = False
                for col in df.columns:
                    if any(keyword in str(col) for keyword in ['岩性', '名称', 'name', 'rock']):
                        name_col_found = True
                        break
                
                if not name_col_found:
                    reply = QMessageBox.question(self, "数据验证", 
                                               "未找到明确的岩性名称列，是否继续导入？",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # 更新主窗口数据库
                self.main_win.rock_db_raw = df
                self.main_win.rock_db_raw_path = file_path

                aggregated_view = self.main_win._aggregate_raw_database(df)
                if aggregated_view is not None and not aggregated_view.empty:
                    self.main_win.rock_db = aggregated_view
                    self.main_win._save_rock_database(aggregated_view)
                else:
                    self.main_win.rock_db = df

                # 刷新显示
                self.populate_table()
                
                QMessageBox.information(self, "导入成功", 
                                      f"成功导入 {len(df)} 条记录，{len(df.columns)} 个字段。\n\n"
                                      f"文件: {os.path.basename(file_path)}\n"
                                      f"请检查数据并保存修改。")
                
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入CSV文件时发生错误：\n{str(e)}")

    def export_csv(self):
        """导出当前数据到CSV文件"""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "提示", "没有数据可以导出。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存CSV文件", "rock_properties_database.csv", "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 从表格获取数据
                data = []
                headers = []
                
                # 获取表头
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column_{col}")
                
                # 获取数据
                for row in range(self.table.rowCount()):
                    row_data = {}
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        value = item.text() if item else ""
                        
                        # 尝试转换为数值
                        if col > 0:  # 除第一列（岩性名称）外
                            try:
                                if value.strip() == "":
                                    value = np.nan
                                else:
                                    value = float(value)
                            except ValueError:
                                pass  # 保持原始字符串
                        
                        row_data[headers[col]] = value
                    
                    data.append(row_data)
                
                # 转换为DataFrame并保存
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                QMessageBox.information(self, "导出成功", 
                                      f"数据已成功导出到:\n{file_path}\n\n"
                                      f"导出 {len(df)} 条记录，{len(df.columns)} 个字段。")
                
                # 询问是否打开文件夹
                reply = QMessageBox.question(self, "打开文件夹", "是否要打开文件所在的文件夹？",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    import subprocess
                    if sys.platform == "win32":
                        subprocess.Popen(['explorer', '/select,', file_path])
                    elif sys.platform == "darwin":
                        subprocess.Popen(['open', '-R', file_path])
                    else:
                        subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
                
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出CSV文件时发生错误：\n{str(e)}")

    
class CustomRockLibraryTab(QWidget):
    """管理用户自建的力学参数库，并提供查询模块数据源切换支持"""

    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.preview_limit = 300
        self.status_label: Optional[QLabel] = None
        self.record_label: Optional[QLabel] = None
        self.path_label: Optional[QLabel] = None
        self.table: Optional[QTableWidget] = None
        self.empty_hint: Optional[QLabel] = None
        self.load_btn: Optional[QPushButton] = None
        self.clear_btn: Optional[QPushButton] = None
        self._init_ui()
        self.refresh_view()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("自建力学参数库管理")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)

        subtitle = QLabel("导入独立维护的力学参数CSV，并在查询模块中切换至自建库进行检索。")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #64748b; font-size: 13px; line-height: 1.6;")
        layout.addWidget(subtitle)

        control_bar = QHBoxLayout()
        control_bar.setSpacing(10)

        self.load_btn = ModernButton("导入自建库CSV", color="#2563eb", icon_path="icons/import.png")
        self.load_btn.clicked.connect(self.load_custom_csv)
        control_bar.addWidget(self.load_btn)

        self.clear_btn = ModernButton("清空自建库", color="#ef4444", icon_path="icons/delete.png")
        self.clear_btn.clicked.connect(self.clear_custom_library)
        self.clear_btn.setEnabled(False)
        control_bar.addWidget(self.clear_btn)

        control_bar.addStretch()
        layout.addLayout(control_bar)

        info_card = QFrame()
        info_card.setObjectName("customLibraryInfoCard")
        info_card.setStyleSheet(
            "QFrame#customLibraryInfoCard { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; }"
        )
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(18, 16, 18, 16)
        info_layout.setSpacing(6)

        self.status_label = QLabel("自建库状态：未加载")
        self.status_label.setStyleSheet("color: #1f2937; font-size: 13px; font-weight: 600;")
        info_layout.addWidget(self.status_label)

        self.record_label = QLabel("记录数：0")
        self.record_label.setStyleSheet("color: #475569; font-size: 12px;")
        info_layout.addWidget(self.record_label)

        self.path_label = QLabel("来源文件：--")
        self.path_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.path_label.setWordWrap(True)
        info_layout.addWidget(self.path_label)

        layout.addWidget(info_card)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; }"
        )
        layout.addWidget(self.table, 1)

        self.empty_hint = QLabel("尚未加载数据，点击“导入自建库CSV”按钮选择文件。")
        self.empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_hint.setStyleSheet(
            "color: #94a3b8; font-size: 13px; padding: 60px 12px; border: 1px dashed #cbd5f5; border-radius: 12px;"
        )
        layout.addWidget(self.empty_hint, 1)

        self.table.hide()

    def load_custom_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择自建库CSV文件",
            "",
            "CSV 文件 (*.csv);;所有文件 (*)",
        )
        if not file_path:
            return

        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception:
                continue

        if df is None:
            QMessageBox.critical(self, "导入失败", "无法解析所选CSV文件，请确认编码与格式是否正确。")
            return

        df.columns = [str(col).strip() for col in df.columns]
        df = df.loc[:, [col for col in df.columns if str(col).strip() and not str(col).startswith('Unnamed')]]

        if df.empty:
            QMessageBox.warning(self, "导入失败", "文件中未检测到有效数据，请检查内容后重试。")
            return

        self.main_win.custom_rock_db = df
        self.main_win.custom_rock_db_path = file_path
        self.refresh_view()

        if getattr(self.main_win, 'rock_lookup_page', None) is not None:
            self.main_win.rock_lookup_page.refresh_data(retain_selection=False, requested_dataset="custom")

        display_name = os.path.basename(file_path)
        self.main_win.set_global_status(f"自建库已加载：{display_name}", "#16a34a")
        QMessageBox.information(
            self,
            "导入成功",
            f"已成功加载自建库：{display_name}\n共 {len(df)} 条记录可用于查询。",
        )

    def clear_custom_library(self):
        if getattr(self.main_win, 'custom_rock_db', None) is None:
            QMessageBox.information(self, "提示", "当前未加载自建库，无需清空。")
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            "清空后将无法在查询模块中继续使用自建库数据，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.main_win.custom_rock_db = None
        self.main_win.custom_rock_db_path = None
        self.refresh_view()

        if getattr(self.main_win, 'rock_lookup_page', None) is not None:
            self.main_win.rock_lookup_page.refresh_data(retain_selection=False)

        self.main_win.set_global_status("自建库已清空", "#2563eb")
        QMessageBox.information(self, "已清空", "自建库数据已移除，可重新导入新的CSV。")

    def refresh_view(self):
        df = getattr(self.main_win, 'custom_rock_db', None)
        path = getattr(self.main_win, 'custom_rock_db_path', None)

        if df is None or df.empty:
            self.clear_btn.setEnabled(False)
            self.table.hide()
            self.empty_hint.show()
            if self.table is not None:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
            if self.status_label is not None:
                self.status_label.setText("自建库状态：未加载")
            if self.record_label is not None:
                self.record_label.setText("记录数：0")
            if self.path_label is not None:
                self.path_label.setText("来源文件：--")
            return

        self.clear_btn.setEnabled(True)
        self.empty_hint.hide()
        self.table.show()

        preview_df = df.head(self.preview_limit)
        headers = [str(col) for col in preview_df.columns]
        row_count = len(preview_df)

        self.table.blockSignals(True)
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(row_count)
        self.table.setHorizontalHeaderLabels(headers)

        for row_idx in range(row_count):
            for col_idx, column in enumerate(headers):
                value = preview_df.iloc[row_idx, col_idx]
                display_text = "" if pd.isna(value) else str(value)
                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.table.blockSignals(False)

        total_records = len(df)
        record_text = f"记录数：{total_records}"
        if total_records > self.preview_limit:
            record_text += f"（仅预览前 {self.preview_limit} 条）"

        if self.status_label is not None:
            self.status_label.setText("自建库状态：已加载")
        if self.record_label is not None:
            self.record_label.setText(record_text)
        if self.path_label is not None:
            source = os.path.basename(path) if path else "--"
            self.path_label.setText(f"来源文件：{source}")


class ContourPlotTab(QWidget):
    """等值线图生成与高级验证分析的UI界面 - 结合v2.4版本逻辑"""
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win # 保存主窗口的引用
        self.borehole_files = []  # 改为支持多个钻孔文件
        self.coords_file = None
        self.merged_df = None
        self.comparison_results = []
        self.detailed_comparison_data = []
        
        # 根据可用库调整插值方法
        self.interpolation_methods = self._get_available_methods()
        self.init_ui()

    def init_ui(self):
        """初始化等值线图标签页的UI界面"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- 左侧控制面板 - 优化尺寸策略 ---
        control_panel = QFrame()
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #fafbfc;
                border-right: 1px solid #e5e7eb;
            }
        """)
        
        # 使用 QScrollArea 使控制面板在内容过多时可以滚动
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(control_panel)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 20, 15, 20)  # 减小左右边距
        control_layout.setSpacing(15)  # 减小组件间距
        
        # 1. 文件加载组 - 紧凑设计
        file_group = QGroupBox("数据文件加载")
        file_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")  # 减小内边距
        file_layout = QVBoxLayout(file_group)  # 改为垂直布局
        file_layout.setSpacing(8)  # 减小间距
        
        # 数据文件行
        data_file_layout = QHBoxLayout()
        data_file_layout.setSpacing(8)
        self.select_data_btn = ModernButton("钻孔数据", color="#2563eb")
        self.select_data_btn.setMaximumHeight(32)  # 限制按钮高度
        self.data_file_label = QLabel("未选择")
        self.data_file_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        self.data_file_label.setWordWrap(True)
        self.select_data_btn.clicked.connect(self.select_data_file)
        data_file_layout.addWidget(self.select_data_btn, 0)
        data_file_layout.addWidget(self.data_file_label, 1)
        
        # 坐标文件行
        coord_file_layout = QHBoxLayout()
        coord_file_layout.setSpacing(8)
        self.select_coords_btn = ModernButton("坐标数据", color="#2563eb")
        self.select_coords_btn.setMaximumHeight(32)  # 限制按钮高度
        self.coords_file_label = QLabel("未选择")
        self.coords_file_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        self.coords_file_label.setWordWrap(True)
        self.select_coords_btn.clicked.connect(self.select_coordinate_file)
        coord_file_layout.addWidget(self.select_coords_btn, 0)
        coord_file_layout.addWidget(self.coords_file_label, 1)
        
        file_layout.addLayout(data_file_layout)
        file_layout.addLayout(coord_file_layout)
        control_layout.addWidget(file_group)
        
        # 2. 列选择组 - 紧凑设计
        column_group = QGroupBox("列选择")
        column_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        column_layout = QFormLayout(column_group)
        column_layout.setVerticalSpacing(6)  # 减小垂直间距
        column_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 设置下拉框样式，减小高度
        combo_style = """
            QComboBox {
                border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px;
                background-color: #ffffff; color: #374151; font-size: 13px; 
                min-height: 16px; max-height: 24px;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox:focus { border-color: #2563eb; outline: none; }
        """
        
        self.x_col_combo = QComboBox()
        self.x_col_combo.setStyleSheet(combo_style)
        self.y_col_combo = QComboBox()
        self.y_col_combo.setStyleSheet(combo_style)
        self.z_col_combo = QComboBox()
        self.z_col_combo.setStyleSheet(combo_style)
        self.seam_col_combo = QComboBox()
        self.seam_col_combo.setStyleSheet(combo_style)
        self.layer_spacing_combo = QComboBox()
        self.layer_spacing_combo.setStyleSheet(combo_style)
        self.layer_spacing_combo.addItem("自动(均匀间距)", userData=None)
        self.validation_col_combo = QComboBox()
        self.validation_col_combo.setStyleSheet(combo_style)
        
        column_layout.addRow("X坐标:", self.x_col_combo)
        column_layout.addRow("Y坐标:", self.y_col_combo)
        column_layout.addRow("Z值:", self.z_col_combo)
        column_layout.addRow("煤层列:", self.seam_col_combo)
        column_layout.addRow("层间距列:", self.layer_spacing_combo)
        column_layout.addRow("验证列:", self.validation_col_combo)
        control_layout.addWidget(column_group)
        
        # 连接煤层列变化信号，自动更新岩层选择
        self.seam_col_combo.currentTextChanged.connect(lambda: self._update_layer_select_combo())
        
        # 3. 插值设置组 - 紧凑设计
        interp_group = QGroupBox("插值设置")
        interp_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        interp_layout = QFormLayout(interp_group)
        interp_layout.setVerticalSpacing(6)
        
        self.interp_method_combo = QComboBox()
        self.interp_method_combo.setStyleSheet(combo_style)
        self.interp_method_combo.addItems(list(self.interpolation_methods.values()))
        # 默认选择Cubic（三次插值），效果类似参考图
        cubic_method = next((method for method in self.interpolation_methods.values() if 'Cubic' in method or '三次' in method), None)
        if cubic_method:
            self.interp_method_combo.setCurrentText(cubic_method)
        
        # 添加岩层选择下拉框（用于3D曲面图）
        self.layer_select_combo = QComboBox()
        self.layer_select_combo.setStyleSheet(combo_style)
        self.layer_select_combo.addItem("请先加载数据", userData=None)
        
        self.validation_slider = QSlider(Qt.Orientation.Horizontal)
        self.validation_slider.setRange(10, 50)
        self.validation_slider.setValue(20)
        self.validation_slider.setMaximumHeight(20)  # 限制滑块高度
        self.validation_label = QLabel("20%")
        self.validation_label.setStyleSheet("font-size: 12px; min-width: 30px;")
        
        def update_validation_label(value): 
            self.validation_label.setText(f"{value}%")
        self.validation_slider.valueChanged.connect(update_validation_label)
        
        validation_layout = QHBoxLayout()
        validation_layout.setSpacing(8)
        validation_layout.addWidget(self.validation_slider, 1)
        validation_layout.addWidget(self.validation_label, 0)
        
        interp_layout.addRow("插值方法:", self.interp_method_combo)
        interp_layout.addRow("3D曲面岩层:", self.layer_select_combo)
        interp_layout.addRow("验证比例:", validation_layout)
        control_layout.addWidget(interp_group)
        
        # 4. 操作按钮组 - 2列网格布局
        action_group = QGroupBox("操作")
        action_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        action_layout = QGridLayout(action_group)
        action_layout.setSpacing(8)  # 设置按钮间距
        
        # 创建紧凑的按钮
        button_style = "QPushButton { padding: 8px 12px; font-size: 12px; min-height: 16px; max-height: 32px; }"
        
        self.generate_btn = ModernButton("生成等值线图 & 3D曲面", color="#059669")
        self.generate_btn.setStyleSheet(self.generate_btn.styleSheet() + button_style)
        self.validate_btn = ModernButton("验证插值效果", color="#0891b2")
        self.validate_btn.setStyleSheet(self.validate_btn.styleSheet() + button_style)
        self.surface_btn = ModernButton("生成煤层3D曲面", color="#2563eb")
        self.surface_btn.setStyleSheet(self.surface_btn.styleSheet() + button_style)
        self.compare_btn = ModernButton("对比所有插值法", color="#7c3aed")
        self.compare_btn.setStyleSheet(self.compare_btn.styleSheet() + button_style)
        self.export_plot_btn = ModernButton("导出图像", color="#dc2626")
        self.export_plot_btn.setStyleSheet(self.export_plot_btn.styleSheet() + button_style)
        self.export_results_btn = ModernButton("导出对比结果", color="#ea580c")
        self.export_results_btn.setStyleSheet(self.export_results_btn.styleSheet() + button_style)
        
        # 连接信号
        self.generate_btn.clicked.connect(self.generate_plot)
        self.validate_btn.clicked.connect(self.perform_validation)
        self.surface_btn.clicked.connect(self.generate_surface_plots)
        self.compare_btn.clicked.connect(self.compare_all_methods)
        self.export_plot_btn.clicked.connect(self.export_plot)
        self.export_results_btn.clicked.connect(self.export_comparison_results)
        
        # 2列布局排列按钮
        action_layout.addWidget(self.generate_btn, 0, 0)       # 第1行第1列
        action_layout.addWidget(self.validate_btn, 0, 1)      # 第1行第2列
        action_layout.addWidget(self.surface_btn, 1, 0, 1, 2)  # 第2行跨2列
        action_layout.addWidget(self.compare_btn, 2, 0, 1, 2)  # 第3行跨2列
        action_layout.addWidget(self.export_plot_btn, 3, 0)    # 第4行第1列
        action_layout.addWidget(self.export_results_btn, 3, 1) # 第4行第2列
        
        control_layout.addWidget(action_group)
        control_layout.addStretch()  # 添加弹性空间
        
        # --- 右侧结果面板 ---
        results_panel = QFrame()
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_tabs = QTabWidget()
        
        # 图表标签页
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        self.canvas = ChartCanvas(plot_widget, width=12, height=6, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, plot_widget)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        self.results_tabs.addTab(plot_widget, "等值线图")

        # 三维曲面标签页
        self.surface_tab = QWidget()
        surface_layout = QVBoxLayout(self.surface_tab)
        # 修改画布宽高比，使其更接近参考图（宽:高 = 2:1）
        self.surface_canvas = ChartCanvas(self.surface_tab, width=14, height=7, dpi=100)
        self.surface_toolbar = NavigationToolbar(self.surface_canvas, self.surface_tab)
        surface_layout.addWidget(self.surface_toolbar)
        surface_layout.addWidget(self.surface_canvas)
        self.results_tabs.addTab(self.surface_tab, "3D曲面图")
        
        # 对比结果汇总标签页
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_title = QLabel("插值方法对比汇总")
        summary_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        summary_layout.addWidget(summary_title)
        self.summary_table = QTableWidget()
        self.summary_table.setAlternatingRowColors(True)
        summary_layout.addWidget(self.summary_table)
        self.results_tabs.addTab(summary_widget, "对比汇总")
        
        # 详细结果标签页
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_title = QLabel("预测vs实际值详细对比")
        detail_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        detail_layout.addWidget(detail_title)
        self.detail_table = QTableWidget()
        self.detail_table.setAlternatingRowColors(True)
        detail_layout.addWidget(self.detail_table)
        self.results_tabs.addTab(detail_widget, "详细对比")
        
        results_layout.addWidget(self.results_tabs)
        
        # --- 添加到主分割器 ---
        # 使用带滚动条的 scroll_area 替代 control_panel
        main_splitter.addWidget(scroll_area) 
        main_splitter.addWidget(results_panel)
        
        # --- 优化比例 ---
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([420, 960])  # 减小左侧面板宽度
        
        main_layout.addWidget(main_splitter)

    def _get_available_methods(self):
        """根据可用的库返回支持的插值方法 - 从v2.4版本移植"""
        methods = {}
        
        try:
            from scipy.interpolate import griddata, Rbf
            # Scipy griddata方法
            methods.update({
                "linear": "Linear (线性)",
                "cubic": "Cubic (三次样条)", 
                "nearest": "Nearest Neighbor (最近邻)",
            })
            
            # RBF径向基函数方法
            methods.update({
                "multiquadric": "Multiquadric (多重二次)",
                "inverse": "Inverse Distance (反距离)",
                "gaussian": "Gaussian (高斯)",
                "linear_rbf": "Linear RBF (线性RBF)",
                "cubic_rbf": "Cubic RBF (三次RBF)",
                "quintic_rbf": "Quintic RBF (五次RBF)",
                "thin_plate": "Thin Plate Spline (薄板样条)",
            })
        except ImportError:
            print("警告: scipy未安装，某些插值方法将不可用")
        
        # 添加基础插值方法（不依赖外部库）
        methods.update({
            "inverse_distance": "Simple Inverse Distance (简单反距离)",
            "bilinear": "Bilinear (双线性)",
        })
        
        # 添加克里金方法（使用简化实现）
        methods.update({
            "ordinary_kriging": "Ordinary Kriging (普通克里金)",
            "universal_kriging": "Universal Kriging (通用克里金)",
            "modified_shepard": "Modified Shepard (修正谢泼德)",
            "natural_neighbor": "Natural Neighbor (自然邻点)",
            "radial_basis": "Radial Basis Function (径向基)"
        })
        
        if len(methods) == 0:
            # 如果没有可用的插值库，至少提供最基础的方法
            methods["nearest_simple"] = "Simple Nearest (简单最近邻)"
        
        return methods

    def select_data_file(self):
        """选择钻孔数据文件（支持多文件）"""
        filepaths, _ = QFileDialog.getOpenFileNames(self, "选择钻孔数据文件", "", "CSV Files (*.csv)")
        if filepaths:
            self.borehole_files = list(filepaths)
            preview_names = [os.path.basename(path) for path in self.borehole_files[:3]]
            label_text = "；".join(preview_names)
            if len(self.borehole_files) > 3:
                label_text += f" 等 {len(self.borehole_files)} 个文件"
            self.data_file_label.setText(label_text)
            self._load_and_merge_data()
        else:
            if not self.borehole_files:
                self.data_file_label.setText("未选择")
                self.merged_df = None

    def select_coordinate_file(self):
        """选择坐标文件"""
        filepath, _ = QFileDialog.getOpenFileName(self, "选择坐标数据文件", "", "CSV Files (*.csv)")
        if filepath:
            self.coords_file = filepath
            self.coords_file_label.setText(os.path.basename(filepath))
            self._load_and_merge_data()

    def _load_and_merge_data(self):
        """加载并合并数据 - 使用与煤层块体建模相同的逻辑"""
        if not self.borehole_files:
            return False
        if not self.coords_file:
            return False
            
        try:
            # 使用aggregate_boreholes函数合并数据（与煤层块体建模一致）
            merged_df, _ = aggregate_boreholes(self.borehole_files, self.coords_file)
            
            # 调用数据填充功能
            if hasattr(self.main_win, 'rock_db') and getattr(self.main_win, 'rock_db', None) is not None:
                stat_preference = getattr(self.main_win, 'stat_preference', 'median')
                filled_df, filled_count, filled_cols = fill_missing_properties(
                    merged_df,
                    self.main_win.rock_db,
                    stat_preference=stat_preference,
                )
                if filled_count > 0:
                    merged_df = filled_df
                    metric_label = '平均值' if stat_preference == 'mean' else '中位数'
                    QMessageBox.information(
                        self,
                        "数据自动填充",
                        f"已填充 {filled_count} 条记录的参数（优先使用{metric_label}）：\n- {', '.join(filled_cols)}",
                    )

            self.merged_df = merged_df
            self._update_column_options()
            
            QMessageBox.information(
                self, 
                "合并成功", 
                f"数据合并成功，钻孔文件 {len(self.borehole_files)} 个，记录数: {len(self.merged_df)}"
            )
            
            # 刷新仪表板
            if hasattr(self.main_win, "dashboard_page") and self.main_win.dashboard_page:
                self.main_win.dashboard_page.refresh_cards()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "合并错误", f"合并数据时发生错误: {e}\n\n{traceback.format_exc()}")
            self.merged_df = None
            return False

    def _update_column_options(self):
        """更新列选择选项"""
        if self.merged_df is not None:
            num_cols = self.merged_df.select_dtypes(include=np.number).columns.tolist()
            for combo in [self.x_col_combo, self.y_col_combo, self.z_col_combo, self.validation_col_combo]:
                combo.clear()
                combo.addItems(num_cols)
            # 更新煤层列下拉框（文本/分类列）
            categorical_cols = self.merged_df.select_dtypes(include=['object', 'category']).columns.tolist()
            self.seam_col_combo.clear()
            if categorical_cols:
                self.seam_col_combo.addItems(categorical_cols)
                default_seam_col = next((col for col in categorical_cols if '煤' in col or '层' in col), categorical_cols[0])
                self.seam_col_combo.setCurrentText(default_seam_col)
            else:
                self.seam_col_combo.addItem("未检测到文本列")
                self.seam_col_combo.setCurrentIndex(0)

            # 更新层间距列下拉框（数值列）
            current_index = self.layer_spacing_combo.currentIndex()
            self.layer_spacing_combo.blockSignals(True)
            self.layer_spacing_combo.clear()
            self.layer_spacing_combo.addItem("自动(均匀间距)", userData=None)
            for col in num_cols:
                self.layer_spacing_combo.addItem(col, userData=col)
            default_spacing_col = next((col for col in num_cols if any(keyword in col for keyword in ['距', '间距', '深', '厚', '高程'])), None)
            if default_spacing_col:
                idx = self.layer_spacing_combo.findData(default_spacing_col)
                if idx != -1:
                    self.layer_spacing_combo.setCurrentIndex(idx)
            else:
                self.layer_spacing_combo.setCurrentIndex(0)
            self.layer_spacing_combo.blockSignals(False)
            
            # 更新3D曲面岩层选择下拉框
            self._update_layer_select_combo()
            
            # 智能设置默认值
            if num_cols:
                # 智能识别X坐标列
                x_candidates = [col for col in num_cols if any(kw in col.lower() for kw in ['x', '坐标x', 'east', '东'])]
                if x_candidates:
                    self.x_col_combo.setCurrentText(x_candidates[0])
                elif len(num_cols) >= 1:
                    self.x_col_combo.setCurrentText(num_cols[0])
                
                # 智能识别Y坐标列
                y_candidates = [col for col in num_cols if any(kw in col.lower() for kw in ['y', '坐标y', 'north', '北'])]
                if y_candidates:
                    self.y_col_combo.setCurrentText(y_candidates[0])
                elif len(num_cols) >= 2:
                    self.y_col_combo.setCurrentText(num_cols[1])
                
                # 智能识别厚度列
                z_candidates = [col for col in num_cols if any(kw in col for kw in ['厚度', '厚', 'thick', 'h'])]
                if z_candidates:
                    self.z_col_combo.setCurrentText(z_candidates[0])
                    self.validation_col_combo.setCurrentText(z_candidates[0])
                elif len(num_cols) >= 3:
                    self.z_col_combo.setCurrentText(num_cols[2])
                    self.validation_col_combo.setCurrentText(num_cols[2])

    def _update_layer_select_combo(self):
        """更新3D曲面岩层选择下拉框"""
        self.layer_select_combo.blockSignals(True)
        self.layer_select_combo.clear()
        
        if self.merged_df is None:
            self.layer_select_combo.addItem("请先加载数据", userData=None)
            self.layer_select_combo.blockSignals(False)
            return
        
        # 获取煤层列
        seam_col = self.seam_col_combo.currentText()
        if not seam_col or seam_col == "未检测到文本列" or seam_col not in self.merged_df.columns:
            self.layer_select_combo.addItem("请选择有效的煤层列", userData=None)
            self.layer_select_combo.blockSignals(False)
            return
        
        # 获取所有唯一的岩层
        unique_layers = self.merged_df[seam_col].dropna().unique()
        unique_layers = sorted([str(layer) for layer in unique_layers])
        
        if len(unique_layers) == 0:
            self.layer_select_combo.addItem("无可用岩层", userData=None)
        else:
            self.layer_select_combo.addItem("全部岩层（等值线用）", userData="__all__")
            for layer in unique_layers:
                # 统计该岩层的数据点数
                layer_count = len(self.merged_df[self.merged_df[seam_col] == layer])
                self.layer_select_combo.addItem(f"{layer} ({layer_count}点)", userData=layer)
            
            # 默认选择第一个具体岩层（用于3D曲面）
            if len(unique_layers) > 0:
                self.layer_select_combo.setCurrentIndex(1)  # 跳过"全部岩层"选项
        
        self.layer_select_combo.blockSignals(False)

    def _perform_interpolation(self, x_train, y_train, z_train, x_val, y_val, method):
        """执行指定方法的插值 - 从v2.4版本移植"""
        try:
            # 获取方法键值
            method_key = None
            for key, value in self.interpolation_methods.items():
                if value == method:
                    method_key = key
                    break
            if method_key is None:
                method_key = method.lower()
                
            # 修正：griddata只支持linear, nearest, cubic
            if method_key == "linear":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            
            elif method_key == "cubic":
                if len(x_train) >= 16:  # 三次样条至少需要16个点
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='cubic')
                else:
                    print(f"数据点不足，从cubic降级为linear插值")
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            
            elif method_key == "quintic":
                # quintic使用RBF实现
                rbf = Rbf(x_train, y_train, z_train, function='quintic')
                return rbf(x_val, y_val)
            
            elif method_key == "nearest":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
                
            elif method_key in ["multiquadric", "inverse", "gaussian", "linear_rbf", "cubic_rbf", 
                          "quintic_rbf", "thin_plate"]:
                rbf_method_map = {
                    "multiquadric": "multiquadric",
                    "inverse": "inverse",
                    "gaussian": "gaussian", 
                    "linear_rbf": "linear",
                    "cubic_rbf": "cubic",
                    "quintic_rbf": "quintic",
                    "thin_plate": "thin_plate"
                }
                rbf = Rbf(x_train, y_train, z_train, function=rbf_method_map[method_key])
                return rbf(x_val, y_val)
            
            elif method_key == "bilinear":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            
            elif method_key == "bicubic":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='cubic')
            
            elif method_key in ["spline", "akima"]:
                # 使用cubic样条代替
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='cubic')
            
            elif method_key == "modified_shepard":
                # 修正谢泼德插值实现
                result = []
                for i, (xv, yv) in enumerate(zip(x_val, y_val)):
                    distances = np.sqrt((x_train - xv)**2 + (y_train - yv)**2)
                    # 避免除零错误
                    distances = np.where(distances == 0, 1e-12, distances)
                    weights = 1.0 / (distances**2)
                    weights = weights / np.sum(weights)
                    result.append(np.sum(weights * z_train))
                return np.array(result)
            
            elif method_key == "natural_neighbor":
                # 使用linear作为近似
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            
            elif method_key == "radial_basis":
                rbf = Rbf(x_train, y_train, z_train, function='multiquadric', smooth=0.1)
                return rbf(x_val, y_val)
            
            elif method_key == "ordinary_kriging":
                # 使用高斯RBF近似克里金，添加平滑参数避免矩阵奇异
                # 检查数据点数量
                if len(x_train) < 4:
                    # 数据点太少，降级为最近邻
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
                try:
                    rbf = Rbf(x_train, y_train, z_train, function='gaussian', smooth=0.5)
                    return rbf(x_val, y_val)
                except (np.linalg.LinAlgError, ZeroDivisionError, ValueError) as e:
                    # Kriging失败时静默降级为线性插值
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            
            elif method_key == "universal_kriging":
                # 使用薄板样条近似通用克里金，添加平滑参数
                if len(x_train) < 4:
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
                try:
                    rbf = Rbf(x_train, y_train, z_train, function='thin_plate', smooth=0.5)
                    return rbf(x_val, y_val)
                except (np.linalg.LinAlgError, ZeroDivisionError, ValueError) as e:
                    # 失败时降级为线性插值
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
                
            else:
                # 默认使用linear
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
                
        except Exception as e:
            # 只在非预期错误时打印
            if not isinstance(e, (np.linalg.LinAlgError, ZeroDivisionError)):
                print(f"插值方法 {method} 失败: {e}")
            # 如果所选方法失败，尝试使用最基本的linear方法
            try:
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            except:
                return np.full(len(x_val), np.nan)

    def compare_all_methods(self):
        """对比所有插值方法的性能 - 修复除零错误版本"""
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return
        
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        z_col = self.z_col_combo.currentText()
        validation_col = self.validation_col_combo.currentText()
        
        if not all([x_col, y_col, z_col, validation_col]):
            QMessageBox.warning(self, "缺少列", "请为X, Y, Z和验证列选择有效的列。")
            return
        
        try:
            # 获取有效数据
            valid_data = self.merged_df.dropna(subset=[x_col, y_col, z_col, validation_col])
            if len(valid_data) < 10:
                QMessageBox.warning(self, "数据不足", "需要至少10个有效数据点进行验证。")
                return
            
            # 随机分割训练和验证数据
            validation_ratio = self.validation_slider.value() / 100.0
            np.random.seed(42)  # 设置随机种子保证结果可重现
            n_validation = int(len(valid_data) * validation_ratio)
            validation_indices = np.random.choice(valid_data.index, n_validation, replace=False)
            
            training_data = valid_data.drop(validation_indices)
            validation_data = valid_data.loc[validation_indices]
            
            x_train = training_data[x_col].values
            y_train = training_data[y_col].values
            z_train = training_data[z_col].values
            
            x_val = validation_data[x_col].values
            y_val = validation_data[y_col].values
            z_val_actual = validation_data[validation_col].values
            
            self.comparison_results = []
            self.detailed_comparison_data = []
            
            # 创建进度对话框
            progress_dialog = QProgressDialog("正在测试所有插值方法...", "取消", 0, len(self.interpolation_methods), self)
            progress_dialog.setWindowTitle("插值方法对比进行中...")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.setCancelButtonText("取消")
            progress_dialog.setAutoClose(True)
            progress_dialog.setAutoReset(True)
            progress_dialog.setMinimumWidth(300)
            
            successful_methods = 0
            failed_methods = []
            
            # 测试所有插值方法
            for i, (method_key, method_name) in enumerate(self.interpolation_methods.items()):
                try:
                    # 检查是否被用户取消
                    if progress_dialog.wasCanceled():
                        QMessageBox.warning(self, "操作取消", "插值方法对比已取消")
                        progress_dialog.close()
                        return
                        
                    # 更新进度显示
                    progress_dialog.setValue(i)
                    progress_dialog.setLabelText(f"正在测试: {method_name} ({i+1}/{len(self.interpolation_methods)})")
                    QApplication.processEvents()
                    
                    # 执行插值预测
                    z_val_predicted = self._perform_interpolation(x_train, y_train, z_train, x_val, y_val, method_name)
                    
                    # 计算误差指标
                    valid_predictions = ~np.isnan(z_val_predicted)
                    n_valid = np.sum(valid_predictions)
                    
                    if n_valid == 0:
                        failed_methods.append(f"{method_name} (无有效预测)")
                        continue
                    
                    # 提取有效的预测值和实际值
                    z_actual_valid = z_val_actual[valid_predictions]
                    z_predicted_valid = z_val_predicted[valid_predictions]
                    x_val_valid = x_val[valid_predictions]
                    y_val_valid = y_val[valid_predictions]
                    
                    # 计算误差指标
                    mae = np.mean(np.abs(z_actual_valid - z_predicted_valid))
                    rmse = np.sqrt(np.mean((z_actual_valid - z_predicted_valid)**2))
                    
                    # 计算R² - 修复除零错误
                    ss_res = np.sum((z_actual_valid - z_predicted_valid)**2)
                    ss_tot = np.sum((z_actual_valid - np.mean(z_actual_valid))**2)
                    
                    # 添加除零保护
                    if ss_tot != 0 and not np.isclose(ss_tot, 0, atol=1e-10):
                        r2 = 1 - (ss_res / ss_tot)
                        # 确保R²在合理范围内
                        r2 = max(-10, min(1, r2))  # 限制R²在[-10, 1]范围内
                    else:
                        # 如果所有实际值都相同（方差为0），设置R²为特殊值
                        if ss_res == 0:
                            r2 = 1.0  # 完美预测
                        else:
                            r2 = -999.0  # 标记为无效R²
                    
                    # 计算MAPE - 添加保护
                    nonzero_mask = np.abs(z_actual_valid) > 1e-10  # 避免除以非常小的数
                    if np.sum(nonzero_mask) > 0:
                        mape = np.mean(np.abs((z_actual_valid[nonzero_mask] - z_predicted_valid[nonzero_mask]) / z_actual_valid[nonzero_mask]) * 100)
                        # 限制MAPE在合理范围内
                        mape = min(mape, 1000.0)  # 最大1000%
                    else:
                        mape = float('inf')
                    
                    # 计算准确率 - 添加保护
                    relative_errors = np.abs((z_actual_valid - z_predicted_valid) / (np.abs(z_actual_valid) + 1e-10))
                    accuracy_10 = np.mean(relative_errors < 0.1) * 100  # 10%误差范围内的准确率
                    accuracy_5 = np.mean(relative_errors < 0.05) * 100  # 5%误差范围内的准确率
                    
                    # 保存结果
                    self.comparison_results.append({
                        'method_key': method_key,
                        'method_name': method_name,
                        'mae': mae,
                        'rmse': rmse,
                        'r2': r2,
                        'mape': mape,
                        'accuracy_10': accuracy_10,
                        'accuracy_5': accuracy_5,
                        'n_valid_predictions': n_valid
                    })
                    
                    # 保存详细对比数据
                    for j in range(min(len(z_actual_valid), 20)):  # 限制详细数据数量
                        absolute_error = abs(z_actual_valid[j] - z_predicted_valid[j])
                        # 计算相对误差时添加保护
                        if abs(z_actual_valid[j]) > 1e-10:
                            relative_error = abs((z_actual_valid[j] - z_predicted_valid[j]) / z_actual_valid[j]) * 100
                            relative_error = min(relative_error, 1000.0)  # 限制最大相对误差
                        else:
                            relative_error = float('inf') if absolute_error > 1e-10 else 0.0
                        
                        self.detailed_comparison_data.append({
                            '插值方法': method_name,
                            'X坐标': round(float(x_val_valid[j]), 4),
                            'Y坐标': round(float(y_val_valid[j]), 4),
                            '实际值': round(float(z_actual_valid[j]), 4),
                            '预测值': round(float(z_predicted_valid[j]), 4),
                            '绝对误差': round(absolute_error, 4),
                            '相对误差(%)': round(relative_error, 2) if relative_error != float('inf') else 'N/A'
                        })
                    
                    successful_methods += 1
                    
                except Exception as e:
                    error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
                    failed_methods.append(f"{method_name} ({error_msg})")
                    print(f"方法 {method_name} 测试失败: {e}")
                    continue
            
            # 关闭进度对话框
            progress_dialog.close()
            
            # 结果处理和显示
            if not self.comparison_results:
                error_msg = f"所有插值方法都失败了。\n\n失败原因:\n" + "\n".join(failed_methods[:5])
                if len(failed_methods) > 5:
                    error_msg += f"\n... 还有 {len(failed_methods) - 5} 个方法失败"
                QMessageBox.critical(self, "对比失败", error_msg)
                return
            
            # 按R²排序（R²越高越好，但排除无效R²）
            valid_r2_results = [r for r in self.comparison_results if r['r2'] > -900]
            invalid_r2_results = [r for r in self.comparison_results if r['r2'] <= -900]
            
            # 先对有效R²的结果排序，再添加无效R²的结果
            valid_r2_results.sort(key=lambda x: x['r2'], reverse=True)
            invalid_r2_results.sort(key=lambda x: x['mae'])  # 对无效R²的按MAE排序
            
            self.comparison_results = valid_r2_results + invalid_r2_results
            
            # 显示结果
            self._display_comparison_results()
            self._display_detailed_results()
            
            # 显示最佳方法的详细信息
            best_method = self.comparison_results[0]
            
            # 格式化R²显示
            r2_display = f"{best_method['r2']:.4f}" if best_method['r2'] > -900 else "无效(数据方差为0)"
            mape_display = f"{best_method['mape']:.2f}%" if best_method['mape'] != float('inf') else "N/A"
            
            best_method_msg = f"""🏆 推荐的最佳插值方法:

    方法名称: {best_method['method_name']}

    详细性能指标:
    • 平均绝对误差 (MAE): {best_method['mae']:.4f}
    • 均方根误差 (RMSE): {best_method['rmse']:.4f}  
    • 决定系数 (R²): {r2_display}
    • 平均绝对百分比误差 (MAPE): {mape_display}
    • 准确率 (10%误差范围): {best_method['accuracy_10']:.1f}%
    • 准确率 (5%误差范围): {best_method['accuracy_5']:.1f}%

    有效预测点数: {best_method['n_valid_predictions']}
    训练数据点: {len(training_data)}
    验证数据点: {len(validation_data)}

    评估结论:
    • 该方法在所有{len(self.comparison_results)}种插值方法中表现最佳
    • 预测准确率为{best_method['accuracy_10']:.1f}%（10%误差范围内）
    • 平均预测误差为{best_method['mae']:.4f}

    建议: 使用 '{best_method['method_name']}' 方法生成最终的等值线图。
    可在"详细对比"标签页查看具体预测结果。"""

            QMessageBox.information(self, "插值方法对比完成", best_method_msg)
            
            # 自动设置最佳方法
            self.interp_method_combo.setCurrentText(best_method['method_name'])
            
        except Exception as e:
            QMessageBox.critical(self, "对比过程失败", f"插值方法对比过程中发生错误:\n\n{str(e)}")

    
    def _classify_error(self, relative_error):
        """根据相对误差百分比对误差进行分级"""
        if relative_error <= 5:
            return "优秀"
        elif relative_error <= 10:
            return "良好"
        elif relative_error <= 20:
            return "一般"
        elif relative_error <= 50:
            return "较差"
        else:
            return "很差"
    def _display_comparison_results(self):
        """显示对比结果汇总"""
        self.summary_table.clear()
        if not self.comparison_results: 
            return
        
        headers = ["排名", "插值方法", "MAE", "RMSE", "R²", "MAPE(%)", "准确率(%)"]
        self.summary_table.setRowCount(len(self.comparison_results))
        self.summary_table.setColumnCount(len(headers))
        self.summary_table.setHorizontalHeaderLabels(headers)
        
        for i, result in enumerate(self.comparison_results):
            rank = i + 1
            self.summary_table.setItem(i, 0, QTableWidgetItem(str(rank)))
            self.summary_table.setItem(i, 1, QTableWidgetItem(result['method_name']))
            self.summary_table.setItem(i, 2, QTableWidgetItem(f"{result['mae']:.4f}"))
            self.summary_table.setItem(i, 3, QTableWidgetItem(f"{result['rmse']:.4f}"))
            self.summary_table.setItem(i, 4, QTableWidgetItem(f"{result['r2']:.4f}"))
            mape_text = f"{result['mape']:.2f}" if result['mape'] != float('inf') else "N/A"
            self.summary_table.setItem(i, 5, QTableWidgetItem(mape_text))
            self.summary_table.setItem(i, 6, QTableWidgetItem(f"{result['accuracy_10']:.1f}"))
        
        self.summary_table.resizeColumnsToContents()

    def _display_detailed_results(self):
        """显示详细对比数据"""
        self.detail_table.clear()
        if not self.detailed_comparison_data: 
            return
        
        headers = list(self.detailed_comparison_data[0].keys())
        self.detail_table.setRowCount(len(self.detailed_comparison_data))
        self.detail_table.setColumnCount(len(headers))
        self.detail_table.setHorizontalHeaderLabels(headers)
        
        for i, row in enumerate(self.detailed_comparison_data):
            for j, value in enumerate(row.values()):
                self.detail_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.detail_table.resizeColumnsToContents()

    def perform_validation(self):
        """单一方法验证 - 修复除零错误版本"""
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return
        
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        z_col = self.z_col_combo.currentText()
        validation_col = self.validation_col_combo.currentText()
        
        if not all([x_col, y_col, z_col, validation_col]):
            QMessageBox.warning(self, "缺少列", "请为X, Y, Z和验证列选择有效的列。")
            return

        try:
            # 获取有效数据
            valid_data = self.merged_df.dropna(subset=[x_col, y_col, z_col, validation_col])
            if len(valid_data) < 10:
                QMessageBox.warning(self, "数据不足", "需要至少10个有效数据点进行验证。")
                return
            
            # 随机分割训练和验证数据
            validation_ratio = self.validation_slider.value() / 100.0
            n_validation = int(len(valid_data) * validation_ratio)
            validation_indices = np.random.choice(valid_data.index, n_validation, replace=False)
            
            training_data = valid_data.drop(validation_indices)
            validation_data = valid_data.loc[validation_indices]
            
            # 使用训练数据建立插值模型
            x_train = training_data[x_col].values
            y_train = training_data[y_col].values
            z_train = training_data[z_col].values
            
            x_val = validation_data[x_col].values
            y_val = validation_data[y_col].values
            z_val_actual = validation_data[validation_col].values
            
            # 插值预测
            method_name = self.interp_method_combo.currentText()
            z_val_predicted = self._perform_interpolation(x_train, y_train, z_train, x_val, y_val, method_name)
            
            # 计算误差指标
            valid_predictions = ~np.isnan(z_val_predicted)
            z_val_actual = z_val_actual[valid_predictions]
            z_val_predicted = z_val_predicted[valid_predictions]
            
            if len(z_val_actual) == 0:
                QMessageBox.critical(self, "验证失败", "插值预测失败")
                return
            
            mae = np.mean(np.abs(z_val_actual - z_val_predicted))
            rmse = np.sqrt(np.mean((z_val_actual - z_val_predicted)**2))
            
            # 计算R² - 修复除零错误
            ss_res = np.sum((z_val_actual - z_val_predicted)**2)
            ss_tot = np.sum((z_val_actual - np.mean(z_val_actual))**2)
            
            if ss_tot != 0 and not np.isclose(ss_tot, 0, atol=1e-10):
                r2 = 1 - (ss_res / ss_tot)
                r2 = max(-10, min(1, r2))  # 限制R²在合理范围内
                r2_display = f"{r2:.4f}"
            else:
                if ss_res == 0:
                    r2_display = "1.0000 (完美预测)"
                else:
                    r2_display = "无效 (数据方差为0)"
            
            # 计算MAPE和准确率 - 添加保护
            nonzero_mask = np.abs(z_val_actual) > 1e-10
            if np.sum(nonzero_mask) > 0:
                mape = np.mean(np.abs((z_val_actual[nonzero_mask] - z_val_predicted[nonzero_mask]) / z_val_actual[nonzero_mask]) * 100)
                mape = min(mape, 1000.0)
                mape_display = f"{mape:.2f}%"
            else:
                mape_display = "N/A"
            
            relative_errors = np.abs((z_val_actual - z_val_predicted) / (np.abs(z_val_actual) + 1e-10))
            accuracy = np.mean(relative_errors < 0.1) * 100
            
            # 显示验证结果
            result_msg = f"""验证结果 - {method_name}:

训练数据点: {len(training_data)}
验证数据点: {len(validation_data)}
有效预测点: {len(z_val_actual)}

性能指标:
• 平均绝对误差 (MAE): {mae:.4f}
• 均方根误差 (RMSE): {rmse:.4f}
• 决定系数 (R²): {r2_display}
• 平均绝对百分比误差 (MAPE): {mape_display}
• 准确率 (10%误差范围): {accuracy:.1f}%

建议: 如需对比不同插值方法，请点击"对比所有插值法"按钮。"""
            
            QMessageBox.information(self, "验证完成", result_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "验证失败", f"验证失败: {e}")    

    def generate_plot(self):
        """生成等值线图和3D曲面图 - 使用指定边距"""
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return
        
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        z_col = self.z_col_combo.currentText()
        
        if not all([x_col, y_col, z_col]):
            QMessageBox.warning(self, "缺少列", "请为X, Y, Z轴选择有效的列。")
            return

        try:
            # 清除之前的图形
            self.canvas.figure.clear()
            self.surface_canvas.figure.clear()
            
            # 获取等值线图的数据（使用全部数据）
            valid_data_all = self.merged_df.dropna(subset=[x_col, y_col, z_col])
            if valid_data_all.empty:
                QMessageBox.warning(self, "数据不足", "没有有效的数据点。")
                return
            
            x_all = valid_data_all[x_col].values
            y_all = valid_data_all[y_col].values
            z_all = valid_data_all[z_col].values
            
            # 创建网格
            xi = np.linspace(x_all.min(), x_all.max(), 100)
            yi = np.linspace(y_all.min(), y_all.max(), 100)
            XI, YI = np.meshgrid(xi, yi)
            
            # 插值
            method_name = self.interp_method_combo.currentText()
            
            # 将网格点转换为一维数组进行插值
            xi_flat = XI.flatten()
            yi_flat = YI.flatten()
            zi_flat_all = self._perform_interpolation(x_all, y_all, z_all, xi_flat, yi_flat, method_name)
            ZI_all = zi_flat_all.reshape(XI.shape)
            
            # 处理NaN值
            mask = ~np.isnan(ZI_all)
            if not np.any(mask):
                QMessageBox.critical(self, "绘图失败", f"插值方法 '{method_name}' 无法为此数据生成有效结果")
                return
            
            # ========== 1. 绘制等值线图（使用全部数据）==========
            ax = self.canvas.figure.add_subplot(111)
            
            contour = ax.contourf(XI, YI, ZI_all, levels=20, cmap='viridis', alpha=0.8)
            contour_lines = ax.contour(XI, YI, ZI_all, levels=20, colors='black', alpha=0.6, linewidths=0.5)
            
            # 添加数据点
            scatter = ax.scatter(x_all, y_all, c=z_all, cmap='viridis', s=50, edgecolors='black', alpha=0.8)
            
            # 添加颜色条 - 确保中文正确显示
            cbar = self.canvas.figure.colorbar(contour, ax=ax, shrink=0.8)
            cbar.set_label(z_col, fontproperties=self.canvas.chinese_font)
            
            # 设置标签和标题 - 强制使用中文字体
            ax.set_xlabel(x_col, fontproperties=self.canvas.chinese_font)
            ax.set_ylabel(y_col, fontproperties=self.canvas.chinese_font)
            
            # 设置标题 - 强制使用中文字体
            title_text = f'{z_col} 等值线图 ({method_name})'
            ax.set_title(title_text, fontproperties=self.canvas.title_chinese_font)
            
            # 设置网格
            ax.grid(True, alpha=0.3)
            
            # 设置刻度标签字体（数字使用英文字体）
            for tick in ax.get_xticklabels():
                tick.set_fontproperties(self.canvas.english_font)
            for tick in ax.get_yticklabels():
                tick.set_fontproperties(self.canvas.english_font)
            
            # *** 强制使用指定边距，不使用 tight_layout ***
            self.canvas.figure.subplots_adjust(
                left=0.15,    # 左边距
                bottom=0.15,  # 下边距
                right=1.00,   # 右边距
                top=0.85      # 上边距
            )
            
            # 刷新等值线画布
            self.canvas.draw()
            
            # ========== 2. 绘制3D曲面图（根据选择的岩层）==========
            # 获取选择的岩层
            selected_layer = self.layer_select_combo.currentData()
            seam_col = self.seam_col_combo.currentText()
            
            if selected_layer is None or selected_layer == "__all__":
                # 使用全部数据
                valid_data_3d = valid_data_all
                layer_display = "全部岩层"
            elif seam_col and seam_col != "未检测到文本列" and seam_col in self.merged_df.columns:
                # 筛选特定岩层
                valid_data_3d = self.merged_df[self.merged_df[seam_col] == selected_layer].dropna(subset=[x_col, y_col, z_col])
                layer_display = str(selected_layer)
                
                if valid_data_3d.empty:
                    QMessageBox.warning(self, "数据不足", f"岩层 '{selected_layer}' 没有有效的数据点。")
                    return
                
                if len(valid_data_3d) < 4:
                    QMessageBox.warning(self, "数据不足", f"岩层 '{selected_layer}' 的数据点太少（{len(valid_data_3d)}点），至少需要4个点。")
                    return
            else:
                valid_data_3d = valid_data_all
                layer_display = "全部岩层"
            
            # 获取3D曲面的数据
            x_3d = valid_data_3d[x_col].values
            y_3d = valid_data_3d[y_col].values
            z_3d = valid_data_3d[z_col].values
            
            # 为3D曲面创建网格（使用3D数据的范围）
            xi_3d = np.linspace(x_3d.min(), x_3d.max(), 100)
            yi_3d = np.linspace(y_3d.min(), y_3d.max(), 100)
            XI_3d, YI_3d = np.meshgrid(xi_3d, yi_3d)
            
            # 3D曲面插值
            xi_flat_3d = XI_3d.flatten()
            yi_flat_3d = YI_3d.flatten()
            zi_flat_3d = self._perform_interpolation(x_3d, y_3d, z_3d, xi_flat_3d, yi_flat_3d, method_name)
            ZI_3d = zi_flat_3d.reshape(XI_3d.shape)
            
            # 检查3D插值结果
            if np.all(np.isnan(ZI_3d)):
                QMessageBox.critical(self, "绘图失败", f"无法为岩层 '{layer_display}' 生成3D曲面")
                return
            
            ax3d = self.surface_canvas.figure.add_subplot(111, projection='3d')
            
            # 绘制3D曲面 - 使用彩虹配色（jet: 蓝-青-绿-黄-红，类似参考图）
            surf = ax3d.plot_surface(XI_3d, YI_3d, ZI_3d, cmap='jet', 
                                     edgecolor='none', 
                                     alpha=0.95,
                                     antialiased=True,
                                     shade=True,
                                     rstride=1, cstride=1,
                                     vmin=np.nanmin(ZI_3d), 
                                     vmax=np.nanmax(ZI_3d))
            
            # 移除网格线
            ax3d.grid(False)
            
            # 移除背景面板
            ax3d.xaxis.pane.fill = False
            ax3d.yaxis.pane.fill = False
            ax3d.zaxis.pane.fill = False
            
            # 设置面板边框为透明或浅色
            ax3d.xaxis.pane.set_edgecolor('lightgray')
            ax3d.yaxis.pane.set_edgecolor('lightgray')
            ax3d.zaxis.pane.set_edgecolor('lightgray')
            ax3d.xaxis.pane.set_alpha(0.1)
            ax3d.yaxis.pane.set_alpha(0.1)
            ax3d.zaxis.pane.set_alpha(0.1)
            
            # 不显示等高线投影
            # (已移除底部等高线代码)
            
            # 不显示原始数据点
            # (已移除散点图代码)
            
            # 添加颜色条 - 调整位置和大小
            cbar3d = self.surface_canvas.figure.colorbar(surf, ax=ax3d, shrink=0.5, aspect=15, pad=0.1)
            cbar3d.set_label(z_col, fontproperties=self.surface_canvas.chinese_font, fontsize=10)
            
            # 设置标签 - 使用中文字体
            ax3d.set_xlabel(x_col, fontproperties=self.surface_canvas.chinese_font, labelpad=8, fontsize=11)
            ax3d.set_ylabel(y_col, fontproperties=self.surface_canvas.chinese_font, labelpad=8, fontsize=11)
            ax3d.set_zlabel(z_col, fontproperties=self.surface_canvas.chinese_font, labelpad=8, fontsize=11)
            
            # 设置标题 - 显示岩层名称
            title_3d = f'{layer_display} - {z_col} 三维曲面图 ({method_name})'
            ax3d.set_title(title_3d, fontproperties=self.surface_canvas.title_chinese_font, pad=15, fontsize=13)
            
            # 设置视角 - 参考图的视角（俯视角度更大）
            ax3d.view_init(elev=45, azim=235)
            
            # 设置刻度字体 - 调整字体大小
            for tick in ax3d.get_xticklabels():
                tick.set_fontproperties(self.surface_canvas.english_font)
                tick.set_fontsize(9)
            for tick in ax3d.get_yticklabels():
                tick.set_fontproperties(self.surface_canvas.english_font)
                tick.set_fontsize(9)
            for tick in ax3d.get_zticklabels():
                tick.set_fontproperties(self.surface_canvas.english_font)
                tick.set_fontsize(9)
            
            # 设置Z轴范围
            z_range_3d = np.nanmax(ZI_3d) - np.nanmin(ZI_3d)
            ax3d.set_zlim(np.nanmin(ZI_3d) - 0.05 * z_range_3d, np.nanmax(ZI_3d) + 0.05 * z_range_3d)
            
            # 设置背景色为白色
            ax3d.set_facecolor('white')
            self.surface_canvas.figure.patch.set_facecolor('white')
            
            # 优化3D图形布局 - 调整边距使图形更宽
            self.surface_canvas.figure.subplots_adjust(
                left=0.02,
                bottom=0.02,
                right=0.98,
                top=0.95
            )
            
            # 刷新3D曲面画布
            self.surface_canvas.draw()
            
            # 切换到3D曲面标签页以显示新生成的图
            self.results_tabs.setCurrentWidget(self.surface_tab)
            
            QMessageBox.information(self, "生成成功", 
                                  f"等值线图和3D曲面图生成完成\n\n"
                                  f"插值方法: {method_name}\n"
                                  f"3D曲面岩层: {layer_display}\n"
                                  f"数据点数: {len(valid_data_3d)}\n\n"
                                  f"可在标签页间切换查看不同视图。")
            
        except Exception as e:
            QMessageBox.critical(self, "绘图失败", f"生成图形失败: {e}\n\n{traceback.format_exc()}")

    def generate_surface_plots(self):
        """生成所有煤层的三维曲面图"""
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return

        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        z_col = self.z_col_combo.currentText()
        seam_col = self.seam_col_combo.currentText()

        if not all([x_col, y_col, z_col]) or seam_col in ("", "未检测到文本列"):
            QMessageBox.warning(self, "缺少列", "请先选择有效的X、Y、Z列以及煤层列。")
            return

        if seam_col not in self.merged_df.columns:
            QMessageBox.warning(self, "列缺失", f"数据中不存在名为 '{seam_col}' 的煤层列。")
            return

        required_cols = [x_col, y_col, z_col, seam_col]
        valid_data = self.merged_df.dropna(subset=required_cols)
        if len(valid_data) < 12:
            QMessageBox.warning(self, "数据不足", "生成三维曲面至少需要12个完整的数据点。")
            return

        method_name = self.interp_method_combo.currentText()
        spacing_col = self.layer_spacing_combo.currentData()
        if spacing_col and spacing_col not in self.merged_df.columns:
            spacing_col = None

        # 构建统一网格
        x_values = valid_data[x_col].astype(float)
        y_values = valid_data[y_col].astype(float)
        xi = np.linspace(x_values.min(), x_values.max(), 80)
        yi = np.linspace(y_values.min(), y_values.max(), 80)
        XI, YI = np.meshgrid(xi, yi)
        xi_flat = XI.flatten()
        yi_flat = YI.flatten()

        surfaces = []
        skipped_seams = []
        for seam_value, group in valid_data.groupby(seam_col):
            group_numeric = group.dropna(subset=[x_col, y_col, z_col])
            if len(group_numeric) < 4:
                skipped_seams.append(f"{seam_value} (有效点 {len(group_numeric)})")
                continue

            x_points = group_numeric[x_col].astype(float).values
            y_points = group_numeric[y_col].astype(float).values
            z_points = group_numeric[z_col].astype(float).values

            try:
                zi_flat = self._perform_interpolation(x_points, y_points, z_points, xi_flat, yi_flat, method_name)
            except Exception as interp_err:
                skipped_seams.append(f"{seam_value} (插值失败: {interp_err}")
                continue

            if zi_flat is None:
                skipped_seams.append(f"{seam_value} (插值无结果)")
                continue

            ZI = zi_flat.reshape(XI.shape)
            if np.all(np.isnan(ZI)):
                skipped_seams.append(f"{seam_value} (插值仅返回NaN)")
                continue

            thickness_matrix = np.nan_to_num(ZI, nan=0.0, posinf=0.0, neginf=0.0)
            thickness_matrix = np.clip(thickness_matrix, 0.0, None)

            layer_metric = None
            if spacing_col:
                spacing_values = pd.to_numeric(group_numeric[spacing_col], errors='coerce').dropna()
                if not spacing_values.empty:
                    layer_metric = float(spacing_values.mean())

            z_values_clean = np.clip(pd.to_numeric(group_numeric[z_col], errors='coerce').dropna(), 0.0, None)
            mean_thickness = float(z_values_clean.mean()) if not z_values_clean.empty else float(np.mean(thickness_matrix))
            if not np.isfinite(mean_thickness):
                mean_thickness = 0.0
            if layer_metric is None or not np.isfinite(layer_metric):
                layer_metric = mean_thickness

            surfaces.append({
                'name': str(seam_value),
                'points': len(group_numeric),
                'thickness': thickness_matrix,
                'metric': float(layer_metric),
                'mean_thickness': mean_thickness
            })

        if not surfaces:
            QMessageBox.warning(self, "无可绘制煤层", "无法生成三维曲面，请检查煤层数据是否完整。")
            return

        # 根据层间距或均匀间距排列煤层
        surfaces.sort(key=lambda item: item['metric'])
        default_gap = np.nanstd(valid_data[z_col].astype(float))
        if not np.isfinite(default_gap) or default_gap <= 0:
            default_gap = np.nanmax(valid_data[z_col].astype(float)) - np.nanmin(valid_data[z_col].astype(float))
        if not np.isfinite(default_gap) or default_gap <= 0:
            default_gap = 10.0

        offsets = []
        prev_metric = None
        for surface in surfaces:
            metric = surface['metric']
            if not np.isfinite(metric):
                metric = surface['mean_thickness'] if np.isfinite(surface['mean_thickness']) else 0.0
            if prev_metric is None:
                offsets.append(0.0)
            else:
                delta = metric - prev_metric
                if not np.isfinite(delta) or abs(delta) < 1e-3:
                    delta = default_gap
                offsets.append(offsets[-1] + delta)
            prev_metric = metric

        # 绘制3D曲面
        fig = self.surface_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111, projection='3d')

        color_manager = getattr(self.main_win, "color_manager", None)
        fallback_cmap = plt.get_cmap('tab20')
        fallback_palette = list(getattr(fallback_cmap, "colors", []))
        if not fallback_palette:
            palette_size = getattr(fallback_cmap, "N", 0) or 8
            fallback_palette = [fallback_cmap(i / max(palette_size - 1, 1)) for i in range(palette_size)]
        fallback_color_map = {}
        legend_handles = []

        def resolve_layer_color(layer_name: str):
            name_str = str(layer_name)
            if color_manager is not None:
                qcolor = color_manager.color_for(name_str)
                return mcolors.to_rgba(qcolor.name())

            key = self._normalize_layer_key(name_str)
            if key not in fallback_color_map:
                idx = len(fallback_color_map) % len(fallback_palette)
                fallback_color_map[key] = fallback_palette[idx]
            return fallback_color_map[key]

        def _build_side(x_line, y_line, z_top_line, base_z):
            verts_top = list(zip(x_line.astype(float), y_line.astype(float), z_top_line.astype(float)))
            verts_base = list(zip(x_line[::-1].astype(float), y_line[::-1].astype(float), np.full_like(z_top_line, base_z, dtype=float)))
            return verts_top + verts_base

        def _plot_coal_block(ax_obj, XI_grid, YI_grid, thickness_grid, base_z, face_color):
            thickness_grid = np.array(thickness_grid, dtype=float)
            thickness_grid = np.nan_to_num(thickness_grid, nan=0.0, posinf=0.0, neginf=0.0)
            thickness_grid = np.clip(thickness_grid, 0.0, None)
            top_surface = base_z + thickness_grid
            base_surface = np.full_like(top_surface, base_z)

            ax_obj.plot_surface(XI_grid, YI_grid, top_surface, color=face_color, linewidth=0, antialiased=True, alpha=0.92, shade=True)
            ax_obj.plot_surface(XI_grid, YI_grid, base_surface, color=face_color, linewidth=0, antialiased=True, alpha=0.25, shade=False)

            side_polys = [
                _build_side(XI_grid[0], YI_grid[0], top_surface[0], base_z),
                _build_side(XI_grid[-1], YI_grid[-1], top_surface[-1], base_z),
                _build_side(XI_grid[:, 0], YI_grid[:, 0], top_surface[:, 0], base_z),
                _build_side(XI_grid[:, -1], YI_grid[:, -1], top_surface[:, -1], base_z),
            ]
            side_collection = Poly3DCollection(side_polys, facecolors=face_color, alpha=0.55, linewidths=0)
            ax_obj.add_collection3d(side_collection)

            # 勾勒上表面边缘
            ax_obj.plot(XI_grid[0], YI_grid[0], top_surface[0], color='k', linewidth=0.6, alpha=0.6)
            ax_obj.plot(XI_grid[-1], YI_grid[-1], top_surface[-1], color='k', linewidth=0.6, alpha=0.6)
            ax_obj.plot(XI_grid[:, 0], YI_grid[:, 0], top_surface[:, 0], color='k', linewidth=0.6, alpha=0.6)
            ax_obj.plot(XI_grid[:, -1], YI_grid[:, -1], top_surface[:, -1], color='k', linewidth=0.6, alpha=0.6)

            return float(np.max(top_surface))

        max_top = 0.0
        for surface, offset in zip(surfaces, offsets):
            face_color = resolve_layer_color(surface['name'])
            max_top = max(max_top, _plot_coal_block(ax, XI, YI, surface['thickness'], offset, face_color))
            avg_thickness = surface['mean_thickness'] if np.isfinite(surface['mean_thickness']) else 0.0
            legend_label = f"{surface['name']} (点{surface['points']}, 平均厚{avg_thickness:.2f})"
            legend_handles.append(mpatches.Patch(color=face_color, label=legend_label))

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        if spacing_col:
            ax.set_zlabel(f"{spacing_col} / 层序")
        else:
            ax.set_zlabel(f"{z_col} (厚度叠置)")
        ax.set_title("煤层三维块体叠置图")
        ax.view_init(elev=28, azim=-120)
        ax.grid(True, which='both', linestyle=':', alpha=0.3)

        z_min = min(offsets) if offsets else 0.0
        z_max = max_top if np.isfinite(max_top) else 1.0
        if z_max <= z_min:
            z_max = z_min + 1.0
        ax.set_zlim(z_min, z_max * 1.05)
        ax.set_box_aspect((np.ptp(xi) if np.ptp(xi) > 0 else 1,
                           np.ptp(yi) if np.ptp(yi) > 0 else 1,
                           (z_max - z_min) if (z_max - z_min) > 0 else 1))

        if legend_handles:
            legend = ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.02, 1.0))
            if legend:
                for text in legend.get_texts():
                    if self.surface_canvas._contains_chinese(text.get_text()):
                        text.set_fontproperties(self.surface_canvas.chinese_font)
                    else:
                        text.set_fontproperties(self.surface_canvas.english_font)

        self.surface_canvas.apply_mixed_fonts(ax)
        self.surface_canvas.draw()
        self.results_tabs.setCurrentWidget(self.surface_tab)

        info_lines = [f"✅ 成功生成 {len(surfaces)} 个煤层块体模型"]
        if spacing_col:
            info_lines.append(f"• 层间距依据列: {spacing_col}")
        else:
            info_lines.append("• 层间距采用自动均匀排列")
        info_lines.append("• 每个块体底面保持平整，顶部厚度由插值结果决定")
        info_lines.append("• 推荐使用鼠标右键拖拽调整视角，滚轮缩放")
        if skipped_seams:
            info_lines.append("\n以下煤层未能绘制:")
            info_lines.extend([f"  - {reason}" for reason in skipped_seams[:6]])
            if len(skipped_seams) > 6:
                info_lines.append(f"  ... 另有 {len(skipped_seams) - 6} 条被跳过")

        QMessageBox.information(self, "三维曲面生成完成", "\n".join(info_lines))

    def export_plot(self):
        """导出图像 - 同时导出等值线图和3D曲面图"""
        has_contour = bool(self.canvas.figure.get_axes())
        has_surface = bool(self.surface_canvas.figure.get_axes())
        
        if not has_contour and not has_surface:
            QMessageBox.warning(self, "无图表", "请先生成图表再导出。")
            return
        
        output_dir = os.path.join(os.getcwd(), "output", "plots")
        os.makedirs(output_dir, exist_ok=True)
        method_name = self.interp_method_combo.currentText().replace(" ", "_").replace("(", "").replace(")", "")
        
        # 创建导出对话框让用户选择导出哪些图
        export_dialog = QDialog(self)
        export_dialog.setWindowTitle("选择导出选项")
        export_dialog.setModal(True)
        
        layout = QVBoxLayout(export_dialog)
        layout.addWidget(QLabel("请选择要导出的图表："))
        
        contour_check = QCheckBox("等值线图")
        contour_check.setChecked(has_contour)
        contour_check.setEnabled(has_contour)
        
        surface_check = QCheckBox("3D曲面图")
        surface_check.setChecked(has_surface)
        surface_check.setEnabled(has_surface)
        
        layout.addWidget(contour_check)
        layout.addWidget(surface_check)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(export_dialog.accept)
        button_box.rejected.connect(export_dialog.reject)
        layout.addWidget(button_box)
        
        if export_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        export_contour = contour_check.isChecked()
        export_surface = surface_check.isChecked()
        
        if not export_contour and not export_surface:
            QMessageBox.warning(self, "未选择", "请至少选择一个图表导出。")
            return
        
        # 选择保存目录和格式
        save_path, file_filter = QFileDialog.getSaveFileName(
            self, "保存图像", 
            os.path.join(output_dir, f"等值线图_{method_name}.png"), 
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)")
        
        if save_path:
            try:
                # 获取文件扩展名
                file_ext = os.path.splitext(save_path)[1]
                base_path = os.path.splitext(save_path)[0]
                
                # 设置输出参数，确保字体正确嵌入
                save_kwargs = {
                    'dpi': 300,
                    'bbox_inches': 'tight',
                    'facecolor': 'white',
                    'edgecolor': 'none'
                }
                
                # 对于PDF和SVG格式，确保字体正确嵌入
                if file_ext.lower() == '.pdf':
                    save_kwargs['format'] = 'pdf'
                    # 设置PDF字体嵌入
                    import matplotlib
                    matplotlib.rcParams['pdf.fonttype'] = 42  # TrueType字体
                elif file_ext.lower() == '.svg':
                    save_kwargs['format'] = 'svg'
                
                saved_files = []
                
                # 导出等值线图
                if export_contour:
                    contour_path = f"{base_path}_等值线{file_ext}"
                    for ax in self.canvas.figure.get_axes():
                        self.canvas.apply_mixed_fonts(ax)
                    self.canvas.figure.savefig(contour_path, **save_kwargs)
                    saved_files.append(contour_path)
                
                # 导出3D曲面图
                if export_surface:
                    surface_path = f"{base_path}_3D曲面{file_ext}"
                    for ax in self.surface_canvas.figure.get_axes():
                        self.surface_canvas.apply_mixed_fonts(ax)
                    self.surface_canvas.figure.savefig(surface_path, **save_kwargs)
                    saved_files.append(surface_path)
                
                files_info = "\n".join(saved_files)
                QMessageBox.information(
                    self, "导出成功", 
                    f"图像已保存到:\n{files_info}\n\n字体设置: 中文-宋体，数字英文-Times New Roman")
                
                if QMessageBox.question(self, "打开文件夹", "是否要打开保存文件夹？") == QMessageBox.StandardButton.Yes:
                    open_file_auto(output_dir)
                    
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"保存图像时发生错误: {e}\n\n{traceback.format_exc()}")

    def export_comparison_results(self):
        """导出对比结果到Excel - 添加最佳方法总结"""
        if not self.comparison_results:
            QMessageBox.warning(self, "无数据", "没有对比结果可导出，请先运行插值法对比")
            return
        
        output_dir = os.path.join(os.getcwd(), "output", "plots")
        os.makedirs(output_dir, exist_ok=True)
        save_path, _ = QFileDialog.getSaveFileName(self, "保存对比结果", 
                                                os.path.join(output_dir, "插值方法对比结果.xlsx"), 
                                                "Excel (*.xlsx);;CSV (*.csv)")
        
        if save_path:
            try:
                # 获取最佳方法
                best_method = self.comparison_results[0]
                
                if save_path.endswith('.xlsx'):
                    # 创建Excel文件，包含多个工作表
                    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                        # 添加执行总结工作表
                        summary_info = {
                            '项目': ['最佳插值方法', '决定系数(R²)', '平均绝对误差(MAE)', 
                                '均方根误差(RMSE)', '平均绝对百分比误差(MAPE)', 
                                '准确率(10%误差内)', '对比方法总数', '数据点总数'],
                            '结果': [
                                best_method['method_name'],
                                f"{best_method['r2']:.4f}",
                                f"{best_method['mae']:.4f}",
                                f"{best_method['rmse']:.4f}",
                                f"{best_method['mape']:.2f}%" if best_method['mape'] != float('inf') else 'N/A',
                                f"{best_method['accuracy_10']:.1f}%",
                                len(self.comparison_results),
                                best_method['n_valid_predictions']
                            ]
                        }
                        summary_df = pd.DataFrame(summary_info)
                        summary_df.to_excel(writer, sheet_name='插值最佳方法总结', index=False)
                        
                        # 导出汇总对比结果
                        comparison_df = pd.DataFrame([
                            {
                                '排名': i + 1,
                                '插值方法': result['method_name'],
                                '是否最佳': '✓' if i == 0 else '',
                                'MAE': round(result['mae'], 4),
                                'RMSE': round(result['rmse'], 4),
                                'R²': round(result['r2'], 4),
                                'MAPE(%)': round(result['mape'], 2) if result['mape'] != float('inf') else 'N/A',
                                '准确率(10%)': round(result['accuracy_10'], 1),
                                '有效预测点数': result['n_valid_predictions']
                            }
                            for i, result in enumerate(self.comparison_results)
                        ])
                        comparison_df.to_excel(writer, sheet_name='插值方法对比汇总', index=False)
                        
                        # 导出详细对比数据
                        if self.detailed_comparison_data:
                            detail_df = pd.DataFrame(self.detailed_comparison_data)
                            # 添加最佳方法标记
                            detail_df['是否最佳方法'] = detail_df['插值方法'].apply(
                                lambda x: '是' if x == best_method['method_name'] else '否')
                            # 添加误差评级
                            if '相对误差(%)' in detail_df.columns:
                                detail_df['误差评级'] = detail_df['相对误差(%)'].apply(
                                    lambda x: self._classify_error(float(x)))
                            detail_df.to_excel(writer, sheet_name='预测值vs实际值详细对比', index=False)
                        
                        QMessageBox.information(self, "导出成功", 
                                            f"对比结果已保存到:\n{save_path}\n\n包含以下工作表:\n• 插值最佳方法总结\n• 插值方法对比汇总\n• 预测值vs实际值详细对比")
                else:
                    # 导出为CSV（仅汇总结果）
                    summary_df = pd.DataFrame([
                        {
                            '排名': i + 1,
                            '插值方法': result['method_name'],
                            '是否最佳': '✓' if i == 0 else '',
                            'MAE': round(result['mae'], 4),
                            'RMSE': round(result['rmse'], 4),
                            'R²': round(result['r2'], 4),
                            'MAPE(%)': round(result['mape'], 2) if result['mape'] != float('inf') else 'N/A',
                            '准确率(10%)': round(result['accuracy_10'], 1)
                        }
                        for i, result in enumerate(self.comparison_results)
                    ])
                    summary_df.to_csv(save_path, index=False, encoding='utf-8-sig')
                    QMessageBox.information(self, "导出成功", f"对比结果汇总已保存到:\n{save_path}")
                
                if QMessageBox.question(self, "打开文件", "是否要打开保存的文件？") == QMessageBox.StandardButton.Yes:
                    open_file_auto(save_path)
                    
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出失败: {e}")
    
class SummaryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("建模摘要")
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.resize(420, 560)
        self.setMinimumSize(360, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet(
            "QTextBrowser {"
            "background-color: #ffffff;"
            "border: 1px solid #cbd5f5;"
            "border-radius: 8px;"
            "padding: 12px;"
            "color: #1e293b;"
            "font-size: 12px;"
            "line-height: 1.6;"
            "}"
        )
        layout.addWidget(self.text_browser, 1)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(10)

        self.pin_checkbox = QCheckBox("置顶显示", self)
        self.pin_checkbox.setStyleSheet("color: #475569; font-size: 12px;")
        self.pin_checkbox.toggled.connect(self._toggle_on_top)
        controls.addWidget(self.pin_checkbox, 0, Qt.AlignmentFlag.AlignLeft)

        controls.addStretch(1)

        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(30)
        close_btn.setStyleSheet(
            "QPushButton {"
            "background-color: #6366f1;"
            "color: white;"
            "border: none;"
            "border-radius: 6px;"
            "padding: 6px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover { background-color: #4f46e5; }"
            "QPushButton:pressed { background-color: #4338ca; }"
        )
        close_btn.clicked.connect(self.close)
        controls.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(controls)

        self._default_html = "<p style='margin:0;'>提示：生成煤层块体后将在此显示详细的建模摘要。</p>"
        self.update_summary(self._default_html, auto_show=False)

    def update_summary(self, html: str, auto_show: bool = False):
        if not html:
            html = self._default_html
        self.text_browser.setHtml(html)
        if auto_show:
            self.show()
            self.raise_()
            self.activateWindow()

    def clear_summary(self):
        self.text_browser.clear()
        self.text_browser.setHtml(self._default_html)

    def _toggle_on_top(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.raise_()


class GeologicalModelingHomePage(QWidget):
    def __init__(self, main_win=None, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        title = QLabel("地质建模 - 首页总览")
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title)

        subtitle = QLabel(
            "集中展示数据准备规范、建模步骤与成果形态，帮助您快速进入煤层块体建模与等值线分析流程。"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #475569; font-size: 14px; line-height: 1.6;")
        header_layout.addWidget(subtitle)

        layout.addWidget(header, 0)

        step_card = QFrame()
        step_card.setObjectName("modelStepCard")
        step_card.setStyleSheet(
            "QFrame#modelStepCard {"
            "background: #eef2ff;"
            "border: 1px solid #c7d2fe;"
            "border-radius: 18px;"
            "}"
            "QFrame#modelStepCard QLabel {"
            "color: #1f2937;"
            "font-size: 13px;"
            "line-height: 1.7;"
            "}"
        )
        step_layout = QVBoxLayout(step_card)
        step_layout.setContentsMargins(22, 18, 22, 18)
        step_layout.setSpacing(8)

        step_title = QLabel("建模流程速览")
        step_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #312e81;")
        step_layout.addWidget(step_title)

        steps_html = (
            "<ul style='margin:4px 0 0 14px; padding:0; color:#1f2937;'>"
            "<li>准备坐标文件（如 <code>data/input/zuobiao.csv</code>），字段需包含“钻孔名”“坐标x”“坐标y”。</li>"
            "<li>为每个钻孔整理独立的CSV文件（示例 <code>data/input/测试钻孔/BK-1.csv</code>），建议包含厚度、弹性模量、容重等关键力学指标。</li>"
            "<li>在“煤层块体建模”中加载坐标文件与钻孔样本，选择目标煤层与插值算法生成三维块体。</li>"
            "<li>切换至“等值线图与插值分析”快速评估不同方法的预测精度，并输出曲面成果。</li>"
            "</ul>"
        )
        step_desc = QLabel()
        step_desc.setWordWrap(True)
        step_desc.setTextFormat(Qt.TextFormat.RichText)
        step_desc.setText(steps_html)
        step_layout.addWidget(step_desc)

        layout.addWidget(step_card)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(18)

        left_column = QVBoxLayout()
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(16)

        coord_headers = ["钻孔名", "坐标x", "坐标y"]
        coord_rows = [
            ("BK-1", "523656.20", "4371034.33"),
            ("BK-2", "523484.16", "4371392.21"),
            ("BK-3", "525091.64", "4371062.91"),
            ("BK-4", "523975.24", "4371159.01"),
            ("BK-5", "524311.42", "4371281.15"),
            ("BK-7", "523130.55", "4371061.01"),
        ]
        coord_card = self._build_table_card(
            title="坐标文件标准格式",
            subtitle="统一的坐标表可确保钻孔空间位置正确匹配，推荐使用米制平面坐标。",
            headers=coord_headers,
            rows=coord_rows,
            button_text="打开示例坐标文件",
            relative_path=os.path.join("data", "input", "zuobiao.csv"),
        )
        left_column.addWidget(coord_card)

        borehole_headers = [
            "序号(从下到上)",
            "岩层名称",
            "厚度/m",
            "弹性模量/GPa",
            "容重/kN·m-3",
            "抗拉强度/MPa",
            "备注/附加信息",
        ]
        borehole_rows = [
            ("10", "黄土", "91.57", "0.54", "1800", "0.00", ""),
            ("9", "粗粒砂岩", "12.17", "11.49", "2780", "3.08", ""),
            ("8", "黄土·断层", "9.52", "0.54", "1800", "0.00", "断层夹层"),
            ("7", "砂质泥岩", "8.70", "7.17", "2680", "1.32", ""),
            ("6", "细粒砂岩", "5.21", "9.54", "2830", "2.05", ""),
            ("5", "中粒砂岩", "13.37", "20.00", "2570", "2.72", ""),
        ]
        borehole_card = self._build_table_card(
            title="钻孔文件标准格式",
            subtitle="每个钻孔对应一个CSV文件，自下而上罗列岩层并提供力学参数，备注列可用于记录特殊情况。",
            headers=borehole_headers,
            rows=borehole_rows,
            button_text="打开示例钻孔文件",
            relative_path=os.path.join("data", "input", "测试钻孔", "BK-1.csv"),
        )
        left_column.addWidget(borehole_card)
        left_column.addStretch(1)

        content.addLayout(left_column, 1)

        image_card = self._build_image_card()
        content.addWidget(image_card, 1)

        layout.addLayout(content, 1)

        tips_card = QFrame()
        tips_card.setObjectName("modelTipsCard")
        tips_card.setStyleSheet(
            "QFrame#modelTipsCard {"
            "background: #f8fafc;"
            "border: 1px dashed #cbd5f5;"
            "border-radius: 16px;"
            "}"
            "QFrame#modelTipsCard QLabel {"
            "color: #475569;"
            "font-size: 12px;"
            "line-height: 1.6;"
            "}"
        )
        tips_layout = QVBoxLayout(tips_card)
        tips_layout.setContentsMargins(18, 14, 18, 14)
        tips_layout.setSpacing(6)

        tips_label = QLabel(
            "温馨提示：坐标文件需与钻孔文件中的“钻孔名”一致；若存在多煤层，请在“煤层块体建模”步骤中选定目标煤层并合理设置插值步长。"
        )
        tips_label.setWordWrap(True)
        tips_layout.addWidget(tips_label)

        layout.addWidget(tips_card, 0)

    def _build_table_card(
        self,
        *,
        title: str,
        subtitle: str,
        headers: List[str],
        rows: List[Tuple[str, ...]],
        button_text: str,
        relative_path: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("modelTableCard")
        card.setStyleSheet(
            "QFrame#modelTableCard {"
            "background: #ffffff;"
            "border: 1px solid #e2e8f0;"
            "border-radius: 18px;"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #0f172a;")
        card_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("color: #475569; font-size: 12px; line-height: 1.6;")
        card_layout.addWidget(subtitle_label)

        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for row_idx, row_values in enumerate(rows):
            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setForeground(QColor("#0f172a"))
                table.setItem(row_idx, col_idx, item)

        table.setMaximumHeight(220)
        card_layout.addWidget(table)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)

        path_label = QLabel(f"示例路径：{relative_path.replace(os.sep, '/')}")
        path_label.setStyleSheet("color: #64748b; font-size: 11px;")
        footer_layout.addWidget(path_label, 1)

        open_btn = QPushButton(button_text)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setStyleSheet(
            "QPushButton {"
            "background: #6366f1;"
            "color: white;"
            "border: none;"
            "border-radius: 6px;"
            "padding: 6px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover { background: #4f46e5; }"
            "QPushButton:pressed { background: #4338ca; }"
        )
        open_btn.clicked.connect(partial(self._open_file, relative_path))
        footer_layout.addWidget(open_btn, 0, Qt.AlignmentFlag.AlignRight)

        card_layout.addLayout(footer_layout)

        return card

    def _build_image_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("modelImageCard")
        card.setStyleSheet(
            "QFrame#modelImageCard {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #1f2937);"
            "border-radius: 20px;"
            "border: 1px solid rgba(148, 163, 184, 0.35);"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        caption = QLabel("煤层建模成果示意")
        caption.setStyleSheet("color: #e2e8f0; font-size: 15px; font-weight: 600;")
        card_layout.addWidget(caption, 0, Qt.AlignmentFlag.AlignLeft)

        image_label = QLabel()
        image_label.setMinimumHeight(280)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet(
            "QLabel {"
            "background: rgba(15, 23, 42, 0.4);"
            "border-radius: 14px;"
            "color: #cbd5f5;"
            "font-size: 13px;"
            "}"
        )

        image_path_candidates = [
            os.path.join("icons", "Gemini_Generated_Image_3yuo953yuo953yuo.png"),
            os.path.join("icons", "geology_shield.png"),
        ]
        pixmap = QPixmap()
        for candidate in image_path_candidates:
            abs_path = resource_path(candidate)
            pixmap = QPixmap(abs_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(520, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                break
        if pixmap.isNull():
            image_label.setText("未找到示意图资源，请检查 icons/ 目录。")
        else:
            image_label.setPixmap(pixmap)
        card_layout.addWidget(image_label, 1)

        caption2 = QLabel(
            "图示：整合坐标点与钻孔参数后生成的三维煤层块体，可进一步导出等值面与厚度分布。"
        )
        caption2.setWordWrap(True)
        caption2.setStyleSheet("color: #cbd5f5; font-size: 12px; line-height: 1.6;")
        card_layout.addWidget(caption2)

        return card

    def _open_file(self, relative_path: str):
        abs_path = resource_path(relative_path)
        if not os.path.exists(abs_path):
            QMessageBox.warning(self, "文件未找到", f"示例文件不存在，请检查路径：\n{abs_path}")
            return
        open_file_auto(abs_path)


class CoalSeamBlockTab(QWidget):
    """基于插值的煤层厚度块体建模功能"""
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        self.borehole_files = []
        self.coords_file = None
        self.merged_df = None
        self.base_seam_column = None
        self.interpolation_methods = self._get_available_methods()
        self.vertical_scale = 1.0
        self.preview_quality_map = {
            "高精度": 1,
            "标准": 2,
            "流畅": 4,
        }
        self.preview_stride = self.preview_quality_map["标准"]
        self.seam_summary_lines = []
        self.last_plot_payload = None
        self.current_method_label = ""
        self.seam_column = None
        self.comparison_results = []
        self.comparison_details = []
        self._scroll_cid = None
        self.preview_filter_mode = "all"
        self.preview_custom_layers = []
        self.available_display_layers = []
        self.current_display_models = []
        self.current_focus_layers = set()
        self._layer_filter_prev_index = 0
        self.layer_filter_combo = None
        self.layer_filter_button = None
        self.layer_filter_status_label = None
        self.summary_window = SummaryWindow(self)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        control_panel = QFrame()
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #fafbfc;
                border-right: 1px solid #e5e7eb;
            }
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(control_panel)

        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(18, 22, 18, 22)
        control_layout.setSpacing(14)

        file_group = QGroupBox("数据文件加载")
        file_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(8)

        data_layout = QHBoxLayout()
        data_layout.setSpacing(8)
        self.select_data_btn = ModernButton("钻孔数据", color="#2563eb")
        self.select_data_btn.setMaximumHeight(34)
        self.select_data_btn.clicked.connect(self.select_borehole_files)
        self.data_file_label = QLabel("未选择")
        self.data_file_label.setWordWrap(True)
        self.data_file_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        data_layout.addWidget(self.select_data_btn, 0)
        data_layout.addWidget(self.data_file_label, 1)

        coord_layout = QHBoxLayout()
        coord_layout.setSpacing(8)
        self.select_coord_btn = ModernButton("坐标数据", color="#2563eb")
        self.select_coord_btn.setMaximumHeight(34)
        self.select_coord_btn.clicked.connect(self.select_coordinate_file)
        self.coord_file_label = QLabel("未选择")
        self.coord_file_label.setWordWrap(True)
        self.coord_file_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        coord_layout.addWidget(self.select_coord_btn, 0)
        coord_layout.addWidget(self.coord_file_label, 1)

        file_layout.addLayout(data_layout)
        file_layout.addLayout(coord_layout)
        control_layout.addWidget(file_group)

        column_group = QGroupBox("列选择")
        column_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        column_layout = QFormLayout(column_group)
        column_layout.setVerticalSpacing(6)

        combo_style = """
            QComboBox {
                border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px;
                background-color: #ffffff; color: #374151; font-size: 13px;
                min-height: 18px; max-height: 26px;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox:focus { border-color: #2563eb; outline: none; }
        """

        self.x_col_combo = QComboBox(); self.x_col_combo.setStyleSheet(combo_style)
        self.y_col_combo = QComboBox(); self.y_col_combo.setStyleSheet(combo_style)
        self.thickness_col_combo = QComboBox(); self.thickness_col_combo.setStyleSheet(combo_style)
        self.seam_detect_label = QLabel("自动识别: 未检测")
        self.seam_detect_label.setStyleSheet("color: #475569; font-size: 12px;")

        column_layout.addRow("X坐标:", self.x_col_combo)
        column_layout.addRow("Y坐标:", self.y_col_combo)
        column_layout.addRow("厚度列:", self.thickness_col_combo)
        column_layout.addRow("煤层列:", self.seam_detect_label)
        control_layout.addWidget(column_group)

        seam_group = QGroupBox("岩层选择")
        seam_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        seam_layout = QVBoxLayout(seam_group)
        seam_layout.setSpacing(8)

        self.seam_list = QListWidget()
        self.seam_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.seam_list.setStyleSheet("QListWidget { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 6px; }")

        seam_btn_layout = QHBoxLayout()
        self.select_all_btn = ModernButton("全选", color="#14b8a6")
        self.select_all_btn.setMaximumHeight(34)
        self.select_all_btn.clicked.connect(self.select_all_seams)
        self.clear_select_btn = ModernButton("清空", color="#f97316")
        self.clear_select_btn.setMaximumHeight(34)
        self.clear_select_btn.clicked.connect(self.clear_seam_selection)
        seam_btn_layout.addWidget(self.select_all_btn)
        seam_btn_layout.addWidget(self.clear_select_btn)

        self.seam_summary_label = QLabel("请先加载数据")
        self.seam_summary_label.setWordWrap(True)
        self.seam_summary_label.setStyleSheet("color: #475569; font-size: 12px;")

        seam_layout.addWidget(self.seam_list)
        seam_layout.addLayout(seam_btn_layout)
        seam_layout.addWidget(self.seam_summary_label)
        control_layout.addWidget(seam_group)

        param_group = QGroupBox("建模参数")
        param_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        param_layout = QFormLayout(param_group)
        param_layout.setVerticalSpacing(6)

        self.method_combo = QComboBox(); self.method_combo.setStyleSheet(combo_style)
        self.method_combo.addItems(list(self.interpolation_methods.values()))
        default_method_text = next((name for name in self.interpolation_methods.values() if "修正谢泼德" in name), None)
        if default_method_text:
            default_index = self.method_combo.findText(default_method_text)
            if default_index != -1:
                self.method_combo.setCurrentIndex(default_index)
        self.resolution_spin = QSpinBox(); self.resolution_spin.setRange(20, 200); self.resolution_spin.setValue(80); self.resolution_spin.setSuffix(" 点")
        self.base_level_spin = QDoubleSpinBox(); self.base_level_spin.setRange(-5000.0, 5000.0); self.base_level_spin.setDecimals(2); self.base_level_spin.setSingleStep(5.0); self.base_level_spin.setValue(0.0); self.base_level_spin.setSuffix(" m")
        self.gap_spin = QDoubleSpinBox(); self.gap_spin.setRange(0.0, 2000.0); self.gap_spin.setDecimals(2); self.gap_spin.setSingleStep(5.0); self.gap_spin.setValue(0.0); self.gap_spin.setSuffix(" m")
        self.validation_spin = QSpinBox(); self.validation_spin.setRange(10, 50); self.validation_spin.setSingleStep(5); self.validation_spin.setValue(30); self.validation_spin.setSuffix(" %")

        param_layout.addRow("插值方法:", self.method_combo)
        param_layout.addRow("网格分辨率:", self.resolution_spin)
        param_layout.addRow("起始基底标高:", self.base_level_spin)
        param_layout.addRow("岩层间距(附加):", self.gap_spin)
        param_layout.addRow("验证占比:", self.validation_spin)
        control_layout.addWidget(param_group)

        action_group = QGroupBox("操作")
        action_group.setStyleSheet("QGroupBox { margin-top: 12px; padding: 12px 8px 8px 8px; }")
        action_layout = QHBoxLayout(action_group)
        action_layout.setSpacing(10)

        self.generate_btn = ModernButton("生成煤层块体", color="#0ea5e9")
        self.generate_btn.clicked.connect(self.generate_block_model)
        self.compare_btn = ModernButton("插值方法对比", color="#8b5cf6")
        self.compare_btn.clicked.connect(self.compare_interpolation_methods)
        self.export_btn = ModernButton("导出图像", color="#dc2626")
        self.export_btn.clicked.connect(self.export_plot)
        action_layout.addWidget(self.generate_btn)
        action_layout.addWidget(self.compare_btn)
        action_layout.addWidget(self.export_btn)
        control_layout.addWidget(action_group)

        self.status_label = QLabel("等待数据加载…")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #2563eb; font-size: 12px; line-height: 1.4;")
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()

        results_panel = QFrame()
        results_panel.setStyleSheet("QFrame { background-color: #ffffff; }")
        results_panel.setMinimumWidth(1100)
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(12, 12, 12, 12)
        results_layout.setSpacing(12)

        self.canvas = ChartCanvas(results_panel, width=18, height=10, dpi=100)
        self.canvas.setMinimumSize(1240, 720)
        self.toolbar = NavigationToolbar(self.canvas, results_panel)
        self.toolbar.setStyleSheet("background-color: transparent; border: none;")

        plot_container = QFrame()
        plot_container.setStyleSheet(
            "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; }"
        )
        plot_container.setMinimumHeight(720)
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(14, 14, 14, 14)
        plot_layout.setSpacing(12)

        control_bar = QFrame()
        control_bar.setStyleSheet(
            "QFrame { background-color: #edf2ff; border: 1px solid #dbe4ff; border-radius: 12px; }"
            "QLabel { color: #364152; }"
            "QComboBox { border: 1px solid #dbe4ff; border-radius: 6px; padding: 4px 8px; }"
            "QCheckBox { color: #364152; font-size: 12px; }"
        )
        control_bar_layout = QGridLayout(control_bar)
        control_bar_layout.setContentsMargins(12, 10, 12, 10)
        control_bar_layout.setHorizontalSpacing(12)
        control_bar_layout.setVerticalSpacing(8)

        view_label = QLabel("视角")
        control_bar_layout.addWidget(view_label, 0, 0)

        self.view_combo = QComboBox()
        self.view_combo.addItems(["透视视图", "俯视", "北向", "东向", "南向"])
        self.view_combo.currentIndexChanged.connect(self.on_view_preset_changed)
        self.view_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        control_bar_layout.addWidget(self.view_combo, 0, 1)

        scale_label = QLabel("垂向缩放")
        control_bar_layout.addWidget(scale_label, 0, 2)

        self.vertical_slider = QSlider(Qt.Orientation.Horizontal)
        self.vertical_slider.setRange(10, 300)
        self.vertical_slider.setValue(120)
        self.vertical_slider.setSingleStep(5)
        self.vertical_slider.setFixedWidth(200)
        self.vertical_slider.valueChanged.connect(self.on_vertical_scale_changed)
        control_bar_layout.addWidget(self.vertical_slider, 0, 3, 1, 2)

        self.vertical_value_label = QLabel("1.20×")
        self.vertical_value_label.setMinimumWidth(52)
        self.vertical_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_bar_layout.addWidget(self.vertical_value_label, 0, 5)

        quality_label = QLabel("显示品质")
        control_bar_layout.addWidget(quality_label, 0, 6)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(list(self.preview_quality_map.keys()))
        self.quality_combo.setCurrentText("标准")
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        self.quality_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        control_bar_layout.addWidget(self.quality_combo, 0, 7)

        filter_label = QLabel("显示岩层")
        control_bar_layout.addWidget(filter_label, 1, 0)

        self.layer_filter_combo = QComboBox()
        self.layer_filter_combo.addItems(["显示全部", "仅含“煤”", "自定义", "关键层优先"])
        self.layer_filter_combo.setEnabled(False)
        self.layer_filter_combo.currentIndexChanged.connect(self.on_layer_filter_mode_changed)
        control_bar_layout.addWidget(self.layer_filter_combo, 1, 1)

        self.layer_filter_button = QPushButton("选择…")
        self.layer_filter_button.setFixedHeight(30)
        self.layer_filter_button.setStyleSheet(
            "QPushButton {"
            "background-color: #38bdf8;"
            "color: #ffffff;"
            "border: none;"
            "border-radius: 6px;"
            "padding: 4px 12px;"
            "font-size: 12px;"
            "}"
            "QPushButton:hover { background-color: #0ea5e9; }"
            "QPushButton:pressed { background-color: #0284c7; }"
        )
        self.layer_filter_button.setEnabled(False)
        self.layer_filter_button.clicked.connect(self.on_layer_filter_button_clicked)
        control_bar_layout.addWidget(self.layer_filter_button, 1, 2)

        self.layer_filter_status_label = QLabel("当前：未生成")
        self.layer_filter_status_label.setMinimumWidth(180)
        self.layer_filter_status_label.setWordWrap(True)
        self.layer_filter_status_label.setStyleSheet("color: #475569; font-size: 12px;")
        self.layer_filter_status_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        control_bar_layout.addWidget(self.layer_filter_status_label, 1, 3, 1, 2)

        self.outline_check = QCheckBox("显示边缘线")
        self.outline_check.setChecked(True)
        self.outline_check.toggled.connect(self.on_outline_toggled)
        control_bar_layout.addWidget(self.outline_check, 1, 5)

        self.summary_button = QPushButton("建模摘要")
        self.summary_button.setFixedHeight(32)
        self.summary_button.setStyleSheet(
            "QPushButton {"
            "background-color: #4f46e5;"
            "color: #ffffff;"
            "border: none;"
            "border-radius: 8px;"
            "padding: 4px 16px;"
            "font-size: 12px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover { background-color: #4338ca; }"
            "QPushButton:pressed { background-color: #3730a3; }"
        )
        self.summary_button.clicked.connect(self.show_summary_window)
        control_bar_layout.addWidget(self.summary_button, 1, 6)

        self.view_hint_label = QLabel("提示：拖拽旋转，滚轮缩放。")
        self.view_hint_label.setStyleSheet("color: #4f46e5; font-size: 11px;")
        self.view_hint_label.setWordWrap(True)
        self.view_hint_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        control_bar_layout.addWidget(self.view_hint_label, 1, 7)

        control_bar_layout.setColumnStretch(3, 2)
        control_bar_layout.setColumnStretch(4, 1)
        control_bar_layout.setColumnStretch(7, 2)

        plot_layout.addWidget(control_bar)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, 1)

        results_layout.addWidget(plot_container, 1)

        scroll_area.setMinimumWidth(420)
        splitter.addWidget(scroll_area)
        splitter.addWidget(results_panel)
        splitter.setCollapsible(0, False)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 8)
        splitter.setSizes([480, 1420])

        main_layout.addWidget(splitter)

    def on_view_preset_changed(self, index):
        ax = self._get_current_axes()
        if ax is None:
            if self.last_plot_payload:
                self._rerender_last_plot()
            return
        self._apply_current_view(ax, index)
        self.canvas.draw_idle()

    def on_vertical_scale_changed(self, value):
        try:
            scale = max(0.1, float(value) / 100.0)
        except (TypeError, ValueError):
            scale = self.vertical_scale
        self.vertical_scale = scale
        if hasattr(self, "vertical_value_label"):
            self.vertical_value_label.setText(f"{scale:.2f}×")
        if self.last_plot_payload:
            self._rerender_last_plot()

    def on_quality_changed(self, text):
        stride = self.preview_quality_map.get(str(text), self.preview_quality_map.get("标准", 2))
        self.preview_stride = max(1, int(stride))
        if self.last_plot_payload:
            self._rerender_last_plot()

    def on_outline_toggled(self, checked):
        if self.last_plot_payload:
            self._rerender_last_plot()

    def select_borehole_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, "选择钻孔数据文件", "", "CSV Files (*.csv)")
        if filepaths:
            self.borehole_files = list(filepaths)
            preview_names = [os.path.basename(path) for path in self.borehole_files[:3]]
            label_text = "；".join(preview_names)
            if len(self.borehole_files) > 3:
                label_text += f" 等 {len(self.borehole_files)} 个文件"
            self.data_file_label.setText(label_text)
            self._aggregate_data()
        else:
            if not self.borehole_files:
                self.data_file_label.setText("未选择")
                self.merged_df = None
                self._update_status("等待数据加载…", color="#2563eb")
                self._update_seam_list(clear_only=True)

    def select_coordinate_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择坐标数据文件", "", "CSV Files (*.csv)")
        if filepath:
            self.coords_file = filepath
            self.coord_file_label.setText(os.path.basename(filepath))
            self._aggregate_data()

    def _aggregate_data(self):
        if not self.borehole_files:
            self._update_status("请选择钻孔数据文件", color="#2563eb")
            return False
        if not self.coords_file:
            self._update_status("请选择坐标数据文件", color="#2563eb")
            return False
        try:
            merged_df, _ = aggregate_boreholes(self.borehole_files, self.coords_file)
            if hasattr(self.main_win, 'rock_db') and getattr(self.main_win, 'rock_db', None) is not None:
                stat_preference = getattr(self.main_win, 'stat_preference', 'median')
                filled_df, filled_cnt, filled_cols = fill_missing_properties(
                    merged_df,
                    self.main_win.rock_db,
                    stat_preference=stat_preference,
                )
                if filled_cnt > 0:
                    merged_df = filled_df
                    metric_label = '平均值' if stat_preference == 'mean' else '中位数'
                    QMessageBox.information(
                        self,
                        "数据自动填充",
                        f"已填充 {filled_cnt} 条记录的参数（优先使用{metric_label}）：\n- {', '.join(filled_cols)}",
                    )

            self.merged_df = merged_df
            self._update_column_options()
            self._update_status(
                f"✅ 数据合并成功，钻孔文件 {len(self.borehole_files)} 个，记录数: {len(self.merged_df)}",
                color="#16a34a"
            )
            if hasattr(self.main_win, "dashboard_page") and self.main_win.dashboard_page:
                self.main_win.dashboard_page.refresh_cards()
            return True
        except Exception as e:
            QMessageBox.critical(self, "合并错误", f"合并数据时发生错误: {e}")
            self.merged_df = None
            self._update_status("❌ 数据合并失败", color="#dc2626")
            self._update_seam_list(clear_only=True)
            return False

    def _update_column_options(self):
        if self.merged_df is None:
            return

        numeric_cols = self.merged_df.select_dtypes(include=np.number).columns.tolist()
        text_cols = self.merged_df.select_dtypes(include=['object', 'category']).columns.tolist()

        for combo in [self.x_col_combo, self.y_col_combo, self.thickness_col_combo]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(numeric_cols)
            combo.blockSignals(False)

        self._set_default_column(self.x_col_combo, numeric_cols, ["坐标x", "_x", " x", "east", "东", "x"])
        self._set_default_column(self.y_col_combo, numeric_cols, ["坐标y", "_y", " y", "north", "北", "y"])
        self._set_default_column(self.thickness_col_combo, numeric_cols, ["厚度", "thick", "h", "煤厚", "厚"], fallback_index=0)

        self._detect_seam_column(text_cols)

    def _set_default_column(self, combo: QComboBox, columns, keywords, fallback_index=None):
        if not columns:
            return
        lower_columns = [col.lower() for col in columns]
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for idx, lower_col in enumerate(lower_columns):
                if keyword_lower in lower_col:
                    combo.setCurrentText(columns[idx])
                    return
        if fallback_index is not None and 0 <= fallback_index < len(columns):
            combo.setCurrentText(columns[fallback_index])
        elif columns:
            combo.setCurrentText(columns[0])

    def _detect_seam_column(self, text_cols=None):
        if self.merged_df is None or self.merged_df.empty:
            self._set_seam_column(None, auto=True)
            return

        if text_cols is None:
            text_cols = self.merged_df.select_dtypes(include=['object', 'category']).columns.tolist()

        candidates = [col for col in text_cols if str(col).lower() not in {"钻孔名", "borehole", "孔号", "hole_id", "id"}]
        best_col = None
        best_score = -1
        for col in candidates:
            score = 0
            col_str = str(col)
            for keyword, weight in [("煤", 5), ("层", 3), ("名称", 2), ("岩", 1)]:
                if keyword in col_str:
                    score += weight * 2

            series = self.merged_df[col].dropna().astype(str)
            if not series.empty:
                contains_coal = series.str.contains("煤")
                contains_layer = series.str.contains("层")
                score += contains_coal.mean() * 10
                score += contains_layer.mean() * 6
                unique_count = series.nunique()
                score += min(unique_count, 50) / 10

            if score > best_score:
                best_score = score
                best_col = col

        self._set_seam_column(best_col, auto=True)

    def _set_seam_column(self, column_name, auto=False):
        label_prefix = "自动识别" if auto else "当前列"
        if self.merged_df is None or column_name is None or column_name not in self.merged_df.columns:
            self.base_seam_column = None
            self.seam_column = None
            self.seam_detect_label.setText(f"{label_prefix}: 未检测")
            self._update_seam_list(clear_only=True)
            return

        self.base_seam_column = column_name
        numbered_col = self._ensure_numbered_seam_column(column_name)
        self.seam_column = numbered_col

        seam_series = self.merged_df[numbered_col].dropna().astype(str)
        seam_series = seam_series.str.strip()
        seam_series = seam_series[seam_series != ""]
        seam_count = seam_series.nunique()

        suffix_note = "（重复岩层按钻孔序号自动编号）"
        self.seam_detect_label.setText(f"{label_prefix}: {column_name}{suffix_note} · 岩层 {seam_count} 个")
        self._update_seam_list()

    def _ensure_numbered_seam_column(self, base_col: str) -> str:
        numbered_col = f"{base_col}_编号"
        numbering = self._generate_numbered_seam_series(base_col)
        if numbering is not None:
            self.merged_df[numbered_col] = numbering
        else:
            self.merged_df[numbered_col] = self.merged_df[base_col]
        return numbered_col

    def _generate_numbered_seam_series(self, base_col: str) -> pd.Series:
        if self.merged_df is None or base_col not in self.merged_df.columns:
            return None

        df = self.merged_df
        if df.empty:
            return pd.Series(dtype=object, index=df.index)

        result = pd.Series(index=df.index, dtype=object)
        borehole_candidates = ["钻孔名", "borehole", "孔号", "hole_id", "ID", "id"]
        order_candidates = ["序号", "序号(从下到上)", "层序", "层号", "index", "Index"]
        depth_candidates = ["底板深度", "顶板深度", "深度", "深度(m)", "Depth"]

        borehole_col = next((col for col in borehole_candidates if col in df.columns), None)
        group_iter = df.groupby(borehole_col, sort=False) if borehole_col else [(None, df)]

        for _, group_df in group_iter:
            if group_df.empty:
                continue

            ordered_idx = list(group_df.index)

            order_col = next((col for col in order_candidates if col in group_df.columns), None)
            if order_col:
                order_values = pd.to_numeric(group_df[order_col], errors='coerce')
                if order_values.notna().any():
                    ordered_idx = order_values.sort_values(ascending=True).index.tolist()
            else:
                depth_col = next((col for col in depth_candidates if col in group_df.columns), None)
                if depth_col:
                    depth_values = pd.to_numeric(group_df[depth_col], errors='coerce')
                    if depth_values.notna().any():
                        ordered_idx = depth_values.sort_values(ascending=True).index.tolist()

            names = group_df.loc[ordered_idx, base_col].fillna("").astype(str).str.strip()
            group_counts = names.groupby(names).transform('size')
            cumulative = names.groupby(names).cumcount() + 1
            numbered = names.copy()
            mask = (group_counts > 1) & (names != "")
            numbered.loc[mask] = names.loc[mask] + cumulative.loc[mask].astype(str)
            numbered.loc[names == ""] = ""
            result.loc[ordered_idx] = numbered.values

        return result.where(result != "", np.nan)

    def _update_seam_list(self, clear_only=False):
        self.seam_list.clear()
        if clear_only or self.merged_df is None or not self.seam_column or self.seam_column not in self.merged_df.columns:
            self.seam_summary_label.setText("未检测到岩层列")
            return

        seam_series = self.merged_df[self.seam_column].dropna().astype(str).str.strip()
        seam_series = seam_series[seam_series != ""]
        if seam_series.empty:
            self.seam_summary_label.setText("岩层列无有效数据")
            return

        seam_counts = seam_series.value_counts()
        for seam_name, count in seam_counts.items():
            item = QListWidgetItem(f"{seam_name} ({count})")
            item.setData(Qt.ItemDataRole.UserRole, seam_name)
            item.setSelected(True)
            self.seam_list.addItem(item)

        self.seam_summary_label.setText(f"已识别岩层 {len(seam_counts)} 个（重复岩层已自动编号）")

    def select_all_seams(self):
        for i in range(self.seam_list.count()):
            self.seam_list.item(i).setSelected(True)

    def clear_seam_selection(self):
        self.seam_list.clearSelection()

    def _collect_selected_seams(self):
        if self.seam_list.count() == 0:
            return []
        selected_items = self.seam_list.selectedItems()
        if not selected_items:
            return [self.seam_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.seam_list.count())]
        return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]

    def _get_available_methods(self):
        methods = {}
        try:
            from scipy.interpolate import griddata, Rbf
            methods.update({
                "linear": "Linear (线性)",
                "cubic": "Cubic (三次样条)",
                "nearest": "Nearest Neighbor (最近邻)",
                "multiquadric": "Multiquadric (多重二次)",
                "inverse": "Inverse Distance (反距离)",
                "gaussian": "Gaussian (高斯)",
                "linear_rbf": "Linear RBF (线性RBF)",
                "cubic_rbf": "Cubic RBF (三次RBF)",
                "quintic_rbf": "Quintic RBF (五次RBF)",
                "thin_plate": "Thin Plate Spline (薄板样条)"
            })
        except ImportError:
            print("警告: scipy未安装，部分插值方法不可用")
        methods.update({
            "inverse_distance": "Simple Inverse Distance (简单反距离)",
            "bilinear": "Bilinear (双线性)",
            "ordinary_kriging": "Ordinary Kriging (普通克里金)",
            "modified_shepard": "Modified Shepard (修正谢泼德)",
            "radial_basis": "Radial Basis Function (径向基)"
        })
        if not methods:
            methods["nearest_simple"] = "Simple Nearest (简单最近邻)"
        return methods

    def _perform_interpolation(self, x_train, y_train, z_train, x_val, y_val, method_name):
        method_key = None
        for key, value in self.interpolation_methods.items():
            if value == method_name:
                method_key = key
                break
        if method_key is None:
            method_key = method_name.lower()
        try:
            if method_key == "linear":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            if method_key == "cubic":
                if len(x_train) >= 16:
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='cubic')
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            if method_key == "nearest":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
            if method_key in ["multiquadric", "inverse", "gaussian", "linear_rbf", "cubic_rbf", "quintic_rbf", "thin_plate"]:
                rbf_map = {
                    "multiquadric": "multiquadric",
                    "inverse": "inverse",
                    "gaussian": "gaussian",
                    "linear_rbf": "linear",
                    "cubic_rbf": "cubic",
                    "quintic_rbf": "quintic",
                    "thin_plate": "thin_plate"
                }
                # 添加平滑参数，避免矩阵奇异性问题
                rbf = Rbf(x_train, y_train, z_train, function=rbf_map[method_key], smooth=0.1)
                return rbf(x_val, y_val)
            if method_key == "bilinear":
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            if method_key == "modified_shepard":
                result = []
                for xv, yv in zip(x_val, y_val):
                    distances = np.sqrt((x_train - xv) ** 2 + (y_train - yv) ** 2)
                    distances = np.where(distances == 0, 1e-12, distances)
                    weights = 1.0 / (distances ** 2)
                    weights = weights / np.sum(weights)
                    result.append(np.sum(weights * z_train))
                return np.array(result)
            if method_key == "ordinary_kriging":
                # 添加数据点检查和错误处理
                if len(x_train) < 4:
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='nearest')
                try:
                    rbf = Rbf(x_train, y_train, z_train, function='gaussian', smooth=0.5)
                    return rbf(x_val, y_val)
                except (np.linalg.LinAlgError, ZeroDivisionError, ValueError):
                    # 静默降级为线性插值，不打印错误
                    return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            if method_key == "radial_basis":
                rbf = Rbf(x_train, y_train, z_train, function='multiquadric', smooth=0.1)
                return rbf(x_val, y_val)
        except Exception as e:
            # 只打印非预期的错误
            if not isinstance(e, (np.linalg.LinAlgError, ZeroDivisionError)):
                print(f"插值方法 {method_name} 失败: {e}")
            try:
                return griddata((x_train, y_train), z_train, (x_val, y_val), method='linear')
            except Exception as inner:
                print(f"线性插值退化失败: {inner}")
                return np.full(len(x_val), np.nan)

    def _prepare_seam_validation_sets(self, selected_seams, seam_col, x_col, y_col, thickness_col, validation_ratio):
        datasets = {}
        skipped = []
        rng = np.random.default_rng(42)

        for seam_name in selected_seams:
            seam_df = self.merged_df[self.merged_df[seam_col].astype(str) == str(seam_name)].copy()
            if seam_df.empty:
                skipped.append(f"{seam_name}: 无匹配数据")
                continue

            for col in [x_col, y_col, thickness_col]:
                seam_df[col] = pd.to_numeric(seam_df[col], errors='coerce')

            seam_df = seam_df.dropna(subset=[x_col, y_col, thickness_col])
            total_points = len(seam_df)
            if total_points < 6:
                skipped.append(f"{seam_name}: 样本数仅 {total_points} 条，少于 6 条，跳过验证")
                continue

            validation_points = max(1, int(total_points * validation_ratio))
            if validation_points >= total_points:
                validation_points = max(1, total_points // 3)

            training_points = total_points - validation_points
            if training_points < 4:
                skipped.append(f"{seam_name}: 训练点仅 {training_points} 条，无法进行稳定插值")
                continue

            indices = np.arange(total_points)
            val_idx = rng.choice(indices, size=validation_points, replace=False)
            train_idx = np.setdiff1d(indices, val_idx)

            seam_df = seam_df.reset_index(drop=True)

            datasets[seam_name] = {
                'x_train': seam_df.loc[train_idx, x_col].values.astype(float),
                'y_train': seam_df.loc[train_idx, y_col].values.astype(float),
                'thickness_train': seam_df.loc[train_idx, thickness_col].values.astype(float),
                'x_val': seam_df.loc[val_idx, x_col].values.astype(float),
                'y_val': seam_df.loc[val_idx, y_col].values.astype(float),
                'thickness_val': seam_df.loc[val_idx, thickness_col].values.astype(float),
                'total_points': int(total_points),
                'train_points': int(training_points),
                'val_points': int(validation_points)
            }

        return datasets, skipped

    @staticmethod
    def _calculate_error_metrics(actual, predicted):
        mae = float(np.mean(np.abs(actual - predicted)))
        rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))

        if len(actual) > 1 and not np.allclose(actual, actual[0]):
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            if ss_tot != 0:
                r2 = float(1 - (ss_res / ss_tot))
            else:
                r2 = -999.0
        else:
            r2 = -999.0

        nonzero_mask = np.abs(actual) > 1e-8
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((actual[nonzero_mask] - predicted[nonzero_mask]) / actual[nonzero_mask]) * 100))
        else:
            mape = float('inf')

        with np.errstate(divide='ignore', invalid='ignore'):
            denom = np.abs(actual) + 1e-8
            relative_errors = np.abs((actual - predicted) / denom)
        accuracy_10 = float(np.mean(relative_errors < 0.10) * 100)
        accuracy_5 = float(np.mean(relative_errors < 0.05) * 100)

        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'accuracy_10': accuracy_10,
            'accuracy_5': accuracy_5
        }

    @staticmethod
    def _aggregate_method_metrics(method_key, method_name, seam_metrics_list):
        if not seam_metrics_list:
            return None

        avg = lambda field: float(np.mean([metrics[field] for metrics in seam_metrics_list]))

        return {
            'method_key': method_key,
            'method_name': method_name,
            'avg_mae': avg('mae'),
            'avg_rmse': avg('rmse'),
            'avg_r2': avg('r2'),
            'avg_mape': avg('mape'),
            'avg_accuracy_10': avg('accuracy_10'),
            'avg_accuracy_5': avg('accuracy_5'),
            'seam_count': len(seam_metrics_list),
            'total_valid_points': int(sum(metrics['n_valid'] for metrics in seam_metrics_list)),
            'total_samples': int(sum(metrics['total_points'] for metrics in seam_metrics_list))
        }

    def generate_block_model(self):
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return

        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        thickness_col = self.thickness_col_combo.currentText()
        seam_col = self.seam_column

        if not all([x_col, y_col, thickness_col]):
            QMessageBox.warning(self, "缺少列", "请为X、Y、厚度列选择有效字段。")
            return

        if not seam_col:
            QMessageBox.warning(self, "列缺失", "未检测到可用的煤层列，请检查数据格式。")
            return

        if seam_col not in self.merged_df.columns:
            QMessageBox.warning(self, "列缺失", f"数据中不存在名为 '{seam_col}' 的煤层列。")
            return

        selected_seams = self._collect_selected_seams()
        if not selected_seams:
            QMessageBox.warning(self, "无煤层", "请至少选择一个煤层进行建模。")
            return

        try:
            method_name = self.method_combo.currentText()
            grid_res = self.resolution_spin.value()
            start_base = self.base_level_spin.value()
            gap_value = self.gap_spin.value()

            def interpolation_wrapper(x_points, y_points, thickness_points, xi_flat, yi_flat):
                return self._perform_interpolation(x_points, y_points, thickness_points, xi_flat, yi_flat, method_name)

            block_model_objs, skipped, (XI, YI) = build_block_models(
                self.merged_df,
                seam_col,
                x_col,
                y_col,
                thickness_col,
                selected_seams,
                interpolation_wrapper,
                grid_res,
                start_base,
                gap_value
            )

            block_models = []
            for model in block_model_objs:
                block_models.append({
                    'name': model.name,
                    'points': model.points,
                    'top_surface': model.top_surface,
                    'bottom_surface': model.bottom_surface,
                    'thickness_grid': model.thickness_grid,
                    'avg_thickness': model.avg_thickness,
                    'max_thickness': model.max_thickness,
                    'avg_height': model.avg_height,
                    'max_height': model.max_height,
                    'min_height': model.min_height,
                    'avg_bottom': model.avg_bottom,
                    'min_bottom': model.min_bottom,
                })

            block_models.sort(
                key=lambda m: m['avg_bottom'] if (m.get('avg_bottom') is not None and np.isfinite(m['avg_bottom'])) else float('inf')
            )

            if not block_models:
                QMessageBox.warning(self, "无可建模煤层", "选定的煤层数据不足以生成块体。")
                return

            self.last_plot_payload = (XI, YI, block_models, method_name)
            self.current_method_label = method_name
            self.available_display_layers = [m['name'] for m in block_models]

            if self.preview_filter_mode == "custom":
                self.preview_custom_layers = [name for name in self.preview_custom_layers if name in self.available_display_layers]
                if not self.preview_custom_layers:
                    self.preview_filter_mode = "all"

            if self.preview_filter_mode == "coal":
                if not any("煤" in str(name) for name in self.available_display_layers):
                    self.preview_filter_mode = "all"

            mode_index_map = {"all": 0, "coal": 1, "custom": 2}
            target_index = mode_index_map.get(self.preview_filter_mode, 0)

            if self.layer_filter_combo is not None:
                self.layer_filter_combo.blockSignals(True)
                self.layer_filter_combo.setCurrentIndex(target_index)
                self.layer_filter_combo.setEnabled(True)
                self.layer_filter_combo.blockSignals(False)
                self._layer_filter_prev_index = target_index
            else:
                self._layer_filter_prev_index = target_index

            if self.layer_filter_button is not None:
                self.layer_filter_button.setEnabled(True)

            self._apply_display_filter()

            info_lines = [f"✅ 成功构建 {len(block_models)} 个煤层块体"]
            info_lines.append(f"• 插值方法: {method_name}")
            info_lines.append(
                f"• 首层基底: {start_base:.2f} m · 层间间距: {gap_value:.2f} m (用于可视化间隔)"
            )
            info_lines.append(f"• 垂向缩放: {self.vertical_scale:.2f}× (可在面板调整)")
            info_lines.append("• 建模摘要窗口已更新，可通过右上角按钮查看")
            finite_bottoms = [m['min_bottom'] for m in block_models if np.isfinite(m['min_bottom'])]
            finite_tops = [m['max_height'] for m in block_models if np.isfinite(m['max_height'])]
            if finite_bottoms and finite_tops:
                info_lines.append(
                    f"• 模型高程范围: {min(finite_bottoms):.2f} ~ {max(finite_tops):.2f} m"
                )
            if skipped:
                info_lines.append("\n以下煤层未能生成块体:")
                info_lines.extend([f"  - {reason}" for reason in skipped[:6]])
                if len(skipped) > 6:
                    info_lines.append(f"  ... 另有 {len(skipped) - 6} 条被跳过")

            self._update_status("块体生成完成，图形区域已更新", color="#16a34a")
            if hasattr(self.main_win, "dashboard_page") and self.main_win.dashboard_page:
                self.main_win.dashboard_page.refresh_cards()
            QMessageBox.information(self, "块体建模完成", "\n".join(info_lines))
        except ValueError as ve:
            self._update_status(f"⚠️ 数据校验失败: {ve}", color="#f97316")
            QMessageBox.warning(self, "数据不足", str(ve))
        except Exception as e:
            self._update_status(f"❌ 生成失败: {e}", color="#dc2626")
            QMessageBox.critical(self, "建模失败", f"生成煤层块体失败: {e}")

    def compare_interpolation_methods(self):
        if self.merged_df is None:
            QMessageBox.warning(self, "无数据", "请先加载并合并数据文件和坐标文件。")
            return

        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        thickness_col = self.thickness_col_combo.currentText()
        seam_col = self.seam_column

        if not all([x_col, y_col, thickness_col]):
            QMessageBox.warning(self, "缺少列", "请为X、Y、厚度列选择有效字段。")
            return

        if not seam_col:
            QMessageBox.warning(self, "列缺失", "未检测到可用的煤层列，请检查数据格式。")
            return

        selected_seams = self._collect_selected_seams()
        if not selected_seams:
            QMessageBox.warning(self, "无煤层", "请至少选择一个煤层进行对比分析。")
            return

        validation_ratio = max(0.1, self.validation_spin.value() / 100.0)
        datasets, skipped_messages = self._prepare_seam_validation_sets(
            selected_seams, seam_col, x_col, y_col, thickness_col, validation_ratio
        )

        if not datasets:
            message = "所选煤层均无法用于验证，请检查样本数量或数据质量。"
            if skipped_messages:
                message += "\n\n" + "\n".join(skipped_messages[:6])
                if len(skipped_messages) > 6:
                    message += f"\n... 另有 {len(skipped_messages) - 6} 条记录被跳过"
            QMessageBox.warning(self, "验证数据不足", message)
            return

        progress = QProgressDialog("正在对比各插值方法...", "取消", 0, len(self.interpolation_methods), self)
        progress.setWindowTitle("插值方法对比")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(True)
        progress.setAutoClose(True)
        progress.setMinimumWidth(320)

        aggregated_results = []
        seam_details = []

        for idx, (method_key, method_name) in enumerate(self.interpolation_methods.items()):
            if progress.wasCanceled():
                progress.close()
                self._update_status("对比已取消", color="#f97316")
                return

            progress.setValue(idx)
            progress.setLabelText(f"正在评估 {method_name} ({idx + 1}/{len(self.interpolation_methods)})")
            QApplication.processEvents()

            seam_metrics_list = []

            for seam_name, data in datasets.items():
                try:
                    predictions = self._perform_interpolation(
                        data['x_train'],
                        data['y_train'],
                        data['thickness_train'],
                        data['x_val'],
                        data['y_val'],
                        method_name
                    )
                except Exception as e:
                    seam_details.append({
                        'seam': seam_name,
                        'method_name': method_name,
                        'status': f"失败: {e}",
                        'mae': np.nan,
                        'rmse': np.nan,
                        'r2': -999.0,
                        'mape': np.nan,
                        'accuracy_10': 0.0,
                        'accuracy_5': 0.0,
                        'n_valid': 0,
                        'total_points': data['total_points'],
                        'train_points': data['train_points'],
                        'val_points': data['val_points']
                    })
                    continue

                predictions = np.asarray(predictions, dtype=float)
                target = data['thickness_val']

                if predictions.shape[0] != target.shape[0]:
                    min_len = min(predictions.shape[0], target.shape[0])
                    predictions = predictions[:min_len]
                    target = target[:min_len]

                valid_mask = np.isfinite(predictions)
                if not np.any(valid_mask):
                    seam_details.append({
                        'seam': seam_name,
                        'method_name': method_name,
                        'status': "无有效预测值",
                        'mae': np.nan,
                        'rmse': np.nan,
                        'r2': -999.0,
                        'mape': np.nan,
                        'accuracy_10': 0.0,
                        'accuracy_5': 0.0,
                        'n_valid': 0,
                        'total_points': data['total_points'],
                        'train_points': data['train_points'],
                        'val_points': data['val_points']
                    })
                    continue

                actual = target[valid_mask]
                predicted = predictions[valid_mask]

                if actual.size == 0:
                    seam_details.append({
                        'seam': seam_name,
                        'method_name': method_name,
                        'status': "无有效验证数据",
                        'mae': np.nan,
                        'rmse': np.nan,
                        'r2': -999.0,
                        'mape': np.nan,
                        'accuracy_10': 0.0,
                        'accuracy_5': 0.0,
                        'n_valid': 0,
                        'total_points': data['total_points'],
                        'train_points': data['train_points'],
                        'val_points': data['val_points']
                    })
                    continue

                metrics = self._calculate_error_metrics(actual, predicted)
                metrics.update({
                    'seam': seam_name,
                    'method_name': method_name,
                    'status': "成功",
                    'n_valid': int(actual.size),
                    'total_points': data['total_points'],
                    'train_points': data['train_points'],
                    'val_points': data['val_points']
                })

                seam_metrics_list.append(metrics)
                seam_details.append(metrics)

            aggregated = self._aggregate_method_metrics(method_key, method_name, seam_metrics_list)
            if aggregated:
                aggregated_results.append(aggregated)

        progress.setValue(len(self.interpolation_methods))
        progress.close()

        if not aggregated_results:
            QMessageBox.warning(self, "对比失败", "所有插值方法都未能完成验证，请检查数据质量。")
            return

        aggregated_results.sort(
            key=lambda r: (
                r['avg_r2'] if r['avg_r2'] > -900 else -1e6,
                -r['avg_rmse']
            ),
            reverse=True
        )

        self.comparison_results = aggregated_results
        self.comparison_details = seam_details
        dialog = InterpolationComparisonDialog(
            self,
            aggregated_results,
            seam_details,
            validation_ratio,
            skipped_messages
        )
        dialog.exec()

        best_method = aggregated_results[0]
        if best_method['avg_r2'] > -900:
            summary = f"推荐方法: {best_method['method_name']} (平均R² {best_method['avg_r2']:.3f}, 平均RMSE {best_method['avg_rmse']:.3f})"
        else:
            summary = f"推荐方法: {best_method['method_name']} (平均RMSE {best_method['avg_rmse']:.3f})"
        self._update_status(summary, color="#0ea5e9")
        self.method_combo.setCurrentText(best_method['method_name'])

    def on_layer_filter_mode_changed(self, index):
        if self.layer_filter_combo is None:
            return

        mode_by_index = {0: "all", 1: "coal", 2: "custom", 3: "key"}
        requested_mode = mode_by_index.get(index, "all")

        if not self.last_plot_payload:
            self.preview_filter_mode = requested_mode
            if requested_mode != "custom":
                self.preview_custom_layers = []
            self._layer_filter_prev_index = index
            self._update_layer_filter_status(0, 0)
            return

        block_models = self.last_plot_payload[2] if len(self.last_plot_payload) >= 3 else []

        if index == 1:
            if not any("煤" in str(m.get('name', '')) for m in block_models):
                QMessageBox.information(
                    self,
                    "无匹配岩层",
                    "当前模型中未找到名称包含“煤”的岩层，已保持原有显示。",
                )
                self._restore_layer_filter_selection()
                return
            self.preview_filter_mode = "coal"
            self.preview_custom_layers = []

        elif index == 2:
            selected_layers = self._prompt_custom_layer_selection()
            if not selected_layers:
                self._restore_layer_filter_selection()
                return
            self.preview_filter_mode = "custom"
            self.preview_custom_layers = selected_layers

        elif index == 3:
            key_focus_layers = self._collect_key_focus_layers(block_models)
            if not key_focus_layers:
                QMessageBox.information(
                    self,
                    "无关键层数据",
                    "未检测到可用于预览的关键层结果。请先在“关键层计算”中完成计算，并确保结果岩层名称与当前模型匹配。",
                )
                self._restore_layer_filter_selection()
                return
            self.preview_filter_mode = "key"
            self.preview_custom_layers = []

        else:
            self.preview_filter_mode = "all"
            self.preview_custom_layers = []

        self._layer_filter_prev_index = index
        self._apply_display_filter()

    def _restore_layer_filter_selection(self):
        if self.layer_filter_combo is None:
            return
        self.layer_filter_combo.blockSignals(True)
        self.layer_filter_combo.setCurrentIndex(self._layer_filter_prev_index)
        self.layer_filter_combo.blockSignals(False)

    @staticmethod
    def _normalize_layer_key(name: str) -> str:
        text = str(name).strip()
        if not text:
            return "未命名岩层"
        if "煤" in text:
            return "煤"
        base = re.split(r'[（(]', text, 1)[0].strip()
        base = re.sub(r'[\uFF10-\uFF19\d]+$', '', base)
        base = re.sub(r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩIVXivx一二三四五六七八九十]+$', '', base)
        base = base.rstrip("-_/ ·•.　")
        return base or text

    @staticmethod
    def _soften_color(rgba, blend=0.6):
        blend = min(max(blend, 0.0), 1.0)
        r, g, b, a = rgba
        return (
            r + (1 - r) * blend,
            g + (1 - g) * blend,
            b + (1 - b) * blend,
            a,
        )

    def _collect_key_focus_layers(self, block_models):
        key_tab = getattr(self.main_win, "key_stratum_tab", None)
        if key_tab is None:
            return set()

        processed_df = getattr(key_tab, "processed_df", None)
        if processed_df is None or processed_df.empty:
            return set()

        if "关键层标记" not in processed_df.columns or "岩层名称" not in processed_df.columns:
            return set()

        key_rows = processed_df[processed_df["关键层标记"].astype(str).str.contains("SK", na=False)]
        if key_rows.empty:
            return set()

        target_keys = {
            self._normalize_layer_key(name)
            for name in key_rows["岩层名称"].dropna().astype(str)
        }

        matched_layers = set()
        for model in block_models:
            layer_name = str(model.get("name", ""))
            if self._normalize_layer_key(layer_name) in target_keys:
                matched_layers.add(layer_name)
        return matched_layers

    def _determine_focus_layers(self, block_models):
        if not block_models:
            return set()

        available_names = {str(m.get("name", "")) for m in block_models}

        if self.preview_filter_mode == "coal":
            focused = {name for name in available_names if "煤" in name}
        elif self.preview_filter_mode == "custom":
            focused = {name for name in self.preview_custom_layers if name in available_names}
        elif self.preview_filter_mode == "key":
            focused = self._collect_key_focus_layers(block_models)
        else:
            focused = set(available_names)

        if not focused:
            return set(available_names)
        return focused

    def on_layer_filter_button_clicked(self):
        selected_layers = self._prompt_custom_layer_selection()
        if not selected_layers:
            return
        self.preview_filter_mode = "custom"
        self.preview_custom_layers = selected_layers
        if self.layer_filter_combo is not None:
            self.layer_filter_combo.blockSignals(True)
            self.layer_filter_combo.setCurrentIndex(2)
            self.layer_filter_combo.blockSignals(False)
        self._layer_filter_prev_index = 2
        self._apply_display_filter()

    def _prompt_custom_layer_selection(self):
        if not self.available_display_layers:
            QMessageBox.information(self, "无可选岩层", "请先生成块体模型后再筛选显示。")
            return None

        dialog = QDialog(self)
        dialog.setWindowTitle("选择显示的岩层")
        dialog.setMinimumWidth(320)

        dlg_layout = QVBoxLayout(dialog)
        info_label = QLabel("勾选要重点高亮的岩层（其他岩层将自动淡化）：")
        info_label.setStyleSheet("color: #475569; font-size: 12px; margin-bottom: 6px;")
        dlg_layout.addWidget(info_label)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        if self.preview_filter_mode == "custom" and self.preview_custom_layers:
            default_selected = set(self.preview_custom_layers)
        elif self.preview_filter_mode == "coal":
            default_selected = {name for name in self.available_display_layers if "煤" in str(name)}
        elif self.preview_filter_mode == "key" and self.last_plot_payload:
            default_selected = self._collect_key_focus_layers(self.last_plot_payload[2])
        else:
            default_selected = set(self.available_display_layers)

        for name in self.available_display_layers:
            item = QListWidgetItem(str(name))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check_state = Qt.CheckState.Checked if name in default_selected else Qt.CheckState.Unchecked
            item.setCheckState(check_state)
            list_widget.addItem(item)

        dlg_layout.addWidget(list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dlg_layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        selected = [list_widget.item(i).text() for i in range(list_widget.count())
                    if list_widget.item(i).checkState() == Qt.CheckState.Checked]

        if not selected:
            QMessageBox.warning(self, "未选择岩层", "请至少选择一个岩层进行显示。")
            return None

        return selected

    def _filter_block_models(self, block_models):
        if not block_models:
            return [], [], set()

        focus_layers = self._determine_focus_layers(block_models)
        if not focus_layers:
            focus_layers = {str(m.get('name', '')) for m in block_models}

        focus_lookup = set(focus_layers)
        focus_models = [m for m in block_models if str(m.get('name', '')) in focus_lookup]

        if not focus_models:
            focus_models = list(block_models)
            focus_lookup = {str(m.get('name', '')) for m in block_models}

        return list(block_models), focus_models, focus_lookup

    def _update_layer_filter_status(self, total, visible):
        if self.layer_filter_status_label is None:
            return
        if total == 0:
            self.layer_filter_status_label.setText("当前：未生成")
            return

        mode_text = {
            "all": "全部岩层",
            "coal": "仅含“煤”",
            "custom": "自定义",
            "key": "关键层优先",
        }.get(self.preview_filter_mode, "全部岩层")

        if self.preview_filter_mode == "all" or visible >= total:
            self.layer_filter_status_label.setText(f"当前：{mode_text}（{total}）")
        else:
            self.layer_filter_status_label.setText(f"当前：{mode_text}高亮（{visible}/{total}）")

    def _apply_display_filter(self):
        if not self.last_plot_payload:
            self.current_display_models = []
            self.current_focus_layers = set()
            self._update_layer_filter_status(0, 0)
            return

        XI, YI, block_models, method_name = self.last_plot_payload
        plot_models, focus_models, focus_layers = self._filter_block_models(block_models)
        total = len(block_models)

        if not focus_layers and block_models:
            QMessageBox.information(
                self,
                "筛选为空",
                "当前筛选条件下没有可高亮的岩层，已恢复为全部显示。",
            )
            self.layer_filter_combo.blockSignals(True)
            self.layer_filter_combo.setCurrentIndex(self._layer_filter_prev_index)
            self.layer_filter_combo.blockSignals(False)
            plot_models, focus_models, focus_layers = self._filter_block_models(block_models)
        else:
            self._layer_filter_prev_index = self.layer_filter_combo.currentIndex()

        self.current_display_models = focus_models
        self.current_focus_layers = set(focus_layers)
        visible = len(focus_layers)
        self._update_layer_filter_status(total, visible)

        self._plot_block_models(XI, YI, plot_models, focus_layers, method_name)
        self._update_seam_table(focus_models)
        self._update_summary_window(focus_models, method_name)

    def _rerender_last_plot(self):
        self._apply_display_filter()

    def show_summary_window(self):
        if not hasattr(self, 'summary_window') or self.summary_window is None:
            return
        self.summary_window.show()
        self.summary_window.raise_()
        self.summary_window.activateWindow()

    def _bind_scroll_event(self, ax):
        if not hasattr(self, 'canvas'):
            return
        if self._scroll_cid is not None:
            try:
                self.canvas.mpl_disconnect(self._scroll_cid)
            except Exception:
                pass
        def _on_scroll(event):
            if event.inaxes is not ax:
                return
            if event.button == 'up':
                ax.dist = max(1.2, ax.dist * 0.9)
            elif event.button == 'down':
                ax.dist = min(40.0, ax.dist * 1.1)
            else:
                return
            self.canvas.draw_idle()
        self._scroll_cid = self.canvas.mpl_connect('scroll_event', _on_scroll)

    def _get_current_axes(self):
        axes = self.canvas.figure.get_axes()
        return axes[0] if axes else None

    def _apply_current_view(self, ax, index=None):
        if index is None:
            index = self.view_combo.currentIndex() if hasattr(self, 'view_combo') else 0

        presets = {
            0: (25, -125, 'persp'),  # 默认透视
            1: (90, -90, 'ortho'),   # 俯视
            2: (15, -180, 'ortho'),  # 北向
            3: (15, -90, 'ortho'),   # 东向
            4: (15, 0, 'ortho'),     # 南向
        }
        elev, azim, proj = presets.get(index, presets[0])
        try:
            ax.set_proj_type(proj)
        except Exception:
            pass
        ax.view_init(elev=elev, azim=azim)
        ax.dist = 9

    def _update_seam_table(self, block_models):
        if not block_models:
            self.seam_summary_lines = []
            return

        summary_lines = []
        for model in block_models:
            summary_lines.append(
                f"<span style='color:#1e3a8a;font-weight:600;'>{model['name']}</span>："
                f"样本 {model['points']} 条 · 平均厚度 {model['avg_thickness']:.2f} m · "
                f"最大厚度 {model['max_thickness']:.2f} m · 顶面均值 {model['avg_height']:.2f} m · "
                f"底面均值 {model['avg_bottom']:.2f} m"
            )

        self.seam_summary_lines = summary_lines

    def _update_summary_window(self, block_models, method_name, auto_show=False):
        if not hasattr(self, 'summary_window') or self.summary_window is None:
            return

        if not block_models or not self.last_plot_payload:
            self.seam_summary_lines = []
            default_html = "<p style='margin:0;'>提示：加载数据后选择岩层并点击“生成煤层块体”。</p>"
            self.summary_window.update_summary(default_html, auto_show=False)
            return

        XI, YI, _, _ = self.last_plot_payload
        x_min, x_max = float(np.nanmin(XI)), float(np.nanmax(XI))
        y_min, y_max = float(np.nanmin(YI)), float(np.nanmax(YI))
        total_points = sum(model['points'] for model in block_models)
        finite_thickness = [model['max_thickness'] for model in block_models if np.isfinite(model['max_thickness'])]
        max_thickness = max(finite_thickness) if finite_thickness else 0.0
        finite_bottoms = [model['min_bottom'] for model in block_models if np.isfinite(model['min_bottom'])]
        finite_tops = [model['max_height'] for model in block_models if np.isfinite(model['max_height'])]
        min_bottom = min(finite_bottoms) if finite_bottoms else 0.0
        max_top = max(finite_tops) if finite_tops else max_thickness

        lines = [
            f"<b>插值方法:</b> {method_name}",
            f"<b>岩层数量:</b> {len(block_models)} 个 · 样本总计 {total_points} 条",
            f"<b>垂向缩放:</b> {self.vertical_scale:.2f}× (滑块可调整)",
            f"<b>场区范围:</b> X {x_min:.1f}~{x_max:.1f} · Y {y_min:.1f}~{y_max:.1f} m",
            f"<b>最大厚度:</b> {max_thickness:.2f} m",
            f"<b>高程范围:</b> {min_bottom:.2f} ~ {max_top:.2f} m"
        ]

        if self.seam_summary_lines:
            lines.append("<b>岩层摘要:</b>")
            lines.extend(self.seam_summary_lines)

        summary_html = "<br>".join(lines)
        self.summary_window.update_summary(summary_html, auto_show=auto_show)

    def _style_3d_axes(self, ax):
        fig = ax.get_figure()
        fig.set_facecolor("#f8fafc")
        fig.subplots_adjust(left=0.04, right=0.86, top=0.88, bottom=0.06)

        for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
            try:
                pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
                pane.set_edgecolor("#e2e8f0")
            except Exception:
                pass

        ax.set_facecolor("#ffffff")
        ax.grid(False)
        ax.tick_params(colors="#475569", labelsize=9)
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            try:
                axis.line.set_color("#cbd5e1")
            except Exception:
                pass

    def _plot_block_models(self, XI, YI, block_models, focus_layers, method_name):
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111, projection='3d')
        self._style_3d_axes(ax)

        if not block_models:
            ax.set_title(f"{method_name} 块体模型 · 无可显示岩层")
            ax.text2D(0.5, 0.5, "当前筛选条件下没有可显示的岩层", transform=ax.transAxes,
                      ha='center', va='center', fontsize=12, color="#475569")
            ax.set_axis_off()
            self._apply_current_view(ax)
            self.canvas.draw_idle()
            return

        focus_lookup = set(focus_layers) if focus_layers else {
            str(model.get('name', '')) for model in block_models
        }
        source_layer_names = (
            list(self.available_display_layers)
            if self.available_display_layers
            else [str(model.get('name', '')) for model in block_models]
        )

        color_manager = getattr(self.main_win, "color_manager", None)
        cmap = plt.get_cmap('tab20')
        category_color_map = {}
        legend_handles = []
        coal_face_rgba = mcolors.to_rgba("#000000")
        focus_top_alpha = 0.90
        focus_bottom_alpha = 0.16
        focus_edge_alpha = 0.60
        focus_edge_linewidth = 0.7
        focus_side_alpha = 0.28
        focus_edge_rgba = mcolors.to_rgba("#1f2937")
        muted_top_alpha = 0.22
        muted_bottom_alpha = 0.05
        muted_edge_alpha = 0.18
        muted_edge_linewidth = 0.4
        muted_side_alpha = 0.12
        muted_edge_rgba = self._soften_color(focus_edge_rgba, blend=0.55)
        coal_focus_top_alpha = 0.96
        coal_focus_bottom_alpha = 0.45
        coal_focus_edge_alpha = 0.95
        coal_focus_linewidth = 0.9
        coal_focus_side_alpha = 0.45
        coal_focus_edge_rgba = coal_face_rgba
        coal_muted_top_alpha = 0.32
        coal_muted_bottom_alpha = 0.08
        coal_muted_edge_alpha = 0.35
        coal_muted_linewidth = 0.55
        coal_muted_side_alpha = 0.20
        coal_muted_edge_rgba = self._soften_color(coal_face_rgba, blend=0.6)
        highlighting_active = bool(focus_lookup and len(focus_lookup) < len(block_models))

        bottom_min_candidates = [np.nanmin(model['bottom_surface']) for model in block_models if np.isfinite(model['bottom_surface']).any()]
        global_min = float(min(bottom_min_candidates)) if bottom_min_candidates else 0.0
        z_min = global_min
        z_max = global_min
        show_edges = getattr(self, 'outline_check', None)
        show_edges_flag = True if show_edges is None else show_edges.isChecked()
        stride = max(1, int(self.preview_stride))
        surface_kwargs = {
            'rstride': stride,
            'cstride': stride,
            'linewidth': 0,
            'antialiased': False,
        }

        for idx, model in enumerate(block_models):
            bottom_surface = np.array(model['bottom_surface'], dtype=float)
            top_surface = np.array(model['top_surface'], dtype=float)
            bottom_surface = np.where(np.isfinite(bottom_surface), bottom_surface, global_min)
            top_surface = np.where(np.isfinite(top_surface), top_surface, bottom_surface)
            top_surface = np.maximum(top_surface, bottom_surface)

            scaled_bottom = global_min + (bottom_surface - global_min) * self.vertical_scale
            scaled_top = scaled_bottom + (top_surface - bottom_surface) * self.vertical_scale
            layer_name = str(model.get('name', ''))
            normalized_key = self._normalize_layer_key(layer_name)
            is_coal_layer = "煤" in layer_name
            is_focus_layer = (not focus_lookup) or (layer_name in focus_lookup)

            if is_coal_layer:
                base_face_color = coal_face_rgba
            elif color_manager is not None:
                qcolor = color_manager.color_for(layer_name)
                base_face_color = mcolors.to_rgba(qcolor.name())
            else:
                base_color = category_color_map.get(normalized_key)
                if base_color is None:
                    base_color = cmap(len(category_color_map) % cmap.N)
                    category_color_map[normalized_key] = base_color
                base_face_color = mcolors.to_rgba(base_color)

            if is_focus_layer:
                face_color = base_face_color
                if is_coal_layer:
                    top_alpha = coal_focus_top_alpha
                    bottom_alpha = coal_focus_bottom_alpha
                    edge_color = coal_focus_edge_rgba
                    edge_alpha = coal_focus_edge_alpha
                    edge_linewidth = coal_focus_linewidth
                    side_alpha = coal_focus_side_alpha
                else:
                    top_alpha = focus_top_alpha
                    bottom_alpha = focus_bottom_alpha
                    edge_color = focus_edge_rgba
                    edge_alpha = focus_edge_alpha
                    edge_linewidth = focus_edge_linewidth
                    side_alpha = focus_side_alpha
            else:
                face_color = self._soften_color(base_face_color, blend=0.6)
                if is_coal_layer:
                    top_alpha = coal_muted_top_alpha
                    bottom_alpha = coal_muted_bottom_alpha
                    edge_color = coal_muted_edge_rgba
                    edge_alpha = coal_muted_edge_alpha
                    edge_linewidth = coal_muted_linewidth
                    side_alpha = coal_muted_side_alpha
                else:
                    top_alpha = muted_top_alpha
                    bottom_alpha = muted_bottom_alpha
                    edge_color = muted_edge_rgba
                    edge_alpha = muted_edge_alpha
                    edge_linewidth = muted_edge_linewidth
                    side_alpha = muted_side_alpha

            ax.plot_surface(
                XI,
                YI,
                scaled_top,
                color=face_color,
                alpha=top_alpha,
                shade=True,
                **surface_kwargs,
            )
            ax.plot_surface(
                XI,
                YI,
                scaled_bottom,
                color=face_color,
                alpha=bottom_alpha,
                shade=False,
                **surface_kwargs,
            )

            if show_edges_flag:
                edge_sets = [
                    (XI[0, ::stride], YI[0, ::stride], scaled_top[0, ::stride]),
                    (XI[-1, ::stride], YI[-1, ::stride], scaled_top[-1, ::stride]),
                    (XI[::stride, 0], YI[::stride, 0], scaled_top[::stride, 0]),
                    (XI[::stride, -1], YI[::stride, -1], scaled_top[::stride, -1])
                ]
                for x_edge, y_edge, z_edge in edge_sets:
                    ax.plot(x_edge, y_edge, z_edge, color=edge_color, linewidth=edge_linewidth, alpha=edge_alpha)

                side_faces = []
                side_faces.append([
                    (XI[0, 0], YI[0, 0], scaled_bottom[0, 0]),
                    (XI[0, -1], YI[0, -1], scaled_bottom[0, -1]),
                    (XI[0, -1], YI[0, -1], scaled_top[0, -1]),
                    (XI[0, 0], YI[0, 0], scaled_top[0, 0])
                ])
                side_faces.append([
                    (XI[-1, 0], YI[-1, 0], scaled_bottom[-1, 0]),
                    (XI[-1, -1], YI[-1, -1], scaled_bottom[-1, -1]),
                    (XI[-1, -1], YI[-1, -1], scaled_top[-1, -1]),
                    (XI[-1, 0], YI[-1, 0], scaled_top[-1, 0])
                ])
                side_faces.append([
                    (XI[0, 0], YI[0, 0], scaled_bottom[0, 0]),
                    (XI[-1, 0], YI[-1, 0], scaled_bottom[-1, 0]),
                    (XI[-1, 0], YI[-1, 0], scaled_top[-1, 0]),
                    (XI[0, 0], YI[0, 0], scaled_top[0, 0])
                ])
                side_faces.append([
                    (XI[0, -1], YI[0, -1], scaled_bottom[0, -1]),
                    (XI[-1, -1], YI[-1, -1], scaled_bottom[-1, -1]),
                    (XI[-1, -1], YI[-1, -1], scaled_top[-1, -1]),
                    (XI[0, -1], YI[0, -1], scaled_top[0, -1])
                ])
                poly = Poly3DCollection(side_faces, facecolors=face_color, alpha=side_alpha, linewidths=0)
                poly.set_edgecolor(edge_color)
                ax.add_collection3d(poly)

            legend_label = (
                f"{model['name']} · {model['points']}点 · 厚度{model['avg_thickness']:.2f}m · "
                f"顶面均值{model['avg_height']:.1f}m"
            )
            if is_coal_layer or (highlighting_active and is_focus_layer):
                legend_label = f"★ {legend_label}"
            legend_handles.append(mpatches.Patch(color=face_color, alpha=top_alpha, label=legend_label))

            with np.errstate(invalid='ignore'):
                z_min = min(z_min, float(np.nanmin(scaled_bottom)))
            z_max = max(z_max, float(np.nanmax(scaled_top)))

        ax.set_xlabel(self.x_col_combo.currentText())
        ax.set_ylabel(self.y_col_combo.currentText())
        ax.set_zlabel("块体标高 (m)")
        ax.set_title(f"{method_name} 块体模型 · 垂向×{self.vertical_scale:.2f}")

        if z_max <= z_min:
            z_max = z_min + 1.0
        ax.set_zlim(z_min, z_max * 1.05)
        ax.set_box_aspect((np.ptp(XI) if np.ptp(XI) > 0 else 1,
                           np.ptp(YI) if np.ptp(YI) > 0 else 1,
                           (z_max - z_min) if (z_max - z_min) > 0 else 1))

        if legend_handles:
            legend = ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.02, 1.0))
            if legend:
                legend.set_title(None)
                legend.get_frame().set_facecolor('#ffffff')
                legend.get_frame().set_edgecolor('#e2e8f0')
                for text in legend.get_texts():
                    if self.canvas._contains_chinese(text.get_text()):
                        text.set_fontproperties(self.canvas.chinese_font)
                    else:
                        text.set_fontproperties(self.canvas.english_font)

        self._apply_current_view(ax)
        self._bind_scroll_event(ax)
        self.canvas.apply_mixed_fonts(ax)
        self.canvas.draw_idle()

    def export_plot(self):
        if not self.canvas.figure.get_axes() or not self.last_plot_payload:
            QMessageBox.warning(self, "无图表", "请先生成煤层块体模型后再导出。")
            return

        format_box = QMessageBox(self)
        format_box.setWindowTitle("选择导出类型")
        format_box.setText("请选择导出的文件类型：")
        static_btn = format_box.addButton("静态图像", QMessageBox.ButtonRole.ActionRole)
        interactive_btn = format_box.addButton("交互式模型", QMessageBox.ButtonRole.ActionRole)
        format_box.addButton(QMessageBox.StandardButton.Cancel)
        format_box.exec()

        clicked = format_box.clickedButton()
        if clicked == static_btn:
            self._export_static_image()
        elif clicked == interactive_btn:
            self._export_interactive_html()

    def _export_static_image(self):
        output_dir = os.path.join(os.getcwd(), "output", "blocks")
        os.makedirs(output_dir, exist_ok=True)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存块体图像",
            os.path.join(output_dir, "煤层块体模型.png"),
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)"
        )

        if not save_path:
            return

        try:
            for ax in self.canvas.figure.get_axes():
                self.canvas.apply_mixed_fonts(ax)

            save_kwargs = {
                'dpi': 300,
                'bbox_inches': 'tight',
                'facecolor': 'white',
                'edgecolor': 'none'
            }
            if save_path.lower().endswith('.pdf'):
                import matplotlib
                matplotlib.rcParams['pdf.fonttype'] = 42
            self.canvas.figure.savefig(save_path, **save_kwargs)
            QMessageBox.information(self, "导出成功", f"图像已保存到:\n{save_path}")
            if QMessageBox.question(self, "打开图像", "是否打开保存位置？") == QMessageBox.StandardButton.Yes:
                open_file_auto(save_path)
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"保存图像时发生错误: {e}")

    def _export_interactive_html(self):
        if not self.last_plot_payload:
            QMessageBox.warning(self, "无数据", "请先生成煤层块体模型后再导出。")
            return

        try:
            import plotly.graph_objects as go
            import plotly.io as pio
        except ImportError:
            QMessageBox.critical(
                self,
                "缺少依赖",
                "生成交互式模型需要安装 Plotly。\n可在终端中执行: pip install plotly"
            )
            return

        XI, YI, block_models, method_name = self.last_plot_payload
        if not block_models:
            QMessageBox.warning(self, "无数据", "当前没有可导出的块体模型。")
            return

        output_dir = os.path.join(os.getcwd(), "output", "blocks")
        os.makedirs(output_dir, exist_ok=True)
        default_name = os.path.join(output_dir, "煤层块体模型_交互版.html")
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存交互式模型",
            default_name,
            "HTML 文件 (*.html)"
        )

        if not save_path:
            return

        try:
            fig = go.Figure()
            color_manager = getattr(self.main_win, "color_manager", None)
            fallback_cmap = plt.get_cmap('tab20')
            fallback_palette = list(getattr(fallback_cmap, "colors", []))
            if not fallback_palette:
                palette_size = getattr(fallback_cmap, "N", 0) or 8
                fallback_palette = [fallback_cmap(i / max(palette_size - 1, 1)) for i in range(palette_size)]
            fallback_color_map = {}

            bottom_min_candidates = [
                np.nanmin(np.array(model['bottom_surface'], dtype=float))
                for model in block_models
                if np.isfinite(model['bottom_surface']).any()
            ]
            global_min = float(min(bottom_min_candidates)) if bottom_min_candidates else 0.0
            vertical_scale = max(self.vertical_scale, 0.1)

            x_flat = XI.flatten().astype(float)
            y_flat = YI.flatten().astype(float)
            finite_anchor_mask = np.isfinite(x_flat) & np.isfinite(y_flat)
            if np.any(finite_anchor_mask):
                anchor_index = int(np.flatnonzero(finite_anchor_mask)[0])
                anchor_x = float(x_flat[anchor_index])
                anchor_y = float(y_flat[anchor_index])
            else:
                anchor_x = 0.0
                anchor_y = 0.0

            scaled_z_values = []

            for idx, model in enumerate(block_models):
                bottom_surface = np.array(model['bottom_surface'], dtype=float)
                top_surface = np.array(model['top_surface'], dtype=float)

                bottom_surface = np.where(np.isfinite(bottom_surface), bottom_surface, global_min)
                top_surface = np.where(np.isfinite(top_surface), top_surface, bottom_surface)
                top_surface = np.maximum(top_surface, bottom_surface)

                scaled_bottom = global_min + (bottom_surface - global_min) * vertical_scale
                scaled_top = scaled_bottom + (top_surface - bottom_surface) * vertical_scale

                seam_name = str(model.get('name', ''))
                if color_manager is not None:
                    qcolor = color_manager.color_for(seam_name)
                    base_rgba = mcolors.to_rgba(qcolor.name())
                else:
                    key = self._normalize_layer_key(seam_name)
                    if key not in fallback_color_map:
                        palette_index = len(fallback_color_map) % len(fallback_palette)
                        fallback_color_map[key] = fallback_palette[palette_index]
                    base_rgba = fallback_color_map[key]

                rgb = base_rgba[:3]
                rgb_full = f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 1.0)"
                rgb_faint = f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.35)"
                legend_label = (
                    f"{model['name']} · 样本{model['points']} · 平均厚度{model['avg_thickness']:.2f}m"
                )

                color_scale_full = [[0, rgb_full], [1, rgb_full]]
                color_scale_faint = [[0, rgb_faint], [1, rgb_faint]]

                scaled_z_values.extend(scaled_top.flatten())
                scaled_z_values.extend(scaled_bottom.flatten())

                top_flat = scaled_top.flatten().astype(float)
                finite_top_mask = np.isfinite(top_flat)
                if np.any(finite_top_mask):
                    anchor_z = float(top_flat[np.flatnonzero(finite_top_mask)[0]])
                else:
                    anchor_z = float(global_min)

                fig.add_surface(
                    x=XI,
                    y=YI,
                    z=scaled_top,
                    surfacecolor=np.full_like(scaled_top, idx, dtype=float),
                    colorscale=color_scale_full,
                    showscale=False,
                    opacity=0.93,
                    name=model['name'],
                    legendgroup=model['name']
                )

                fig.add_surface(
                    x=XI,
                    y=YI,
                    z=scaled_bottom,
                    surfacecolor=np.full_like(scaled_bottom, idx + 0.01, dtype=float),
                    colorscale=color_scale_faint,
                    showscale=False,
                    opacity=0.48,
                    name=f"{model['name']} 底面",
                    legendgroup=model['name']
                )

                fig.add_trace(
                    go.Scatter3d(
                        x=[anchor_x],
                        y=[anchor_y],
                        z=[anchor_z],
                        mode='markers',
                        marker=dict(size=4, color=rgb_full, opacity=0),
                        showlegend=True,
                        name=legend_label,
                        legendgroup=model['name'],
                        hoverinfo='skip'
                    )
                )

            scaled_z_values = np.asarray(scaled_z_values, dtype=float)
            finite_mask = np.isfinite(scaled_z_values)
            if finite_mask.any():
                z_min = float(np.nanmin(scaled_z_values[finite_mask]))
                z_max = float(np.nanmax(scaled_z_values[finite_mask]))
            else:
                z_min, z_max = 0.0, 1.0

            if not np.isfinite(z_min) or not np.isfinite(z_max) or z_min == z_max:
                z_min, z_max = 0.0, max(1.0, float(vertical_scale))

            fig.update_layout(
                title=f"{method_name} 煤层块体模型 (交互导出)",
                template='plotly_white',
                legend=dict(bgcolor='rgba(255,255,255,0.88)', itemsizing='constant'),
                margin=dict(l=20, r=20, t=60, b=10),
                scene=dict(
                    xaxis_title=self.x_col_combo.currentText(),
                    yaxis_title=self.y_col_combo.currentText(),
                    zaxis_title="块体标高 (m)",
                    xaxis=dict(backgroundcolor='rgb(248,250,252)', gridcolor='white', showbackground=True, zerolinecolor='#cbd5e1'),
                    yaxis=dict(backgroundcolor='rgb(248,250,252)', gridcolor='white', showbackground=True, zerolinecolor='#cbd5e1'),
                    zaxis=dict(
                        backgroundcolor='rgb(248,250,252)',
                        gridcolor='white',
                        showbackground=True,
                        zerolinecolor='#cbd5e1',
                        range=[z_min, z_max]
                    ),
                    aspectmode='data',
                    camera=dict(eye=dict(x=1.6, y=1.6, z=0.9))
                ),
                hovermode='closest'
            )

            fig.add_annotation(
                text=f"垂向缩放: ×{vertical_scale:.2f} · 拖拽旋转，滚轮缩放",
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0,
                y=-0.12,
                font=dict(color='#475569', size=11)
            )

            pio.write_html(fig, file=save_path, include_plotlyjs='cdn', auto_open=False, full_html=True)

            QMessageBox.information(self, "导出成功", f"交互式模型已保存到:\n{save_path}")
            if QMessageBox.question(self, "打开模型", "是否立即打开查看？") == QMessageBox.StandardButton.Yes:
                open_file_auto(save_path)
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"生成交互式模型时发生错误: {e}")

    def _update_status(self, message, color="#2563eb"):
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px; line-height: 1.4;")
        self.status_label.setText(message)


class InterpolationComparisonDialog(QDialog):
    def __init__(self, parent, aggregated_results, seam_details, validation_ratio, skipped_messages):
        super().__init__(parent)
        self.aggregated_results = aggregated_results
        self.seam_details = seam_details
        self.validation_ratio = validation_ratio
        self.skipped_messages = skipped_messages or []
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("煤层块体插值方法对比结果")
        self.resize(920, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        best_method = self.aggregated_results[0]
        if best_method['avg_r2'] > -900:
            summary_text = (
                f"推荐方法: <b>{best_method['method_name']}</b> · 平均R² = {best_method['avg_r2']:.3f} · "
                f"平均RMSE = {best_method['avg_rmse']:.3f}"
            )
        else:
            summary_text = (
                f"推荐方法: <b>{best_method['method_name']}</b> · 平均RMSE = {best_method['avg_rmse']:.3f}"
            )
        summary_label = QLabel(summary_text)
        summary_label.setTextFormat(Qt.TextFormat.RichText)
        summary_label.setStyleSheet("font-size: 14px; color: #1d4ed8;")
        layout.addWidget(summary_label)

        info_label = QLabel(
            f"验证比例: {int(self.validation_ratio * 100)}% · 覆盖煤层 {best_method['seam_count']} 个 · "
            f"有效预测点 {best_method['total_valid_points']} / 样本总数 {best_method['total_samples']}"
        )
        info_label.setStyleSheet("color: #475569; font-size: 12px;")
        layout.addWidget(info_label)

        if self.skipped_messages:
            skipped_label = QLabel("\n".join(self.skipped_messages[:4]))
            skipped_label.setStyleSheet("color: #dc2626; font-size: 11px;")
            skipped_label.setWordWrap(True)
            layout.addWidget(skipped_label)

        tabs = QTabWidget()
        layout.addWidget(tabs, 1)

        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(8)

        self.summary_table = QTableWidget(len(self.aggregated_results), 8)
        self.summary_table.setHorizontalHeaderLabels([
            "排名", "插值方法", "平均MAE", "平均RMSE", "平均R²", "平均MAPE(%)",
            "10%准确率(%)", "5%准确率(%)"
        ])
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.summary_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.summary_table.setAlternatingRowColors(True)

        for row, result in enumerate(self.aggregated_results):
            self.summary_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.summary_table.setItem(row, 1, QTableWidgetItem(result['method_name']))
            self.summary_table.setItem(row, 2, QTableWidgetItem(f"{result['avg_mae']:.4f}"))
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"{result['avg_rmse']:.4f}"))
            r2_text = "--" if result['avg_r2'] <= -900 else f"{result['avg_r2']:.4f}"
            self.summary_table.setItem(row, 4, QTableWidgetItem(r2_text))
            mape_text = "--" if np.isinf(result['avg_mape']) else f"{result['avg_mape']:.2f}"
            self.summary_table.setItem(row, 5, QTableWidgetItem(mape_text))
            self.summary_table.setItem(row, 6, QTableWidgetItem(f"{result['avg_accuracy_10']:.2f}"))
            self.summary_table.setItem(row, 7, QTableWidgetItem(f"{result['avg_accuracy_5']:.2f}"))

        self.summary_table.resizeColumnsToContents()
        summary_layout.addWidget(self.summary_table)

        stats_label = QLabel(
            f"平均指标基于 {self.aggregated_results[0]['seam_count']} 个煤层、"
            f"{self.aggregated_results[0]['total_valid_points']} 个有效预测点"
        )
        stats_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        summary_layout.addWidget(stats_label)

        tabs.addTab(summary_tab, "汇总排名")

        detail_tab = QWidget()
        detail_layout = QVBoxLayout(detail_tab)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(8)

        headers = ["煤层", "插值方法", "状态", "MAE", "RMSE", "R²", "MAPE(%)", "10%准确率(%)", "5%准确率(%)", "样本(总/训/验)", "有效点数"]
        self.detail_table = QTableWidget(len(self.seam_details), len(headers))
        self.detail_table.setHorizontalHeaderLabels(headers)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.detail_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.detail_table.setAlternatingRowColors(True)

        for row, detail in enumerate(self.seam_details):
            self.detail_table.setItem(row, 0, QTableWidgetItem(str(detail.get('seam', '-'))))
            self.detail_table.setItem(row, 1, QTableWidgetItem(detail.get('method_name', '-')))
            self.detail_table.setItem(row, 2, QTableWidgetItem(detail.get('status', '')))

            def format_value(key, precision=4, default="--"):
                value = detail.get(key)
                if value is None or (isinstance(value, float) and np.isnan(value)):
                    return default
                return f"{value:.{precision}f}"

            self.detail_table.setItem(row, 3, QTableWidgetItem(format_value('mae')))
            self.detail_table.setItem(row, 4, QTableWidgetItem(format_value('rmse')))
            r2_val = detail.get('r2')
            r2_text = "--" if r2_val is None or r2_val <= -900 else f"{r2_val:.4f}"
            self.detail_table.setItem(row, 5, QTableWidgetItem(r2_text))
            mape_val = detail.get('mape')
            mape_text = "--" if mape_val is None or np.isinf(mape_val) or np.isnan(mape_val) else f"{mape_val:.2f}"
            self.detail_table.setItem(row, 6, QTableWidgetItem(mape_text))
            self.detail_table.setItem(row, 7, QTableWidgetItem(format_value('accuracy_10', precision=2)))
            self.detail_table.setItem(row, 8, QTableWidgetItem(format_value('accuracy_5', precision=2)))

            sample_text = f"{detail.get('total_points', 0)}/{detail.get('train_points', 0)}/{detail.get('val_points', 0)}"
            self.detail_table.setItem(row, 9, QTableWidgetItem(sample_text))
            self.detail_table.setItem(row, 10, QTableWidgetItem(str(detail.get('n_valid', 0))))

        self.detail_table.resizeColumnsToContents()
        detail_layout.addWidget(self.detail_table)

        tabs.addTab(detail_tab, "煤层详细")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box, 0, Qt.AlignmentFlag.AlignRight)


class PlaceholderModuleWidget(QWidget):
    """占位模块，用于提示后续规划功能"""

    def __init__(self, title: str, description: str = "功能建设中，敬请期待。", parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(24)

        headline = QLabel(f"{title}")
        headline.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")
        layout.addWidget(headline, 0, Qt.AlignmentFlag.AlignHCenter)

        subtitle = QLabel(description)
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #475569; font-size: 14px; line-height: 1.6;")
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("placeholderCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)

        road_map = QLabel(
            "\n".join([
                "\u2022 功能需求调研与方案设计",
                "\u2022 数据模型与算法选型",
                "\u2022 与现有模块的数据联动",
                "\u2022 可视化与交互界面设计",
            ])
        )
        road_map.setStyleSheet("color: #334155; font-size: 13px; line-height: 1.8;")
        road_map.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        card_layout.addWidget(road_map)

        layout.addWidget(card, 1)


class ModulePage(QWidget):
    """顶层功能模块容器，内部可切换子功能"""

    def __init__(self, module_name: str, description: str, features: List[dict]):
        super().__init__()
        self.module_name = module_name
        self.features = features
        self._feature_lookup = {}
        self.tab_widget = None
        self._init_ui(description)

    def _init_ui(self, description: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        title_label = QLabel(self.module_name)
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #475569; font-size: 14px; line-height: 1.6;")
            header_layout.addWidget(desc_label)

        layout.addWidget(header, 0)

        if not self.features:
            placeholder = PlaceholderModuleWidget("功能规划中")
            layout.addWidget(placeholder, 1)
            return

        if len(self.features) == 1:
            feature = self.features[0]
            widget = feature.get("widget")
            if widget is None:
                widget = PlaceholderModuleWidget(feature.get("title", "功能规划中"))
            widget.setParent(self)
            layout.addWidget(widget, 1)
            self._feature_lookup[feature.get("title", "")] = widget
        else:
            tabs = QTabWidget()
            tabs.setDocumentMode(True)
            tabs.setTabPosition(QTabWidget.TabPosition.North)
            tabs.setObjectName("moduleTab")
            for feature in self.features:
                title = feature.get("title", "子功能")
                widget = feature.get("widget")
                if widget is None:
                    widget = PlaceholderModuleWidget(title)
                widget.setParent(tabs)
                tabs.addTab(widget, title)
                summary = feature.get("summary")
                if summary:
                    tabs.setTabToolTip(tabs.count() - 1, summary)
                self._feature_lookup[title] = widget
            layout.addWidget(tabs, 1)
            self.tab_widget = tabs
        layout.addStretch(0)

    def activate_feature(self, feature_title: Optional[str] = None):
        if not feature_title:
            return
        widget = self._feature_lookup.get(feature_title)
        if widget is None:
            return
        if self.tab_widget is not None:
            index = self.tab_widget.indexOf(widget)
            if index != -1:
                self.tab_widget.setCurrentIndex(index)


class MainWindow(QMainWindow):
    def __init__(self, app_config, username):
        super().__init__()
        self.app_config = app_config
        self.current_user = username
        self.setWindowTitle("矿山工程关键层分析与可视化系统 v3.3")
        self.setGeometry(120, 80, 1380, 840)
        self.setMinimumSize(1180, 720)
        self.app_icon = self._load_app_icon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)
        
        self.color_manager = LithologyColorManager(
            palette=self.app_config.color_scheme.lithology_palette,
            default_palette=self.app_config.color_scheme.default_palette,
        )

        self.rock_db = None  # 聚合后的岩石数据库
        self.rock_db_raw = None  # 原始样本数据库
        self.custom_rock_db = None  # 用户自建的力学参数库
        self.custom_rock_db_path: Optional[str] = None
        self.stat_preference = "median"  # 填充参数时默认使用的统计指标
        self._load_rock_database()  # 加载数据库

        self.nav_items = []
        self.nav_list = None
        self.content_stack = None
        self.current_page_title = ""
        self.current_page_hint = ""
        self.global_status_label = None
        self.page_title_label = None
        self.page_hint_label = None
        self.clock_label = None
        self.clock_timer = None
        self.dashboard_page = None
        self.db_overview_page = None
        self.module_pages = {}

        self.apply_stylesheet()
        self.init_ui()
        self.center_window()

    def _load_app_icon(self) -> QIcon:
        icon_path = resolve_app_icon_path()
        if icon_path:
            return QIcon(icon_path)
        return QIcon()

    def _load_rock_database(self):
        """在程序启动时加载岩石属性数据库。"""
        db_path = resource_path(os.path.join('data', 'output', 'rock_properties_database.csv'))
        self.rock_db = None
        aggregated_loaded = False
        try:
            if os.path.exists(db_path):
                encodings_to_try = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
                for encoding in encodings_to_try:
                    try:
                        self.rock_db = pd.read_csv(db_path, encoding=encoding)
                        aggregated_loaded = True
                        print(f"✓ 岩石属性数据库加载成功 (使用{encoding}编码，{len(self.rock_db)}条记录)。")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"使用{encoding}编码加载数据库时发生错误: {e}")
                        continue

                if not aggregated_loaded:
                    print(f"错误: 无法使用任何编码加载数据库文件: {db_path}")
                    self.rock_db = None
            else:
                print(f"警告: 未找到岩石属性数据库文件: {db_path}")
                print("尝试自动生成数据库...")
                try:
                    from create_database import create_rock_database
                    candidate_inputs = [
                        os.path.join('data', 'input', '汇总表.csv'),
                        os.path.join('data', 'input', 'huizongbiao.csv'),
                        '汇总表.csv',
                    ]
                    input_path = None
                    for candidate in candidate_inputs:
                        candidate_path = resource_path(candidate)
                        if os.path.exists(candidate_path):
                            input_path = candidate_path
                            break

                    if input_path and os.path.exists(input_path):
                        create_rock_database(input_path, db_path)
                        if os.path.exists(db_path):
                            print("数据库生成完成，正在重新加载...")
                            for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                                try:
                                    self.rock_db = pd.read_csv(db_path, encoding=encoding)
                                    aggregated_loaded = True
                                    print(f"✓ 数据库自动生成并加载成功 (使用{encoding}编码，{len(self.rock_db)}条记录)。")
                                    break
                                except UnicodeDecodeError:
                                    continue
                                except Exception as e:
                                    print(f"重新加载时使用{encoding}编码发生错误: {e}")
                                    continue

                            if not aggregated_loaded:
                                print("错误: 数据库生成成功但无法重新加载")
                                self.rock_db = None
                        else:
                            print("错误: 数据库生成失败")
                            self.rock_db = None
                    else:
                        print("错误: 无法自动生成数据库，未找到 '汇总表.csv' 或 'huizongbiao.csv' 源文件。")
                        self.rock_db = None
                except ImportError:
                    print("错误: 无法导入 'create_database' 模块。请确保 create_database.py 文件存在。")
                    self.rock_db = None
                except Exception as creation_error:
                    print(f"自动生成数据库时发生错误: {creation_error}")
                    self.rock_db = None

        except Exception as e:
            print(f"加载岩石数据库时发生未预期的错误: {e}")
            self.rock_db = None

        # 无论聚合数据库是否加载成功，都尝试加载原始样本数据库
        self._load_raw_source_database()

        # 使用原始样本动态生成归并后的聚合视图（包含平均值与中位数）
        if self.rock_db_raw is not None and not self.rock_db_raw.empty:
            aggregated_view = self._aggregate_raw_database(self.rock_db_raw)
            if aggregated_view is not None and not aggregated_view.empty:
                self.rock_db = aggregated_view
                print(f"✓ 已根据原始样本重建归并后的岩石属性数据库（{len(self.rock_db)} 条归并岩性）。")

    def _load_raw_source_database(self):
        """加载包含省份、矿名等信息的原始样本数据库。"""
        self.rock_db_raw = None

        candidate_inputs = [
            os.path.join('data', 'input', '汇总表.csv'),
            os.path.join('data', 'input', 'huizongbiao.csv'),
            '汇总表.csv',
        ]

        source_path = None
        for candidate in candidate_inputs:
            candidate_path = resource_path(candidate)
            if os.path.exists(candidate_path):
                source_path = candidate_path
                break

        if source_path is None:
            print("提示: 未找到原始岩石数据库源文件，无法加载省份与矿井信息。")
            return

        encodings_to_try = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
        raw_df = None
        for encoding in encodings_to_try:
            try:
                raw_df = pd.read_csv(source_path, encoding=encoding)
                print(f"✓ 原始岩石数据库加载成功 (使用{encoding}编码，{len(raw_df)}条记录)。")
                break
            except UnicodeDecodeError:
                continue
            except Exception as exc:
                print(f"读取原始数据库时使用{encoding}编码发生错误: {exc}")
                continue

        if raw_df is None:
            print(f"错误: 无法读取原始岩石数据库源文件: {source_path}")
            return

        raw_df.columns = [str(col).strip() for col in raw_df.columns]
        raw_df = raw_df.loc[:, [col for col in raw_df.columns if col and not str(col).startswith('Unnamed')]]

        rename_map: Dict[str, str] = {}
        for col in raw_df.columns:
            clean_col = str(col).strip()
            if clean_col == '份':
                rename_map[col] = '省份'
            elif clean_col in {'省份', '省', '省市', '所属省', '所在省份', '所在省'}:
                rename_map[col] = '省份'
            elif clean_col in {'市/县', '市县', '地市'}:
                rename_map[col] = '地市'
            elif clean_col in {'矿井', '矿山', '矿山名称', '矿井名称', '矿名'}:
                rename_map[col] = '矿名'
            else:
                normalized = (
                    clean_col
                    .replace('（', '(')
                    .replace('）', ')')
                    .replace('㎥', 'm3')
                    .replace('㎥', 'm3')
                    .replace('·', '·')
                    .replace('　', '')
                    .replace(' ', '')
                )
                rename_map[col] = normalized

        raw_df = raw_df.rename(columns=rename_map)
        raw_df = raw_df.loc[:, ~raw_df.columns.duplicated()]
        raw_df = raw_df.dropna(axis=1, how='all')

        if '省份' not in raw_df.columns:
            raw_df['省份'] = pd.NA

        str_columns = ['文献', '矿名', '省份', '地市', '岩性', '岩层名称', '岩层', '岩石名称']
        for col in [c for c in str_columns if c in raw_df.columns]:
            raw_df[col] = raw_df[col].astype(str).str.strip()
            raw_df[col] = raw_df[col].replace({'nan': pd.NA, 'None': pd.NA, '': pd.NA})

        numeric_candidates = [col for col in raw_df.columns if col not in str_columns]
        for col in numeric_candidates:
            if raw_df[col].dtype == object:
                cleaned_series = (
                    raw_df[col]
                    .astype(str)
                    .str.replace(',', '', regex=False)
                    .str.replace('，', '', regex=False)
                    .str.replace(' ', '', regex=False)
                )
                numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                if numeric_series.notna().sum() > 0:
                    raw_df[col] = numeric_series
                else:
                    # 保留原始字符串列（可能为分类信息）
                    continue

        self.rock_db_raw = raw_df
        self.rock_db_raw_path = source_path
        print(f"✓ 已加载原始岩石样本数据库：{os.path.relpath(source_path, resource_path(''))} · 字段数 {len(raw_df.columns)}")

    def _aggregate_raw_database(self, raw_df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """基于原始样本数据生成聚合后的岩性参数视图。"""
        if raw_df is None or raw_df.empty:
            return None

        lithology_candidates = ['岩性', '岩层名称', '岩层', '岩石名称', '岩层名']
        lithology_col = None
        normalized_columns = {
            col: str(col).strip().replace('（', '(').replace('）', ')').replace(' ', '').lower()
            for col in raw_df.columns
        }

        for candidate in lithology_candidates:
            normalized_candidate = candidate.replace('（', '(').replace('）', ')').replace(' ', '').lower()
            for col, normalized in normalized_columns.items():
                if normalized == normalized_candidate:
                    lithology_col = col
                    break
            if lithology_col is not None:
                break

        if lithology_col is None:
            print("提示: 原始数据集中缺少岩性字段，无法生成聚合数据库。")
            return None

        df = raw_df.copy()
        df[lithology_col] = df[lithology_col].astype(str).str.strip()
        df = df[df[lithology_col].notna() & (df[lithology_col] != '') & (df[lithology_col].str.lower() != 'nan')]

        if df.empty:
            print("提示: 原始数据中的岩性字段为空，无法生成聚合数据库。")
            return None

        def normalize_label(value: Any) -> str:
            if value is None:
                return ''
            label = str(value).strip()
            if not label or label.lower() in {'nan', 'none', 'null'}:
                return ''
            if '煤' in label:
                return '煤类'
            if '土' in label:
                return '土类'
            return label

        normalized_col = '__normalized_lithology__'
        df[normalized_col] = df[lithology_col].map(normalize_label)
        df = df[df[normalized_col] != '']

        if df.empty:
            print("提示: 原始数据中的岩性字段在归一化后为空，无法生成聚合数据库。")
            return None

        string_columns = {'文献', '矿名', '省份', '地市', lithology_col, normalized_col}
        numeric_columns: List[str] = []

        for col in df.columns:
            if col in string_columns:
                continue

            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                if series.notna().sum() > 0:
                    numeric_columns.append(col)
                continue

            cleaned = (
                series.astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('，', '', regex=False)
                .str.replace(' ', '', regex=False)
            )
            numeric_series = pd.to_numeric(cleaned, errors='coerce')
            if numeric_series.notna().sum() > 0:
                df[col] = numeric_series
                numeric_columns.append(col)

        grouped = df.groupby(normalized_col)

        stats_df = None
        if numeric_columns:
            stats_df = grouped[numeric_columns].agg(['mean', 'median'])
            stats_df.columns = [
                f"{col}({'平均值' if stat == 'mean' else '中位数'})"
                for col, stat in stats_df.columns
            ]
            stats_df = stats_df.dropna(axis=1, how='all')

        if stats_df is None or stats_df.empty:
            stats_df = grouped.size().to_frame(name='样本数')

        stats_df = stats_df.reset_index().rename(columns={normalized_col: '岩性'})

        sample_counts = grouped.size()
        stats_df['样本数'] = stats_df['岩性'].map(sample_counts)

        def join_unique(series: pd.Series) -> str:
            unique_values = sorted({str(v).strip() for v in series.dropna() if str(v).strip()})
            return '、'.join(unique_values)

        original_name_map = grouped[lithology_col].apply(join_unique)
        stats_df['原始名称'] = stats_df['岩性'].map(original_name_map).replace({'': pd.NA})

        if '文献' in df.columns:
            reference_counts = grouped['文献'].nunique(dropna=True)
            stats_df['文献来源数'] = stats_df['岩性'].map(reference_counts)

        if '矿名' in df.columns:
            mine_counts = grouped['矿名'].nunique(dropna=True)
            stats_df['矿井数量'] = stats_df['岩性'].map(mine_counts)

        if '省份' in df.columns:
            province_map = grouped['省份'].apply(join_unique)
            stats_df['省份覆盖'] = stats_df['岩性'].map(province_map).replace({'': pd.NA})

        if '原始名称' in stats_df.columns:
            stats_df = stats_df.drop(columns=['原始名称'])

        if '省份覆盖' in stats_df.columns:
            stats_df.insert(0, '省份', stats_df['省份覆盖'])
            stats_df = stats_df.drop(columns=['省份覆盖'])
        else:
            stats_df.insert(0, '省份', pd.NA)

        value_columns = [
            col for col in stats_df.columns
            if col not in {'省份', '岩性', '样本数', '文献来源数', '矿井数量'}
        ]
        tail_columns = [col for col in ['样本数', '矿井数量', '文献来源数'] if col in stats_df.columns]
        ordered_columns = [col for col in ['省份', '岩性'] if col in stats_df.columns] + sorted(value_columns) + tail_columns
        ordered_columns = [col for col in ordered_columns if col in stats_df.columns]
        stats_df = stats_df[ordered_columns]

        return stats_df.sort_values('岩性').reset_index(drop=True)

    def _save_rock_database(self, df=None):
        """保存岩石属性数据库到文件"""
        try:
            if df is None:
                df = self.rock_db
            
            if df is None or df.empty:
                raise ValueError("没有数据可以保存")
            
            db_path = resource_path(os.path.join('data', 'output', 'rock_properties_database.csv'))
            
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 保存为UTF-8编码
            df.to_csv(db_path, index=False, encoding='utf-8-sig')
            
            # 更新当前数据库
            self.rock_db = df
            if hasattr(self, "rock_lookup_page") and self.rock_lookup_page is not None:
                self.rock_lookup_page.refresh_data(retain_selection=True)
            
            print(f"✓ 岩石属性数据库保存成功: {db_path} ({len(df)}条记录)")
            return True
            
        except Exception as e:
            print(f"保存岩石数据库时发生错误: {e}")
            return False

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.header_bar = self._build_header()
        root_layout.addWidget(self.header_bar)

        body_frame = QFrame()
        body_frame.setObjectName("bodyFrame")
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.navigation_panel = self._build_navigation()
        body_layout.addWidget(self.navigation_panel)

        divider = QFrame()
        divider.setObjectName("bodyDivider")
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setFixedWidth(1)
        body_layout.addWidget(divider)

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("pageStack")
        self.content_stack.setContentsMargins(0, 0, 0, 0)
        body_layout.addWidget(self.content_stack, 1)

        root_layout.addWidget(body_frame, 1)

        self.footer_bar = self._build_footer()
        root_layout.addWidget(self.footer_bar)

        # --- 实例化功能页 ---
        self.module_pages.clear()
        self.dashboard_page = DashboardPage(main_win=self)
        self.csv_formatter_tab = CSVFormatterTab()
        self.borehole_tab = BoreholeTab(main_win=self)
        self.key_stratum_tab = KeyStratumTab(main_win=self)
        self.db_overview_page = DatabaseOverviewPage(main_win=self)
        self.rock_lookup_page = RockParameterLookupPage(main_win=self)
        self.db_viewer_tab = DatabaseViewerTab(main_win=self)
        self.custom_library_tab = CustomRockLibraryTab(main_win=self)
        self.contour_plot_tab = ContourPlotTab(main_win=self)
        self.geo_model_home = GeologicalModelingHomePage(main_win=self)
        self.coal_block_tab = CoalSeamBlockTab(main_win=self)

        data_features = [
            {
                "title": "数据库概览",
                "widget": self.db_overview_page,
                "summary": "查看全国分布、样本统计与快速入口。",
            },
            {
                "title": "参数取值查询",
                "widget": self.rock_lookup_page,
                "summary": "按岩性浏览力学参数的小提琴图与统计指标。",
            },
            {
                "title": "岩石属性数据库",
                "widget": self.db_viewer_tab,
                "summary": "维护和扩展煤岩层力学参数库。",
            },
            {
                "title": "自建库管理",
                "widget": self.custom_library_tab,
                "summary": "导入自建力学参数库并与查询模块联动。",
            },
        ]
        self.module_pages["煤岩层力学参数数据库"] = ModulePage(
            "煤岩层力学参数数据库",
            "集中管理煤岩层物性数据、自建库以及相关查询能力。",
            data_features,
        )

        tools_features = [
            {
                "title": "CSV标准化工具",
                "widget": self.csv_formatter_tab,
                "summary": "将外部数据转换为统一的标准格式。",
            },
            {
                "title": "钻孔数据分析",
                "widget": self.borehole_tab,
                "summary": "批量处理钻孔数据并汇总煤层参数。",
            },
        ]
        self.module_pages["小工具集"] = ModulePage(
            "小工具集",
            "收纳常用的数据预处理与钻孔分析小工具。",
            tools_features,
        )

        modeling_features = [
            {
                "title": "建模首页",
                "widget": self.geo_model_home,
                "summary": "了解数据规范、示例模板与建模成果形态。",
            },
            {
                "title": "煤层块体建模",
                "widget": self.coal_block_tab,
                "summary": "构建三维块体模型并输出交互式成果。",
            },
            {
                "title": "等值线图与插值分析",
                "widget": self.contour_plot_tab,
                "summary": "生成等值线与煤层曲面，支持插值方法对比。",
            },
        ]
        self.module_pages["地质建模"] = ModulePage(
            "地质建模",
            "完成煤层空间建模、数据插值与等值线绘制。",
            modeling_features,
        )

        theory_features = [
            {
                "title": "关键层计算",
                "widget": self.key_stratum_tab,
                "summary": "依据力学参数自动识别关键层及其结构类型。",
            }
        ]
        self.module_pages["基础力学理论计算"] = ModulePage(
            "基础力学理论计算",
            "围绕支承结构与关键层理论开展快速核算与分析。",
            theory_features,
        )

        self.module_pages["煤层群开采扰动评价"] = ModulePage(
            "煤层群开采扰动评价",
            "规划对多煤层协同开采过程中的扰动程度进行量化评估。",
            [
                {
                    "title": "功能规划中",
                    "widget": PlaceholderModuleWidget(
                        "煤层群开采扰动评价",
                        "即将支持多煤层协同开采扰动建模、监测指标接入与风险分级评估。",
                    ),
                }
            ],
        )

        self.module_pages["覆岩开采扰动评价"] = ModulePage(
            "覆岩开采扰动评价",
            "拟构建覆岩结构演化、离层监测与沉降预测的一体化评价体系。",
            [
                {
                    "title": "功能规划中",
                    "widget": PlaceholderModuleWidget(
                        "覆岩开采扰动评价",
                        "将引入覆岩动力学分析、监测数据融合和预警指标配置能力。",
                    ),
                }
            ],
        )

        self.module_pages["智能开采设计与动态调控"] = ModulePage(
            "智能开采设计与动态调控",
            "面向智慧矿山建设，预留智能开采设计与调控策略模块。",
            [
                {
                    "title": "功能规划中",
                    "widget": PlaceholderModuleWidget(
                        "智能开采设计与动态调控",
                        "预计融合智能优化、实时监测与反馈调控算法，支撑动态决策。",
                    ),
                }
            ],
        )

        page_configs = [
            {
                "title": "工作台",
                "hint": "概览关键指标并快速进入常用功能",
                "widget": self.dashboard_page,
                "on_navigate": self.dashboard_page.refresh_cards,
            },
            {
                "title": "煤岩层力学参数数据库",
                "hint": "统一管理煤岩层物性参数、自建库与查询能力。",
                "widget": self.module_pages["煤岩层力学参数数据库"],
            },
            {
                "title": "小工具集",
                "hint": "包含CSV标准化、钻孔分析等辅助工具。",
                "widget": self.module_pages["小工具集"],
            },
            {
                "title": "地质建模",
                "hint": "完成煤层建模、插值分析与等值线展示。",
                "widget": self.module_pages["地质建模"],
            },
            {
                "title": "基础力学理论计算",
                "hint": "提供关键层计算等核心力学分析工具。",
                "widget": self.module_pages["基础力学理论计算"],
            },
            {
                "title": "煤层群开采扰动评价",
                "hint": "多煤层协同开采扰动评价功能规划中。",
                "widget": self.module_pages["煤层群开采扰动评价"],
            },
            {
                "title": "覆岩开采扰动评价",
                "hint": "覆岩动力学与扰动监测评估能力预留接口。",
                "widget": self.module_pages["覆岩开采扰动评价"],
            },
            {
                "title": "智能开采设计与动态调控",
                "hint": "面向智慧矿山的设计优化与调控策略平台。",
                "widget": self.module_pages["智能开采设计与动态调控"],
            },
        ]
        self._register_pages(page_configs)

        if self.clock_timer is None:
            self.clock_timer = QTimer(self)
            self.clock_timer.timeout.connect(self._update_clock)
        if not self.clock_timer.isActive():
            self.clock_timer.start(1000)
        self._update_clock()

        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(18)

        logo_label = QLabel()
        logo_label.setObjectName("headerLogo")
        logo_label.setFixedSize(40, 40)
        logo_pixmap = QPixmap()
        if hasattr(self, 'app_icon') and self.app_icon and not self.app_icon.isNull():
            logo_pixmap = self.app_icon.pixmap(48, 48)
        if logo_pixmap.isNull():
            icon_path = resolve_app_icon_path()
            if icon_path:
                logo_pixmap = QPixmap(icon_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("⛏")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignVCenter)

        title_container = QVBoxLayout()
        title_container.setContentsMargins(0, 0, 0, 0)
        title_container.setSpacing(2)

        app_label = QLabel("矿山工程关键层分析与可视化系统")
        app_label.setObjectName("appTitle")
        title_container.addWidget(app_label)

        self.page_title_label = QLabel("")
        self.page_title_label.setObjectName("pageTitle")
        title_container.addWidget(self.page_title_label)

        self.page_hint_label = QLabel("")
        self.page_hint_label.setObjectName("pageHint")
        self.page_hint_label.setWordWrap(True)
        title_container.addWidget(self.page_hint_label)

        layout.addLayout(title_container, 1)

        layout.addStretch(1)

        self.clock_label = QLabel("")
        self.clock_label.setObjectName("clockLabel")
        layout.addWidget(self.clock_label, 0, Qt.AlignmentFlag.AlignVCenter)

        return header

    def _build_navigation(self) -> QFrame:
        nav_frame = QFrame()
        nav_frame.setObjectName("navPanel")
        nav_frame.setMinimumWidth(240)

        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(20, 24, 20, 24)
        nav_layout.setSpacing(18)

        section_label = QLabel("功能模块")
        section_label.setObjectName("navTitle")
        nav_layout.addWidget(section_label)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setIconSize(QSize(22, 22))
        self.nav_list.setSpacing(6)
        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.nav_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav_list.currentRowChanged.connect(self._handle_nav_changed)
        nav_layout.addWidget(self.nav_list, 1)

        actions_frame = QFrame()
        actions_frame.setObjectName("navActions")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        reload_btn = QPushButton("刷新岩石库")
        reload_btn.setProperty("class", "navAction")
        reload_btn.clicked.connect(self._handle_reload_database)
        actions_layout.addWidget(reload_btn)

        data_btn = QPushButton("打开数据目录")
        data_btn.setProperty("class", "navAction")
        data_btn.clicked.connect(self._handle_open_data_dir)
        actions_layout.addWidget(data_btn)

        manual_btn = QPushButton("查看操作指南")
        manual_btn.setProperty("class", "navAction")
        manual_btn.clicked.connect(self._handle_open_manual)
        actions_layout.addWidget(manual_btn)

        nav_layout.addSpacing(12)
        nav_layout.addWidget(actions_frame, 0)

        return nav_frame

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("footerBar")

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)

        self.global_status_label = QLabel("就绪")
        self.global_status_label.setObjectName("globalStatus")
        layout.addWidget(self.global_status_label)

        layout.addStretch(1)

        build_label = QLabel(f"Build {QDateTime.currentDateTime().toString('yyyy.MM.dd')}")
        build_label.setObjectName("footerMeta")
        layout.addWidget(build_label)

        return footer

    def _register_pages(self, configs):
        if self.nav_list is None or self.content_stack is None:
            return

        # 清理旧内容
        while self.content_stack.count():
            widget = self.content_stack.widget(0)
            self.content_stack.removeWidget(widget)

        self.nav_list.blockSignals(True)
        self.nav_list.clear()
        self.nav_items = []

        for config in configs:
            widget = config.get("widget")
            if widget is None:
                continue
            self.content_stack.addWidget(widget)

            item = QListWidgetItem()
            item.setText(config.get("title", "未命名模块"))
            icon_path = config.get("icon")
            icon = QIcon()
            if icon_path:
                resolved_icon = resource_path(icon_path)
                if os.path.exists(resolved_icon):
                    icon = QIcon(resolved_icon)
            if not icon.isNull():
                item.setIcon(icon)
            item.setSizeHint(QSize(188, 58))
            item.setToolTip(config.get("hint", ""))
            item.setData(Qt.ItemDataRole.UserRole, config)

            self.nav_list.addItem(item)
            self.nav_items.append(config)

        self.nav_list.blockSignals(False)

        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)
            self._handle_nav_changed(0)

    def _handle_nav_changed(self, index: int):
        if not self.nav_items or index < 0 or index >= len(self.nav_items):
            return

        if self.content_stack and self.content_stack.count() > index:
            self.content_stack.setCurrentIndex(index)

        config = self.nav_items[index]
        self.current_page_title = config.get("title", "")
        self.current_page_hint = config.get("hint", "")

        if self.page_title_label is not None:
            self.page_title_label.setText(self.current_page_title)
        if self.page_hint_label is not None:
            self.page_hint_label.setText(self.current_page_hint)
            self.page_hint_label.setVisible(bool(self.current_page_hint))

        callback = config.get("on_navigate")
        if callable(callback):
            callback()

        self.set_global_status(f"正在浏览：{self.current_page_title}", "#2563eb")

    def _update_clock(self):
        if self.clock_label is None:
            return
        now = QDateTime.currentDateTime()
        self.clock_label.setText(now.toString("yyyy-MM-dd dddd HH:mm:ss"))

    def navigate_to_page(self, title: str) -> bool:
        if not self.nav_items or self.nav_list is None:
            return False
        for idx, config in enumerate(self.nav_items):
            if config.get("title") == title:
                self.nav_list.setCurrentRow(idx)
                return True
        return False

    def navigate_to_module_feature(self, module_title: str, feature_title: Optional[str] = None) -> bool:
        navigated = self.navigate_to_page(module_title)
        if navigated and feature_title:
            module_page = self.module_pages.get(module_title)
            if module_page is not None:
                module_page.activate_feature(feature_title)
        return navigated

    def set_global_status(self, message: str, color: str = "#2563eb"):
        if self.global_status_label is None:
            return
        self.global_status_label.setText(message)
        self.global_status_label.setStyleSheet(f"color: {color}; font-weight: 600;")

    def _handle_reload_database(self):
        previous_count = len(self.rock_db) if self.rock_db is not None else 0
        self._load_rock_database()
        if self.rock_db is not None:
            current_count = len(self.rock_db)
            self.set_global_status(f"岩石数据库已刷新（{current_count} 条记录）", "#16a34a")
            QMessageBox.information(self, "刷新成功", f"已重新加载岩石属性数据库：\n原有 {previous_count} → 当前 {current_count} 条记录。")
            if self.dashboard_page is not None:
                self.dashboard_page.refresh_cards()
            if self.db_overview_page is not None:
                self.db_overview_page.refresh_content()
        else:
            self.set_global_status("岩石数据库加载失败", "#dc2626")
            QMessageBox.warning(self, "刷新失败", "无法加载岩石属性数据库，请检查数据文件。")

    def _handle_open_data_dir(self):
        data_dir = resource_path('data')
        if os.path.exists(data_dir):
            open_file_auto(data_dir)
            self.set_global_status("已打开数据目录", "#2563eb")
        else:
            QMessageBox.warning(self, "目录缺失", "未找到数据目录，请检查程序安装路径。")

    def _handle_open_manual(self):
        manual_candidates = [
            resource_path('coal_selection_manual.md'),
            resource_path(os.path.join('docs', 'coal_selection_manual.md')),
            resource_path('database_update_instructions.md'),
        ]
        for path in manual_candidates:
            if os.path.exists(path):
                open_file_auto(path)
                self.set_global_status("已打开操作指南", "#2563eb")
                return
        QMessageBox.information(self, "未找到文档", "未能定位操作指南文件，请确认文档是否存在。")

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #eef2f7;
                color: #374151;
            }

            QFrame#headerBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:1 #1d4ed8);
                border-bottom: 1px solid #1e3a8a;
            }

            QLabel#appTitle {
                color: #e2e8f0;
                font-size: 18px;
                font-weight: 600;
                letter-spacing: 1px;
            }

            QLabel#pageTitle {
                color: #ffffff;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#pageHint {
                color: rgba(255, 255, 255, 0.85);
                font-size: 12px;
            }

            QLabel#clockLabel {
                color: #e2e8f0;
                padding: 6px 12px;
                border-radius: 12px;
                background-color: rgba(15, 23, 42, 0.35);
                font-size: 12px;
            }

            QFrame#dashboardHero {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 64, 175, 0.96), stop:1 rgba(30, 64, 175, 0.72));
                border-radius: 18px;
                color: #e2e8f0;
            }

            QLabel#dashboardHeroTitle {
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            QLabel#dashboardHeroSubtitle {
                font-size: 13px;
                color: rgba(226, 232, 240, 0.92);
            }

            QFrame#dashboardActionBar {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }

            QPushButton#dashboardAction {
                background-color: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 13px;
                color: #1d4ed8;
                font-weight: 600;
            }

            QPushButton#dashboardAction:hover {
                background-color: #eff6ff;
                border-color: #2563eb;
                color: #1e3a8a;
            }

            QPushButton#dashboardAction:pressed {
                background-color: #dbeafe;
                border-color: #1d4ed8;
            }

            QFrame#dashboardStats {
                background-color: transparent;
            }

            QFrame#dashboardStatCard {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }

            QFrame#placeholderCard {
                background: #ffffff;
                border: 1px dashed #cbd5f5;
                border-radius: 16px;
            }

            QLabel#dashboardStatTitle {
                font-size: 13px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            QLabel#dashboardStatValue {
                font-size: 28px;
                color: #0f172a;
                font-weight: 700;
            }

            QLabel#dashboardStatSubtitle {
                font-size: 12px;
                color: #94a3b8;
            }

            QFrame#navPanel {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }

            QLabel#navTitle {
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 1px;
                color: #475569;
                text-transform: uppercase;
            }

            QListWidget#navList {
                background: transparent;
                border: none;
                outline: none;
            }

            QListWidget#navList::item {
                margin: 4px 0px;
                padding: 12px 14px;
                border-radius: 12px;
                color: #1f2937;
                font-size: 14px;
            }

            QListWidget#navList::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: #ffffff;
            }

            QListWidget#navList::item:hover:!selected {
                background: rgba(37, 99, 235, 0.12);
                color: #1d4ed8;
            }

            QFrame#navActions {
                background-color: transparent;
            }

            QPushButton[class="navAction"] {
                padding: 10px 14px;
                border-radius: 10px;
                border: 1px solid #dbeafe;
                background-color: rgba(59, 130, 246, 0.08);
                color: #1d4ed8;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }

            QPushButton[class="navAction"]:hover {
                background-color: rgba(37, 99, 235, 0.16);
                border-color: #2563eb;
            }

            QPushButton[class="navAction"]:pressed {
                background-color: rgba(37, 99, 235, 0.32);
            }

            QFrame#bodyFrame {
                background: #ffffff;
            }

            QFrame#footerBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
            }

            QLabel#globalStatus {
                font-size: 13px;
            }

            QLabel#footerMeta {
                color: #64748b;
                font-size: 12px;
            }

            /* 分组框样式 */
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #111827;
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 20px;
                padding: 24px 16px 16px 16px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                left: 12px;
                top: 0px;
                background-color: transparent;
                color: #374151;
                border: none;
            }
            
            /* 表单标签样式 */
            QLabel {
                color: #374151;
                font-size: 14px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            
            /* 输入框和下拉框基础样式 */
            QComboBox, QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #ffffff;
                color: #374151;
                font-size: 14px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
                min-height: 20px;
            }
            
            QComboBox:hover, QLineEdit:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
            
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #2563eb;
                background-color: #ffffff;
                outline: none;
            }
            
            /* 下拉框特殊样式 */
            QComboBox::drop-down {
                border: none;
                width: 24px;
                background: transparent;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background: #6b7280;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #6b7280;
                margin-right: 6px;
            }
            
            QComboBox::down-arrow:hover {
                border-top-color: #2563eb;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #eff6ff;
                selection-color: #1e40af;
                padding: 4px;
            }
            
            /* 滑块样式 */
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background-color: #f3f4f6;
                border-radius: 3px;
                margin: 6px 0;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: 2px solid #ffffff;
                width: 18px;
                height: 18px;
                border-radius: 11px;
                margin: -8px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #3b82f6);
                border: 2px solid #dbeafe;
            }
            
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e40af);
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 3px;
            }
            
            /* 进度条样式 */
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #f3f4f6;
                text-align: center;
                font-size: 12px;
                font-weight: 500;
                color: #374151;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 6px;
                margin: 1px;
            }
            
            /* 表格通用样式优化 */
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
                background-color: #ffffff;
                alternate-background-color: #f9fafb;
                selection-background-color: #eff6ff;
                selection-color: #1e40af;
                font-size: 14px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            
            QTableWidget::item {
                padding: 8px 12px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            
            QTableWidget::item:hover {
                background-color: #f1f5f9;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                font-weight: 600;
                color: #374151;
                font-size: 13px;
            }
            
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e2e8f0, stop:1 #cbd5e1);
            }
            
            /* 消息框样式 */
            QMessageBox {
                background-color: #ffffff;
                color: #374151;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            
            QMessageBox QLabel {
                color: #374151;
                font-size: 14px;
                padding: 10px;
            }
            
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
                margin: 4px;
            }
            
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #3b82f6);
            }
            
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e40af);
            }
            
            /* 滚动条样式 */
            QScrollBar:vertical {
                background-color: #f8fafc;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #64748b;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background-color: #f8fafc;
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #94a3b8;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: #64748b;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            /* 工具提示样式 */
            QToolTip {
                background-color: #1f2937;
                color: #f9fafb;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            
            /* 分隔器样式 */
            QSplitter::handle {
                background-color: #e5e7eb;
                width: 2px;
                height: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #cbd5e1;
            }
            
            QSplitter::handle:pressed {
                background-color: #94a3b8;
            }
        """)

    def center_window(self):
        screen_geometry = self.screen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

if __name__ == "__main__":
    configure_logging()
    dpi_attrs = []
    if hasattr(Qt, "ApplicationAttribute"):
        attr_enum = Qt.ApplicationAttribute
        for attr_name in ("AA_EnableHighDpiScaling", "AA_UseHighDpiPixmaps"):
            attr_value = getattr(attr_enum, attr_name, None)
            if attr_value is not None:
                dpi_attrs.append(attr_value)
    for attr in dpi_attrs:
        try:
            QApplication.setAttribute(attr, True)
        except Exception:
            logging.debug("无法设置高DPI属性 %s", attr)

    app = QApplication(sys.argv)
    install_exception_hook()

    try:
        app_config = load_app_config()
    except Exception as exc:
        logging.exception("加载应用配置失败")
        QMessageBox.critical(
            None,
            "配置加载失败",
            f"未能读取应用配置文件，请检查 config\\app_settings.json 是否有效。\n\n错误详情: {exc}",
        )
        sys.exit(1)

    errors, warnings = perform_startup_checks(app_config)
    if errors:
        QMessageBox.critical(
            None,
            "启动检查失败",
            "启动自检过程中检测到以下阻塞问题：\n\n" + "\n".join(f"• {item}" for item in errors),
        )
        sys.exit(1)
    if warnings:
        QMessageBox.information(
            None,
            "启动检查提醒",
            "以下项目需要关注，但不会阻止程序启动：\n\n" + "\n".join(f"• {item}" for item in warnings),
        )

    def show_main_window(username: str):
        main_window = MainWindow(app_config, username)
        login_widget.main_window = main_window
        main_window.show()
        login_widget.close()

    login_widget = LoginWidget(app_config, on_login_success=show_main_window)
    login_widget.show()

    sys.exit(app.exec())