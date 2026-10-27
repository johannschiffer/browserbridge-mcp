"""Open source support notice. Printed to stderr so MCP stdio traffic on stdout is never affected."""
import os
import sys

NOTICE = '100% Free & Open Source (MIT). Support development on Ko-fi: https://ko-fi.com/johannschiffer'


def print_upgrade_notice():
    if os.environ.get("GENESIS_NO_NOTICE") == "1":
        return
    print(NOTICE, file=sys.stderr)
