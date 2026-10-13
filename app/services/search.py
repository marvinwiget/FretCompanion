from app.integrations.listenbrainz import get_latest_songs, get_top_songs
from app.integrations.song_analysis import analyze_songs
from app.schemas.song import Song
from app.schemas.profile import GuitarProfile
from app.match_evaluation import evaluate_match
from app.database import tracks as db


def search_songs(username: str, count: int, result_type: str,
                 time_range: str, user_profile: GuitarProfile) -> list[Song]:
    """Fetch, analyze, cache and score songs without reading HTTP or session data."""
    all_tracks = []
    all_tracks_dict = []

    if result_type == "last_listened_songs":
        all_tracks_dict = get_latest_songs(username, count=count)

        for track_dict in all_tracks_dict:
            metadata = track_dict["track_metadata"]

            all_tracks.append(Song(
                rec_mbid=(metadata.get("mbid_mapping") or {}).get("recording_mbid"),
                artist_name=metadata["artist_name"],
                song_name=metadata["track_name"]
                )
            )

    else:
        all_tracks_dict = get_top_songs(username, count=count, time_range=time_range)

        for track_dict in all_tracks_dict:
            all_tracks.append(Song(
                rec_mbid=track_dict["recording_mbid"] if "recording_mbid" in track_dict.keys() else None,
                artist_name=track_dict["artist_name"],
                song_name=track_dict["track_name"]
                )
            )


    needs_analysis = [s for s in all_tracks if db.load_track(s) is None]
    unique_needs_analysis = []
    for s in needs_analysis:
        if s in unique_needs_analysis: continue
        unique_needs_analysis.append(s)

    needs_analysis = unique_needs_analysis

    if needs_analysis:
        analyze_songs(needs_analysis)
        db.save_tracks(needs_analysis)

    songs = db.load_tracks([s for s in all_tracks])

    evaluate_match(songs=songs, user=user_profile)

    return songs
