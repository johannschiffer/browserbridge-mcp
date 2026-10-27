import pytest
import time
from datetime import datetime, timezone, timedelta
from browserbridge.core.session_pool import SessionPoolManager

def test_get_or_create_session():
    pool = SessionPoolManager(idle_ttl_seconds=60)
    sess1 = pool.get_or_create("user_alpha")
    assert sess1.session_id == "user_alpha"
    assert len(pool.sessions) == 1

    sess1_repeat = pool.get_or_create("user_alpha")
    assert sess1 is sess1_repeat

def test_close_session():
    pool = SessionPoolManager(idle_ttl_seconds=60)
    pool.get_or_create("sess_to_close")
    assert "sess_to_close" in pool.sessions

    closed = pool.close_session("sess_to_close")
    assert closed is True
    assert "sess_to_close" not in pool.sessions

    closed_again = pool.close_session("non_existent")
    assert closed_again is False

def test_reap_zombies():
    pool = SessionPoolManager(idle_ttl_seconds=1)
    s1 = pool.get_or_create("active_session")
    s2 = pool.get_or_create("idle_zombie")

    # Manually backdate s2 last_active by 10 seconds
    past_time = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
    s2.last_active = past_time

    reaped = pool.reap_zombies()
    assert "idle_zombie" in reaped
    assert "active_session" not in reaped
    assert "idle_zombie" not in pool.sessions
    assert "active_session" in pool.sessions

def test_pool_status():
    pool = SessionPoolManager(idle_ttl_seconds=120)
    pool.get_or_create("s1")
    pool.get_or_create("s2")

    status = pool.get_pool_status()
    assert status["active_sessions_count"] == 2
    assert status["idle_ttl_seconds"] == 120
    assert "s1" in status["session_ids"]
    assert "s2" in status["session_ids"]
