"""
BrowserBridge Session Pool Manager (Anti-Zombie Reaper)
Guarantees memory isolation and automatically cleans up expired headless sessions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from ..engine import BrowserSession

class SessionPoolManager:
    def __init__(self, idle_ttl_seconds: int = 180):
        self.idle_ttl_seconds = idle_ttl_seconds
        self.sessions: Dict[str, BrowserSession] = {}

    def get_or_create(self, session_id: str = "default") -> BrowserSession:
        """Retrieves or spins up a new isolated browser context."""
        # Auto-reap on access
        self.reap_zombies()
        if session_id not in self.sessions:
            self.sessions[session_id] = BrowserSession(session_id=session_id)
        return self.sessions[session_id]

    def reap_zombies(self) -> List[str]:
        """Scans and terminates sessions that have exceeded idle TTL."""
        now = datetime.now(timezone.utc)
        reaped: List[str] = []

        for sid, sess in list(self.sessions.items()):
            last_active = datetime.fromisoformat(sess.last_active)
            if now - last_active > timedelta(seconds=self.idle_ttl_seconds):
                del self.sessions[sid]
                reaped.append(sid)

        return reaped

    def close_session(self, session_id: str) -> bool:
        """Explicitly closes a browser session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_pool_status(self) -> Dict[str, Any]:
        """Returns statistics on active browser sessions."""
        return {
            "active_sessions_count": len(self.sessions),
            "idle_ttl_seconds": self.idle_ttl_seconds,
            "session_ids": list(self.sessions.keys())
        }
