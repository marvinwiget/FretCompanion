# flask --app app/routes run
from flask import Flask, request, render_template, session
from .api.listenbrainz_api import get_latest_songs, get_top_songs
from .api.analysis import get_songs_analysis
from .schemas.song import Song
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex()

@app.route("/", methods=['GET', 'POST'])
def home():
    params = {"user_found": True,
              "recent_activity": True,
              "result_type": "last_listened_songs",
              "eva_songs": []
              }
    
    if request.method == 'POST':
        username = request.form["username"].strip()
        count = request.form["count"]
        result_type = request.form["result_type"]
        time_range = request.form["time_range"]
        songs_batch = []
        raw_songs = []

        try: 
            if result_type == "last_listened_songs":
                raw_songs = get_latest_songs(username, count=count)
            else:
                raw_songs = get_top_songs(username, count=count, time_range=time_range)
                params["result_type"] = "top_songs"

            if not raw_songs: params["recent_activity"] = False

            for raw_song in raw_songs:
                metadata = raw_song["track_metadata"] # wont work with top songs -> different json return

                songs_batch.append(Song(
                    artist_name=metadata["artist_name"],
                    song_name=metadata["track_name"]
                ))

            analysed_batch = get_songs_analysis(songs_batch)

            for song, analysis in zip(songs_batch, analysed_batch):
                song.analysis = analysis
            params["eva_songs"] = songs_batch


        except NameError:
            params["user_found"] = False
            params["recent_activity"] = False
        # except Exception as e:
        #     print(e)
        #     print(e)
        #     params["recent_activity"] = False

    return render_template("home.html", params=params)

