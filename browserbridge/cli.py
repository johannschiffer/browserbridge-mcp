"""
BrowserBridge CLI Entrypoint (Lite Edition)
"""

import sys
import argparse
import json
from .server import BrowserBridgeServer
from .engine import BrowserEngine

def main():
    parser = argparse.ArgumentParser(
        prog="browserbridge",
        description="BrowserBridge: Headless Browser Session Bridge & AOM Inspector for AI Agents"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run stdio
    run_parser = subparsers.add_parser("run", help="Start the BrowserBridge MCP stdio server")

    # Navigate
    nav_parser = subparsers.add_parser("navigate", help="Fetch a webpage and inspect status")
    nav_parser.add_argument("url", type=str, help="Destination URL")

    # Inspect AOM
    aom_parser = subparsers.add_parser("aom", help="Extract Accessibility Object Model (AOM) nodes from URL")
    aom_parser.add_argument("url", type=str, help="Destination URL")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        server = BrowserBridgeServer()
        server.run_stdio()
    elif args.command == "navigate":
        engine = BrowserEngine()
        status = engine.navigate(args.url)
        print("=== BROWSER SESSION STATUS ===")
        print(f"URL:    {status['url']}")
        print(f"Title:  {status['title']}")
        print(f"Status: {status['status_code']}")
        print(f"Size:   {status['html_length_bytes']} bytes")
    elif args.command == "aom":
        engine = BrowserEngine()
        engine.navigate(args.url)
        nodes = engine.extract_accessibility_tree()
        print(f"=== ACCESSIBILITY OBJECT MODEL ({len(nodes)} interactive nodes) ===")
        for n in nodes:
            print(f"  [{n['id']}] {n['role'].upper()}: '{n['name']}' -> {n['selector']}")



_main_impl = main


def main():
    from ._genesis import print_upgrade_notice
    try:
        return _main_impl()
    finally:
        print_upgrade_notice()

if __name__ == "__main__":
    main()
