from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT.parent / "data" / "database.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None
_metadata = MetaData()
_records_table: Table | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return _engine


def get_sessionmaker() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return _SessionLocal


@contextmanager
def session_scope() -> Iterator[Session]:
    SessionLocal = get_sessionmaker()
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_records_table() -> Table:
    global _records_table
    if _records_table is None:
        metadata = MetaData()
        metadata.reflect(bind=get_engine(), only=["records"])
        if "records" not in metadata.tables:
            raise RuntimeError("数据库尚未初始化，请先运行数据导入脚本")
        _records_table = metadata.tables["records"]
    return _records_table


def reset_table_cache() -> None:
    global _records_table
    _records_table = None


def get_session() -> Iterator[Session]:
    SessionLocal = get_sessionmaker()
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
