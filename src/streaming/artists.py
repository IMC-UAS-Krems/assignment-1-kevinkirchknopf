"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.tracks import Track


class Artist:
    """A music artist or content creator."""

    def __init__(self, artist_id: str, name: str, *, genre: str) -> None:
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks: list[Track] = []

    def add_track(self, track: Track) -> None:
        self.tracks.append(track)

    def track_count(self) -> int:
        return len(self.tracks)

    def __repr__(self) -> str:
        return f"Artist(id={self.artist_id!r}, name={self.name!r})"
