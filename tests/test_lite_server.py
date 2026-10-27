import pytest
import json
from browserbridge.server import BrowserBridgeServer

def test_lite_server():
    server = BrowserBridgeServer()
    assert server.name == "browserbridge-mcp"
    assert len(server.tools) >= 6

    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    res = server.handle_request(req)
    assert res["result"]["serverInfo"]["name"] == "browserbridge-mcp"

    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    tools_res = server.handle_request(tools_req)
    assert len(tools_res["result"]["tools"]) >= 6
