"""
sessions.py
-----------
Implement the ListeningSession class for recording listening events.

Classes to implement:
  - ListeningSession
"""

from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.users import User
    from streaming.tracks import Track


class ListeningSession:
    """Records a user listening to a track."""

    def __init__(
        self,
        session_id: str,
        user: User,
        track: Track,
        timestamp: datetime,
        duration_listened_seconds: int,
    ) -> None:
        self.session_id = session_id
        self.user = user
        self.track = track
        self.timestamp = timestamp
        self.duration_listened_seconds = duration_listened_seconds

    def duration_listened_minutes(self) -> float:
        return self.duration_listened_seconds / 60

    def __repr__(self) -> str:
        return (
            f"ListeningSession(id={self.session_id!r}, "
            f"user={self.user.user_id!r}, track={self.track.track_id!r})"
        )
