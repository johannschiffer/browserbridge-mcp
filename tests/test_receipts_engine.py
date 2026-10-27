import pytest
import tempfile
import os
from browserbridge.core.receipts_engine import DurableReceiptsEngine

@pytest.fixture
def temp_receipts_engine():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = DurableReceiptsEngine(db_path=path)
    yield engine
    if os.path.exists(path):
        os.remove(path)

def test_issue_and_get_receipt(temp_receipts_engine):
    receipt = temp_receipts_engine.issue_receipt(
        session_id="sess_123",
        action_type="click",
        target="button#checkout",
        pre_state_hash="a" * 64,
        post_state_hash="b" * 64,
        payload="click-payload"
    )

    assert receipt["receipt_id"].startswith("rcpt_")
    assert receipt["session_id"] == "sess_123"
    assert receipt["action_type"] == "click"

    fetched = temp_receipts_engine.get_receipt(receipt["receipt_id"])
    assert fetched is not None
    assert fetched["receipt_id"] == receipt["receipt_id"]
    assert fetched["target"] == "button#checkout"
    assert fetched["payload"] == "click-payload"

def test_list_receipts(temp_receipts_engine):
    temp_receipts_engine.issue_receipt("sess_abc", "navigate", "https://site.com", "h1", "h2")
    temp_receipts_engine.issue_receipt("sess_abc", "click", "#btn", "h2", "h3")
    temp_receipts_engine.issue_receipt("sess_other", "click", "#btn2", "h3", "h4")

    receipts = temp_receipts_engine.list_receipts("sess_abc")
    assert len(receipts) == 2
    assert receipts[0]["action_type"] == "navigate"
    assert receipts[1]["action_type"] == "click"

def test_verify_action_trail_valid(temp_receipts_engine):
    temp_receipts_engine.issue_receipt("sess_trail", "navigate", "https://site.com", "hash_0", "hash_1")
    temp_receipts_engine.issue_receipt("sess_trail", "click", "#first", "hash_1", "hash_2")
    temp_receipts_engine.issue_receipt("sess_trail", "fill", "#input", "hash_2", "hash_3")

    audit = temp_receipts_engine.verify_action_trail("sess_trail")
    assert audit["valid"] is True
    assert audit["broken_transitions"] == 0
    assert audit["status"] == "VERIFIED_AUDITABLE"
    assert audit["total_actions"] == 3

def test_verify_action_trail_broken(temp_receipts_engine):
    temp_receipts_engine.issue_receipt("sess_bad", "navigate", "https://site.com", "hash_0", "hash_1")
    # Discontinuous pre_state_hash
    temp_receipts_engine.issue_receipt("sess_bad", "click", "#first", "hash_tampered", "hash_3")

    audit = temp_receipts_engine.verify_action_trail("sess_bad")
    assert audit["valid"] is False
    assert audit["broken_transitions"] == 1
    assert audit["status"] == "COMPROMISED_CHAIN"
