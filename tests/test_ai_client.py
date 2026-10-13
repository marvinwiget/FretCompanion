import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest
from google.genai import errors
from google.genai._gaos.lib import compat_errors

from app.integrations import song_analysis as ai
from app.exceptions import AnalysisUnavailable, InvalidAnalysisResponse
from app.schemas.song import Song


@pytest.fixture
def provider(monkeypatch, analysis):
    client = MagicMock()
    client.__enter__.return_value = client
    client.interactions.create.return_value = SimpleNamespace(output_text=json.dumps([analysis.model_dump(mode="json")]))
    monkeypatch.setattr(ai, "get_client", lambda: client)
    return client


def songs(count=1):
    return [Song(song_name=f"Example {i}", artist_name="Artist") for i in range(count)]


def test_valid_analysis_is_assigned(provider):
    batch = songs()
    assert ai.analyze_songs(batch) is True
    assert batch[0].analysis.tuning == "EADGBE"
    assert provider.interactions.create.call_args.kwargs["response_format"]["schema"]["type"] == "array"


def test_empty_batch_does_not_call_provider(provider):
    ai.analyze_songs([])
    provider.interactions.create.assert_not_called()


@pytest.mark.parametrize("text", [None, "", "not JSON", "{}", '{"songs": []}', '[{"tuning": "wrong"}]', '[null]', '[]'])
def test_invalid_response_leaves_songs_unchanged(provider, text):
    batch = songs()
    provider.interactions.create.return_value = SimpleNamespace(output_text=text)
    with pytest.raises(InvalidAnalysisResponse):
        ai.analyze_songs(batch)
    assert batch[0].analysis is None


@pytest.mark.parametrize("returned", [0, 1, 3])
def test_batch_length_must_match(provider, analysis, returned):
    batch = songs(2)
    provider.interactions.create.return_value.output_text = json.dumps([analysis.model_dump(mode="json")] * returned)
    with pytest.raises(InvalidAnalysisResponse):
        ai.analyze_songs(batch)
    assert all(song.analysis is None for song in batch)


def test_later_invalid_item_does_not_partially_update(provider, analysis):
    batch = songs(2)
    provider.interactions.create.return_value.output_text = json.dumps([analysis.model_dump(mode="json"), {"invalid": True}])
    with pytest.raises(InvalidAnalysisResponse):
        ai.analyze_songs(batch)
    assert all(song.analysis is None for song in batch)


@pytest.mark.parametrize("code", [400, 401, 403, 429, 500, 503])
@pytest.mark.parametrize("hierarchy", ["standard", "interactions"])
def test_provider_api_errors_are_translated(provider, code, hierarchy):
    if hierarchy == "standard":
        error = errors.APIError(code, {"error": {"message": "private details"}})
    else:
        response = httpx.Response(code, request=httpx.Request("POST", "https://example.test"))
        error = compat_errors.APIError.generate(code, {}, "private details", response)
    provider.interactions.create.side_effect = error
    with pytest.raises(AnalysisUnavailable) as raised:
        ai.analyze_songs(songs())
    assert "private details" not in str(raised.value)
    if code == 429:
        assert "request limit" in str(raised.value)


@pytest.mark.parametrize("error", [
    httpx.ReadTimeout("timeout"),
    httpx.ConnectError("offline"),
    compat_errors.APITimeoutError(request=httpx.Request("POST", "https://example.test")),
    compat_errors.APIConnectionError(request=httpx.Request("POST", "https://example.test")),
])
def test_transport_errors_are_translated(provider, error):
    provider.interactions.create.side_effect = error
    with pytest.raises(AnalysisUnavailable):
        ai.analyze_songs(songs())


def test_missing_key_is_a_configuration_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(AnalysisUnavailable, match="not configured"):
        ai.get_client()


def test_programming_errors_are_not_hidden(provider):
    provider.interactions.create.side_effect = TypeError("programming bug")
    with pytest.raises(TypeError, match="programming bug"):
        ai.analyze_songs(songs())


def test_prompt_only_includes_identity(analysis):
    song = Song(id=123456, song_name="Example", artist_name="Artist", match=73, analysis=analysis)
    prompt = ai.get_prompt([song])
    assert "Example - Artist" in prompt
    assert "123456" not in prompt
    assert analysis.explanation not in prompt
    assert 'Return exactly one valid JSON array' in prompt
