"""
BrowserBridge MCP workflow recipe.
Demonstrates session DOM interaction, AOM extraction, and SHA-256 receipt chain verification.
"""
import json
import tempfile
from pathlib import Path

from browserbridge.server import BrowserBridgeServer


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_file = Path(tmp) / "receipts.db"
        server = BrowserBridgeServer(db_path=str(db_file))
        sess = server.pool.get_or_create("demo")
        sess.html = (
            "<html><head><title>Portal</title></head>"
            "<body><form><input name='email' /><button id='login'>Sign In</button></form></body></html>"
        )

        aom = server.call_tool("extract_accessibility_tree", {"session_id": "demo"})
        server.call_tool(
            "fill_form_field",
            {"selector": "input[name='email']", "value": "agent@example.com", "session_id": "demo"},
        )
        server.call_tool("click_element", {"selector": "#login", "session_id": "demo"})
        trail = server.call_tool("verify_action_trail", {"session_id": "demo"})

        print(
            json.dumps(
                {
                    "aom_nodes": len(aom),
                    "trail": trail,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
