from __future__ import annotations

import io
import json
import re
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from scipy.interpolate import griddata, Rbf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy import String, cast, func, or_, select, text
from sqlalchemy.orm import Session

from coal_seam_blocks.aggregator import aggregate_boreholes, unify_columns
from api import calculate_key_strata_details, process_single_borehole_file
from coal_seam_blocks.modeling import build_block_models
from db import get_engine, get_records_table, get_session, reset_table_cache

# 性能优化模块
from performance_config import (
    MAX_UPLOAD_SIZE_MB, MAX_RESOLUTION, CACHE_ENABLED,
    print_config_summary
)
from cache import cached, get_cache_stats, start_cache_cleanup_task, cache_database_query
from rate_limiter import RateLimitMiddleware, start_rate_limit_cleanup_task
from memory_utils import (
    optimize_dataframe_memory, check_memory_usage,
    memory_efficient_operation, clear_dataframe_cache, limit_dataframe_size
)

# 算法优化模块
from interpolation import get_interpolator, interpolate_smart
from data_validation import validate_geological_data, GeologicalDataValidator

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT.parent / "data" / "input"
CHINA_JSON_CANDIDATES = [
    APP_ROOT.parent / "frontend" / "public" / "china.json",
    APP_ROOT.parent / "frontend" / "src" / "assets" / "china.json",
]

SEAM_COLUMN_CANDIDATES = ["煤层", "煤层名称", "层位", "岩层", "岩层名称", "煤层名"]


class ModelingState:
    """In-memory storage for the geological modeling workflow."""

    def __init__(self) -> None:
        self.merged_df: Optional[pd.DataFrame] = None
        self.coords_df: Optional[pd.DataFrame] = None
        self.numeric_columns: List[str] = []
        self.text_columns: List[str] = []
        self.last_selected_seam_column: Optional[str] = None
        self.borehole_file_count: int = 0

    def ensure_loaded(self) -> None:
        if self.merged_df is None:
            raise HTTPException(status_code=400, detail="请先上传并合并钻孔与坐标数据")


modeling_state = ModelingState()


class KeyStratumState:
    def __init__(self) -> None:
        self.files: Dict[str, pd.DataFrame] = {}
        self.filled: bool = False
        self.last_result: Optional[pd.DataFrame] = None

    def reset(self) -> None:
        self.files = {}
        self.filled = False
        self.last_result = None


key_stratum_state = KeyStratumState()


def _get_numeric_and_text_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    numeric_cols: List[str] = []
    text_cols: List[str] = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
            continue
        # 尝试数字化判断列类型
        coerced = pd.to_numeric(series.dropna(), errors="coerce")
        if not coerced.empty and coerced.notna().mean() > 0.8:
            numeric_cols.append(col)
        else:
            text_cols.append(col)
    return {"numeric": numeric_cols, "text": text_cols}


def _get_records_table_or_500():
    """获取 records 表，如果失败则抛出 HTTPException
    
    已废弃：建议直接使用 get_records_table() 并自行处理异常
    """
    try:
        return get_records_table()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _get_records_table_safe():
    """安全获取 records 表，如果失败返回 None
    
    Returns:
        Table 对象或 None（如果数据库未初始化）
    """
    try:
        return get_records_table()
    except RuntimeError as e:
        print(f"[WARNING] 获取 records 表失败: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 获取 records 表时发生未预期错误: {e}")
        return None


def _serialize_row(row: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
    payload = {}
    for column in columns:
        value = row.get(column)
        payload[column] = "" if value is None else value
    if "__rowid__" in row:
        payload["__rowid__"] = row["__rowid__"]
    return payload


def _build_optional_filters(table, search: Optional[str]):
    if not search:
        return None
    keyword = search.strip()
    if not keyword:
        return None
    pattern = f"%{keyword}%"
    conditions = []
    for column in table.columns:
        try:
            if column.type.python_type is str:
                conditions.append(column.ilike(pattern))
        except NotImplementedError:
            continue
    if not conditions:
        return None
    return or_(*conditions)


PROVINCE_COLUMN_CANDIDATES = [
    "省份",
    "省份名称",
    "所在省份",
    "所属省份",
    "省",
    "省市",
    "省份/地区",
    "省份(地区)",
    "行政区",
    "份",
]


DEFAULT_NUMERIC_COLUMNS = [
    "弹性模量/GPa",
    "容重/kN·m-3",
    "抗拉强度/MPa",
    "泊松比",
    "内摩擦角",
    "粘聚力/MPa",
]


def _resolve_column(column_map: Dict[str, Any], candidates: List[str]):
    for key in candidates:
        column = column_map.get(key)
        if column is not None:
            return column, key
    return None, None


def _normalize_province_name(name: str) -> str:
    if name is None:
        return ""
    value = str(name).strip()
    if not value:
        return ""

    replacements = {
        "内蒙古自治区": "内蒙古",
        "广西壮族自治区": "广西",
        "宁夏回族自治区": "宁夏",
        "新疆维吾尔自治区": "新疆",
        "西藏自治区": "西藏",
        "香港特别行政区": "香港",
        "澳门特别行政区": "澳门",
        "黑龙江省": "黑龙江",
    }
    if value in replacements:
        return replacements[value]

    suffixes = ["省", "市", "地区", "自治区", "特别行政区"]
    for suffix in suffixes:
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break
    return value.strip()


COAL_ALIASES = {"煤"}
COAL_NORMALIZED_NAME = "煤"


def _normalize_lithology_name(name: str) -> str:
    if name is None:
        return ""
    value = str(name).strip()
    if not value:
        return ""
    candidate = value.replace("煤层", COAL_NORMALIZED_NAME)
    simplified = re.sub(r"[0-9０-９一二三四五六七八九十百千万点·\-_/\\（）()\s]+", "", candidate)
    if simplified in COAL_ALIASES:
        return COAL_NORMALIZED_NAME
    return value


def _infer_numeric_columns(
    table,
    db_session: Session,
    exclude: Optional[set[str]] = None,
    sample_size: int = 200,
) -> List[str]:
    exclude_set = set(exclude or set())
    candidate_names: List[str] = [
        column.name
        for column in table.columns
        if column.name not in exclude_set
    ]
    if not candidate_names:
        return []

    stmt = select(*[table.c[name] for name in candidate_names]).limit(sample_size)
    rows = db_session.execute(stmt).all()
    if not rows:
        return []

    df = pd.DataFrame(rows, columns=candidate_names)
    inferred: List[str] = []
    for name in candidate_names:
        series = pd.to_numeric(df[name], errors="coerce")
        valid_ratio = series.notna().mean()
        if series.notna().sum() >= 3 and valid_ratio >= 0.5:
            inferred.append(name)

    if not inferred:
        return []

    preferred_order = {col: idx for idx, col in enumerate(DEFAULT_NUMERIC_COLUMNS)}
    inferred.sort(key=lambda col: preferred_order.get(col, len(preferred_order)))
    return inferred


def _load_china_geojson() -> Dict:
    for candidate in CHINA_JSON_CANDIDATES:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as f:
                return json.load(f)
    raise HTTPException(status_code=404, detail="未找到中国地图 JSON 文件")


def _read_csv_bytes(data: bytes) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "gbk"]
    last_error: Optional[Exception] = None
    for enc in encodings:
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc)
        except Exception as exc:
            last_error = exc
            continue
    raise HTTPException(status_code=400, detail=f"CSV读取失败: {last_error}")


def _ensure_seam_column(df: pd.DataFrame) -> pd.DataFrame:
    for candidate in SEAM_COLUMN_CANDIDATES:
        if candidate in df.columns:
            if candidate != "煤层":
                df["煤层"] = df[candidate]
            break
    if "煤层" not in df.columns:
        df["煤层"] = ""
    return df


def _prepare_preview(dfs: Dict[str, pd.DataFrame], limit: int = 200) -> Dict[str, List[Dict]]:
    if not dfs:
        return {"columns": [], "rows": []}
    combined = pd.concat(list(dfs.values()), ignore_index=True, sort=False)
    combined = combined.fillna("")
    preview_df = combined.head(limit)
    columns = preview_df.columns.tolist()
    rows = json.loads(preview_df.to_json(orient="records", force_ascii=False))
    return {"columns": columns, "rows": rows}


