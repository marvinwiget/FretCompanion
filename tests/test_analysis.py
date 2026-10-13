import pytest
from pydantic import ValidationError

from app.schemas.song import Song, SongAnalysis


@pytest.mark.parametrize("field, value", [
    ("tuning", "Standard E"),
    ("overall_difficulty", "Expert"),
    ("playing_style", "Indifferent"),
    ("main_techniques", ["Flying fingers"]),
    ("rhythm_difficulty", 0),
    ("lead_difficulty", 11),
    ("confidence", -0.1),
    ("confidence", 1.1),
])
def test_invalid_analysis_values_are_rejected(analysis, field, value):
    data = analysis.model_dump(mode="json")
    data[field] = value
    with pytest.raises(ValidationError) as error:
        SongAnalysis.model_validate(data)
    assert any(item["loc"][0] == field for item in error.value.errors())


def test_required_analysis_field_cannot_be_missing(analysis):
    data = analysis.model_dump(mode="json")
    del data["playing_style"]
    with pytest.raises(ValidationError):
        SongAnalysis.model_validate(data)


def test_analysis_dictionary_round_trip(analysis):
    restored = SongAnalysis.model_validate(analysis.model_dump(mode="json"))
    assert restored == analysis


def test_analysis_json_text_round_trip(analysis):
    restored = SongAnalysis.model_validate_json(analysis.model_dump_json())
    assert restored == analysis


@pytest.mark.parametrize("score", [-1, 101])
def test_invalid_match_is_rejected(score):
    with pytest.raises(ValidationError):
        Song(song_name="Example", artist_name="Artist", match=score)


def test_song_match_defaults_to_none():
    assert Song(song_name="Example", artist_name="Artist").match is None
