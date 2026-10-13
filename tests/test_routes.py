from unittest.mock import Mock

import pytest
from flask import Flask

from app.exceptions import LBUnavailable, LBUserNotFound, NoUserActivity, AnalysisUnavailable, InvalidAnalysisResponse
from app.schemas.song import Song


FORM = {"username": "example-user", "count": "2", "result_type": "last_listened_songs", "time_range": "month"}


@pytest.fixture
def search_sources(routes, monkeypatch, analysis):
    fetch = Mock(return_value=[{"track_metadata": {"track_name": "Example", "artist_name": "Artist"}}])
    monkeypatch.setattr(routes.search_service, "get_latest_songs", fetch)
    def analyze(songs):
        for song in songs:
            song.analysis = analysis.model_copy(deep=True)
    analyze_mock = Mock(side_effect=analyze)
    monkeypatch.setattr(routes.search_service, "analyze_songs", analyze_mock)
    return fetch, analyze_mock


def test_search_saves_and_restores_scored_results(client, search_sources):
    fetch, analyze = search_sources
    response = client.post("/search", data=FORM)
    assert response.status_code == 200
    assert b"100% match" in response.data
    assert b"Example" in response.data
    with client.session_transaction() as session:
        assert len(session["last_searched_ids"]) == 1
    restored = client.get("/search")
    assert b"100% match" in restored.data
    assert fetch.call_count == 1
    assert analyze.call_count == 1


def test_second_search_uses_cached_analysis(client, search_sources):
    client.post("/search", data=FORM)
    client.post("/search", data=FORM)
    assert search_sources[1].call_count == 1


@pytest.mark.parametrize("failure", [LBUnavailable("Provider unavailable"), LBUserNotFound("User not found")])
def test_listening_errors_show_message_not_empty_state(client, search_sources, failure):
    search_sources[0].side_effect = failure
    response = client.post("/search", data=FORM)
    assert response.status_code == 200
    assert str(failure).encode() in response.data
    assert b"No listening data" not in response.data
    search_sources[1].assert_not_called()


@pytest.mark.parametrize("failure", [AnalysisUnavailable("Analysis unavailable"), InvalidAnalysisResponse("Invalid analysis")])
def test_ai_failure_does_not_save_partial_results(client, routes, search_sources, monkeypatch, failure):
    search_sources[1].side_effect = failure
    save = Mock()
    monkeypatch.setattr(routes.db, "save_tracks", save)
    response = client.post("/search", data=FORM)
    assert str(failure).encode() in response.data
    assert b"No listening data" not in response.data
    save.assert_not_called()


def test_old_results_do_not_override_failed_search(client, search_sources):
    client.post("/search", data=FORM)
    search_sources[0].side_effect = LBUnavailable("Unavailable now")
    response = client.post("/search", data=FORM)
    assert b"Unavailable now" in response.data
    assert b'class="song-card"' not in response.data
    assert b'class="song-card"' in client.get("/search").data


@pytest.mark.parametrize("empty", [[], NoUserActivity("No statistics")])
def test_empty_results_are_not_errors(client, search_sources, empty):
    if isinstance(empty, Exception):
        search_sources[0].side_effect = empty
    else:
        search_sources[0].return_value = empty
    response = client.post("/search", data=FORM)
    assert b"No listening data is available" in response.data
    assert b'role="alert"' not in response.data
    search_sources[1].assert_not_called()


@pytest.mark.parametrize("field, value", [
    ("username", " "), ("count", "0"), ("count", "101"),
    ("count", "two"), ("count", "1.5"), ("result_type", "bad"), ("time_range", "bad"),
])
def test_invalid_form_is_rejected_before_external_request(client, search_sources, field, value):
    response = client.post("/search", data={**FORM, field: value})
    assert response.status_code == 400
    assert b'role="alert"' in response.data
    search_sources[0].assert_not_called()


@pytest.mark.parametrize("value", [None, {}, {"experience_level": "invalid"}])
def test_missing_or_stale_profile_has_actionable_message(client, search_sources, value):
    with client.session_transaction() as session:
        session["guitar_profile"] = value
    response = client.post("/search", data=FORM)
    assert b"Create or update your guitar profile" in response.data
    search_sources[0].assert_not_called()


def test_provider_message_is_html_escaped(client, search_sources):
    search_sources[0].side_effect = LBUnavailable("<script>alert(1)</script>")
    response = client.post("/search", data=FORM)
    assert b"&lt;script&gt;" in response.data
    assert b"<script>alert(1)</script>" not in response.data


def test_error_preserves_search_form_values(client, search_sources):
    search_sources[0].side_effect = LBUnavailable("Unavailable")
    response = client.post("/search", data={**FORM, "count": "7", "time_range": "year"})
    assert b'value="example-user"' in response.data
    assert b'name="count" value="7"' in response.data
    assert b'value="year" selected' in response.data


def test_top_track_flow(client, routes, search_sources, monkeypatch):
    monkeypatch.setattr(routes.search_service, "get_top_songs", Mock(return_value=[{"track_name": "Top song", "artist_name": "Artist"}]))
    response = client.post("/search", data={**FORM, "result_type": "top_songs"})
    assert b"Top song" in response.data
    search_sources[0].assert_not_called()


def test_save_toggle_uses_integer_ids_and_json(client):
    response = client.post("/tracks/12/toggle-save", headers={"Accept": "application/json"})
    assert response.json == {"saved": True}
    with client.session_transaction() as session:
        assert session["saved_tracks"] == [12]
    assert client.post("/tracks/12/toggle-save", headers={"Accept": "application/json"}).json == {"saved": False}


def test_plain_form_save_keeps_redirect_fallback(client):
    response = client.post("/tracks/12/toggle-save")
    assert response.status_code == 303
    assert response.location == "/search"


def test_cookie_can_be_read_by_new_app_with_same_secret(client, flask_app):
    client.post("/tracks/12/toggle-save")
    cookie = client.get_cookie("session")
    restarted = Flask("restarted")
    restarted.config["SECRET_KEY"] = flask_app.config["SECRET_KEY"]
    serializer = restarted.session_interface.get_signing_serializer(restarted)
    restored = serializer.loads(cookie.value)
    assert restored["saved_tracks"] == [12]
    assert restored["guitar_profile"]["experience_level"] == "Beginner"


def test_saved_feed_reads_session_tracks(client, database, analysis):
    song = Song(song_name="Saved example", artist_name="Artist", analysis=analysis)
    database.save_tracks([song])
    track_id = database.load_track(song).id
    client.post(f"/tracks/{track_id}/toggle-save")
    response = client.get("/saved-tracks")
    assert response.status_code == 200
    assert b"Saved example" in response.data
    assert b"100% match" in response.data
