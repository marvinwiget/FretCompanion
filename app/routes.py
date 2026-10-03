# flask --app app/routes run
from flask import Flask, request, render_template, session
import secrets
import time

from .api.listenbrainz_api import get_latest_songs, get_top_songs
from .api.song_analysis import get_songs_analysis
from .schemas.song import Song
from .schemas.profile import GuitarProfile
from .match_evaluation import evaluate_match
from .helper.chords import get_roots, get_chord_types

app = Flask(__name__)
app.secret_key = secrets.token_hex()

user = GuitarProfile(
    experience_level="Intermediate",
    solo_preference="Indifferent",
    techniques=["Fingerpicking", "Strumming"],
    learned_chords=["C", "D", "E", "F", "G", "A", "B", "Cm", "Dm", "Em", "Fm", "Gm", "Am", "Bm"],
    in_training_chords=["FMaj7"],
    tuning_preferences="EADGBE"
)

@app.route("/", methods=['GET', 'POST'])
def home():
    params = {
        "user_found": True,
        "recent_activity": True,
        "result_type": "last_listened_songs",
        "eva_songs": []
        }
    
    if request.method == 'POST':
        start_time = time.time()

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

            try: 
                evaluate_match(songs=params["eva_songs"], user=session["guitar_profile"])
            except:
                evaluate_match(songs=params["eva_songs"], user=user)

            end_time = time.time()
            print(f"Total time elapsed: {end_time - start_time:.2f} seconds")


        except NameError:
            params["user_found"] = False
            params["recent_activity"] = False
        # except Exception as e:
        #     print(e)
        #     params["recent_activity"] = False

    return render_template("home.html", params=params)

@app.route("/guitar-profile", methods=["GET", "POST"])
def profile(): 
    

    params = {
        "roots": get_roots(),
        "chord_types": get_chord_types()
    }
    if request.method == "POST":
        selected_chords = request.form.getlist("chords")


    return render_template("profile.html", params=params)

