from app.schemas.song import Song


MBID_A = "95bf6a56-a5d8-4206-b624-522797976446"
MBID_B = "00000000-0000-4000-8000-000000000001"


def test_same_mbid_matches_despite_different_metadata():
    first = Song(rec_mbid=MBID_A, song_name="Example", artist_name="Artist")
    second = Song(rec_mbid=MBID_A, song_name="Example (remastered)", artist_name="ARTIST")
    assert first == second


def test_different_known_mbids_do_not_match():
    first = Song(rec_mbid=MBID_A, song_name="Example", artist_name="Artist")
    second = Song(rec_mbid=MBID_B, song_name="Example", artist_name="Artist")
    assert first != second


def test_metadata_matching_ignores_case_and_outer_whitespace():
    first = Song(song_name=" Example ", artist_name=" ARTIST ")
    second = Song(song_name="example", artist_name="artist")
    assert first == second


def test_same_title_by_different_artists_does_not_match():
    first = Song(song_name="Example", artist_name="Artist A")
    second = Song(song_name="Example", artist_name="Artist B")
    assert first != second


def test_comparison_with_another_type_is_false():
    song = Song(song_name="Example", artist_name="Artist")
    assert song != "Example"
