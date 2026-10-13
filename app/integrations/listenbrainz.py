from urllib.parse import quote

import requests

from app.exceptions import LBUserNotFound, LBUnavailable, NoUserActivity

ROOT = "https://api.listenbrainz.org"


def _fetch_tracks(path: str, params: dict, key: str) -> list[dict]:
    try:
        response = requests.get(url=f"{ROOT}{path}", params=params, timeout=20)
    except requests.Timeout as exc:
        raise LBUnavailable("ListenBrainz took too long to respond. Please try again.") from exc
    except requests.RequestException as exc:
        raise LBUnavailable("Couldn’t connect to ListenBrainz. Please try again later.") from exc

    if response.status_code == 204:
        raise NoUserActivity("No listening data is available for this selection.")
    if response.status_code == 429:
        raise LBUnavailable("ListenBrainz is receiving too many requests. Please try again later.")
    if response.status_code == 404:
        # A missing API route can also return 404; only identify an explicit user error.
        try:
            message = response.json().get("error", "")
        except (ValueError, AttributeError):
            message = ""
        if isinstance(message, str) and "user" in message.lower() and any(
            phrase in message.lower() for phrase in ("not found", "does not exist", "doesn't exist")
        ):
            raise LBUserNotFound("We couldn’t find that ListenBrainz user. Check the username and try again.")
        raise LBUnavailable("ListenBrainz couldn’t find the requested API endpoint. Please try again later.")
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise LBUnavailable("ListenBrainz couldn’t complete the request. Please try again later.") from exc

    try:
        tracks = response.json()["payload"][key]
        if not isinstance(tracks, list):
            raise TypeError("Expected a track list")
        for track in tracks:
            metadata = track["track_metadata"] if key == "listens" else track
            if not isinstance(metadata, dict):
                raise TypeError("Expected track metadata")
            for field in ("artist_name", "track_name"):
                if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                    raise ValueError("Missing track identity")
            mapping = metadata.get("mbid_mapping")
            if mapping is not None and not isinstance(mapping, dict):
                raise TypeError("Invalid recording mapping")
            mbid = (mapping or {}).get("recording_mbid") if key == "listens" else metadata.get("recording_mbid")
            if mbid is not None and not isinstance(mbid, str):
                raise TypeError("Invalid recording ID")
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise LBUnavailable("ListenBrainz returned an unexpected response. Please try again later.") from exc
    return tracks


def get_latest_songs(username: str, min_ts=None, max_ts=None, count: int = 20):
    return _fetch_tracks(
        f"/1/user/{quote(username, safe='')}/listens",
        {"min_ts": min_ts, "max_ts": max_ts, "count": count},
        "listens",
    )


def get_top_songs(username: str, count: int = 20, time_range: str = "month"):
    return _fetch_tracks(
        f"/1/stats/user/{quote(username, safe='')}/recordings",
        {"count": count, "range": time_range},
        "recordings",
    )
