# browserbridge-mcp

[![PyPI version](https://img.shields.io/pypi/v/browserbridge-mcp.svg)](https://pypi.org/project/browserbridge-mcp/)
[![CI](https://github.com/johannschiffer/browserbridge-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/browserbridge-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)
[![M8ven Score](https://m8ven.ai/badge/mcp/johannschiffer-browserbridge-mcp-1irvww?v=68bac05bace4b136ae00c003d3b1daeb)](https://m8ven.ai/mcp/johannschiffer-browserbridge-mcp-1irvww?s=readme)

<a href="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp/badge" alt="browserbridge-mcp MCP server" />
</a>

**BrowserBridge MCP** is a lightweight HTTP/DOM session bridge, Accessibility Object Model (AOM) extractor, and SHA-256 action receipt ledger for **Model Context Protocol (2024-11-05)** agents.

Instead of launching heavy browser binaries for static or server-rendered web workflows, BrowserBridge fetches HTML over `httpx`, distills interactive elements into compact `@node` trees, tracks stateful form/click transitions per session, and records append-only SHA-256 DOM hash chains in SQLite.

## Features

- **HTTP Navigation with Redirect SSRF Guard**: Validates initial and redirect URLs against loopback, RFC1918 private networks, and cloud metadata (`169.254.169.254`).
- **Accessibility Object Model (AOM) Extraction**: Condenses `<button>`, `<a href>`, and `<input>` elements into compact `@node-N` descriptors.
- **Clean Text Extraction**: Strips `<script>`, `<style>`, `<svg>`, and markup noise into readable plain text.
- **SHA-256 Durable Action Receipts**: Every `navigate_page`, `click_element`, and `fill_form_field` call records `pre_state_hash` and `post_state_hash` transitions in SQLite (`~/.browserbridge/receipts.db`, `0600`) for audit verification via `verify_action_trail`.
- **Session Pool Reaper**: Isolates concurrent `session_id` states and evicts idle sessions automatically after configurable TTL expiration.

## Quickstart

### Run with `uvx`

```bash
uvx browserbridge-mcp
```

### Claude Desktop / Cursor Configuration

```json
{
  "mcpServers": {
    "browserbridge-mcp": {
      "command": "uvx",
      "args": ["browserbridge-mcp"]
    }
  }
}
```

### CLI Inspection

```bash
# Inspect interactive AOM nodes of a public web page
browserbridge aom https://example.com

# Verify SHA-256 receipt continuity for a session
browserbridge verify-trail --session default
```

## MCP Tools Reference

| Tool | Parameters | Description |
|---|---|---|
| `navigate_page` | `url`, `session_id` | Fetch an HTTP(S) page into session state and issue a SHA-256 receipt |
| `extract_clean_text` | `session_id` | Extract plain readable text from the current session HTML |
| `extract_accessibility_tree` | `session_id` | Extract compact interactive AOM nodes (`@node-1`, buttons, links, inputs) |
| `click_element` | `selector`, `session_id` | Resolve selector/AOM target, record session click state, and issue a receipt |
| `fill_form_field` | `selector`, `value`, `session_id` | Populate session form field state and issue a receipt |
| `get_page_status` | `session_id` | Return current URL, title, HTTP status code, and truncated DOM hash |
| `get_action_receipt` | `receipt_id` | Fetch full stored receipt record by `receipt_id` |
| `verify_action_trail` | `session_id` | Verify contiguous `post_state_hash == next.pre_state_hash` chain across a session |
| `get_pool_status` | *(none)* | Inspect active session count, session IDs, and idle TTL configuration |

## Genesis MCP Ecosystem

| Module | Description | Repository |
|---|---|---|
| **CrawlEngine MCP** | HTTP web extraction to clean Markdown, JSON-LD parsing, and proxy rotation | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Lightweight HTTP/DOM session automation with SHA-256 action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Read-only PostgreSQL/SQLite query guard, PII masking, and dry-run mutations | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification bus with SQLite retry queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Linux systemd inspection, confined log tailing, and port auditing | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Zero-dependency FastMCP framework, CLI scaffolder, and SSE middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

## Support

If you find this project useful, you can support maintenance on [Ko-fi](https://ko-fi.com/johannschiffer).

## License

MIT (c) 2026 [Johann Schiffer](https://github.com/johannschiffer)
