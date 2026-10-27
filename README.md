# browserbridge-mcp (v1.0.0)

[![PyPI version](https://img.shields.io/badge/PyPI-v1.0.0-blue.svg)](https://pypi.org/project/browserbridge-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

<a href="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp/badge" alt="browserbridge-mcp MCP server" />
</a>

[![PyPI](https://img.shields.io/pypi/v/browserbridge-mcp.svg)](https://pypi.org/project/browserbridge-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol: MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![Python: >=3.10](https://img.shields.io/badge/Python->=3.10-yellow.svg)](https://python.org/)

**BrowserBridge MCP** is a lightweight headless browser session bridge and Accessibility Object Model (AOM) inspector designed for AI coding assistants (Claude Desktop, Cursor, OpenAI Codex, LangGraph).

It enables agents to navigate web applications, extract semantic clean text, and interact with web pages without drowning the LLM context window in massive HTML blobs.

---

## Run without cloning

```bash
uvx browserbridge-mcp
```

Claude Desktop / Cursor config entry:

```json
{
  "mcpServers": {
    "browserbridge-mcp": {
      "command": "uvx",
      "args": [
        "browserbridge-mcp"
      ]
    }
  }
}
```

[![CI](https://github.com/johannschiffer/browserbridge-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/browserbridge-mcp/actions/workflows/ci.yml)

## 🎯 The Problem

When autonomous AI agents interact with web pages:
1. **Context Window Exhaustion:** Dumping 2MB of raw HTML, scripts, CSS, and SVG icons into an LLM exhausts the token budget within 3 turns.
3. **Zombie Memory Leaks:** Unmanaged headless browsers leak memory on the host system when agents drop sessions without cleanup.

---

## Features

- 🌐 **Headless Navigation**: Fetch and navigate web pages with automatic redirect handling.
- 🌳 **Accessibility Tree (AOM) Extraction**: Filters noisy DOMs into structured interactive nodes (buttons, links, textboxes) with stable `@node` identifiers.
- 🧹 **Clean Text Extractor**: Strips scripts, ads, and formatting for fast summarization.
- 📜 **Durable Action Receipts Engine**: Generates cryptographic SHA-256 receipts for every web action, linking pre/post DOM hashes with visual state snapshots.
- 🛡️ **Session Pool Manager with Anti-Zombie Auto-Cleanup**: Manages multiple browser contexts with strict inactivity TTLs, preventing memory leaks on your host.
- 🎯 **Visual Element Selector & Coordinate Resolver**: Resolves robust CSS/XPath selectors and handles dynamic single-page applications (SPAs).
- 🐳 **Production Docker & Compose**: Containerized headless Chromium runtime ready for cloud execution.
- 🧪 **100% Passing Pytest Suite**.
---

## 🚀 Quickstart

### 1. Installation

```bash
git clone https://github.com/johannschiffer/browserbridge-mcp.git
cd browserbridge-mcp
pip install -e .
```

### 2. Configure in Claude Desktop or Cursor

Add to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "browserbridge": {
      "command": "browserbridge",
      "args": ["run"]
    }
  }
}
```

### 3. CLI Inspection

```bash
# Inspect clean accessibility nodes of any website
browserbridge aom https://news.ycombinator.com
```

---

## 🛠️ MCP Tools Reference

| Tool | Parameters | Description |
|---|---|---|
| `navigate_page` | `url`, `session_id` | Navigates headless browser to destination URL |
| `extract_clean_text` | `session_id` | Extracts cleaned markdown text from page |
| `extract_accessibility_tree` | `session_id` | Extracts compact interactive elements (AOM) |
| `click_element` | `selector`, `session_id` | Simulates click on interactive element |
| `fill_form_field` | `selector`, `value`, `session_id` | Fills input or textarea field |
| `get_page_status` | `session_id` | Returns current URL, title, and response code |

---

## Genesis MCP Ecosystem

| Module | Description | Repository |
|---|---|---|
| **CrawlEngine MCP** | Anti-bot web scraping, clean Markdown, proxy rotation, and TLS evasion | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Deterministic headless browser automation with cryptographic action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Zero-trust PostgreSQL/SQLite guard, live PII masking, and schema inspection | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification bus with persistent SQLite queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Safe Linux administration, systemd automation, and port auditing | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Production FastMCP server scaffolder with stdio and SSE middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

## Support

If you find this project helpful, you can support its ongoing maintenance on [Ko-fi](https://ko-fi.com/johannschiffer).

## License

MIT © 2026 [Johann Schiffer](https://github.com/johannschiffer)
