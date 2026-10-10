from sqlalchemy import String, create_engine, select, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.schemas.song import Song

### tracks saved in db should only store info about the song, exclduding personal match calculation

memory_engine_url = "sqlite+pysqlite:///:memory:"
local_engine_url = "sqlite+pysqlite:///fret_companion.db"

engine = create_engine(local_engine_url, echo=False)

class Base(DeclarativeBase):
    pass

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    rec_mbid: Mapped[str | None] = mapped_column(String(36), unique=True)
    track_name: Mapped[str] = mapped_column(String(255))
    artist_name: Mapped[str] = mapped_column(String(255))
    analysis: Mapped[dict] = mapped_column(JSON)

Base.metadata.create_all(engine)

def get_track(session: Session, song: Song):
    # check if mbid exists
    if song.rec_mbid is not None:
        existing_track = session.scalar(
            select(Track).where(
                Track.rec_mbid == song.rec_mbid
            )
        )
        return existing_track

    # check if track and artist name in db
    else: 
        existing_track = session.scalar(
            select(Track).where(
                Track.track_name == song.song_name,
                Track.artist_name == song.artist_name
            )
        )
        return existing_track

def save_track(song: Song):
    analysis_data = (
        song.analysis.model_dump(mode="json")
        if song.analysis is not None
        else None
    )

    with Session(engine) as session:
        if get_track(session=session, song=song): return

        track = Track(rec_mbid=song.rec_mbid, 
                      artist_name=song.artist_name,
                      track_name=song.song_name,
                      analysis=analysis_data
                      )
        session.add(track)
        session.commit()

def load_track(song: Song) -> Song | None:
    with Session(engine) as session:
        track = get_track(session, song)

        if not track: return None # track not in db

        return Song.model_validate({
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        })

def load_tracks(songs: list[Song]) -> list[Song] | None:
    with Session(engine) as session:

        tracks = [get_track(session=session, song=song) for song in songs]
        
        if None in tracks: return None # at least 1 song not in db

        return [Song.model_validate({
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        }) for track in tracks]