"""Import the aggregated rock data CSV into the SQLite database used by the FastAPI backend.

Usage:
    python scripts/import_database.py [--csv path/to/汇总表.csv] [--database path/to/database.db]
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT_DIR / "data" / "input" / "汇总表.csv"
DEFAULT_DB = ROOT_DIR / "data" / "database.db"
ENCODINGS = ("utf-8-sig", "utf-8", "gbk", "gb2312")


def read_source(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"未找到源文件: {csv_path}")

    last_error: Optional[Exception] = None
    for encoding in ENCODINGS:
        try:
            return pd.read_csv(csv_path, encoding=encoding)
        except Exception as exc:  # pragma: no cover - fallback decoding attempts
            last_error = exc
            continue
    raise RuntimeError(f"无法读取 CSV，最后一次错误: {last_error}")


def import_to_sqlite(csv_path: Path, db_path: Path) -> None:
    df = read_source(csv_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS records"))
    df.to_sql("records", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        if "份" in df.columns:
            conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_province ON records ("份")')
        if "矿名" in df.columns:
            conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_mine ON records ("矿名")')
        if "岩性" in df.columns:
            conn.exec_driver_sql('CREATE INDEX IF NOT EXISTS idx_records_lithology ON records ("岩性")')

    print(f"已导入 {len(df)} 条记录到 {db_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将汇总数据导入 SQLite 数据库")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="原始 CSV 文件路径")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB, help="SQLite 数据库存放路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import_to_sqlite(args.csv, args.database)


if __name__ == "__main__":
    main()
