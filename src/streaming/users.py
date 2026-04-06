"""
users.py
--------
Implement the class hierarchy for platform users.

Classes to implement:
  - User (base class)
    - FreeUser
    - PremiumUser
    - FamilyAccountUser
    - FamilyMember
"""

from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.sessions import ListeningSession


class User:
    """Base class for all platform users."""

    def __init__(self, user_id: str, name: str, *, age: int) -> None:
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions: list[ListeningSession] = []

    def add_session(self, session: ListeningSession) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(s.duration_listened_seconds for s in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self) -> set[str]:
        return {s.track.track_id for s in self.sessions}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.user_id!r}, name={self.name!r})"


class FreeUser(User):
    """Free tier user with limited features."""

    MAX_SKIPS_PER_HOUR: int = 6

    def __init__(self, user_id: str, name: str, *, age: int) -> None:
        super().__init__(user_id, name, age=age)


class PremiumUser(User):
    """Paid subscriber with full access."""

    def __init__(
        self,
        user_id: str,
        name: str,
        *,
        age: int,
        subscription_start: date,
    ) -> None:
        super().__init__(user_id, name, age=age)
        self.subscription_start = subscription_start


class FamilyAccountUser(User):
    """Premium user managing a family account."""

    def __init__(self, user_id: str, name: str, *, age: int) -> None:
        super().__init__(user_id, name, age=age)
        self.sub_users: list[FamilyMember] = []

    def add_sub_user(self, sub_user: FamilyMember) -> None:
        self.sub_users.append(sub_user)

    def all_members(self) -> list[User]:
        """Return the account holder followed by all sub-users."""
        return [self] + list(self.sub_users)


class FamilyMember(User):
    """A user profile belonging to a family account."""

    def __init__(
        self,
        user_id: str,
        name: str,
        *,
        age: int,
        parent: FamilyAccountUser,
    ) -> None:
        super().__init__(user_id, name, age=age)
        self.parent = parent
