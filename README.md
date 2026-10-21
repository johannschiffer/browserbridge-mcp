# BrowserBridge MCP (Lite Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol: MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![Python: >=3.10](https://img.shields.io/badge/Python->=3.10-yellow.svg)](https://python.org/)

**BrowserBridge MCP** is a lightweight headless browser session bridge and Accessibility Object Model (AOM) inspector designed for AI coding assistants (Claude Desktop, Cursor, OpenAI Codex, LangGraph).

It enables agents to navigate web applications, extract semantic clean text, and interact with web pages without drowning the LLM context window in massive HTML blobs.

---

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

👉 **[Get BrowserBridge Pro on Gumroad ($14.99 USD)](https://johanld.gumroad.com/l/cfqto)**

---

## 📄 License

MIT © 2026 [Johann Schiffer](https://github.com/johannschiffer)
