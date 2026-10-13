from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.model import Track
from app.schemas.song import Song


def test_analysis_round_trip_and_personal_match_not_persisted(database, analysis):
    song = Song(song_name="Example", artist_name="Artist", analysis=analysis, match=42)
    database.save_tracks([song])
    restored = database.load_track(song)
    assert restored.id is not None
    assert restored.analysis == analysis
    assert restored.match is None
    with Session(database.get_engine()) as session:
        assert isinstance(session.get(Track, restored.id).analysis, dict)


def test_existing_track_does_not_stop_rest_of_batch(database, analysis):
    first = Song(song_name="First", artist_name="Artist", analysis=analysis)
    second = Song(song_name="Second", artist_name="Artist", analysis=analysis)
    database.save_tracks([first])
    database.save_tracks([first, second])
    assert database.load_track(second) is not None
    with Session(database.get_engine()) as session:
        assert session.scalar(select(func.count()).select_from(Track)) == 2


def test_duplicate_batch_only_inserts_once(database, analysis):
    song = Song(song_name="Example", artist_name="Artist", analysis=analysis)
    database.save_tracks([song, song])
    with Session(database.get_engine()) as session:
        assert session.scalar(select(func.count()).select_from(Track)) == 1


def test_metadata_lookup_ignores_case_and_outer_spaces(database, analysis):
    database.save_tracks([Song(song_name="Example", artist_name="Artist", analysis=analysis)])
    assert database.load_track(Song(song_name=" EXAMPLE ", artist_name=" artist ")) is not None


def test_load_ids_preserves_order(database, analysis):
    songs = [Song(song_name=name, artist_name="Artist", analysis=analysis) for name in ["First", "Second"]]
    database.save_tracks(songs)
    ids = [database.load_track(song).id for song in songs]
    assert [song.song_name for song in database.load_tracks_with_id(ids[::-1])] == ["Second", "First"]


def test_empty_batch(database):
    database.save_tracks([])
    assert database.load_tracks([]) == []
    assert database.load_tracks_with_id([]) == []


def test_cache_miss(database):
    song = Song(song_name="Missing", artist_name="Artist")
    assert database.load_track(song) is None
    assert database.load_tracks([song]) is None
