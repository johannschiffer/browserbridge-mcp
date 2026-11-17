"""Genesis Blackbox SQLite WAL telemetry bridge."""

import json
import os
import sqlite3
import time
from typing import Any, Optional

NOTICE = ""


def print_upgrade_notice() -> None:
    pass


def resolve_blackbox_db(db_path: Optional[str] = None) -> Optional[str]:
    if db_path:
        return db_path
    env_db = os.environ.get("BLACKBOX_DB_PATH", "").strip()
    if env_db:
        return env_db
    default_db = os.path.join(".blackbox", "wal.sqlite")
    if os.path.exists(default_db) or os.path.isdir(".blackbox"):
        return default_db
    return None


def is_blackbox_enabled(db_path: Optional[str] = None) -> bool:
    return resolve_blackbox_db(db_path) is not None


def record_blackbox_event(
    event_type: str,
    payload: Any,
    source: str,
    duration_ms: Optional[float] = None,
    status: str = "ok",
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Optional[int]:
    target_db = resolve_blackbox_db(db_path)
    if not target_db:
        return None
    try:
        if target_db != ":memory:":
            parent = os.path.dirname(os.path.abspath(target_db))
            if parent:
                os.makedirs(parent, exist_ok=True)
        payload_json = json.dumps(payload, default=str)
        ts = time.time()
        conn = sqlite3.connect(target_db, timeout=5.0)
        try:
            if target_db != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS blackbox_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        event_type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        duration_ms REAL,
                        trace_id TEXT,
                        span_id TEXT,
                        status TEXT NOT NULL,
                        payload TEXT NOT NULL
                    );
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bb_timestamp ON blackbox_events(timestamp);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bb_event_type ON blackbox_events(event_type);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bb_trace_id ON blackbox_events(trace_id);")
                cursor = conn.execute(
                    """
                    INSERT INTO blackbox_events (
                        timestamp, event_type, source, duration_ms, trace_id, span_id, status, payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (ts, event_type, source, duration_ms, trace_id, span_id, status, payload_json),
                )
                return cursor.lastrowid
        finally:
            conn.close()
    except Exception:
        return None
