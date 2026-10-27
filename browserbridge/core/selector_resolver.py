"""
BrowserBridge Visual Element Selector & Coordinate Resolver
Resolves robust selectors that survive dynamic class hashing and client-side SPA re-rendering.
"""

import re
from typing import Dict, Any, Optional

class SelectorResolver:
    @staticmethod
    def resolve_selector(query: str, html: str) -> Dict[str, Any]:
        """
        Translates human queries, AOM node IDs, or text queries into robust CSS/XPath targets.
        """
        clean_q = query.strip()

        # Case 1: Already an explicit CSS/ID selector
        if clean_q.startswith("#") or clean_q.startswith(".") or "[" in clean_q:
            return {
                "resolved_selector": clean_q,
                "strategy": "explicit_css",
                "confidence": 1.0
            }

        # Case 2: AOM node identifier (@node-3)
        if clean_q.startswith("@node-"):
            return {
                "resolved_selector": f"[data-aom-id='{clean_q}']",
                "aom_id": clean_q,
                "strategy": "aom_node",
                "confidence": 0.95
            }

        # Case 3: Test ID or aria-label match
        test_id_m = re.search(rf"data-testid=[\"']({re.escape(clean_q)})[\"']", html, re.IGNORECASE)
        if test_id_m:
            return {
                "resolved_selector": f"[data-testid='{test_id_m.group(1)}']",
                "strategy": "data_testid",
                "confidence": 0.98
            }

        aria_m = re.search(rf"aria-label=[\"']([^\"']*{re.escape(clean_q)}[^\"']*)[\"']", html, re.IGNORECASE)
        if aria_m:
            return {
                "resolved_selector": f"[aria-label='{aria_m.group(1)}']",
                "strategy": "aria_label",
                "confidence": 0.92
            }

        # Case 4: Text-based heuristic (buttons or links containing text)
        btn_m = re.search(rf"<button[^>]*>([^<]*?{re.escape(clean_q)}[^<]*?)</button>", html, re.IGNORECASE)
        if btn_m:
            return {
                "resolved_selector": f"button:has-text('{clean_q}')",
                "strategy": "button_text",
                "confidence": 0.88
            }

        # Default fallback
        return {
            "resolved_selector": f":has-text('{clean_q}')",
            "strategy": "text_fallback",
            "confidence": 0.75
        }
