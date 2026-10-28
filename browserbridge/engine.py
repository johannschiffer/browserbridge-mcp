"""
BrowserBridge Engine.
Lightweight HTTP/DOM session manager with Accessibility Object Model (AOM) extraction
and SHA-256 DOM state hashing for durable receipts.
"""

import hashlib
import html
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

from . import __version__
from .core.url_guard import validate_navigation_url

logger = logging.getLogger("BrowserBridgeEngine")


def _check_redirect_ssrf(request: httpx.Request) -> None:
    validate_navigation_url(str(request.url))


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
        validated_url = validate_navigation_url(url)

        try:
            with httpx.Client(
                timeout=15.0,
                follow_redirects=True,
                max_redirects=5,
                event_hooks={"request": [_check_redirect_ssrf]},
            ) as client:
                resp = client.get(
                    validated_url,
                    headers={"User-Agent": f"BrowserBridge-MCP/{__version__}"},
                )
                self.current_url = str(resp.url)
                self.status_code = resp.status_code
                self.html = resp.text
                m_title = re.search(r"<title>(.*?)</title>", self.html, re.IGNORECASE | re.DOTALL)
                self.title = m_title.group(1).strip() if m_title else "Untitled Page"
        except ValueError:
            raise
        except Exception as e:
            logger.warning("Navigation to %s failed: %s", validated_url, e)
            self.current_url = validated_url
            self.status_code = 502
            self.title = f"Failed to load: {validated_url}"
            safe_err = html.escape(str(e))
            self.html = f"<html><body><h1>Navigation Error</h1><p>{safe_err}</p></body></html>"

        return self.get_status()

    def extract_clean_text(self) -> str:
        self.last_active = datetime.now(timezone.utc).isoformat()
        text = re.sub(r"<(script|style|svg|noscript)[^>]*>.*?</\1>", "", self.html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<(br|p|div|h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def extract_accessibility_tree(self) -> List[Dict[str, Any]]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        aom_nodes: List[Dict[str, Any]] = []
        node_counter = 1

        for m in re.finditer(r"<button([^>]*)>(.*?)</button>", self.html, re.IGNORECASE | re.DOTALL):
            _, content = m.groups()
            text = re.sub(r"<[^>]+>", "", content).strip() or "Unnamed Button"
            aom_nodes.append(
                {
                    "id": f"@node-{node_counter}",
                    "role": "button",
                    "name": text,
                    "selector": f"button:contains('{text[:20]}')",
                }
            )
            node_counter += 1

        for m in re.finditer(
            r"<a\s+([^>]*href=[\"']([^\"']*)[\"'][^>]*)>(.*?)</a>",
            self.html,
            re.IGNORECASE | re.DOTALL,
        ):
            _, href, content = m.groups()
            text = re.sub(r"<[^>]+>", "", content).strip()
            if text and not href.lower().startswith("javascript:"):
                aom_nodes.append(
                    {
                        "id": f"@node-{node_counter}",
                        "role": "link",
                        "name": text[:50],
                        "target_url": href,
                        "selector": f"a[href='{href}']",
                    }
                )
                node_counter += 1

        for m in re.finditer(r"<input\s+([^>]*)/?>", self.html, re.IGNORECASE):
            attrs = m.group(1)
            name_m = re.search(r"name=[\"']([^\"']*)[\"']", attrs, re.IGNORECASE)
            type_m = re.search(r"type=[\"']([^\"']*)[\"']", attrs, re.IGNORECASE)
            name_val = name_m.group(1) if name_m else f"input_{node_counter}"
            type_val = type_m.group(1) if type_m else "text"
            aom_nodes.append(
                {
                    "id": f"@node-{node_counter}",
                    "role": "textbox" if type_val in ("text", "email", "password", "search") else type_val,
                    "name": name_val,
                    "selector": f"input[name='{name_val}']",
                    "current_value": self.form_state.get(name_val, ""),
                }
            )
            node_counter += 1

        return aom_nodes[:50]

    def click(self, selector: str) -> Dict[str, Any]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        safe_sel = selector.replace("--", "- -")
        self.html += f"<!-- Action: Clicked {safe_sel} -->"
        return {
            "status": "clicked",
            "selector": selector,
            "session_id": self.session_id,
            "timestamp": self.last_active,
        }

    def fill(self, selector: str, value: str) -> Dict[str, Any]:
        self.last_active = datetime.now(timezone.utc).isoformat()
        key = selector.replace("input[name='", "").replace("']", "")
        self.form_state[key] = value
        safe_sel = selector.replace("--", "- -")
        safe_val = value.replace("--", "- -")
        self.html += f"<!-- Action: Filled {safe_sel} with '{safe_val}' -->"
        return {
            "status": "filled",
            "selector": selector,
            "value": value,
            "session_id": self.session_id,
            "timestamp": self.last_active,
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
            "last_active": self.last_active,
        }


class BrowserEngine:
    def __init__(self):
        self.sessions: Dict[str, BrowserSession] = {}

    def get_or_create_session(self, session_id: str = "default") -> BrowserSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = BrowserSession(session_id=session_id)
        return self.sessions[session_id]

    def navigate(self, url: str, session_id: str = "default") -> Dict[str, Any]:
        return self.get_or_create_session(session_id).navigate(url)

    def extract_clean_text(self, session_id: str = "default") -> str:
        return self.get_or_create_session(session_id).extract_clean_text()

    def extract_accessibility_tree(self, session_id: str = "default") -> List[Dict[str, Any]]:
        return self.get_or_create_session(session_id).extract_accessibility_tree()

    def click_element(self, selector: str, session_id: str = "default") -> Dict[str, Any]:
        return self.get_or_create_session(session_id).click(selector)

    def fill_form_field(self, selector: str, value: str, session_id: str = "default") -> Dict[str, Any]:
        return self.get_or_create_session(session_id).fill(selector, value)

    def get_page_status(self, session_id: str = "default") -> Dict[str, Any]:
        return self.get_or_create_session(session_id).get_status()
