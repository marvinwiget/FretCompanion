# flask --app app/routes run
from flask import Flask, request, render_template, session
from pydantic import ValidationError
import secrets
import time
import pprint

from .api.listenbrainz_api import get_latest_songs, get_top_songs
from .api.song_analysis import get_songs_analysis
from .schemas.song import Song
from .schemas.profile import GuitarProfile
from .match_evaluation import evaluate_match
from .helper.chords import get_roots, get_chord_types
from .database.session import save_track, load_track, load_tracks

from .exceptions import GuitarProfileInvalid, LBUserNotFound, LBUnavailable, NoUserActivity

app = Flask(__name__)
app.secret_key = secrets.token_hex()

@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")

@app.route("/search", methods=['GET', 'POST'])
def search():

    params = {
        "user_found": True,
        "recent_activity": True,
        "result_type": "last_listened_songs",
        "eva_songs": [],
        "profile_submitted": session.get("profile_submitted")
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
            if session.get("profile_submitted") is None:
                raise GuitarProfileInvalid

            if result_type == "last_listened_songs":
                raw_songs = get_latest_songs(username, count=count)

                for raw_song in raw_songs:
                    metadata = raw_song["track_metadata"] # wont work with top songs -> different json return
                                    #pprint.pprint(metadata)
                    
                    songs_batch.append(Song(
                        rec_mbid=metadata["mbid_mapping"]["recording_mbid"] if "mbid_mapping" in metadata.keys() else None,
                        artist_name=metadata["artist_name"],
                        song_name=metadata["track_name"]
                        )
                    )

            else:
                raw_songs = get_top_songs(username, count=count, time_range=time_range)
                params["result_type"] = "top_songs"

                for raw_song in raw_songs:
                    songs_batch.append(Song(
                        rec_mbid=raw_song["recording_mbid"] if "recording_mbid" in raw_song.keys() else None,
                        artist_name=raw_song["artist_name"],
                        song_name=raw_song["track_name"]
                        )
                    )

            if not raw_songs: params["recent_activity"] = False # no recent activity found for user

            #pprint.pprint(raw_songs)
            
            needs_analysis = [s for s in songs_batch if load_track(s) is None] # make it a set so the same song doesnt get analysed twice
            unique_needs_analysis = []
            for s in needs_analysis:
                if s in unique_needs_analysis: continue
                unique_needs_analysis.append(s)

            needs_analysis = unique_needs_analysis
            
            if needs_analysis:
                analysed_batch = get_songs_analysis(needs_analysis)

                for song, analysis in zip(needs_analysis, analysed_batch):
                    song.analysis = analysis
                    save_track(song=song)

            params["eva_songs"] = load_tracks([s for s in songs_batch])

            evaluate_match(songs=params["eva_songs"], user=GuitarProfile.model_validate(session["guitar_profile"]))

            end_time = time.time()
            print(f"Total time elapsed: {end_time - start_time:.2f} seconds")

        except LBUserNotFound:
            params["user_found"] = False
            params["recent_activity"] = False
        except LBUnavailable:
            params["recent_activity"] = False
        except NoUserActivity:
            params["recent_activity"] = False
        except GuitarProfileInvalid:
            params["profile_submitted"] = False

    return render_template("search.html", params=params)

@app.route("/guitar-profile", methods=["GET", "POST"])
def profile(): 
    

    params = {
        "roots": get_roots(),
        "chord_types": get_chord_types()
    }
    
    if request.method == "POST":
        experience_level = request.form["experience_level"]
        playing_style_preference = request.form["playing_style"]
        techniques = request.form.getlist("techniques")
        chords = request.form.getlist("chords")
        tuning_preference = request.form["tuning"]

        session["guitar_profile"] = GuitarProfile(
            experience_level=experience_level,
            playing_style_preference=playing_style_preference,
            techniques=techniques,
            learned_chords=chords,
            in_training_chords=[],
            tuning_preference=tuning_preference
        ).model_dump(mode="json")
        session["profile_submitted"] = True

    return render_template("profile.html", params=params)

