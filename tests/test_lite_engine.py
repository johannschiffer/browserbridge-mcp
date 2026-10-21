import pytest
from browserbridge.engine import BrowserSession, BrowserEngine

def test_lite_session():
    session = BrowserSession(session_id="test_lite")
    assert session.session_id == "test_lite"
    assert session.status_code == 200

def test_lite_extract_clean_text():
    session = BrowserSession()
    session.html = "<html><body><h1>Title</h1><p>Paragraph with <b>bold</b> text.</p></body></html>"
    text = session.extract_clean_text()
    assert "Title" in text
    assert "Paragraph with bold text." in text

def test_lite_aom_extraction():
    session = BrowserSession()
    session.html = '<html><body><button>Click Me</button><a href="/docs">Docs</a><input name="user" /></body></html>'
    aom = session.extract_accessibility_tree()
    assert len(aom) == 3
    assert aom[0]["role"] == "button"
    assert aom[1]["role"] == "link"
    assert aom[2]["role"] == "textbox"

def test_lite_engine():
    engine = BrowserEngine()
    sess = engine.get_or_create_session("s1")
    assert sess.session_id == "s1"
    status = engine.get_page_status("s1")
    assert status["session_id"] == "s1"
