import json
import sqlite3
import subprocess
import sys

from browserbridge.server import BrowserBridgeServer


def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import browserbridge._genesis; browserbridge._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import browserbridge._genesis
    assert browserbridge._genesis.NOTICE == ""


def test_blackbox_bridge_records_mcp_tool_event(monkeypatch, tmp_path):
    wal_db = tmp_path / "wal.sqlite"
    monkeypatch.setenv("BLACKBOX_DB_PATH", str(wal_db))

    server = BrowserBridgeServer(db_path=str(tmp_path / "receipts.db"))
    res = server.call_tool("get_pool_status", {})
    assert "active_sessions_count" in res

    wal_conn = sqlite3.connect(str(wal_db))
    rows = wal_conn.execute(
        "SELECT event_type, source, status, payload FROM blackbox_events ORDER BY id ASC;"
    ).fetchall()
    wal_conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "MCP_TOOL"
    assert rows[0][1] == "browserbridge-mcp"
    assert rows[0][2] == "ok"
    payload = json.loads(rows[0][3])
    assert payload["tool"] == "get_pool_status"
