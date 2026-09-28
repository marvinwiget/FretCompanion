import requests
import pprint

ROOT = "https://api.listenbrainz.org"

TOKEN = 'YOUR_TOKEN_HERE'
AUTH_HEADER = {
    "Authorization": "Token {0}".format(TOKEN)
}

def get_latest_songs(username: str, min_ts=None, max_ts=None, count: int = 20):
    response = requests.get(
        url="{0}/1/user/{1}/listens".format(ROOT, username),
        params={
            "min_ts": min_ts,
            "max_ts": max_ts,
            "count": count,
        },
        headers=AUTH_HEADER,
        timeout=15
    )

    #print(response.status_code)

    if response.status_code == 402: # user not found
        raise NameError
    
    response.raise_for_status()

    return response.json()['payload']['listens']

def get_top_songs(username: str, count: int = 20, time_range: str = "month"):
    response = requests.get(
        f"{ROOT}/1/stats/user/{username}/recordings",
        params={
            "count": count,
            "range": time_range,
        },
        timeout=15,
    )

    if response.status_code == 204: # no statistics for this user
        return []

    if response.status_code == 402: # user not found
        raise NameError

    response.raise_for_status()

    return response.json()["payload"]["recordings"]