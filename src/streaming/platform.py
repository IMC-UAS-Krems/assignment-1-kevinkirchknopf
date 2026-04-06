"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import Track, Song
from streaming.users import User, PremiumUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


class StreamingPlatform:
    """Central class orchestrating all domain entities and analytics."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._catalogue: dict[str, Track] = {}
        self._users: dict[str, User] = {}
        self._artists: dict[str, Artist] = {}
        self._albums: dict[str, Album] = {}
        self._playlists: dict[str, Playlist] = {}
        self._sessions: list[ListeningSession] = []

    # ------------------------------------------------------------------
    # Registration methods
    # ------------------------------------------------------------------

    def add_track(self, track: Track) -> None:
        self._catalogue[track.track_id] = track

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def add_artist(self, artist: Artist) -> None:
        self._artists[artist.artist_id] = artist

    def add_album(self, album: Album) -> None:
        self._albums[album.album_id] = album

    def add_playlist(self, playlist: Playlist) -> None:
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session: ListeningSession) -> None:
        self._sessions.append(session)
        session.user.add_session(session)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_track(self, track_id: str) -> Track | None:
        return self._catalogue.get(track_id)

    def get_user(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_artist(self, artist_id: str) -> Artist | None:
        return self._artists.get(artist_id)

    def get_album(self, album_id: str) -> Album | None:
        return self._albums.get(album_id)

    def all_users(self) -> list[User]:
        return list(self._users.values())

    def all_tracks(self) -> list[Track]:
        return list(self._catalogue.values())

    # ------------------------------------------------------------------
    # Q1: Total Cumulative Listening Time
    # ------------------------------------------------------------------

    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        """Return total listening time (minutes) for sessions within [start, end]."""
        total_seconds = sum(
            s.duration_listened_seconds
            for s in self._sessions
            if start <= s.timestamp <= end
        )
        return total_seconds / 60

    # ------------------------------------------------------------------
    # Q2: Average Unique Tracks per Premium User
    # ------------------------------------------------------------------

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        """Compute average unique tracks per PremiumUser in the last `days` days."""
        cutoff = datetime.now() - timedelta(days=days)
        premium_users = [u for u in self._users.values() if type(u) is PremiumUser]
        if not premium_users:
            return 0.0
        total_unique = sum(
            len({s.track.track_id for s in u.sessions if s.timestamp >= cutoff})
            for u in premium_users
        )
        return total_unique / len(premium_users)

    # ------------------------------------------------------------------
    # Q3: Track with Most Distinct Listeners
    # ------------------------------------------------------------------

    def track_with_most_distinct_listeners(self) -> Track | None:
        """Return the track listened to by the most distinct users."""
        if not self._sessions:
            return None
        listeners: dict[str, set[str]] = defaultdict(set)
        for s in self._sessions:
            listeners[s.track.track_id].add(s.user.user_id)
        best_id = max(listeners, key=lambda tid: len(listeners[tid]))
        return self._catalogue.get(best_id)

    # ------------------------------------------------------------------
    # Q4: Average Session Duration by User Type
    # ------------------------------------------------------------------

    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        """Return average session duration (seconds) per user subtype, sorted longest first."""
        buckets: dict[str, list[int]] = defaultdict(list)
        for s in self._sessions:
            type_name = type(s.user).__name__
            buckets[type_name].append(s.duration_listened_seconds)
        result = [
            (t, sum(durations) / len(durations))
            for t, durations in buckets.items()
        ]
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    # ------------------------------------------------------------------
    # Q5: Total Listening Time for Underage Sub-Users
    # ------------------------------------------------------------------

    def total_listening_time_underage_sub_users_minutes(
        self, age_threshold: int = 18
    ) -> float:
        """Return total listening time (minutes) for FamilyMember users under `age_threshold`."""
        total_seconds = sum(
            s.duration_listened_seconds
            for s in self._sessions
            if isinstance(s.user, FamilyMember) and s.user.age < age_threshold
        )
        return total_seconds / 60

    # ------------------------------------------------------------------
    # Q6: Top Artists by Listening Time
    # ------------------------------------------------------------------

    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        """Return the top `n` artists ranked by total listening time (minutes) for Song tracks."""
        artist_seconds: dict[str, float] = defaultdict(float)
        for s in self._sessions:
            if isinstance(s.track, Song):
                artist_seconds[s.track.artist.artist_id] += s.duration_listened_seconds
        result = [
            (self._artists[aid], secs / 60)
            for aid, secs in artist_seconds.items()
            if aid in self._artists
        ]
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    # ------------------------------------------------------------------
    # Q7: User's Top Genre
    # ------------------------------------------------------------------

    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        """Return (genre, percentage) for the user's most-listened genre, or None."""
        user = self._users.get(user_id)
        if user is None or not user.sessions:
            return None
        genre_seconds: dict[str, float] = defaultdict(float)
        for s in user.sessions:
            genre_seconds[s.track.genre] += s.duration_listened_seconds
        top_genre = max(genre_seconds, key=lambda g: genre_seconds[g])
        total = sum(genre_seconds.values())
        percentage = (genre_seconds[top_genre] / total) * 100
        return (top_genre, percentage)

    # ------------------------------------------------------------------
    # Q8: Collaborative Playlists with Many Artists
    # ------------------------------------------------------------------

    def collaborative_playlists_with_many_artists(
        self, threshold: int = 3
    ) -> list[CollaborativePlaylist]:
        """Return CollaborativePlaylists with more than `threshold` distinct Song artists."""
        result = []
        for pl in self._playlists.values():
            if not isinstance(pl, CollaborativePlaylist):
                continue
            distinct_artists = {
                t.artist.artist_id
                for t in pl.tracks
                if isinstance(t, Song)
            }
            if len(distinct_artists) > threshold:
                result.append(pl)
        return result

    # ------------------------------------------------------------------
    # Q9: Average Tracks per Playlist Type
    # ------------------------------------------------------------------

    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        """Return dict mapping 'Playlist' and 'CollaborativePlaylist' to average track count."""
        collab = [
            pl for pl in self._playlists.values() if type(pl) is CollaborativePlaylist
        ]
        standard = [
            pl for pl in self._playlists.values() if type(pl) is Playlist
        ]
        avg_standard = (
            sum(len(pl.tracks) for pl in standard) / len(standard) if standard else 0.0
        )
        avg_collab = (
            sum(len(pl.tracks) for pl in collab) / len(collab) if collab else 0.0
        )
        return {
            "Playlist": avg_standard,
            "CollaborativePlaylist": avg_collab,
        }

    # ------------------------------------------------------------------
    # Q10: Users Who Completed Albums
    # ------------------------------------------------------------------

    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        """Return (User, [album_titles]) for users who listened to every track on ≥1 album."""
        # Only consider albums with at least one track
        albums_with_tracks = [
            alb for alb in self._albums.values() if alb.tracks
        ]
        result = []
        for user in self._users.values():
            listened = user.unique_tracks_listened()
            completed_titles = [
                alb.title
                for alb in albums_with_tracks
                if alb.track_ids().issubset(listened)
            ]
            if completed_titles:
                result.append((user, completed_titles))
        return result
