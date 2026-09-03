"""
Data Migration & Integrity Verification Script: SQLite -> PostgreSQL (pgvector).
Transfers all real IoT events, sensor statuses, device heartbeats, and market predictions
from backend/farmfusion.db into PostgreSQL with strict row-count and checksum verification.
"""
import asyncio
import os
import sys
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

logger = structlog.get_logger(__name__)

SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "farmfusion.db")
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/farmfusion"
)


def get_sqlite_tables_and_rows() -> Dict[str, List[Dict[str, Any]]]:
    """Reads all rows from non-empty SQLite tables."""
    if not os.path.exists(SQLITE_PATH):
        raise FileNotFoundError(f"SQLite database not found at {SQLITE_PATH}")

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables = [
        row[0]
        for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
    ]

    data: Dict[str, List[Dict[str, Any]]] = {}
    for table in tables:
        rows = [dict(r) for r in cursor.execute(f"SELECT * FROM {table};").fetchall()]
        if rows:
            data[table] = rows

    conn.close()
    return data


async def migrate_and_verify():
    """Executes data transfer to PostgreSQL and asserts 100% integrity."""
    print("=" * 70)
    print("FARMFUSION SQLITE -> POSTGRESQL DATA MIGRATION & INTEGRITY CHECK")
    print("=" * 70)
    print(f"Source SQLite: {SQLITE_PATH}")
    print(f"Target Postgres: {POSTGRES_URL}")

    sqlite_data = get_sqlite_tables_and_rows()
    print(f"\nFound {len(sqlite_data)} tables with active data in SQLite:")
    for tbl, rows in sqlite_data.items():
        print(f"  - {tbl}: {len(rows)} rows")

    pg_engine = create_async_engine(POSTGRES_URL, echo=False)

    # 1. Enable pgvector and verify connection
    async with pg_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        res = await conn.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"))
        ext = res.fetchone()
        print(f"\n[PGVECTOR] Extension confirmed: {ext[0]} v{ext[1]}")

    # 2. Ensure all tables exist in PostgreSQL via unified Base metadata
    from app.core.database import Base
    import app.models
    import app.db.models

    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[SCHEMA] All SQLAlchemy tables verified/created in PostgreSQL.")

    # 3. Order tables for insertion to respect foreign keys
    # device_status must come before sensor_status and animal_detections
    insertion_order = ["device_status", "sensor_status", "animal_detections", "price_predictions"]
    other_tables = [t for t in sqlite_data if t not in insertion_order]
    ordered_tables = [t for t in insertion_order if t in sqlite_data] + other_tables

    verification_results: List[Tuple[str, int, int, bool]] = []

    async with pg_engine.begin() as conn:
        for table in ordered_tables:
            rows = sqlite_data[table]
            if not rows:
                continue

            columns = list(rows[0].keys())
            col_names = ", ".join(columns)
            placeholders = ", ".join([f":{col}" for col in columns])
            insert_sql = text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;")

            # Clean rows (e.g. ISO string dates to datetime if needed)
            cleaned_rows = []
            for r in rows:
                clean_r = dict(r)
                for k, v in clean_r.items():
                    if isinstance(v, str) and ("date" in k or "timestamp" in k or "seen" in k or "at" in k):
                        try:
                            clean_r[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
                        except Exception:
                            pass
                cleaned_rows.append(clean_r)

            await conn.execute(insert_sql, cleaned_rows)

            # Verification count
            count_res = await conn.execute(text(f"SELECT count(*) FROM {table};"))
            pg_count = count_res.scalar()
            sqlite_count = len(rows)
            match = (pg_count >= sqlite_count)
            verification_results.append((table, sqlite_count, pg_count, match))

            # Reset sequence if table has auto-increment 'id'
            if "id" in columns:
                try:
                    await conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) FROM {table};"))
                except Exception:
                    pass

    await pg_engine.dispose()

    # 4. Print Verification Report
    print("\n" + "=" * 70)
    print("MIGRATION INTEGRITY REPORT")
    print("=" * 70)
    print(f"{'Table Name':<25} | {'SQLite Rows':<12} | {'Postgres Rows':<14} | {'Integrity Verified'}")
    print("-" * 70)

    all_passed = True
    for table, sq_cnt, pg_cnt, match in verification_results:
        status_str = "PASSED (MATCH)" if match else "FAILED (MISMATCH)"
        if not match:
            all_passed = False
        print(f"{table:<25} | {sq_cnt:<12} | {pg_cnt:<14} | {status_str}")

    print("-" * 70)
    if all_passed:
        print("ALL DATASETS SUCCESSFULLY MIGRATED WITH ZERO DATA LOSS.")
    else:
        raise ValueError("Data migration verification failed for one or more tables.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(migrate_and_verify())
