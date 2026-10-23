"""Upgrade notice. Printed to stderr so MCP stdio traffic on stdout is never affected."""
import os
import sys

NOTICE = 'BrowserBridge MCP (open edition). Starter Kit, free: https://johanld.gumroad.com/l/khffw | Enterprise Suite ($19): https://johanld.gumroad.com/l/tzuvz'


def print_upgrade_notice():
    if os.environ.get("GENESIS_NO_NOTICE") == "1":
        return
    print(NOTICE, file=sys.stderr)
