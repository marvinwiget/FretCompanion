# flask --app app/routes run
from flask import Flask, request, render_template
from .api.lb_api import get_latest_songs

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    params = {"user_found": True,
              "recent_activity": True,
              "songs": {}
              }
    
    if request.method == 'POST':
        username = request.form["username"]
        try: 
            params["songs"] = get_latest_songs(username)
            if not params["songs"]: params["recent_activity"] = False
        except:
            params["user_found"] = False
            params["recent_activity"] = False
            
    return render_template("home.html", params=params)

