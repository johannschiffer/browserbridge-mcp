"""
BrowserBridge Durable Action Receipts Engine.
Issues append-only SHA-256 DOM state transition receipts for web agent actions.
"""

import contextlib
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class DurableReceiptsEngine:
    def __init__(self, db_path: Optional[str] = None):
        env_path = os.getenv("BROWSERBRIDGE_DB_PATH", "").strip()
        resolved = db_path or env_path
        if not resolved:
            data_dir = Path.home() / ".browserbridge"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "receipts.db")
        else:
            self.db_path = resolved
            if self.db_path != ":memory:":
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self) -> None:
        with contextlib.closing(self._get_connection()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_receipts (
                    receipt_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    payload TEXT,
                    pre_state_hash TEXT NOT NULL,
                    post_state_hash TEXT NOT NULL,
                    status TEXT DEFAULT 'success',
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_receipts_session ON action_receipts(session_id);")
        if self.db_path != ":memory:":
            try:
                os.chmod(self.db_path, 0o600)
            except OSError:
                pass

    def issue_receipt(
        self,
        session_id: str,
        action_type: str,
        target: str,
        pre_state_hash: str,
        post_state_hash: str,
        payload: str = "",
        status: str = "success",
    ) -> Dict[str, Any]:
        """Creates and stores an action receipt."""
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        with contextlib.closing(self._get_connection()) as conn:
            conn.execute(
                """
                INSERT INTO action_receipts (
                    receipt_id, session_id, action_type, target, payload,
                    pre_state_hash, post_state_hash, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (receipt_id, session_id, action_type, target, payload, pre_state_hash, post_state_hash, status, now),
            )

        return {
            "receipt_id": receipt_id,
            "session_id": session_id,
            "action_type": action_type,
            "target": target,
            "pre_state_hash": pre_state_hash[:16],
            "post_state_hash": post_state_hash[:16],
            "status": status,
            "timestamp": now,
        }

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """Fetches receipt details by receipt_id."""
        with contextlib.closing(self._get_connection()) as conn:
            cursor = conn.execute("SELECT * FROM action_receipts WHERE receipt_id = ?;", (receipt_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_receipts(self, session_id: str = "default", limit: int = 20) -> List[Dict[str, Any]]:
        """Lists chronological action receipts for a session."""
        with contextlib.closing(self._get_connection()) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM action_receipts
                WHERE session_id = ?
                ORDER BY created_at ASC, rowid ASC
                LIMIT ?;
                """,
                (session_id, limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def verify_action_trail(self, session_id: str = "default") -> Dict[str, Any]:
        """Validates that all actions form a contiguous chain of DOM state transitions."""
        receipts = self.list_receipts(session_id, limit=100)
        if not receipts:
            return {
                "session_id": session_id,
                "valid": True,
                "total_actions": 0,
                "broken_transitions": 0,
                "status": "VERIFIED_AUDITABLE",
                "message": "No receipts recorded.",
            }

        broken_links = 0
        for i in range(len(receipts) - 1):
            curr_post = receipts[i]["post_state_hash"]
            next_pre = receipts[i + 1]["pre_state_hash"]
            if curr_post != next_pre:
                broken_links += 1

        return {
            "session_id": session_id,
            "valid": broken_links == 0,
            "total_actions": len(receipts),
            "broken_transitions": broken_links,
            "status": "VERIFIED_AUDITABLE" if broken_links == 0 else "COMPROMISED_CHAIN",
        }
