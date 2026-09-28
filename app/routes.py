# flask --app app/routes run
from flask import Flask, request, render_template, session
from .api.listenbrainz_api import get_latest_songs, get_top_songs
from .api.analysis import get_song_analysis
from .schemas.song import Song
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex()

@app.route("/", methods=['GET', 'POST'])
def home():
    params = {"user_found": True,
              "recent_activity": True,
              "result_type": "last_listened_songs",
              "raw_songs": [],
              "eva_songs": []
              }
    
    if request.method == 'POST':
        username = request.form["username"].strip()
        count = request.form["count"]
        result_type = request.form["result_type"]
        time_range = request.form["time_range"]

        try: 
            if result_type == "last_listened_songs":
                params["raw_songs"] = get_latest_songs(username, count=count)
            else:
                params["raw_songs"] = get_top_songs(username, count=count, time_range=time_range)
                params["result_type"] = "top_songs"

            if not params["raw_songs"]: params["recent_activity"] = False

            for listen in params["raw_songs"]:
                metadata = listen["track_metadata"]

                song = Song(
                    artist_name=metadata["artist_name"],
                    song_name=metadata["track_name"],
                )

                song.analysis = get_song_analysis(song)

                params["eva_songs"].append(song)


        except NameError:
            params["user_found"] = False
            params["recent_activity"] = False
        except Exception as e:
            print(e)
            params["recent_activity"] = False

    for song in params["eva_songs"]:
        print(song.song_name, song.analysis)

    return render_template("home.html", params=params)