def _fill_from_database(df: pd.DataFrame, stats_map: pd.DataFrame) -> pd.DataFrame:
    if stats_map.empty:
        return df
    df = df.copy()
    lithology_series = df.get("岩层名称")
    if lithology_series is None:
        return df
    numeric_cols = DEFAULT_NUMERIC_COLUMNS
    for idx, lith in lithology_series.items():
        key = str(lith).strip()
        if not key or key not in stats_map.index:
            continue
        stats_row = stats_map.loc[key]
        for col in numeric_cols:
            if col not in df.columns or col not in stats_row:
                continue
            current_value = df.at[idx, col]
            if pd.isna(current_value) or (isinstance(current_value, (int, float)) and float(current_value) == 0.0):
                df.at[idx, col] = stats_row[col]
    return df


def _normalize_key_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "岩层": "岩层名称",
        "岩层名": "岩层名称",
        "层位": "岩层名称",
        "名称": "岩层名称",
        "厚度": "厚度/m",
        "厚度m": "厚度/m",
        "厚度/M": "厚度/m",
        "厚度(米)": "厚度/m",
        "厚度（m）": "厚度/m",
        "弹性模量": "弹性模量/GPa",
        "容重": "容重/kN·m-3",
        "抗拉强度": "抗拉强度/MPa",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


class ContourRequest(BaseModel):
    x_col: str
    y_col: str
    z_col: str
    method: str
    seams: Optional[List[str]] = None
    resolution: Optional[int] = 80


class BlockModelRequest(BaseModel):
    x_col: str
    y_col: str
    thickness_col: str
    seam_col: str
    selected_seams: List[str]
    method: str
    resolution: Optional[int] = 80
    base_level: Optional[float] = 0
    gap: Optional[float] = 0


class ComparisonRequest(BaseModel):
    x_col: str
    y_col: str
    z_col: str
    validation_ratio: float = 0.2
    seams: Optional[List[str]] = None


app = FastAPI(title="Mining System API", version="0.1.0")

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 性能优化: 请求限流中间件
rate_limit_middleware = RateLimitMiddleware(app, rate_per_minute=60)
app.add_middleware(RateLimitMiddleware, rate_per_minute=60)


# 启动事件: 初始化性能优化组件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("\n" + "=" * 70)
    print("Mining System API 启动中...".center(70))
    print("=" * 70)

    # 打印性能配置
    print_config_summary()

    # 启动缓存清理任务
    start_cache_cleanup_task()

    # 启动限流清理任务
    start_rate_limit_cleanup_task(rate_limit_middleware)

    # 显示内存状态
    mem_usage = check_memory_usage()
    if "error" not in mem_usage:
        print(f"当前内存使用: {mem_usage['process_mb']:.1f}MB")
        print(f"系统总内存: {mem_usage['system_total_mb']:.1f}MB")
        print(f"系统可用内存: {mem_usage['system_available_mb']:.1f}MB")

    # 检查并初始化数据库
    await check_and_init_database()

    print("=" * 70 + "\n")


async def check_and_init_database():
    """检查数据库状态，如果为空则自动导入数据"""
    try:
        from sqlalchemy import create_engine, inspect
        from db import DB_PATH, get_engine
        
        # 检查数据库文件是否存在
        if not DB_PATH.exists():
            print(f"⚠️  数据库文件不存在: {DB_PATH}")
            print("📥 尝试自动初始化数据库...")
            await auto_import_csv()
            return
        
        # 检查数据库表和数据
        engine = get_engine()
        inspector = inspect(engine)
        
        if 'records' not in inspector.get_table_names():
            print("⚠️  数据库表不存在")
            print("📥 尝试自动初始化数据库...")
            await auto_import_csv()
            return
        
        # 检查记录数
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM records'))
            count = result.fetchone()[0]
            
            if count == 0:
                print("⚠️  数据库为空（0条记录）")
                print("📥 尝试自动初始化数据库...")
                await auto_import_csv()
            else:
                print(f"✓ 数据库已加载 ({count} 条记录)")
                
    except Exception as e:
        print(f"⚠️  数据库检查失败: {e}")
        print("📥 尝试自动初始化数据库...")
        await auto_import_csv()


async def auto_import_csv():
    """自动导入 CSV 数据到数据库"""
    try:
        csv_path = APP_ROOT / "data" / "input" / "汇总表.csv"
        
        if not csv_path.exists():
            print(f"❌ CSV 文件不存在: {csv_path}")
            print(f"   查找路径: {csv_path}")
            print(f"   APP_ROOT: {APP_ROOT}")
            # 尝试其他可能的路径
            alternative_paths = [
                Path("/app/data/input/汇总表.csv"),
                APP_ROOT.parent / "data" / "input" / "汇总表.csv",
            ]
            for alt_path in alternative_paths:
                if alt_path.exists():
                    csv_path = alt_path
                    print(f"✓ 在备用路径找到: {csv_path}")
                    break
            else:
                return
        
        print(f"📂 找到 CSV 文件: {csv_path}")
        print("📊 开始导入数据...")
        
        # 读取 CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"   读取 {len(df)} 条记录")
        print(f"   列名: {list(df.columns)}")
        
        # 导入到数据库
        from sqlalchemy import create_engine
        from db import DB_PATH
        
        # 确保目录存在
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建引擎并导入
        engine = create_engine(f'sqlite:///{DB_PATH}')
        df.to_sql('records', engine, if_exists='replace', index=False)
        
        print(f"✅ 数据库初始化完成！导入 {len(df)} 条记录到 {DB_PATH}")
        
        # 创建索引（尝试多个可能的列名）
        try:
            with engine.connect() as conn:
                # 获取实际的列名
                actual_columns = df.columns.tolist()
                
                # 为常见列创建索引
                province_cols = ['省份', 'Province', 'province', '省', 'sheng']
                mine_cols = ['矿名', 'Mine', 'mine', '矿', 'kuang']
                lithology_cols = ['岩性', 'Lithology', 'lithology', '岩', 'yan']
                
                for col_list, idx_name in [
                    (province_cols, 'idx_province'),
                    (mine_cols, 'idx_mine'),
                    (lithology_cols, 'idx_lithology')
                ]:
                    for col in col_list:
                        if col in actual_columns:
                            conn.execute(text(f'CREATE INDEX IF NOT EXISTS {idx_name} ON records ("{col}")'))
                            print(f"   创建索引: {idx_name} on {col}")
                            break
                
                conn.commit()
        except Exception as idx_err:
            print(f"⚠️  创建索引失败（不影响使用）: {idx_err}")
        
        # 重置表缓存
        reset_table_cache()
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("\n[系统] 正在关闭，清理资源...")
    clear_dataframe_cache([modeling_state, key_stratum_state])
    print("[系统] 资源清理完成\n")


@app.post("/api/modeling/columns")
async def load_modeling_columns(
    borehole_files: List[UploadFile] = File(..., description="多个钻孔CSV"),
    coords_file: UploadFile = File(..., description="坐标CSV"),
):
    if not borehole_files:
        raise HTTPException(status_code=400, detail="请至少上传一个钻孔文件")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            borehole_paths: List[str] = []
            
            # 保存钻孔文件
            for idx, file in enumerate(borehole_files):
                try:
                    data = await file.read()
                    if not data:
                        raise ValueError(f"文件 {file.filename} 为空")
                    
                    # 使用索引避免文件名冲突
                    filename = file.filename or f"borehole_{idx}.csv"
                    target = tmp_path / filename
                    target.write_bytes(data)
                    borehole_paths.append(str(target))
                    print(f"[DEBUG] 保存钻孔文件: {filename}, 大小: {len(data)} bytes")
                except Exception as e:
                    print(f"[ERROR] 保存钻孔文件失败: {file.filename}, 错误: {e}")
                    raise HTTPException(status_code=400, detail=f"保存钻孔文件失败: {file.filename} - {str(e)}")

            # 保存坐标文件
            try:
                coords_data = await coords_file.read()
                if not coords_data:
                    raise ValueError("坐标文件为空")
                coords_path = tmp_path / (coords_file.filename or "coordinates.csv")
                coords_path.write_bytes(coords_data)
                print(f"[DEBUG] 保存坐标文件: {coords_file.filename}, 大小: {len(coords_data)} bytes")
            except Exception as e:
                print(f"[ERROR] 保存坐标文件失败: {e}")
                raise HTTPException(status_code=400, detail=f"保存坐标文件失败: {str(e)}")

            # 聚合数据
            try:
                print(f"[DEBUG] 开始聚合数据，钻孔文件数: {len(borehole_paths)}")
                merged_df, coords_df = aggregate_boreholes(borehole_paths, str(coords_path))
                print(f"[DEBUG] 数据聚合成功，记录数: {len(merged_df)}")
            except Exception as e:
                print(f"[ERROR] 数据聚合失败: {e}")
                raise HTTPException(status_code=400, detail=f"数据聚合失败: {str(e)}")

        modeling_state.merged_df = merged_df
        modeling_state.coords_df = coords_df
        modeling_state.borehole_file_count = len(borehole_files)
        columns_info = _get_numeric_and_text_columns(merged_df)
        modeling_state.numeric_columns = columns_info["numeric"]
        modeling_state.text_columns = columns_info["text"]

        return {
            "status": "success",
            "numeric_columns": modeling_state.numeric_columns,
            "text_columns": modeling_state.text_columns,
            "record_count": int(len(merged_df)),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] load_modeling_columns 发生未预期错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/modeling/seams")
