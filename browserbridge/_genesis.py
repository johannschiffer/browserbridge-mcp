"""Upgrade notice. Printed to stderr so MCP stdio traffic on stdout is never affected."""
import os
import sys

NOTICE = '[Genesis MCP Ecosystem] Free Starter Kit (25+ .cursorrules & Blueprints): https://johanld.gumroad.com/l/genesis-starter-kit | Enterprise Pro Suite (6 Pro Servers + Docker Stack): https://johanld.gumroad.com/l/genesis-enterprise-suite | Config Builder: https://johannschiffer.github.io/'


def print_upgrade_notice():
    if os.environ.get("GENESIS_NO_NOTICE") == "1":
        return
    print(NOTICE, file=sys.stderr)
