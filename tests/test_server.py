import pytest
import tempfile
import os
import json
from browserbridge.server import BrowserBridgeServer

@pytest.fixture
def temp_server():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    server = BrowserBridgeServer(db_path=path, idle_ttl_seconds=60)
    yield server
    if os.path.exists(path):
        os.remove(path)

def test_server_initialization(temp_server):
    assert temp_server.name == "browserbridge-mcp"
    assert len(temp_server.tools) == 9

def test_jsonrpc_initialize(temp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    resp = temp_server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "browserbridge-mcp"
    assert resp["result"]["protocolVersion"] == "2024-11-05"

def test_jsonrpc_tools_list(temp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = temp_server.handle_request(req)
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "navigate_page" in tool_names
    assert "click_element" in tool_names
    assert "fill_form_field" in tool_names
    assert "extract_clean_text" in tool_names
    assert "extract_accessibility_tree" in tool_names
    assert "get_page_status" in tool_names
    assert "get_action_receipt" in tool_names
    assert "verify_action_trail" in tool_names
    assert "get_pool_status" in tool_names

def test_jsonrpc_navigate_and_receipt(temp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "navigate_page",
            "arguments": {
                "url": "https://httpbin.org/status/200",
                "session_id": "test_call_sess"
            }
        }
    }
    resp = temp_server.handle_request(req)
    assert resp["id"] == 3
    assert not resp["result"]["isError"]
    content = json.loads(resp["result"]["content"][0]["text"])
    assert "action_receipt" in content
    assert content["action_receipt"]["action_type"] == "navigate"

def test_jsonrpc_click_and_fill(temp_server):
    # Setup session with simulated DOM
    sess = temp_server.pool.get_or_create("form_sess")
    sess.html = "<html><body><form><input name='query' /><button id='sub'>Go</button></form></body></html>"

    # Fill
    fill_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "fill_form_field",
            "arguments": {
                "selector": "input[name='query']",
                "value": "MCP automation",
                "session_id": "form_sess"
            }
        }
    }
    fill_resp = temp_server.handle_request(fill_req)
    assert not fill_resp["result"]["isError"]
    fill_data = json.loads(fill_resp["result"]["content"][0]["text"])
    assert fill_data["status"] == "filled"
    assert "action_receipt" in fill_data

    # Click
    click_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "click_element",
            "arguments": {
                "selector": "#sub",
                "session_id": "form_sess"
            }
        }
    }
    click_resp = temp_server.handle_request(click_req)
    assert not click_resp["result"]["isError"]

    # Verify action trail
    verify_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "verify_action_trail",
            "arguments": {
                "session_id": "form_sess"
            }
        }
    }
    verify_resp = temp_server.handle_request(verify_req)
    verify_data = json.loads(verify_resp["result"]["content"][0]["text"])
    assert verify_data["valid"] is True
    assert verify_data["total_actions"] == 2

def test_jsonrpc_invalid_tool(temp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 99,
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool",
            "arguments": {}
        }
    }
    resp = temp_server.handle_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601