async def get_unique_seams(column: str = Query(..., description="岩层列名")):
    modeling_state.ensure_loaded()
    if column not in modeling_state.merged_df.columns:
        raise HTTPException(status_code=404, detail=f"在合并数据中未找到列: {column}")
    values = (
        modeling_state.merged_df[column]
        .dropna()
        .astype(str)
        .map(str.strip)
        .replace({"nan": ""})
    )
    unique_values = sorted({v for v in values if v})
    modeling_state.last_selected_seam_column = column
    return {"status": "success", "values": unique_values}


def _filter_dataframe_by_seams(df: pd.DataFrame, seams: Optional[List[str]], seam_column: Optional[str]) -> pd.DataFrame:
    if not seams or not seam_column or seam_column not in df.columns:
        return df
    seam_set = {str(s) for s in seams}
    return df[df[seam_column].astype(str).isin(seam_set)]


@app.post("/api/modeling/contour")
async def generate_contour(data: ContourRequest):
    modeling_state.ensure_loaded()
    df = modeling_state.merged_df.copy()

    seam_col = modeling_state.last_selected_seam_column
    df = _filter_dataframe_by_seams(df, data.seams, seam_col)

    if df.empty:
        raise HTTPException(status_code=400, detail="过滤后的数据为空，无法生成等值线")

    required_cols = [data.x_col, data.y_col, data.z_col]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise HTTPException(status_code=404, detail=f"数据集中缺少列: {missing}")

    subset = df.dropna(subset=required_cols).copy()
    if subset.empty:
        raise HTTPException(status_code=400, detail="有效数据点不足以进行插值")

    x = pd.to_numeric(subset[data.x_col], errors="coerce").dropna()
    y = pd.to_numeric(subset[data.y_col], errors="coerce").dropna()
    z = pd.to_numeric(subset[data.z_col], errors="coerce").dropna()
    valid_length = min(len(x), len(y), len(z))
    if valid_length < 4:
        raise HTTPException(status_code=400, detail="至少需要4个有效数据点来生成等值线")

    x = x.iloc[:valid_length]
    y = y.iloc[:valid_length]
    z = z.iloc[:valid_length]

    resolution = max(int(data.resolution or 80), 20)
    xi = np.linspace(x.min(), x.max(), resolution)
    yi = np.linspace(y.min(), y.max(), resolution)
    XI, YI = np.meshgrid(xi, yi)
    
    # 使用增强的插值模块
    try:
        from interpolation import interpolate
        method = data.method.lower()
        zi = interpolate(x.values, y.values, z.values, XI, YI, method)
    except Exception as e:
        print(f"[WARNING] 插值失败: {e}, 使用线性插值")
        try:
            zi = griddata((x, y), z, (XI, YI), method="linear")
        except Exception:
            zi = griddata((x, y), z, (XI, YI), method="nearest")

    zi = np.nan_to_num(zi, nan=float(np.nanmean(z)))

    return {
        "status": "success",
        "grid": {
            "x": xi.tolist(),
            "y": yi.tolist(),
            "z": zi.tolist(),
        },
        "points": {
            "x": x.tolist(),
            "y": y.tolist(),
            "z": z.tolist(),
        },
    }


