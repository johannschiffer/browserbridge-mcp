"""
Security and protocol hardening tests for browserbridge-mcp v2.0.1.
"""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from browserbridge import __version__
from browserbridge.engine import BrowserSession
from browserbridge.server import BrowserBridgeServer


def test_ssrf_guard_blocks_internal_and_metadata_urls(tmp_path):
    server = BrowserBridgeServer(db_path=str(tmp_path / "receipts.db"))
    for bad_url in (
        "http://127.0.0.1:8080/internal",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:3000",
        "file:///etc/passwd",
        "http://2130706433/admin",
    ):
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "navigate_page", "arguments": {"url": bad_url}},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == -32602


def test_verify_action_trail_default_session_and_db_permissions(tmp_path):
    db_file = tmp_path / "perm_receipts.db"
    server = BrowserBridgeServer(db_path=str(db_file))
    assert stat.S_IMODE(os.stat(db_file).st_mode) == 0o600

    # Calling verify_action_trail with empty arguments must use default session
    resp = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "verify_action_trail", "arguments": {}},
        }
    )
    assert resp["result"]["isError"] is False
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["session_id"] == "default"
    assert data["valid"] is True


def test_malformed_jsonrpc_and_cli_aom_and_version(tmp_path):
    server = BrowserBridgeServer(db_path=str(tmp_path / "r.db"))
    assert server.handle_request([1, 2])["error"]["code"] == -32600  # type: ignore[arg-type]

    null_args = server.handle_request(
        {"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "get_pool_status", "arguments": None}}
    )
    assert null_args["result"]["isError"] is False

    repo_root = str(Path(__file__).resolve().parents[1])
    env = {**os.environ, "PYTHONPATH": repo_root, "BROWSERBRIDGE_DB_PATH": str(tmp_path / "cli.db")}
    ver = subprocess.run(
        [sys.executable, "-m", "browserbridge.cli", "--version"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert ver.returncode == 0
    assert __version__ in ver.stdout

    # Test CLI aom subcommand rejection of SSRF URL
    bad_aom = subprocess.run(
        [sys.executable, "-m", "browserbridge.cli", "aom", "http://127.0.0.1:8080"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert bad_aom.returncode == 2

    # Test BrowserSession AOM extraction directly via mocked get
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.url = "https://example.org"
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><button>Submit</button><a href='/about'>About</a></body></html>"
        mock_get.return_value = mock_resp

        sess = BrowserSession("aom-test")
        sess.navigate("https://example.org")
        nodes = sess.extract_accessibility_tree()
        assert len(nodes) == 2
        assert nodes[0]["role"] == "button"
