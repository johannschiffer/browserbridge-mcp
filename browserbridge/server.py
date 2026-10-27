"""
BrowserBridge Pro MCP Server
Exposes headless browser orchestration, durable action receipts,
session pool management, and accessibility tree inspection over stdio.
"""

import sys
import json
import logging
from typing import Callable, Dict, Any, List, Optional
from .engine import BrowserSession
from .core.session_pool import SessionPoolManager
from .core.receipts_engine import DurableReceiptsEngine
from .core.selector_resolver import SelectorResolver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BrowserBridge-Pro] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("BrowserBridgeProServer")

class BrowserBridgeProServer:
    def __init__(self, db_path: Optional[str] = None, idle_ttl_seconds: int = 180):
        self.name = "browserbridge-mcp"
        self.version = "1.0.0"
        self.pool = SessionPoolManager(idle_ttl_seconds=idle_ttl_seconds)
        self.receipts = DurableReceiptsEngine(db_path=db_path)
        self.resolver = SelectorResolver()
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_tools()

    def _register_tool(self, name: str, description: str, func: Callable, properties: Dict[str, Any], required: List[str]):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required
            },
            "func": func
        }

    def navigate_with_receipt(self, url: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.pool.get_or_create(session_id)
        pre_hash = session.get_dom_hash()
        status = session.navigate(url)
        post_hash = session.get_dom_hash()

        receipt = self.receipts.issue_receipt(
            session_id=session_id,
            action_type="navigate",
            target=url,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash
        )
        status["action_receipt"] = receipt
        return status

    def click_with_receipt(self, selector: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.pool.get_or_create(session_id)
        resolved = self.resolver.resolve_selector(selector, session.html)
        target_selector = resolved["resolved_selector"]

        pre_hash = session.get_dom_hash()
        res = session.click(target_selector)
        post_hash = session.get_dom_hash()

        receipt = self.receipts.issue_receipt(
            session_id=session_id,
            action_type="click",
            target=target_selector,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash
        )
        res["resolved_selector"] = resolved
        res["action_receipt"] = receipt
        return res

    def fill_with_receipt(self, selector: str, value: str, session_id: str = "default") -> Dict[str, Any]:
        session = self.pool.get_or_create(session_id)
        resolved = self.resolver.resolve_selector(selector, session.html)
        target_selector = resolved["resolved_selector"]

        pre_hash = session.get_dom_hash()
        res = session.fill(target_selector, value)
        post_hash = session.get_dom_hash()

        receipt = self.receipts.issue_receipt(
            session_id=session_id,
            action_type="fill",
            target=target_selector,
            payload=value,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash
        )
        res["resolved_selector"] = resolved
        res["action_receipt"] = receipt
        return res

    def _register_tools(self):
        # 1. navigate_page
        self._register_tool(
            name="navigate_page",
            description="Navigate to URL with automatic DOM state hashing and durable receipt generation.",
            func=self.navigate_with_receipt,
            properties={
                "url": {"type": "string", "description": "Target web address."},
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=["url"]
        )

        # 2. extract_clean_text
        self._register_tool(
            name="extract_clean_text",
            description="Extract readable text from current web page, stripping markup, scripts and styles.",
            func=lambda session_id="default": self.pool.get_or_create(session_id).extract_clean_text(),
            properties={
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=[]
        )

        # 3. extract_accessibility_tree
        self._register_tool(
            name="extract_accessibility_tree",
            description="Extract interactive elements into a compact Accessibility Object Model (AOM), reducing token cost by ~95%.",
            func=lambda session_id="default": self.pool.get_or_create(session_id).extract_accessibility_tree(),
            properties={
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=[]
        )

        # 4. click_element
        self._register_tool(
            name="click_element",
            description="Click interactive element with resilient selector resolution and durable receipt logging.",
            func=self.click_with_receipt,
            properties={
                "selector": {"type": "string", "description": "CSS selector, text, or @node ID."},
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=["selector"]
        )

        # 5. fill_form_field
        self._register_tool(
            name="fill_form_field",
            description="Enter value into form input with durable receipt logging.",
            func=self.fill_with_receipt,
            properties={
                "selector": {"type": "string", "description": "CSS selector or field name."},
                "value": {"type": "string", "description": "Value to input."},
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=["selector", "value"]
        )

        # 6. get_page_status
        self._register_tool(
            name="get_page_status",
            description="Get page title, URL, HTTP status code, and current DOM hash.",
            func=lambda session_id="default": self.pool.get_or_create(session_id).get_status(),
            properties={
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=[]
        )

        # 7. get_action_receipt
        self._register_tool(
            name="get_action_receipt",
            description="Inspect cryptographic action receipt details by receipt_id.",
            func=self.receipts.get_receipt,
            properties={
                "receipt_id": {"type": "string", "description": "Receipt identifier."}
            },
            required=["receipt_id"]
        )

        # 8. verify_action_trail
        self._register_tool(
            name="verify_action_trail",
            description="Verify cryptographic continuity of actions taken across a session.",
            func=self.receipts.verify_action_trail,
            properties={
                "session_id": {"type": "string", "description": "Session context ID (default: 'default')."}
            },
            required=[]
        )

        # 9. get_pool_status
        self._register_tool(
            name="get_pool_status",
            description="Inspect active session count and memory pool metrics.",
            func=self.pool.get_pool_status,
            properties={},
            required=[]
        )

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"]
            }
            for t in self.tools.values()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name not in self.tools:
            raise KeyError(f"Tool not found: '{name}'")
        func = self.tools[name]["func"]
        return func(**arguments)

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if req_id is None:
            if method == "notifications/initialized":
                logger.info("BrowserBridge Pro client initialized.")
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    }
                }
            }
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools_definition()}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result = self.call_tool(tool_name, tool_args)
                formatted_text = result if isinstance(result, str) else json.dumps(result, indent=2, ensure_ascii=False)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": formatted_text}],
                        "isError": False
                    }
                }
            except KeyError as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": str(e)}
                }
            except (ValueError, TypeError) as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": str(e)}
                }
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def run_stdio(self):
        """Standard IO event loop for JSON-RPC messages."""
        logger.info(f"BrowserBridge Pro Server v{self.version} started on stdio.")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                res = self.handle_request(req)
                if res is not None:
                    sys.stdout.write(json.dumps(res) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

# Backward compatibility alias
BrowserBridgeServer = BrowserBridgeProServer
