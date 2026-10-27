import pytest
from browserbridge.core.selector_resolver import SelectorResolver

def test_explicit_css_resolution():
    res = SelectorResolver.resolve_selector("#submit-btn", "<html></html>")
    assert res["resolved_selector"] == "#submit-btn"
    assert res["strategy"] == "explicit_css"
    assert res["confidence"] == 1.0

def test_aom_node_resolution():
    res = SelectorResolver.resolve_selector("@node-42", "<html></html>")
    assert res["resolved_selector"] == "[data-aom-id='@node-42']"
    assert res["strategy"] == "aom_node"
    assert res["aom_id"] == "@node-42"

def test_data_testid_resolution():
    html = '<button data-testid="login-submit-button">Log In</button>'
    res = SelectorResolver.resolve_selector("login-submit-button", html)
    assert res["resolved_selector"] == "[data-testid='login-submit-button']"
    assert res["strategy"] == "data_testid"

def test_aria_label_resolution():
    html = '<a aria-label="Close modal dialog">X</a>'
    res = SelectorResolver.resolve_selector("Close modal", html)
    assert res["strategy"] == "aria_label"
    assert "Close modal dialog" in res["resolved_selector"]

def test_button_text_resolution():
    html = '<div><button class="primary">Pay Now $14.99</button></div>'
    res = SelectorResolver.resolve_selector("Pay Now", html)
    assert res["strategy"] == "button_text"
    assert res["resolved_selector"] == "button:has-text('Pay Now')"

def test_text_fallback_resolution():
    html = '<div><span>Some random label</span></div>'
    res = SelectorResolver.resolve_selector("random label", html)
    assert res["strategy"] == "text_fallback"
    assert ":has-text('random label')" in res["resolved_selector"]
