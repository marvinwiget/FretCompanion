import pytest

from app.match_evaluation import (
    evaluate_match,
    get_chords_weight,
    get_diff_weight,
    get_style_weight,
    get_technique_weight,
    get_tuning_weight,
)
from app.schemas.song import Song


@pytest.mark.parametrize("known, expected", [
    (["C", "G"], 0),
    (["C"], 0.5),
    ([], 1),
    (["Am"], 1),
])
def test_chord_penalty(analysis, profile, known, expected):
    profile.learned_chords = known
    assert get_chords_weight(analysis, profile) == pytest.approx(expected)


def test_no_chords_required_has_no_penalty(analysis, profile):
    analysis.required_chords = []
    assert get_chords_weight(analysis, profile) == 0


def test_duplicate_known_chords_do_not_improve_compatibility(analysis, profile):
    profile.learned_chords = ["C", "C"]
    assert get_chords_weight(analysis, profile) == pytest.approx(0.5)


@pytest.mark.parametrize("known, expected", [(["Strumming"], 0), ([], 1)])
def test_technique_penalty(analysis, profile, known, expected):
    profile.techniques = known
    assert get_technique_weight(analysis, profile) == expected


def test_no_techniques_required_has_no_penalty(analysis, profile):
    analysis.main_techniques = []
    assert get_technique_weight(analysis, profile) == 0


@pytest.mark.parametrize("level, difficulty, expected", [
    ("Beginner", "Beginner", 0),
    ("Beginner", "Intermediate", 0.5),
    ("Beginner", "Advanced", 1),
    ("Intermediate", "Beginner", 0),
    ("Intermediate", "Advanced", 0.5),
    ("Advanced", "Advanced", 0),
])
def test_difficulty_penalty(analysis, profile, level, difficulty, expected):
    profile.experience_level = level
    analysis.overall_difficulty = difficulty
    assert get_diff_weight(analysis, profile) == expected


@pytest.mark.parametrize("preference, style, expected", [
    ("Rhythm", "Rhythm", 0),
    ("Rhythm", "Balanced", 0.5),
    ("Rhythm", "Lead", 1),
    ("Lead", "Rhythm", 1),
    ("Balanced", "Lead", 0.5),
    ("Indifferent", "Lead", 0),
])
def test_playing_style_penalty(analysis, profile, preference, style, expected):
    profile.playing_style_preference = preference
    analysis.playing_style = style
    assert get_style_weight(analysis, profile) == expected


@pytest.mark.parametrize("preference, expected", [
    ("EADGBE", 0), ("DADGBE", 1), ("Indifferent", 0),
])
def test_tuning_penalty(analysis, profile, preference, expected):
    profile.tuning_preference = preference
    assert get_tuning_weight(analysis, profile) == expected


def test_matching_requirements_give_full_match(analysis, profile):
    song = Song(song_name="Example", artist_name="Artist", analysis=analysis)
    evaluate_match([song], profile)
    assert song.match == 100


def test_missing_half_the_chords_costs_fifteen_points(analysis, profile):
    profile.learned_chords = ["C"]
    song = Song(song_name="Example", artist_name="Artist", analysis=analysis)
    evaluate_match([song], profile)
    assert song.match == 85


def test_learning_bonus_cannot_exceed_one_hundred(analysis, profile):
    profile.in_training_chords = ["C"]
    song = Song(song_name="Example", artist_name="Artist", analysis=analysis)
    evaluate_match([song], profile)
    assert song.match == 100


def test_empty_song_list_returns_empty_list(profile):
    assert evaluate_match([], profile) == []
