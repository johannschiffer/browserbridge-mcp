"""
BrowserBridge MCP Server (Lite Edition)
Model Context Protocol stdio interface for headless browser automation and AOM inspection.
"""

import sys
import json
import logging
from typing import Callable, Dict, Any, List, Optional
from .engine import BrowserEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BrowserBridge] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("BrowserBridgeServer")

class BrowserBridgeServer:
    def __init__(self):
        self.name = "browserbridge-mcp"
        self.version = "1.0.1"
        self.engine = BrowserEngine()
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

    def _register_tools(self):
        # 1. navigate_page
        self._register_tool(
            name="navigate_page",
            description="Navigate headless browser session to target URL.",
            func=self.engine.navigate,
            properties={
                "url": {"type": "string", "description": "Destination web address (e.g., 'https://example.com')."},
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
            required=["url"]
        )

        # 2. extract_clean_text
        self._register_tool(
            name="extract_clean_text",
            description="Extract cleaned, semantic markdown text from current page, stripping scripts and clutter.",
            func=self.engine.extract_clean_text,
            properties={
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
            required=[]
        )

        # 3. extract_accessibility_tree
        self._register_tool(
            name="extract_accessibility_tree",
            description="Extract interactive elements (buttons, links, inputs) as an Accessibility Object Model (AOM), reducing token cost by ~95%.",
            func=self.engine.extract_accessibility_tree,
            properties={
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
            required=[]
        )

        # 4. click_element
        self._register_tool(
            name="click_element",
            description="Click an interactive element by CSS selector or target ID.",
            func=self.engine.click_element,
            properties={
                "selector": {"type": "string", "description": "CSS selector or element name to click."},
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
            required=["selector"]
        )

        # 5. fill_form_field
        self._register_tool(
            name="fill_form_field",
            description="Enter text or value into a form input or textarea.",
            func=self.engine.fill_form_field,
            properties={
                "selector": {"type": "string", "description": "CSS selector or input name."},
                "value": {"type": "string", "description": "Text value to insert."},
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
            required=["selector", "value"]
        )

        # 6. get_page_status
        self._register_tool(
            name="get_page_status",
            description="Inspect active session state, current URL, page title, and HTTP response code.",
            func=self.engine.get_page_status,
            properties={
                "session_id": {"type": "string", "description": "Session identifier (default: 'default')."}
            },
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
                logger.info("BrowserBridge client initialized.")
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
        """Runs JSON-RPC event loop over stdio."""
        from ._genesis import print_upgrade_notice
        print_upgrade_notice()
        logger.info(f"BrowserBridge Server v{self.version} running on stdio.")
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
