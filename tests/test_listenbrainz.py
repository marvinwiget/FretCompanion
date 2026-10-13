import json
from unittest.mock import Mock

import pytest
import requests

from app.integrations import listenbrainz as lb
from app.exceptions import LBUnavailable, LBUserNotFound, NoUserActivity


@pytest.fixture(params=[lb.get_latest_songs, lb.get_top_songs], ids=["recent", "top"])
def fetch(request):
    return request.param


def response(status=200, data=None, body=None):
    result = requests.Response()
    result.status_code = status
    result._content = (body if body is not None else json.dumps(data)).encode()
    result.url = "https://api.listenbrainz.org/example"
    return result


def mock_get(monkeypatch, result):
    get = Mock(return_value=result)
    monkeypatch.setattr(lb.requests, "get", get)
    return get


def payload(fetch, tracks):
    key = "listens" if fetch is lb.get_latest_songs else "recordings"
    return {"payload": {key: tracks}}


def test_success_and_query_parameters(monkeypatch, fetch):
    metadata = {"track_name": "Example", "artist_name": "Artist"}
    tracks = [{"track_metadata": metadata}] if fetch is lb.get_latest_songs else [metadata]
    get = mock_get(monkeypatch, response(data=payload(fetch, tracks)))
    assert fetch("example-user", count=2) == tracks
    assert get.call_args.kwargs["params"]["count"] == 2
    assert get.call_args.kwargs["timeout"] == 20
    assert "headers" not in get.call_args.kwargs


def test_top_time_range_is_forwarded(monkeypatch):
    get = mock_get(monkeypatch, response(data={"payload": {"recordings": []}}))
    lb.get_top_songs("user", time_range="year")
    assert get.call_args.kwargs["params"]["range"] == "year"


def test_username_is_encoded_as_one_path_segment(monkeypatch):
    get = mock_get(monkeypatch, response(data={"payload": {"listens": []}}))
    lb.get_latest_songs("a/b?c")
    assert "/a%2Fb%3Fc/listens" in get.call_args.kwargs["url"]


@pytest.mark.parametrize("failure", [requests.Timeout, requests.ConnectionError, requests.TooManyRedirects])
def test_network_failure_is_translated(monkeypatch, fetch, failure):
    monkeypatch.setattr(lb.requests, "get", Mock(side_effect=failure("internal details")))
    with pytest.raises(LBUnavailable) as error:
        fetch("user")
    assert isinstance(error.value.__cause__, failure)
    assert "internal details" not in str(error.value)


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 502, 503])
def test_http_failure_is_translated(monkeypatch, fetch, status):
    mock_get(monkeypatch, response(status, {"error": "private provider details"}))
    with pytest.raises(LBUnavailable) as error:
        fetch("user")
    assert "private provider details" not in str(error.value)
    if status == 429:
        assert "too many requests" in str(error.value)


def test_confirmed_missing_user(monkeypatch, fetch):
    mock_get(monkeypatch, response(404, {"error": "User missing-user not found"}))
    with pytest.raises(LBUserNotFound):
        fetch("missing-user")


@pytest.mark.parametrize("body", ['{"error":"The requested URL was not found"}', '<html>Not found</html>', '[]', '{"error":null}'])
def test_generic_404_is_not_reported_as_missing_user(monkeypatch, fetch, body):
    mock_get(monkeypatch, response(404, body=body))
    with pytest.raises(LBUnavailable):
        fetch("existing-user")


def test_no_content_is_distinct_from_failure(monkeypatch, fetch):
    mock_get(monkeypatch, response(204, body=""))
    with pytest.raises(NoUserActivity):
        fetch("user")


def test_empty_list_is_valid(monkeypatch, fetch):
    mock_get(monkeypatch, response(data=payload(fetch, [])))
    assert fetch("user") == []


@pytest.mark.parametrize("data", [None, [], {}, {"payload": None}, {"payload": {}}])
def test_missing_payload_is_translated(monkeypatch, fetch, data):
    mock_get(monkeypatch, response(data=data))
    with pytest.raises(LBUnavailable, match="unexpected response"):
        fetch("user")


@pytest.mark.parametrize("tracks", [None, {}, "songs", [None], [1], [{}]])
def test_invalid_track_shape_is_translated(monkeypatch, fetch, tracks):
    mock_get(monkeypatch, response(data=payload(fetch, tracks)))
    with pytest.raises(LBUnavailable, match="unexpected response"):
        fetch("user")


def test_invalid_json_is_translated(monkeypatch, fetch):
    mock_get(monkeypatch, response(body="not json"))
    with pytest.raises(LBUnavailable):
        fetch("user")


@pytest.mark.parametrize("mapping", [None, {}, {"recording_mbid": None}])
def test_optional_mbid_mapping(monkeypatch, mapping):
    tracks = [{"track_metadata": {"track_name": "Example", "artist_name": "Artist", "mbid_mapping": mapping}}]
    mock_get(monkeypatch, response(data={"payload": {"listens": tracks}}))
    assert lb.get_latest_songs("user") == tracks