@app.post("/api/modeling/block_model")
async def generate_block_model(payload: BlockModelRequest):
    modeling_state.ensure_loaded()
    df = modeling_state.merged_df

    for col in [payload.x_col, payload.y_col, payload.thickness_col, payload.seam_col]:
        if col not in df.columns:
            raise HTTPException(status_code=404, detail=f"数据集中缺少列: {col}")

    def interpolation_wrapper(x, y, z, xi_flat, yi_flat):
        """智能插值包装函数,使用增强的interpolation模块"""
        from interpolation import interpolate
        
        num_points = len(x)
        method_key = payload.method.lower()
        
        # 数据验证
        if num_points <= 3:
            print(f"[WARNING] 数据点太少 ({num_points}), 使用最近邻插值")
            method_key = 'nearest'
        
        # 检查点是否共线或接近共线
        if num_points >= 3:
            try:
                x_range = np.max(x) - np.min(x)
                y_range = np.max(y) - np.min(y)
                
                # 如果点在一条线上(某个方向的范围非常小)
                if x_range < 1e-6 or y_range < 1e-6:
                    print(f"[WARNING] 数据点接近共线, 使用最近邻插值")
                    method_key = 'nearest'
            except Exception:
                pass
        
        # 使用增强的插值模块执行插值
        try:
            result = interpolate(x, y, z, xi_flat, yi_flat, method_key)
            
            # 处理NaN值
            if isinstance(result, np.ndarray):
                result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] 插值方法 {method_key} 失败: {e}, 回退到最近邻插值")
            try:
                result = griddata((x, y), z, (xi_flat, yi_flat), method='nearest')
                return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
            except Exception as fallback_error:
                print(f"[ERROR] 最近邻插值也失败: {fallback_error}")
                # 返回零数组作为最后的回退
                return np.zeros_like(xi_flat)

    try:
        block_models, skipped, (XI, YI) = build_block_models(
            merged_df=df,
            seam_column=payload.seam_col,
            x_col=payload.x_col,
            y_col=payload.y_col,
            thickness_col=payload.thickness_col,
            selected_seams=payload.selected_seams,
            method_callable=interpolation_wrapper,
            resolution=int(payload.resolution or 80),
            base_level=float(payload.base_level or 0.0),
            gap_value=float(payload.gap or 0.0),
        )
        print(f"[DEBUG] 块体建模完成: 成功 {len(block_models)} 个, 跳过 {len(skipped)} 个")
        print(f"[DEBUG] 网格尺寸: XI.shape={XI.shape}, YI.shape={YI.shape}")
        if skipped:
            print(f"[DEBUG] 跳过的岩层: {skipped}")
    except Exception as exc:
        print(f"[ERROR] 块体建模失败: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(exc))

    models_payload = []
    print(f"[DEBUG] 准备转换 {len(block_models)} 个模型数据...")
    print(f"[DEBUG] 网格维度: {XI.shape[0]} x {XI.shape[1]} = {XI.shape[0] * XI.shape[1]} 个点")
    
    for model in block_models:
        # 方案1: 使用二维数组格式 (parametric surface)
        # echarts-gl 的 surface 可以接受 data: { type: 'xyz', value: [x_arr, y_arr, z_arr] }
        # 或者 data: [[x,y,z], ...] 格式
        
        # 提取网格的 x, y 坐标(只需要一次)
        x_grid = XI[0, :].tolist()  # X 坐标数组 (第一行)
        y_grid = YI[:, 0].tolist()  # Y 坐标数组 (第一列)
        
        # Z 值以二维数组形式提供
        z_top = model.top_surface.tolist()
        z_bottom = model.bottom_surface.tolist()
        
        print(f"[DEBUG] 岩层 '{model.name}': x维度={len(x_grid)}, y维度={len(y_grid)}, z维度={len(z_top)}x{len(z_top[0]) if z_top else 0}")
        
        models_payload.append(
            {
                "name": model.name,
                "points": int(model.points),
                # 使用 parametric 格式: 分别提供 x, y, z 数组
                "grid_x": x_grid,
                "grid_y": y_grid,
                "top_surface_z": z_top,
                "bottom_surface_z": z_bottom,
                "avg_thickness": float(model.avg_thickness),
                "max_thickness": float(model.max_thickness),
                "avg_height": float(model.avg_height),
            }
        )
        
        # 打印第一个模型的数据样本用于调试
        if len(models_payload) == 1:
            print(f"[DEBUG] 第一个模型数据样本:")
            print(f"  - x_grid前3个值: {x_grid[:3]}")
            print(f"  - y_grid前3个值: {y_grid[:3]}")
            print(f"  - z_top[0]前3个值: {z_top[0][:3] if z_top and z_top[0] else 'N/A'}")

    return {
        "status": "success",
        "grid": {"x": XI[0].tolist(), "y": YI[:, 0].tolist()},
        "models": models_payload,
        "skipped": skipped,
    }


@app.post("/api/modeling/comparison")
async def compare_interpolation(payload: ComparisonRequest):
    modeling_state.ensure_loaded()
    df = modeling_state.merged_df.copy()
    seam_col = modeling_state.last_selected_seam_column
    df = _filter_dataframe_by_seams(df, payload.seams, seam_col)

    required_cols = [payload.x_col, payload.y_col, payload.z_col]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise HTTPException(status_code=404, detail=f"数据集中缺少列: {missing}")

    df = df.dropna(subset=required_cols)
    if len(df) < 12:
        raise HTTPException(status_code=400, detail="数据点不足，无法进行插值对比")

    X = df[[payload.x_col, payload.y_col]].apply(pd.to_numeric, errors="coerce").dropna()
    y = pd.to_numeric(df[payload.z_col], errors="coerce")
    y = y.loc[X.index]

    if len(X) < 12:
        raise HTTPException(status_code=400, detail="有效数据点不足以进行插值对比")

    X_train, X_test, y_train, y_test = train_test_split(
        X.values,
        y.values,
        test_size=min(max(payload.validation_ratio, 0.1), 0.5),
        random_state=42,
    )

    methods = {
        "linear": "线性 (Linear)",
        "cubic": "三次样条 (Cubic)",
        "nearest": "最近邻 (Nearest)",
        "multiquadric": "多重二次 (Multiquadric)",
        "inverse": "反距离 (Inverse)",
        "gaussian": "高斯 (Gaussian)",
        "thin_plate": "薄板样条 (Thin Plate)",
    }

    results = []
    for key, label in methods.items():
        try:
            if key in {"linear", "cubic", "nearest"}:
                preds = griddata(
                    (X_train[:, 0], X_train[:, 1]),
                    y_train,
                    (X_test[:, 0], X_test[:, 1]),
                    method=key,
                )
            else:
                rbf = Rbf(X_train[:, 0], X_train[:, 1], y_train, function=key)
                preds = rbf(X_test[:, 0], X_test[:, 1])
            if preds is None:
                continue
            mask = ~np.isnan(preds)
            if not np.any(mask):
                continue
            mae = float(mean_absolute_error(y_test[mask], preds[mask]))
            rmse = float(np.sqrt(mean_squared_error(y_test[mask], preds[mask])))
            r2 = float(r2_score(y_test[mask], preds[mask]))
            results.append({"method": label, "mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)})
        except Exception:
            continue

    if not results:
        raise HTTPException(status_code=400, detail="所有插值方法都计算失败")

    results.sort(key=lambda item: item["r2"], reverse=True)
    return {"status": "success", "results": results}


@app.get("/api/database/overview")
async def get_database_overview(
    limit: int = Query(40, ge=1, le=200),
    db: Session = Depends(get_session),
):
    """获取数据库概览 (带错误处理)"""
    try:
        # 尝试获取数据库表
        try:
            table = get_records_table()
        except RuntimeError as e:
            # 数据库未初始化，返回空数据
            print(f"[WARNING] 数据库未初始化: {e}")
            return {
                "status": "success",
                "stats": {
                    "records": 0,
                    "provinces": 0,
                    "mines": 0,
                    "lithologies": 0,
                },
                "distribution": [],
                "message": "数据库尚未初始化，请先导入数据"
            }
        
        column_map = {column.name: column for column in table.columns}

        stats = {
            "records": int(db.execute(select(func.count()).select_from(table)).scalar() or 0),
            "provinces": 0,
            "mines": 0,
            "lithologies": 0,
        }

        province_column, _ = _resolve_column(column_map, PROVINCE_COLUMN_CANDIDATES)
        if "矿名" in column_map:
            stats["mines"] = int(
                db.execute(select(func.count(func.distinct(column_map["矿名"])))).scalar() or 0
            )
        if "岩性" in column_map:
            distinct_stmt = (
                select(column_map["岩性"])
                .where(column_map["岩性"].is_not(None))
                .distinct()
            )
            normalized_set: set[str] = set()
            for row in db.execute(distinct_stmt):
                raw_value = row[0]
                normalized_value = _normalize_lithology_name(raw_value)
                if normalized_value:
                    normalized_set.add(normalized_value)
            stats["lithologies"] = len(normalized_set)

        distribution: List[Dict[str, Any]] = []
        if province_column is not None:
            province_stmt = (
                select(
                    province_column.label("raw_name"),
                    func.count().label("value"),
                )
                .where(province_column.is_not(None))
                .group_by(province_column)
                .order_by(func.count().desc())
            )
            province_rows = db.execute(province_stmt).all()
            unique_normalized: set[str] = set()
            for row in province_rows:
                raw_name = str(row.raw_name).strip() if row.raw_name is not None else ""
                normalized = _normalize_province_name(raw_name) or "未知"
                unique_normalized.add(normalized if normalized != "未知" else "")
                if len(distribution) < limit:
                    distribution.append(
                        {
                            "name": normalized,
                            "label": raw_name or normalized,
                            "value": int(row.value or 0),
                        }
                    )

            stats["provinces"] = len({name for name in unique_normalized if name})

        return {"status": "success", "stats": stats, "distribution": distribution}
    
    except Exception as e:
        print(f"[ERROR] get_database_overview 发生错误: {e}")
        import traceback
        traceback.print_exc()
        # 返回空数据而不是抛出异常
        return {
            "status": "success",
            "stats": {
                "records": 0,
                "provinces": 0,
                "mines": 0,
                "lithologies": 0,
            },
            "distribution": [],
            "message": "获取数据库信息时发生错误"
        }


@app.get("/api/database/records")
async def get_database_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="模糊搜索关键字"),
    province: Optional[str] = Query(None, description="按省份过滤"),
    db: Session = Depends(get_session),
):
    """获取数据库记录列表 (带错误处理)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            # 数据库未初始化，返回空结果
            return {
                "status": "success",
                "columns": [],
                "records": [],
                "page": page,
                "page_size": page_size,
                "total": 0,
                "message": "数据库尚未初始化"
            }
        
        columns = [column.name for column in table.columns]
    except Exception as e:
        print(f"[ERROR] get_database_records 获取表信息失败: {e}")
        return {
            "status": "success",
            "columns": [],
            "records": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "message": "获取数据库信息失败"
        }

    province_column, _ = _resolve_column({column.name: column for column in table.columns}, PROVINCE_COLUMN_CANDIDATES)
    province_clause = None
    if province and province_column is not None:
        raw_value = province.strip()
        normalized_value = _normalize_province_name(raw_value)
        candidates: List[str] = []
        if normalized_value:
            candidates.append(normalized_value)
        if raw_value and raw_value not in candidates:
            candidates.append(raw_value)
        suffixes = ["省", "市", "自治区", "特别行政区", "地区"]
        expanded_candidates: List[str] = []
        for base in candidates:
            expanded_candidates.append(base)
            for suffix in suffixes:
                expanded_candidates.append(f"{base}{suffix}")
        patterns = [item for item in expanded_candidates if item]
        if patterns:
            province_clause = or_(
                *[province_column.ilike(f"%{pattern}%") for pattern in patterns]
            )

    filters = _build_optional_filters(table, search)

    base_select = select(*[table.c[column] for column in columns], text("ROWID as __rowid__"))
    if filters is not None:
        base_select = base_select.where(filters)
    if province_clause is not None:
        base_select = base_select.where(province_clause)

    count_query = select(func.count()).select_from(table)
    if filters is not None:
        count_query = count_query.where(filters)
    if province_clause is not None:
        count_query = count_query.where(province_clause)

    total = int(db.execute(count_query).scalar() or 0)
    offset = (page - 1) * page_size

    rows = (
        db.execute(
            base_select.order_by(text("ROWID")).offset(offset).limit(page_size)
        )
        .mappings()
        .all()
    )

    records = []
    for row in rows:
        row_dict = dict(row)
        records.append(_serialize_row(row_dict, columns))

    return {
        "status": "success",
        "columns": columns,
        "records": records,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


class SaveDatabaseRequest(BaseModel):
    updated: List[Dict[str, Any]] = []
    inserted: List[Dict[str, Any]] = []
    deleted: List[int] = []


@app.post("/api/database/save")
async def save_database(request: SaveDatabaseRequest, db: Session = Depends(get_session)):
    table = _get_records_table_or_500()
    columns = [column.name for column in table.columns]

    try:
        if request.inserted:
            payloads = []
            for row in request.inserted:
                payload = {column: row.get(column) for column in columns}
                payloads.append(payload)
            if payloads:
                db.execute(table.insert(), payloads)

        if request.updated:
            for row in request.updated:
                rowid = row.get("__rowid__")
                if rowid is None:
                    continue
                values = {column: row.get(column) for column in columns}
                stmt = table.update().where(text("ROWID = :rowid")).values(**values)
                params = {"rowid": rowid, **values}
                db.execute(stmt, params)

        if request.deleted:
            for rowid in request.deleted:
                db.execute(text("DELETE FROM records WHERE ROWID = :rowid"), {"rowid": rowid})

        db.commit()
        reset_table_cache()
    except Exception as exc:  # pragma: no cover - database failure fallback
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库保存失败: {exc}") from exc

    return {"status": "success", "message": "数据库已更新"}


@app.get("/api/database/lithologies")
async def get_lithology_summary(db: Session = Depends(get_session)):
    """获取岩性摘要 (带错误处理)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            return {
                "status": "success",
                "lithologies": [],
                "numeric_columns": [],
                "counts": {},
                "message": "数据库尚未初始化"
            }
        
        column_map = {column.name: column for column in table.columns}

        lithology_col_name = "岩性"
        if lithology_col_name not in column_map:
            return {
                "status": "success",
                "lithologies": [],
                "numeric_columns": [],
                "counts": {},
                "message": "数据库缺少岩性列"
            }
    except Exception as e:
        print(f"[ERROR] get_lithology_summary 发生错误: {e}")
        return {
            "status": "success",
            "lithologies": [],
            "numeric_columns": [],
            "counts": {},
            "message": "获取岩性数据失败"
        }

    available_numeric = _infer_numeric_columns(table, db, exclude={lithology_col_name}) or [
        col for col in DEFAULT_NUMERIC_COLUMNS if col in column_map
    ]

    stmt = (
        select(
            column_map[lithology_col_name].label("name"),
            func.count().label("count"),
        )
        .where(column_map[lithology_col_name].is_not(None))
        .group_by(column_map[lithology_col_name])
        .order_by(func.count().desc())
    )

    aggregated_counts: Dict[str, int] = {}
    for row in db.execute(stmt):
        raw_name = str(row.name).strip() if row.name is not None else ""
        if not raw_name:
            continue
        normalized_name = _normalize_lithology_name(raw_name)
        if not normalized_name:
            continue
        aggregated_counts[normalized_name] = aggregated_counts.get(normalized_name, 0) + int(row.count or 0)

    sorted_items = sorted(aggregated_counts.items(), key=lambda item: item[1], reverse=True)
    lithologies = [name for name, _ in sorted_items]
    counts = {name: count for name, count in sorted_items}

    return {
        "status": "success",
        "lithologies": lithologies,
        "numeric_columns": available_numeric,
        "counts": counts,
    }


@app.get("/api/database/lithology-data")
async def get_lithology_data(
    lithology: str = Query(..., description="岩性名称"),
    search: Optional[str] = Query(None, description="可选模糊搜索"),
    db: Session = Depends(get_session),
):
    """获取指定岩性的数据 (带错误处理)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            return {
                "status": "success",
                "values": {},
                "count": 0,
                "stats": {},
                "message": "数据库尚未初始化"
            }
        
        column_map = {column.name: column for column in table.columns}

        lithology_col_name = "岩性"
        if lithology_col_name not in column_map:
            return {
                "status": "success",
                "values": {},
                "count": 0,
                "stats": {},
                "message": "数据库缺少岩性列"
            }

        name = lithology.strip()
        if not name:
            raise HTTPException(status_code=400, detail="岩性名称不能为空")
        normalized_name = _normalize_lithology_name(name)
        if not normalized_name:
            raise HTTPException(status_code=400, detail="岩性名称不能为空")

        available_numeric = _infer_numeric_columns(table, db, exclude={lithology_col_name}) or [
            col for col in DEFAULT_NUMERIC_COLUMNS if col in column_map
        ]
        if not available_numeric:
            return {"status": "success", "values": {}, "count": 0, "stats": {}}

        comparator = column_map[lithology_col_name]
        if normalized_name == COAL_NORMALIZED_NAME:
            base_condition = comparator.like("%煤%")
        else:
            base_condition = comparator == normalized_name

        stmt = select(*[column_map[col] for col in available_numeric]).where(base_condition)
        filters = _build_optional_filters(table, search)
        if filters is not None:
            stmt = stmt.where(filters)
        rows = db.execute(stmt).all()
        if not rows:
            return {"status": "success", "values": {}, "count": 0, "stats": {}}

        data_frame = pd.DataFrame(rows, columns=available_numeric)
        values: Dict[str, List[float]] = {}
        stats: Dict[str, Dict[str, float]] = {}
        for col in available_numeric:
            series = pd.to_numeric(data_frame[col], errors="coerce").dropna()
            if series.empty:
                continue
            values[col] = series.tolist()
            stats[col] = {
                "count": int(series.count()),
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std(ddof=0)) if series.count() > 1 else 0.0,
            }

        count_stmt = select(func.count()).select_from(table).where(base_condition)
        if filters is not None:
            count_stmt = count_stmt.where(filters)
        count = int(db.execute(count_stmt).scalar() or 0)

        return {"status": "success", "values": values, "count": count, "stats": stats}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_lithology_data 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "success",
            "values": {},
            "count": 0,
            "stats": {},
            "message": "获取岩性数据失败"
        }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/performance/stats")
async def get_performance_stats():
    """获取性能统计信息"""
    mem_usage = check_memory_usage()
    cache_stats = get_cache_stats()

    return {
        "status": "success",
        "memory": mem_usage,
        "cache": cache_stats,
        "config": {
            "max_upload_mb": MAX_UPLOAD_SIZE_MB,
            "max_resolution": MAX_RESOLUTION,
            "cache_enabled": CACHE_ENABLED
        }
    }


@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_session)):
    """获取仪表板统计信息 (带错误处理)"""
    try:
        def query_rock_db_count():
            try:
                table = get_records_table()
                return int(db.execute(select(func.count()).select_from(table)).scalar() or 0)
            except (RuntimeError, Exception) as e:
                print(f"[WARNING] 查询岩石数据库记录数失败: {e}")
                return 0

        # 使用数据库查询缓存
        rock_db_count = cache_database_query("rock_count", query_rock_db_count, ttl=180)

        modeling_record_count = 0
        if modeling_state.merged_df is not None:
            modeling_record_count = int(len(modeling_state.merged_df))

        borehole_file_count = int(modeling_state.borehole_file_count or 0)

        return {
            "status": "success",
            "stats": {
                "rock_db_count": rock_db_count,
                "borehole_file_count": borehole_file_count,
                "modeling_record_count": modeling_record_count,
            },
        }
    except Exception as e:
        print(f"[ERROR] get_dashboard_stats 发生错误: {e}")
        import traceback
        traceback.print_exc()
        # 返回默认值而不是抛出异常
        return {
            "status": "success",
            "stats": {
                "rock_db_count": 0,
                "borehole_file_count": 0,
                "modeling_record_count": 0,
            },
        }


@app.get("/api/borehole-data")
async def get_borehole_data(db: Session = Depends(get_session)):
    """获取钻孔数据 (从数据库中读取所有记录)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            return []
        
        # 获取所有记录
        columns = [column.name for column in table.columns]
        stmt = select(*[table.c[col] for col in columns])
        rows = db.execute(stmt).mappings().all()
        
        records = []
        for row in rows:
            row_dict = dict(row)
            records.append(_serialize_row(row_dict, columns))
        
        return records
    except Exception as e:
        print(f"[ERROR] get_borehole_data 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.get("/api/summary-data")
async def get_summary_data(db: Session = Depends(get_session)):
    """获取汇总数据 (从数据库中读取并按矿名分组)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            return []
        
        column_map = {column.name: column for column in table.columns}
        
        # 如果有矿名列，按矿名分组统计
        if "矿名" in column_map:
            stmt = (
                select(
                    column_map["矿名"].label("mine_name"),
                    func.count().label("record_count")
                )
                .where(column_map["矿名"].is_not(None))
                .group_by(column_map["矿名"])
            )
            rows = db.execute(stmt).all()
            
            summary = []
            for row in rows:
                summary.append({
                    "矿名": row.mine_name,
                    "记录数": int(row.record_count)
                })
            return summary
        else:
            # 如果没有矿名列，返回空数组
            return []
    except Exception as e:
        print(f"[ERROR] get_summary_data 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.get("/api/coal-seam-data")
async def get_coal_seam_data(db: Session = Depends(get_session)):
    """获取煤层数据 (从数据库中筛选包含"煤"的岩性记录)"""
    try:
        table = _get_records_table_safe()
        if table is None:
            return []
        
        column_map = {column.name: column for column in table.columns}
        columns = [column.name for column in table.columns]
        
        # 如果有岩性列，筛选包含"煤"的记录
        if "岩性" in column_map:
            stmt = (
                select(*[table.c[col] for col in columns])
                .where(column_map["岩性"].like("%煤%"))
            )
            rows = db.execute(stmt).mappings().all()
            
            records = []
            for row in rows:
                row_dict = dict(row)
                records.append(_serialize_row(row_dict, columns))
            return records
        else:
            # 如果没有岩性列，尝试岩层名称列
            if "岩层名称" in column_map:
                stmt = (
                    select(*[table.c[col] for col in columns])
                    .where(column_map["岩层名称"].like("%煤%"))
                )
                rows = db.execute(stmt).mappings().all()
                
                records = []
                for row in rows:
                    row_dict = dict(row)
                    records.append(_serialize_row(row_dict, columns))
                return records
            else:
                return []
    except Exception as e:
        print(f"[ERROR] get_coal_seam_data 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.post("/api/get_feasibility_evaluation_levels")
async def get_feasibility_evaluation_levels():
    """获取上行开采可行性等级评估标准"""
    return {
        "status": "success",
        "data": {
            "levels": [
                {
                    "level": "I级 (不可行/极困难)",
                    "omega_range": "0-2",
                    "description": "煤层基本处于垮落带内，完整度破坏非常严重，上行开采不合理或过于危险。"
                },
                {
                    "level": "II级 (困难)",
                    "omega_range": "2-4",
                    "description": "上行开采难度大，易出现顶板问题和巷道支护困难，需要重型支护或充填。"
                },
                {
                    "level": "III级 (可行，需支护)",
                    "omega_range": "4-6",
                    "description": "中等破坏程度，顶板和煤层少量破碎，但裂隙发育程度大。技术上可行，局部需加强支护。"
                },
                {
                    "level": "IV级 (良好)",
                    "omega_range": "6-8",
                    "description": "轻微破坏，煤层完整性良好，顶板有少量裂隙，下沉量微小，上行开采效果较好。"
                },
                {
                    "level": "V级 (优良)",
                    "omega_range": "8以上",
                    "description": "煤层基本不受下煤层开采的影响，煤层间的相互作用基本不存在，上行开采不存在困难。"
                }
            ]
        }
    }


@app.post("/api/calculate_upward_mining_feasibility")
async def calculate_upward_mining_feasibility(request: dict):
    """计算单个钻孔的上行开采可行度"""
    try:
        from upward_mining_feasibility import process_borehole_csv_for_feasibility
        
        # 验证必需参数
        required_params = ['csv_file_path', 'bottom_coal_name', 'upper_coal_name']
        for param in required_params:
            if param not in request or not request[param]:
                raise HTTPException(status_code=400, detail=f'缺少必需参数: {param}')
        
        csv_file_path = request['csv_file_path']
        bottom_coal_name = request['bottom_coal_name']
        upper_coal_name = request['upper_coal_name']
        lamda = request.get('lamda', 4.95)
        C = request.get('C', -0.84)
        
        # 检查文件是否存在
        if not Path(csv_file_path).exists():
            raise HTTPException(status_code=404, detail=f'文件不存在: {csv_file_path}')
        
        # 调用计算函数
        result = process_borehole_csv_for_feasibility(
            csv_file_path, bottom_coal_name, upper_coal_name, lamda, C
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {"status": "success", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] calculate_upward_mining_feasibility 发生错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'计算失败: {str(e)}')


@app.post("/api/batch_calculate_upward_mining_feasibility")
async def batch_calculate_upward_mining_feasibility(request: dict):
    """批量计算钻孔的上行开采可行度"""
    try:
        from upward_mining_feasibility import batch_process_borehole_files
        
        # 验证必需参数
        required_params = ['csv_file_paths', 'bottom_coal_name', 'upper_coal_name']
        for param in required_params:
            if param not in request or not request[param]:
                raise HTTPException(status_code=400, detail=f'缺少必需参数: {param}')
        
        csv_file_paths = request['csv_file_paths']
        bottom_coal_name = request['bottom_coal_name']
        upper_coal_name = request['upper_coal_name']
        lamda = request.get('lamda', 4.95)
        C = request.get('C', -0.84)
        
        # 验证文件列表
        if not isinstance(csv_file_paths, list) or len(csv_file_paths) == 0:
            raise HTTPException(status_code=400, detail='CSV文件路径列表不能为空')
        
        # 检查所有文件是否存在
        for file_path in csv_file_paths:
            if not Path(file_path).exists():
                raise HTTPException(status_code=404, detail=f'文件不存在: {file_path}')
        
        # 调用批量计算函数
        result = batch_process_borehole_files(
            csv_file_paths, bottom_coal_name, upper_coal_name, lamda, C
        )
        
        return {"status": "success", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] batch_calculate_upward_mining_feasibility 发生错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'批量计算失败: {str(e)}')


@app.post("/api/auto_calibrate_upward_mining_coefficients")
async def auto_calibrate_upward_mining_coefficients(request: dict):
    """自动标定上行开采计算的系数(λ和C)"""
    try:
        from upward_mining_feasibility import auto_calibrate_coefficients
        
        # 验证必需参数
        required_params = ['csv_file_paths', 'bottom_coal_name', 'upper_coal_name']
        for param in required_params:
            if param not in request or not request[param]:
                raise HTTPException(status_code=400, detail=f'缺少必需参数: {param}')
        
        csv_file_paths = request['csv_file_paths']
        bottom_coal_name = request['bottom_coal_name']
        upper_coal_name = request['upper_coal_name']
        initial_lamda = request.get('initial_lamda', 4.95)
        initial_C = request.get('initial_C', -0.84)
        
        # 验证文件列表
        if not isinstance(csv_file_paths, list) or len(csv_file_paths) == 0:
            raise HTTPException(status_code=400, detail='CSV文件路径列表不能为空')
        
        # 检查所有文件是否存在
        for file_path in csv_file_paths:
            if not Path(file_path).exists():
                raise HTTPException(status_code=404, detail=f'文件不存在: {file_path}')
        
        # 调用自动标定函数
        result = auto_calibrate_coefficients(
            csv_file_paths, bottom_coal_name, upper_coal_name, initial_lamda, initial_C
        )
        
        return {"status": "success", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] auto_calibrate_upward_mining_coefficients 发生错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'标定失败: {str(e)}')


@app.post("/api/csv/columns")
async def get_csv_columns(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供CSV文件")
    data = await file.read()
    df = _read_csv_bytes(data)
    return {"status": "success", "columns": df.columns.tolist()}


@app.post("/api/csv/transform")
async def transform_csv(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    target_columns: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供CSV文件")

    try:
        mapping_dict: Dict[str, str] = json.loads(mapping or "{}")
        targets: List[str] = json.loads(target_columns or "[]")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="映射或列信息格式错误")

    data = await file.read()
    df = _read_csv_bytes(data)

    output = pd.DataFrame()
    for target in targets:
        source_col = mapping_dict.get(target)
        if source_col and source_col in df.columns:
            output[target] = df[source_col]
        else:
            output[target] = ["" for _ in range(len(df))]

    filename = file.filename or "formatted.csv"
    if "." in filename:
        stem, ext = filename.rsplit(".", 1)
        download_name = f"{stem}_formatted.{ext}"
    else:
        download_name = f"{filename}_formatted.csv"

    csv_content = output.to_csv(index=False, encoding="utf-8-sig")
    buffer = io.BytesIO(csv_content.encode("utf-8-sig"))
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={download_name}"},
    )


@app.post("/api/borehole/analyze")
async def analyze_borehole_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个钻孔文件")

    summary = {
        "total_files": len(files),
        "successful_files": 0,
        "failed_files": 0,
        "warning_files": 0,
        "total_coal_records": 0,
        "error_details": [],
        "warning_details": [],
        "file_details": [],
        "processing_time": 0.0,
    }

    combined_records: List[Dict[str, Any]] = []
    start_time = time.perf_counter()

    for upload in files:
        filename = upload.filename or "未命名.csv"
        detail = {"file_name": filename, "status": "pending", "message": "", "coal_records": 0}
        try:
            file_bytes = await upload.read()
            if not file_bytes:
                raise ValueError("文件内容为空")

            records, message, level = process_single_borehole_file(file_bytes, filename)
            detail.update({
                "status": level,
                "message": message,
                "coal_records": len(records),
            })

            if level == "error":
                summary["failed_files"] += 1
                summary["error_details"].append(f"{filename}: {message}")
            elif level == "warning":
                summary["warning_files"] += 1
                summary["warning_details"].append(f"{filename}: {message}")
                if records:
                    combined_records.extend(records)
                    summary["total_coal_records"] += len(records)
            else:
                summary["successful_files"] += 1
                if records:
                    combined_records.extend(records)
                    summary["total_coal_records"] += len(records)
        except Exception as exc:  # pragma: no cover - best effort for malformed files
            detail.update({
                "status": "error",
                "message": str(exc),
                "coal_records": 0,
            })
            summary["failed_files"] += 1
            summary["error_details"].append(f"{filename}: {exc}")
        finally:
            summary["file_details"].append(detail)

    summary["processing_time"] = round(time.perf_counter() - start_time, 3)

    columns: List[str] = []
    if combined_records:
        seen: List[str] = []
        for record in combined_records:
            for key in record.keys():
                if key not in seen:
                    seen.append(key)
        columns = seen

    message = "分析完成" if summary["successful_files"] else "未成功处理任何文件"
    if summary["total_coal_records"] == 0:
        message = "未提取到有效煤层记录"

    return {
        "status": "success",
        "message": message,
        "columns": columns,
        "records": combined_records,
        "summary": summary,
    }


@app.post("/api/keystratum/files")
async def upload_keystratum_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一个岩层数据文件")

    key_stratum_state.reset()

    total = len(files)
    valid = 0
    errors: List[str] = []
    stored: Dict[str, pd.DataFrame] = {}

    for upload in files:
        filename = upload.filename or "未命名.csv"
        try:
            content = await upload.read()
            if not content:
                raise ValueError("文件内容为空")
            df = _read_csv_bytes(content)
            df = unify_columns(df)
            df = _normalize_key_columns(df)
            
            # 如果CSV中已经有钻孔名列，删除它(因为会从文件名重新生成)
            if "钻孔名" in df.columns:
                df = df.drop(columns=["钻孔名"])
            
            # 同样删除数据来源列(会从文件名重新生成)
            if "数据来源" in df.columns:
                df = df.drop(columns=["数据来源"])
            
            if "岩层名称" not in df.columns:
                raise ValueError("缺少列: 岩层名称")
            if "厚度/m" not in df.columns:
                raise ValueError("缺少列: 厚度/m")
            df["岩层名称"] = df["岩层名称"].astype(str).str.strip()
            df = _ensure_seam_column(df)
            stored[filename] = df
            valid += 1
        except Exception as exc:
            errors.append(f"{filename}: {exc}")
            continue

    if not stored:
        raise HTTPException(status_code=400, detail="文件解析失败，请检查格式")

    key_stratum_state.files = stored
    preview = _prepare_preview(stored)

    return {
        "status": "success",
        "file_count": total,
        "valid_count": valid,
        "errors": errors,
        "preview": preview,
    }


@app.post("/api/keystratum/fill")
async def fill_keystratum_from_database():
    if not key_stratum_state.files:
        raise HTTPException(status_code=400, detail="请先上传岩层数据文件")

    key_stratum_state.last_result = None

    table = _get_records_table_or_500()
    columns = [column.name for column in table.columns]
    lithology_col = "岩性"
    if lithology_col not in columns:
        raise HTTPException(status_code=400, detail="岩性数据库缺少 '岩性' 列")

    numeric_cols = [col for col in DEFAULT_NUMERIC_COLUMNS if col in columns]

    available_numeric = numeric_cols
    if not available_numeric:
        raise HTTPException(status_code=400, detail="数据库缺少可用于填充的数值列")

    query_columns = [table.c[lithology_col]] + [table.c[col] for col in available_numeric]
    with get_engine().connect() as connection:
        db_df = pd.read_sql(select(*query_columns), connection)

    if db_df.empty:
        raise HTTPException(status_code=400, detail="数据库中没有可用于填充的岩性记录")

    db_df[lithology_col] = db_df[lithology_col].astype(str).str.strip()
    db_df[lithology_col] = db_df[lithology_col].map(_normalize_lithology_name)
    db_df = db_df[db_df[lithology_col].astype(bool)]
    stats_map = (
        db_df.groupby(lithology_col)[available_numeric]
        .median(numeric_only=True)
        .dropna(how="all")
    )
    stats_map = stats_map.reindex(columns=numeric_cols, fill_value=np.nan)

    updated: Dict[str, pd.DataFrame] = {}
    for filename, df in key_stratum_state.files.items():
        updated[filename] = _fill_from_database(df, stats_map)

    key_stratum_state.files = updated
    key_stratum_state.filled = True
    preview = _prepare_preview(updated)

    return {
        "status": "success",
        "message": "已根据数据库填充缺失参数",
        "preview": preview,
    }


@app.get("/api/keystratum/coals")
async def get_keystratum_coals():
    if not key_stratum_state.files:
        raise HTTPException(status_code=400, detail="请先上传岩层数据文件")

    coals: set[str] = set()
    for df in key_stratum_state.files.values():
        column = df.get("岩层名称")
        if column is None:
            continue
        coals.update(
            value
            for value in column.astype(str).str.strip()
            if value and ("煤" in value or "煤层" in value)
        )

    sorted_coals = sorted(coals)
    return {"status": "success", "coals": sorted_coals}


class KeyStratumRequest(BaseModel):
    coal: str


@app.post("/api/keystratum/process")
async def process_keystratum(request: KeyStratumRequest):
    if not key_stratum_state.files:
        raise HTTPException(status_code=400, detail="请先上传岩层数据文件")
    coal_name = request.coal.strip() if request.coal else ""
    if not coal_name:
        raise HTTPException(status_code=400, detail="请选择目标岩层")

    key_stratum_state.last_result = None

    print(f"[DEBUG] 开始处理关键层, 目标煤层: {coal_name}")
    print(f"[DEBUG] 文件数量: {len(key_stratum_state.files)}")
    for filename in key_stratum_state.files.keys():
        print(f"[DEBUG] 文件: {filename}")
        df = key_stratum_state.files[filename]
        print(f"[DEBUG]   行数: {len(df)}, 列: {df.columns.tolist()}")
        if "岩层名称" in df.columns:
            unique_names = df["岩层名称"].unique().tolist()
            print(f"[DEBUG]   岩层名称: {unique_names[:10]}")  # 只打印前10个
        else:
            print(f"[DEBUG]   缺少'岩层名称'列!")

    processed: List[pd.DataFrame] = []
    errors: List[str] = []
    processed_count = 0

    for filename, df in key_stratum_state.files.items():
        print(f"[DEBUG] 处理文件: {filename}, 行数: {len(df)}")
        try:
            working_df = df.copy()
            if "岩层名称" not in working_df.columns:
                raise ValueError("缺少列: 岩层名称")
            
            # 查找煤层
            mask = working_df["岩层名称"].astype(str).str.strip() == coal_name
            print(f"[DEBUG]   查找煤层 '{coal_name}', 匹配行数: {mask.sum()}")
            
            if not mask.any():
                errors.append(f"{filename}: 未找到目标岩层 {coal_name}")
                continue
            coal_indices = working_df[mask].index.tolist()
            coal_idx = coal_indices[0]
            coal_seam_df = working_df.loc[[coal_idx]]
            df_above = working_df.loc[: coal_idx - 1].copy()
            if df_above.empty:
                errors.append(f"{filename}: 目标岩层上方无岩层")
                continue

            required_cols = ["厚度/m", "弹性模量/GPa", "容重/kN·m-3", "抗拉强度/MPa"]
            for col in required_cols:
                if col not in df_above.columns:
                    raise ValueError(f"缺少列: {col}")

            key_info = calculate_key_strata_details(df_above, coal_seam_df)

            result_df = working_df.copy()
            result_df.insert(0, "钻孔名", Path(filename).stem)
            result_df["关键层标记"] = "-"
            result_df["距煤层距离/m"] = 0.0
            result_df.loc[coal_idx, "关键层标记"] = "煤层"

            cumulative_above = 0.0
            for row_idx in range(len(df_above) - 1, -1, -1):
                actual_idx = df_above.index[row_idx]
                thickness = pd.to_numeric(df_above.iloc[row_idx]["厚度/m"], errors="coerce")
                thickness = float(thickness) if pd.notna(thickness) else 0.0
                distance = round(cumulative_above + thickness / 2, 2)
                result_df.loc[actual_idx, "距煤层距离/m"] = distance
                cumulative_above += thickness

            if coal_idx < len(result_df) - 1:
                cumulative_below = 0.0
                for row_idx in range(coal_idx + 1, len(result_df)):
                    thickness = pd.to_numeric(result_df.iloc[row_idx]["厚度/m"], errors="coerce")
                    thickness = float(thickness) if pd.notna(thickness) else 0.0
                    cumulative_below += thickness
                    result_df.iat[row_idx, result_df.columns.get_loc("距煤层距离/m")] = round(-cumulative_below, 2)

            above_mask = result_df.index < coal_idx
            for item in key_info:
                lithology_name = str(item.get("岩性", "")).replace("(PKS)", "").strip()
                if not lithology_name:
                    continue
                distance = float(item.get("距煤层距离", 0))
                match_mask = (
                    above_mask
                    & (result_df["岩层名称"].astype(str).str.strip() == lithology_name)
                    & np.isclose(result_df["距煤层距离/m"], distance, atol=0.1)
                )
                if match_mask.any():
                    result_df.loc[match_mask, "关键层标记"] = item.get("SK_Label", "-")

            processed.append(result_df)
            processed_count += 1
        except Exception as exc:
            errors.append(f"{filename}: {exc}")
            continue

    if not processed:
        key_stratum_state.last_result = None
        print(f"[DEBUG] 处理失败! 错误信息: {errors}")
        return {
            "status": "error",
            "message": "未成功处理任何文件",
            "errors": errors,
        }

    combined_df = pd.concat(processed, ignore_index=True, sort=False).fillna("")
    columns = combined_df.columns.tolist()
    records = json.loads(combined_df.to_json(orient="records", force_ascii=False))

    key_stratum_state.last_result = combined_df

    print(f"[DEBUG] 处理成功! 处理了 {processed_count} 个文件")
    return {
        "status": "success",
        "message": "关键层计算完成",
        "columns": columns,
        "records": records,
        "processed_count": processed_count,
        "errors": errors,
    }


@app.get("/api/keystratum/export")
async def export_keystratum_results(format: str = Query("xlsx", regex="^(xlsx|csv)$")):
    df = key_stratum_state.last_result
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="当前没有可导出的关键层计算结果")

    buffer = io.BytesIO()
    if format == "csv":
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        filename = "关键层计算结果.csv"
        media_type = "text/csv"
    else:
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False, sheet_name="关键层分析结果")
        filename = "关键层计算结果.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    buffer.seek(0)
    quoted_name = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_name}"
    }
    return StreamingResponse(buffer, media_type=media_type, headers=headers)


# ==================== 原始数据导入接口(仅用于全局数据管理) ====================
@app.post("/api/raw/import")
async def import_raw_stratum_data(files: List[UploadFile] = File(...)):
    """
    导入原始岩层数据(不做任何业务处理,直接读取CSV)
    用于Dashboard全局数据管理
    过滤掉关键层计算相关的字段,只保留原始岩层属性
    """
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一个CSV文件")

    # 定义需要排除的列名模式(关键层计算相关字段)
    # 注意: "关键层标记"列不排除,会被改名为"岩层"
    exclude_patterns = [
        r'^关键层\d+',           # 关键层1, 关键层2, 关键层1岩性等
        r'距煤层距离',
        r'距.*煤.*顶',           # 距煤层顶板, 距顶煤等
        r'关键层.*厚度',
        r'关键层.*岩性',
        r'关键层.*距',
    ]
    
    import re
    def should_exclude_column(col_name):
        """判断列名是否应该被排除"""
        for pattern in exclude_patterns:
            if re.search(pattern, str(col_name)):
                return True
        return False

    total = len(files)
    valid = 0
    errors: List[str] = []
    all_records = []
    columns_set = set()
    excluded_columns = set()

    for upload in files:
        filename = upload.filename or "未命名.csv"
        try:
            content = await upload.read()
            if not content:
                raise ValueError("文件内容为空")
            
            # 简单读取CSV,不做任何业务处理
            df = _read_csv_bytes(content)
            
            # 过滤掉计算字段
            original_columns = df.columns.tolist()
            filtered_columns = [col for col in original_columns if not should_exclude_column(col)]
            excluded = [col for col in original_columns if should_exclude_column(col)]
            excluded_columns.update(excluded)
            
            # 只保留原始字段
            df = df[filtered_columns]
            
            # 只做基本的列名统一(厚度/m等)
            df = unify_columns(df)
            
            # 标准化关键列名(名称→岩层名称, 厚度→厚度/m等)
            df = _normalize_key_columns(df)
            
            # 提取钻孔名(从文件名中,去掉扩展名)
            import os
            borehole_name = os.path.splitext(filename)[0]
            
            # 添加钻孔名列(放在最前面)
            df.insert(0, '钻孔名', borehole_name)
            
            # 将"煤层"列改名为"岩层"(如果存在)
            if '煤层' in df.columns:
                df = df.rename(columns={'煤层': '岩层'})
            
            # 添加数据来源列
            df['数据来源'] = filename
            
            # 收集所有列名
            columns_set.update(df.columns.tolist())
            
            # 转为记录
            records = json.loads(df.to_json(orient="records", force_ascii=False))
            all_records.extend(records)
            
            valid += 1
        except Exception as exc:
            errors.append(f"{filename}: {str(exc)}")
            continue

    if not all_records:
        raise HTTPException(status_code=400, detail="未能成功解析任何文件")

    columns = sorted(list(columns_set))
    
    result = {
        "status": "success",
        "file_count": total,
        "valid_count": valid,
        "errors": errors,
        "records": all_records,
        "columns": columns,
        "record_count": len(all_records),
    }
    
    # 添加排除字段信息(用于调试)
    if excluded_columns:
        result["excluded_columns"] = sorted(list(excluded_columns))
    
    return result
