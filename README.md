# BrowserBridge MCP (Lite Edition)

<a href="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/browserbridge-mcp/badge" alt="browserbridge-mcp MCP server" />
</a>



[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol: MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![Python: >=3.10](https://img.shields.io/badge/Python->=3.10-yellow.svg)](https://python.org/)


> ### ⚡ Enterprise Infrastructure & Tooling
> | Package | Access | Features |
> |---|---|---|
> | **Starter Kit** | **Free ($0+)** | 25+ `.cursorrules`, `CLAUDE.md` stack rules & MCP config templates. [Download Free](https://johanld.gumroad.com/l/genesis-starter-kit) |
> | **Enterprise Suite Pro** | **$19 USD** | 6 Pro MCP Servers, Zero-Downtime DB migrations, Residential Proxies, Docker Compose Stack & Commercial License. [Get Pro License](https://johanld.gumroad.com/l/genesis-enterprise-suite) |
> | **Config Generator** | **Free Web Tool** | Interactive visual config generator for Claude Desktop & Cursor. [Open Generator](https://johannschiffer.github.io/) |

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
        "--from",
        "git+https://github.com/johannschiffer/browserbridge-mcp",
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
2. **Brittle Selectors:** Agents fail to find buttons when modern websites use dynamic, hashed class names (`class="btn_3x9a_primary"`).
3. **Zombie Memory Leaks:** Unmanaged headless browsers leak memory on the host system when agents drop sessions without cleanup.

**BrowserBridge** solves this by converting web pages into a compact, token-efficient Accessibility Object Model (AOM) tree (~95% token reduction) and providing clean interaction primitives.

---

## ✨ Features (Lite Edition)

- 🌐 **Headless Navigation:** Fetch and navigate web pages with automatic redirect handling.
- 🌳 **Accessibility Tree (AOM) Extraction:** Filters noisy DOMs into structured interactive nodes (buttons, links, textboxes) with stable `@node` identifiers.
- 🧹 **Clean Text Extractor:** Strips scripts, ads, and formatting for fast summarization.
- ⚡ **Zero Browser Overhead:** Pure Python runtime compatible with Claude Desktop and Cursor.

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

## 🚀 Upgrade to BrowserBridge Pro

Need enterprise-grade auditability, durable execution receipts, and browser pool sandboxing?

The **BrowserBridge Pro Edition** adds:
- 📜 **Durable Action Receipts Engine:** Generates cryptographic SHA-256 receipts for every web action, linking pre/post DOM hashes with visual state snapshots.
- 🛡️ **Session Pool Manager con Anti-Zombie Auto-Cleanup:** Manages multiple browser contexts with strict inactivity TTLs, preventing memory leaks on your host.
- 🎯 **Visual Element Selector & Coordinate Resolver:** Resolves robust CSS/XPath selectors and handles dynamic single-page applications (SPAs).
- 🐳 **Production Docker & Compose:** Containerized headless Chromium runtime ready for cloud execution.
- 🧪 **100% Passing Pytest Suite.**

👉 **[Get the Genesis Enterprise Suite ($19)](https://johanld.gumroad.com/l/genesis-enterprise-suite)**

---

## 📄 License

MIT © 2026 [Johann Schiffer](https://github.com/johannschiffer)

## Recommended Infrastructure

Proxies that work well with BrowserBridge MCP. Some links are referral links.

- [Webshare](https://www.webshare.io/)
- [ScraperAPI](https://www.scraperapi.com/)
- [Bright Data](https://brightdata.com/)

## Genesis MCP Ecosystem

| Module | What it does | Repo |
|---|---|---|
| **CrawlEngine MCP** | Anti-bot web scraping, clean Markdown, proxy rotation and TLS evasion | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** (this repo) | Deterministic headless browser automation with cryptographic action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Zero-trust PostgreSQL/SQLite guard, live PII masking, zero-downtime migration checks | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification and webhook bus with a persistent SQLite WAL queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Safe Linux administration plane: systemd, port audit, isolated execution | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Production MCP server scaffolder: stdio, SSE and auth middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

[Live config builder](https://johannschiffer.github.io) | [Starter Kit, free](https://johanld.gumroad.com/l/genesis-starter-kit) | [Enterprise Suite, $19](https://johanld.gumroad.com/l/genesis-enterprise-suite)