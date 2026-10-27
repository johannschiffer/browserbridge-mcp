"""
BrowserBridge Pro CLI Entrypoint
"""

import sys
import argparse
import json
from .server import BrowserBridgeProServer
from .core.receipts_engine import DurableReceiptsEngine

def main():
    parser = argparse.ArgumentParser(
        prog="browserbridge-pro",
        description="BrowserBridge Pro: Headless Browser Session Bridge & Durable Action Receipts"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run stdio
    run_parser = subparsers.add_parser("run", help="Start the BrowserBridge Pro MCP server over stdio")
    run_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    # Verify receipts
    verify_parser = subparsers.add_parser("verify-trail", help="Verify cryptographic continuity of actions")
    verify_parser.add_argument("--session", type=str, default="default", help="Session ID")
    verify_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    # List receipts
    list_parser = subparsers.add_parser("receipts", help="List action receipts for a session")
    list_parser.add_argument("--session", type=str, default="default", help="Session ID")
    list_parser.add_argument("--db", type=str, default=None, help="Path to receipts database")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        db_path = getattr(args, "db", None)
        server = BrowserBridgeProServer(db_path=db_path)
        server.run_stdio()
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
            print(f"  [{r['status'].upper()}] {r['action_type']} -> {r['target']} (pre: {r['pre_state_hash'][:8]}... post: {r['post_state_hash'][:8]}...) at {r['created_at']}")

if __name__ == "__main__":
    main()
