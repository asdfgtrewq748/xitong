"""
数据库性能优化 - 索引管理
适用于SQLite数据库的轻量级优化
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from contextlib import contextmanager


APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT.parent / "data" / "database.db"


@contextmanager
def get_db_connection():
    """获取数据库连接 (上下文管理器)"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_indexes():
    """创建性能优化索引"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='records'"
        )
        if not cursor.fetchone():
            print("[数据库优化] records表不存在，跳过索引创建")
            return

        # 获取表的列信息
        cursor.execute("PRAGMA table_info(records)")
        columns = {row[1] for row in cursor.fetchall()}

        print("[数据库优化] 开始创建索引...")

        indexes_created = 0

        # 1. 省份索引 (常用于分组查询)
        province_candidates = ["省份", "省份名称", "所在省份", "所属省份"]
        for col in province_candidates:
            if col in columns:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_province ON records({col})")
                    print(f"  ✓ 创建索引: idx_province ({col})")
                    indexes_created += 1
                    break
                except Exception as e:
                    print(f"  ✗ 索引创建失败: {col} - {e}")

        # 2. 岩性索引 (常用于查询和分组)
        if "岩性" in columns:
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_lithology ON records(岩性)")
                print(f"  ✓ 创建索引: idx_lithology (岩性)")
                indexes_created += 1
            except Exception as e:
                print(f"  ✗ 索引创建失败: 岩性 - {e}")

        # 3. 矿名索引
        if "矿名" in columns:
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_mine ON records(矿名)")
                print(f"  ✓ 创建索引: idx_mine (矿名)")
                indexes_created += 1
            except Exception as e:
                print(f"  ✗ 索引创建失败: 矿名 - {e}")

        # 4. 复合索引: 省份 + 岩性 (常见组合查询)
        province_col = None
        for col in province_candidates:
            if col in columns:
                province_col = col
                break

        if province_col and "岩性" in columns:
            try:
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_province_lithology "
                    f"ON records({province_col}, 岩性)"
                )
                print(f"  ✓ 创建复合索引: idx_province_lithology ({province_col}, 岩性)")
                indexes_created += 1
            except Exception as e:
                print(f"  ✗ 复合索引创建失败: {e}")

        conn.commit()
        print(f"\n[数据库优化] 完成! 成功创建 {indexes_created} 个索引")


def analyze_database():
    """分析数据库并更新统计信息"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        print("[数据库优化] 分析数据库...")
        cursor.execute("ANALYZE")
        conn.commit()
        print("  ✓ ANALYZE 完成")


def vacuum_database():
    """清理数据库碎片"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        print("[数据库优化] 清理数据库碎片...")
        cursor.execute("VACUUM")
        conn.commit()
        print("  ✓ VACUUM 完成")


def get_database_stats() -> Dict[str, Any]:
    """获取数据库统计信息"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        stats = {}

        # 数据库大小
        db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
        stats["db_size_mb"] = round(db_size / (1024 * 1024), 2)

        # 表行数
        cursor.execute("SELECT COUNT(*) FROM records")
        stats["record_count"] = cursor.fetchone()[0]

        # 索引列表
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='records'"
        )
        stats["indexes"] = [row[0] for row in cursor.fetchall()]

        # 页面统计
        cursor.execute("PRAGMA page_count")
        stats["page_count"] = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_size")
        stats["page_size"] = cursor.fetchone()[0]

        return stats


def optimize_sqlite_settings(conn: sqlite3.Connection):
    """优化SQLite运行时设置"""
    cursor = conn.cursor()

    # 启用WAL模式 (提高并发性能)
    cursor.execute("PRAGMA journal_mode=WAL")

    # 设置缓存大小 (10MB)
    cursor.execute("PRAGMA cache_size=-10000")  # 负数表示KB

    # 同步模式设置为NORMAL (平衡性能和安全性)
    cursor.execute("PRAGMA synchronous=NORMAL")

    # 临时文件存储在内存中
    cursor.execute("PRAGMA temp_store=MEMORY")

    # 启用mmap (内存映射IO,提升读性能)
    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB

    conn.commit()


def apply_all_optimizations():
    """应用所有数据库优化"""
    print("\n" + "=" * 60)
    print("数据库性能优化".center(60))
    print("=" * 60 + "\n")

    if not DB_PATH.exists():
        print(f"[错误] 数据库文件不存在: {DB_PATH}")
        return

    # 1. 创建索引
    create_indexes()

    # 2. 分析数据库
    analyze_database()

    # 3. 清理碎片
    vacuum_database()

    # 4. 显示统计信息
    stats = get_database_stats()
    print("\n" + "-" * 60)
    print("数据库统计信息".center(60))
    print("-" * 60)
    print(f"数据库大小: {stats['db_size_mb']} MB")
    print(f"记录总数: {stats['record_count']:,}")
    print(f"索引数量: {len(stats['indexes'])}")
    print(f"索引列表: {', '.join(stats['indexes']) if stats['indexes'] else '无'}")
    print(f"页面数量: {stats['page_count']:,}")
    print(f"页面大小: {stats['page_size']} bytes")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    apply_all_optimizations()
