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

    rec_mbid: Mapped[str] = mapped_column(String(36),
                                    primary_key=True)
    artist_name: Mapped[str] = mapped_column(String(255))
    track_name: Mapped[str] = mapped_column(String(255))
    analysis: Mapped[dict] = mapped_column(JSON)

Base.metadata.create_all(engine)

def save_track(song: Song):
    analysis_data = (
        song.analysis.model_dump(mode="json")
        if song.analysis is not None
        else None
    )

    with Session(engine) as session:
        existing_track = session.get(Track, song.rec_mbid)
        if existing_track is not None:
            print(f"Track {song.song_name} already saved in DB")
            return

        track = Track(rec_mbid=song.rec_mbid, 
                      artist_name=song.artist_name,
                      track_name=song.song_name,
                      analysis=analysis_data
                      )
        session.add(track)
        session.commit()

def load_track(recording_mbid: str) -> Song | None:
    with Session(engine) as session:
        track = session.get(Track, recording_mbid)
        if track is None:
            return None

        return Song.model_validate({
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        })

def load_tracks(rec_mbids: list[str]) -> list[Song]:
    with Session(engine) as session:
        tracks = []
        for rec_mbid in rec_mbids:
            tracks.append(session.get(Track, rec_mbid))

        return [Song.model_validate({
            "rec_mbid": track.rec_mbid,
            "artist_name": track.artist_name,
            "song_name": track.track_name,
            "match": None,
            "analysis": track.analysis
        }) for track in tracks]