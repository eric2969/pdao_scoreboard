from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from functools import wraps
import requests, json, os, re, hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for session management

STATUS_FILE = "backend_file/status.json"

# 載入題目與隊伍資訊
def load_contest_metadata():
    try:
        response = requests.get("https://ntu.im/PDAO/contest_data.json", timeout=5)
        response.raise_for_status()
        data = response.json()
        problems = {
            p["id"]: {"name": p["name"], "color": p["color"], "title": p["title"]}
            for p in data.get("problems", [])
        }
        teams = {
            t["id"]: {
                "name": re.sub(r"\s*\(.*?\)", "", t["name"]),
                "position": t["position"] if "position" in t else "?",
            }
            for t in data.get("teams", [])
        }
        return problems, teams
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f)

def load_data():
    try:
        response = requests.get("https://ntu.im/PDAO/runs.php", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["data"]["runs"]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def extract_first_yes_runs(runs):
    seen = set()
    result = []
    for run in runs:
        key = (run["team"], run["problem"])
        if run["result"].startswith("Yes") and key not in seen:
            result.append(run)
            seen.add(key)
    return result

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def balloon():
    pro, tem = load_contest_metadata()
    contest_data = {"problems": pro, "teams": tem}
    return render_template("index.html", contest_data=contest_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        username = request.form.get("username")
        passwd = request.form.get("password")
        if username == "PDAO" and hashlib.sha256(passwd.encode('utf-8')).hexdigest() == "35cc9d732ea9d273479f70d54ba368899bae9a9dff25f56e66e20f8bc44cd1b4":
            session['logged_in'] = True
            return redirect(url_for('balloon'))
        error = True
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/api/runs")
def api_runs():
    runs = load_data()
    status = load_status()
    problem_meta, team_info = load_contest_metadata()

    yes_runs = extract_first_yes_runs(runs)

    for run in yes_runs:
        prob_info = problem_meta.get(run["problem"], {})
        team = team_info.get(run["team"], {})
        run["color"] = prob_info.get("color", "gray")
        run["problem_label"] = prob_info.get("name", "?")
        run["team_name"] = team.get("name", f"Team {run['team']}")
        run["team_position"] = team.get("position", "?")
        run["made"] = status.get(str(run["id"]), {}).get("made", False)
        run["sent"] = status.get(str(run["id"]), {}).get("sent", False)

    return jsonify(yes_runs)

@app.route("/api/update_status", methods=["POST"])
@login_required
def update_status():
    run_id = str(request.json.get("id"))
    field = request.json.get("field")  # 'made' or 'sent'
    value = bool(request.json.get("value"))

    status = load_status()
    if run_id not in status:
        status[run_id] = {"made": False, "sent": False}

    status[run_id][field] = value
    save_status(status)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
