# browserbridge-mcp (v2.0.0)

[![PyPI version](https://img.shields.io/badge/PyPI-v2.0.0-blue.svg)](https://pypi.org/project/browserbridge-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

> **100% Free & Open Source (MIT)**: All features, proxy rotation, migration simulation, Docker stacks, and recipes are completely unlocked. Support open development on [Ko-fi](https://ko-fi.com/johannschiffer).

> ### ⚡ Open Source Ecosystem & Community Tools
> | Resource | Access | Description |
> |---|---|---|
> | **Ruleset Bundle** | **100% Free** | 55+ production rulesets & MCP config templates. [Download Free](https://johannschiffer.github.io/) |
> | **Support & Donate** | **Ko-fi** | Support open-source maintenance. [Support on Ko-fi](https://ko-fi.com/johannschiffer) |

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

## ✨ Features (Open Source v2.0)

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

[Live config builder](https://johannschiffer.github.io) | [GitHub Profile](https://github.com/johannschiffer) | [Support on Ko-fi ☕](https://ko-fi.com/johannschiffer)

## Recommended Infrastructure & Sponsorship

- **Sponsorship & Corporate Support**: Support continued maintenance and priority feature requests via [GitHub Sponsors](https://github.com/sponsors/johannschiffer).
- **Verified Cloud & Network Infrastructure**:
  - **High-Performance VPS & Nodes**: [Hetzner Cloud](https://www.hetzner.com/cloud) & [DigitalOcean](https://m.do.co/c/johannschiffer)
  - **Reliable Proxy Pool & IP Rotation**: [Webshare](https://www.webshare.io/) & [Bright Data](https://brightdata.com/)
  - **Documentation & Setup Guides**: [johannschiffer.github.io](https://johannschiffer.github.io/)
