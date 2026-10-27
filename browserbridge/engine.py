"""
BrowserBridge Pro Engine
Headless browser session manager with DOM state hashing for durable receipts.
"""

import re
import html
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx

logger = logging.getLogger("BrowserBridgeProEngine")

class BrowserSession:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.current_url: str = "about:blank"
        self.title: str = "Blank Page"
        self.html: str = "<html><body></body></html>"
        self.status_code: int = 200
        self.form_state: Dict[str, str] = {}
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.last_active: str = datetime.now(timezone.utc).isoformat()

    def get_dom_hash(self) -> str:
        """Computes SHA-256 hash of the current DOM state."""
        return hashlib.sha256(self.html.encode("utf-8")).hexdigest()

    def navigate(self, url: str) -> Dict[str, Any]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.get(url, headers={"User-Agent": "BrowserBridge-MCP-Pro/1.0.0 (Headless Agent)"})
                self.current_url = str(resp.url)
                self.status_code = resp.status_code
                self.html = resp.text
                m_title = re.search(r"<title>(.*?)</title>", self.html, re.IGNORECASE | re.DOTALL)
                self.title = m_title.group(1).strip() if m_title else "Untitled Page"
        except Exception as e:
            logger.warning(f"Navigation to {url} failed: {e}. Falling back to simulated DOM.")
            self.current_url = url
            self.status_code = 502
            self.title = f"Failed to load: {url}"
            self.html = f"<html><body><h1>Navigation Error</h1><p>{str(e)}</p></body></html>"

        return self.get_status()

    def extract_clean_text(self) -> str:
        self.last_active = datetime.now(timezone.utc).isoformat()
        text = re.sub(r"<(script|style|svg|noscript)[^>]*>.*?</\1>", "", self.html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<(br|p|div|h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        # Compress whitespace
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def extract_accessibility_tree(self) -> List[Dict[str, Any]]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        aom_nodes = []
        node_counter = 1

        # 1. Buttons
        for m in re.finditer(r"<button([^>]*)>(.*?)</button>", self.html, re.IGNORECASE | re.DOTALL):
            attrs, content = m.groups()
            text = re.sub(r"<[^>]+>", "", content).strip() or "Unnamed Button"
            aom_nodes.append({
                "id": f"@node-{node_counter}",
                "role": "button",
                "name": text,
                "selector": f"button:contains('{text[:20]}')"
            })
            node_counter += 1

        # 2. Links
        for m in re.finditer(r"<a\s+([^>]*href=[\"']([^\"']*)[\"'][^>]*)>(.*?)</a>", self.html, re.IGNORECASE | re.DOTALL):
            _, href, content = m.groups()
            text = re.sub(r"<[^>]+>", "", content).strip()
            if text and not href.startswith("javascript:"):
                aom_nodes.append({
                    "id": f"@node-{node_counter}",
                    "role": "link",
                    "name": text[:50],
                    "target_url": href,
                    "selector": f"a[href='{href}']"
                })
                node_counter += 1

        # 3. Inputs
        for m in re.finditer(r"<input\s+([^>]*)/?>", self.html, re.IGNORECASE):
            attrs = m.group(1)
            name_m = re.search(r"name=[\"']([^\"']*)[\"']", attrs, re.IGNORECASE)
            type_m = re.search(r"type=[\"']([^\"']*)[\"']", attrs, re.IGNORECASE)
            name_val = name_m.group(1) if name_m else f"input_{node_counter}"
            type_val = type_m.group(1) if type_m else "text"
            aom_nodes.append({
                "id": f"@node-{node_counter}",
                "role": "textbox" if type_val in ("text", "email", "password", "search") else type_val,
                "name": name_val,
                "selector": f"input[name='{name_val}']",
                "current_value": self.form_state.get(name_val, "")
            })
            node_counter += 1

        return aom_nodes[:50]

    def click(self, selector: str) -> Dict[str, Any]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        # Simulated state change on click
        self.html += f"<!-- Action: Clicked {selector} -->"
        return {
            "status": "clicked",
            "selector": selector,
            "session_id": self.session_id,
            "timestamp": self.last_active
        }

    def fill(self, selector: str, value: str) -> Dict[str, Any]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        key = selector.replace("input[name='", "").replace("']", "")
        self.form_state[key] = value
        self.html += f"<!-- Action: Filled {selector} with '{value}' -->"
        return {
            "status": "filled",
            "selector": selector,
            "value": value,
            "session_id": self.session_id,
            "timestamp": self.last_active
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "url": self.current_url,
            "title": self.title,
            "status_code": self.status_code,
            "dom_hash": self.get_dom_hash()[:16],
            "html_length_bytes": len(self.html),
            "form_fields_filled": len(self.form_state),
            "last_active": self.last_active
        }

# Backward compatibility alias
BrowserEngine = BrowserSession


class BrowserEngine:
    def __init__(self):
        self.sessions: Dict[str, BrowserSession] = {}

    def get_or_create_session(self, session_id: str = "default") -> BrowserSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = BrowserSession(session_id=session_id)
        return self.sessions[session_id]

    def navigate(self, url: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return session.navigate(url)

    def extract_clean_text(self, session_id: str = "default") -> str:
        session = self.get_or_create_session(session_id)
        return session.extract_clean_text()

    def extract_accessibility_tree(self, session_id: str = "default") -> List[Dict[str, Any]]:
        session = self.get_or_create_session(session_id)
        return session.extract_accessibility_tree()

    def click_element(self, selector: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return session.click(selector)

    def fill_form_field(self, selector: str, value: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return session.fill(selector, value)

    def get_page_status(self, session_id: str = "default") -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return session.get_status()
