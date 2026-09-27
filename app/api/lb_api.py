import requests

ROOT = "https://api.listenbrainz.org"

TOKEN = 'YOUR_TOKEN_HERE'
AUTH_HEADER = {
    "Authorization": "Token {0}".format(TOKEN)
}

def get_latest_songs(username: str, min_ts=None, max_ts=None, count=None):
    response = requests.get(
        url="{0}/1/user/{1}/listens".format(ROOT, username),
        params={
            "min_ts": min_ts,
            "max_ts": max_ts,
            "count": count,
        },
        headers=AUTH_HEADER,
    )

    response.raise_for_status()

    return response.json()['payload']['listens']