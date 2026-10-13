from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .model import Track
from .session import get_engine
from app.schemas.song import Song

# Cached tracks exclude the user's personal match calculation.

def get_track(session: Session, song: Song):
    existing_track = None
    # check if mbid exists
    if song.rec_mbid is not None:
        existing_track = session.scalar(
            select(Track).where(
                Track.rec_mbid == song.rec_mbid
            )
        )
    if existing_track is not None: return existing_track

    # check if track and artist name in db
    existing_track = session.scalar(
        select(Track).where(
            func.lower(func.trim(Track.track_name)) == song.song_name.strip().lower(),
            func.lower(func.trim(Track.artist_name)) == song.artist_name.strip().lower()
        )
    )
    return existing_track

def save_tracks(songs: list[Song]):

    with Session(get_engine()) as session:
        for song in songs:
            if get_track(session=session, song=song): continue # already exists in db

            analysis_data = (
                    song.analysis.model_dump(mode="json")
                    if song.analysis is not None
                    else None
                )

            track = Track(rec_mbid=song.rec_mbid, 
                        artist_name=song.artist_name,
                        track_name=song.song_name,
                        analysis=analysis_data
                        )
            session.add(track)
        session.commit()

def load_track(song: Song) -> Song | None:
    with Session(get_engine()) as session:
        track = get_track(session, song)

        if not track: return None # track not in db

        return Song.model_validate({
            "id": track.id,
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        })

def load_tracks(songs: list[Song]) -> list[Song] | None:
    with Session(get_engine()) as session:

        tracks = [get_track(session=session, song=song) for song in songs]
        
        if None in tracks: return None # at least 1 song not in db

        return [Song.model_validate({
            "id": track.id,
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        }) for track in tracks]

def load_tracks_with_id(track_ids: list[int]) -> list[Song]:
    with Session(get_engine()) as session:

        tracks = [session.get(Track, id) for id in track_ids]

        return [Song.model_validate({
            "id": track.id,
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        }) for track in tracks]
