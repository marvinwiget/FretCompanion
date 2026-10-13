import pytest

from app.schemas.profile import GuitarProfile
from app.schemas.song import SongAnalysis


@pytest.fixture
def analysis():
    """Fresh analysis for each test, without calling an AI provider."""
    return SongAnalysis(
        tuning="EADGBE",
        overall_difficulty="Beginner",
        playing_style="Rhythm",
        rhythm_difficulty=2,
        lead_difficulty=1,
        solo_difficulty=1,
        tempo_difficulty=2,
        required_chords=["C", "G"],
        main_techniques=["Strumming"],
        other_techniques=[],
        explanation="An example rhythm arrangement.",
        confidence=0.8,
    )


@pytest.fixture
def profile():
    return GuitarProfile(
        experience_level="Beginner",
        playing_style_preference="Rhythm",
        techniques=["Strumming"],
        learned_chords=["C", "G"],
        in_training_chords=[],
        tuning_preference="EADGBE",
    )


@pytest.fixture(autouse=True)
def block_external_http(monkeypatch):
    """An unmocked provider call must fail immediately, not spend quota."""
    import requests
    import httpx

    def blocked(*args, **kwargs):
        raise AssertionError("Tests must not make real HTTP requests")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    monkeypatch.setattr(httpx.Client, "send", blocked)


@pytest.fixture
def flask_app(tmp_path):
    from app import create_app

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-only-session-signing-key",
        "DATABASE_URL": f"sqlite+pysqlite:///{tmp_path / 'test.db'}",
    })
    with app.app_context():
        yield app
    app.extensions["database_engine"].dispose()


@pytest.fixture
def database(flask_app):
    from app.database import tracks
    return tracks


@pytest.fixture
def routes(flask_app):
    from app import routes
    return routes


@pytest.fixture
def client(flask_app, profile):
    client = flask_app.test_client()
    with client.session_transaction() as session:
        session["guitar_profile"] = profile.model_dump(mode="json")
        session["profile_submitted"] = True
    return client
