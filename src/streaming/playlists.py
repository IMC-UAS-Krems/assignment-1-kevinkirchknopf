"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.tracks import Track
    from streaming.users import User


class Playlist:
    """A user-curated ordered collection of tracks."""

    def __init__(self, playlist_id: str, name: str, *, owner: User) -> None:
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks: list[Track] = []

    def add_track(self, track: Track) -> None:
        """Add a track if not already present (no duplicates)."""
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        """Remove a track by ID; silently ignore if not found."""
        self.tracks = [t for t in self.tracks if t.track_id != track_id]

    def total_duration_seconds(self) -> int:
        return sum(t.duration_seconds for t in self.tracks)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.playlist_id!r}, name={self.name!r})"


class CollaborativePlaylist(Playlist):
    """A playlist with multiple contributors."""

    def __init__(self, playlist_id: str, name: str, *, owner: User) -> None:
        super().__init__(playlist_id, name, owner=owner)
        self.contributors: list[User] = [owner]

    def add_contributor(self, user: User) -> None:
        """Add a contributor if not already present."""
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user: User) -> None:
        """Remove a contributor, but never remove the owner."""
        if user is not self.owner:
            self.contributors = [c for c in self.contributors if c is not user]
