import pytest
from browserbridge.engine import BrowserSession

def test_session_initialization():
    session = BrowserSession(session_id="test_sess_1")
    assert session.session_id == "test_sess_1"
    assert session.current_url == "about:blank"
    assert session.title == "Blank Page"
    assert session.status_code == 200
    assert len(session.get_dom_hash()) == 64

def test_dom_hash_mutation():
    session = BrowserSession(session_id="test_sess_2")
    hash1 = session.get_dom_hash()
    session.click("button#submit")
    hash2 = session.get_dom_hash()
    assert hash1 != hash2
    assert "Clicked button#submit" in session.html

def test_extract_clean_text():
    session = BrowserSession()
    session.html = """
    <html>
        <head><title>Test Page</title><style>body { color: red; }</style></head>
        <body>
            <script>console.log("ignore me");</script>
            <h1>Welcome to BrowserBridge</h1>
            <p>This is a <b>clean</b> paragraph.</p>
        </body>
    </html>
    """
    text = session.extract_clean_text()
    assert "Welcome to BrowserBridge" in text
    assert "This is a clean paragraph." in text
    assert "console.log" not in text
    assert "color: red" not in text

def test_extract_accessibility_tree():
    session = BrowserSession()
    session.html = """
    <html>
        <body>
            <button id="btn1">Sign Up Now</button>
            <a href="https://example.com/login">Login Here</a>
            <input type="text" name="username" />
            <input type="password" name="password" />
        </body>
    </html>
    """
    aom = session.extract_accessibility_tree()
    assert len(aom) == 4
    roles = [node["role"] for node in aom]
    assert "button" in roles
    assert "link" in roles
    assert roles.count("textbox") == 2
    assert aom[0]["id"] == "@node-1"
    assert "Sign Up Now" in aom[0]["name"]

def test_click_and_fill():
    session = BrowserSession()
    session.html = "<html><body><form><input name='email'></form></body></html>"
    
    fill_res = session.fill("input[name='email']", "agent@test.com")
    assert fill_res["status"] == "filled"
    assert session.form_state["email"] == "agent@test.com"

    click_res = session.click("#submit-btn")
    assert click_res["status"] == "clicked"

def test_get_status():
    session = BrowserSession(session_id="status_sess")
    status = session.get_status()
    assert status["session_id"] == "status_sess"
    assert status["url"] == "about:blank"
    assert "dom_hash" in status
    assert status["form_fields_filled"] == 0
