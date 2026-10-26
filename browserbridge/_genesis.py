"""Upgrade notice. Printed to stderr so MCP stdio traffic on stdout is never affected."""
import os
import sys

NOTICE = '[Solución Enterprise] Bypass de rate limits, soporte multi-tenant y Docker precompilado: https://johanld.gumroad.com/l/genesis-enterprise-suite | Starter Kit ($0+): https://johanld.gumroad.com/l/genesis-starter-kit'


def print_upgrade_notice():
    if os.environ.get("GENESIS_NO_NOTICE") == "1":
        return
    print(NOTICE, file=sys.stderr)
