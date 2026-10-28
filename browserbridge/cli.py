"""
BrowserBridge CLI Entrypoint.
"""

import argparse
import json
import sys

from . import __version__
from .core.receipts_engine import DurableReceiptsEngine
from .engine import BrowserSession
from .server import BrowserBridgeServer


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="browserbridge",
        description="BrowserBridge: HTTP/DOM Session Bridge, AOM Extractor, and Durable Action Receipts",
    )
    parser.add_argument("-v", "--version", action="version", version=f"browserbridge-mcp {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    run_parser = subparsers.add_parser("run", help="Start the BrowserBridge MCP server over stdio")
    run_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    aom_parser = subparsers.add_parser("aom", help="Fetch a URL and print its Accessibility Object Model (AOM) nodes")
    aom_parser.add_argument("url", type=str, help="Target HTTP(S) URL")

    verify_parser = subparsers.add_parser("verify-trail", help="Verify SHA-256 continuity of session actions")
    verify_parser.add_argument("--session", type=str, default="default", help="Session ID")
    verify_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    list_parser = subparsers.add_parser("receipts", help="List action receipts for a session")
    list_parser.add_argument("--session", type=str, default="default", help="Session ID")
    list_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        db_path = getattr(args, "db", None)
        server = BrowserBridgeServer(db_path=db_path)
        server.run_stdio()
    elif args.command == "aom":
        session = BrowserSession(session_id="cli-aom")
        try:
            session.navigate(args.url)
        except ValueError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(2)
        print(json.dumps(session.extract_accessibility_tree(), indent=2, ensure_ascii=False))
    elif args.command == "verify-trail":
        receipts = DurableReceiptsEngine(db_path=args.db)
        res = receipts.verify_action_trail(args.session)
        print("=== ACTION TRAIL VERIFICATION ===")
        print(f"Session:     {res['session_id']}")
        print(f"Valid Chain: {res['valid']}")
        print(f"Status:      {res['status']}")
        print(f"Total Acts:  {res['total_actions']}")
    elif args.command == "receipts":
        receipts = DurableReceiptsEngine(db_path=args.db)
        items = receipts.list_receipts(args.session)
        print(f"Found {len(items)} action receipts for session '{args.session}':")
        for r in items:
            print(
                f"  [{r['status'].upper()}] {r['action_type']} -> {r['target']} "
                f"(pre: {r['pre_state_hash'][:8]}... post: {r['post_state_hash'][:8]}...) at {r['created_at']}"
            )


if __name__ == "__main__":
    main()
