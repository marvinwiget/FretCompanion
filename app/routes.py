from flask import Blueprint, current_app, request, render_template, session, redirect, url_for, jsonify
from pydantic import ValidationError
import time

from .services import search as search_service
from .schemas.profile import GuitarProfile
from .match_evaluation import evaluate_match
from .helper.chords import get_roots, get_chord_types
from .database import tracks as db
from .exceptions import (GuitarProfileInvalid, LBUserNotFound, LBUnavailable,
                         NoUserActivity, AnalysisUnavailable, InvalidAnalysisResponse)

pages = Blueprint("pages", __name__)


def read_guitar_profile() -> GuitarProfile:
    try:
        return GuitarProfile.model_validate(session.get("guitar_profile"))
    except ValidationError as exc:
        raise GuitarProfileInvalid("Create or update your guitar profile.") from exc


@pages.route("/", methods=['GET'])
def home():
    return render_template("home.html")

@pages.route("/search", methods=['GET', 'POST'])
def search():

    params = {
        "user_found": True,
        "recent_activity": True,
        "result_type": "last_listened_songs",
        "eva_songs": [],
        "profile_submitted": session.get("profile_submitted"),
        "error_message": None
        }
    
    if request.method == 'POST':
        start_time = time.time()

        username = request.form.get("username", "").strip()
        result_type = request.form.get("result_type", "last_listened_songs")
        time_range = request.form.get("time_range", "month")
        params["result_type"] = result_type
        try:
            count = int(request.form.get("count", "25"))
        except ValueError:
            count = 0
        if not username or not 1 <= count <= 100 or result_type not in {"last_listened_songs", "top_songs"} or time_range not in {"week", "month", "year", "all_time"}:
            params["error_message"] = "Enter a username, a track count from 1 to 100, and a valid listening selection."
            return render_template("search.html", params=params), 400

        try: 
            user_profile = read_guitar_profile()

            params["eva_songs"] = search_service.search_songs(
                username, count, result_type, time_range, user_profile
            )
            if not params["eva_songs"]:
                params["recent_activity"] = False

            session["last_searched_ids"] = [track.id for track in params["eva_songs"]]

            end_time = time.time()
            print(f"Total time elapsed: {end_time - start_time:.2f} seconds")

        except LBUserNotFound as exc:
            params["user_found"] = False
            params["error_message"] = str(exc)
        except (LBUnavailable, AnalysisUnavailable, InvalidAnalysisResponse) as exc:
            # log the category, not provider bodies that may contain sensitive content.
            current_app.logger.warning("Search failed: %s", type(exc).__name__)
            params["eva_songs"] = []
            params["error_message"] = str(exc)
        except NoUserActivity:
            params["recent_activity"] = False
            session["last_searched_ids"] = []
        except GuitarProfileInvalid:
            params["profile_submitted"] = False
            params["error_message"] = "Create or update your guitar profile before searching."

    if request.method == "GET" and session.get("last_searched_ids"):
        try:
            user_profile = read_guitar_profile()
            params["eva_songs"] = db.load_tracks_with_id(session["last_searched_ids"])
            evaluate_match(params["eva_songs"], user=user_profile)
        except GuitarProfileInvalid:
            params["error_message"] = "Create or update your guitar profile to restore your results."

    return render_template("search.html", params=params)

@pages.route("/guitar-profile", methods=["GET", "POST"])
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

@pages.route("/tracks/<int:track_id>/toggle-save", methods=["POST"])
def toggle_saved_track(track_id: int):
    saved_tracks = session.get("saved_tracks", [])

    if track_id in saved_tracks:
        saved_tracks.remove(track_id)
    else:
        saved_tracks.append(track_id)

    session["saved_tracks"] = saved_tracks

    if request.accept_mimetypes.best == "application/json":
        return jsonify(saved=track_id in saved_tracks)

    return redirect(url_for("pages.search"), code=303)

@pages.route("/saved-tracks")
def saved_tracks():
    saved_tracks_id = session.get("saved_tracks", [])
    if saved_tracks_id and session.get("guitar_profile"):
        saved_tracks = db.load_tracks_with_id(saved_tracks_id)
        evaluate_match(songs=saved_tracks, user=GuitarProfile.model_validate(session["guitar_profile"]))
    else:
        saved_tracks = [] # empty list will result in no results, and site will not crash

    return render_template("saved-tracks.html", saved_tracks=saved_tracks)
