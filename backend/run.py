from flask import Flask, render_template, request, redirect, jsonify, session, url_for, abort
from functools import wraps
from flask_cors import CORS
import requests, json, os, re, hashlib, time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = os.urandom(24)  # Generate a random secret key for session management

STATUS_FILE = "backend_file/status.json"
ACCOUNT_FILE = "backend_file/account.json"

config_path = "backend_file/scoreboard.json"
data_path = "backend_file/contest_data.json"

# config data
Frozen_flag = True
sid = None
token = None
scoreboard_cache = {"data": None, "timestamp": 0}
fetch_flag = False
contest_data = None

# 讀取配置檔案
def load_config():
    global sid, token, contest_data
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Configuration file '{config_path}' is not valid JSON.")
    if not config.get("sid") or not config.get("token"):
        raise ValueError("Invalid configuration: 'sid' and 'token' are required.")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            contest_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Contest data file '{data_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Contest data file '{data_path}' is not valid JSON.")
    sid = config.get("sid")
    token = config.get("token")

# 載入帳號資料
def load_accounts():
    if not os.path.exists(ACCOUNT_FILE):
        raise FileNotFoundError(f"Account file '{ACCOUNT_FILE}' not found.")
    with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

# 載入題目與隊伍資訊
def load_contest_metadata():
    global contest_data
    try:
        data = contest_data
        problems = {
            p["id"]: {"name": p["name"], "color": p["color"], "title": p["title"]}
            for p in data.get("problems", [])
        }
        teams = {
            t["id"]: {
                "name": re.sub(r"\s*\(.*?\)", "", t["name"]),
                "position": t.get("position","??"),
                "section": t.get("section","??"),
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

def load_runs():
    global sid, token, scoreboard_cache, Frozen_flag, fetch_flag
    if fetch_flag:
        return {"success": True}
    fetch_flag = True
    print("Loading runs from PDOGS...")
    try:
        url = f"https://be.pdogs.ntu.im/hardcode/team-contest-scoreboard/{sid}/runs"
        headers = {
            "auth-token": token,
            "Content-Type": "application/json"
        }
        res = requests.get(url, headers=headers, timeout=3)
        res.raise_for_status()
        data = res.json()
        contestTime = data["data"]["time"]["contestTime"]
        timestamp = data["data"]["time"]["timestamp"]
        if Frozen_flag and contestTime <= timestamp:
            left,right = -1, len(data["data"]["runs"])  # 因為要找第一個 >= contestTime
            while left + 1 < right:
                mid = (left + right) // 2
                if data["data"]["runs"][mid]["submissionTime"] * 60 + 3600 > contestTime:
                    right = mid
                else:
                    left = mid
            for i in range(left+1, len(data["data"]["runs"])):
                data["data"]["runs"][i]["result"] = "Pending"
        scoreboard_cache["data"] = data
        scoreboard_cache["timestamp"] = time.time()
        fetch_flag = False
        return {"success": True}
    except Exception as e:
        fetch_flag = False
        return {"success": False, "error": str(e)}

def extract_first_yes_runs(runs):
    seen = set()
    result = []
    for run in runs:
        key = (run["team"], run["problem"])
        if ("Yes" in run["result"]) and key not in seen:
            result.append(run)
            seen.add(key)
    return result

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in', False):
            return (jsonify({"success": False, "error": "NoPermission"}))
        return f(*args, **kwargs)
    return decorated_function

# flask app routes

@app.route("/balloon")
@login_required
def balloon():
    pro, tem = load_contest_metadata()
    contest_data = {"problems": pro, "teams": tem}
    return render_template("balloon/index.html", contest_data=contest_data, current_user=session.get("username"))

@app.route("/balloon/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        accounts = load_accounts()

        if username in accounts and accounts[username] == hashlib.sha256(password.encode('utf-8')).hexdigest():
            session['logged_in'] = True
            session['username'] = username
            return redirect("/balloon")
        error = True
    return render_template("balloon/login.html", error=error)

@app.route("/balloon/logout")
def logout():
    session.pop('logged_in', None)
    return redirect("login")

@app.route("/balloon/login_status")
def login_status():
    return jsonify({"logged_in": session.get('logged_in', False)})

@app.route("/api/contest_data", methods=["GET"])
def contest_data_api():
    global contest_data
    return jsonify(contest_data)

@app.route("/api/account_modify", methods=["POST"])
@login_required
def add_account():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "error": "Missing username or password"}), 400

    accounts = load_accounts()
    exist = (username in accounts)
    accounts[username] = hashlib.sha256(password.encode('utf-8')).hexdigest()
    save_accounts(accounts)
    return jsonify({"success": True, "method": "edit" if exist else "add"})

@app.route("/api/account/delete", methods=["POST"])
@login_required
def delete_account():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "error": "Not logged in"}), 403

    accounts = load_accounts()
    if username in accounts:
        if len(accounts) <= 1:
            return jsonify({"success": False, "error": "Last account"}), 403
        del accounts[username]
        save_accounts(accounts)
        session.pop('logged_in', None)
        session.pop('username', None)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Account not found"}), 404

@app.route("/api/runs")
def get_runs():
    global scoreboard_cache
    now = time.time()
    if now - scoreboard_cache["timestamp"] < 1.5:
        return jsonify(scoreboard_cache["data"])
    if load_runs().get("success"):
        return jsonify(scoreboard_cache["data"])
    else:
        return jsonify({"success": False, "error": "Failed to load runs"}), 500

@app.route("/api/runs/balloon")
@login_required_error
def api_runs():
    global scoreboard_cache
    status = load_status()
    problem_meta, team_info = load_contest_metadata()
    if time.time() - scoreboard_cache["timestamp"] < 1:
        data = scoreboard_cache["data"]
    else:
        if load_runs().get("success"):
            data = scoreboard_cache["data"]
        else:
            return jsonify({"success": False, "error": "Failed to load runs"}, 500)
    runs = data["data"]["runs"]
    yes_runs = extract_first_yes_runs(runs)

    for run in yes_runs:
        prob_info = problem_meta.get(run["problem"], {})
        team = team_info.get(run["team"], {})
        run["id"] = run["id"]
        run["color"] = prob_info.get("color", "gray")
        run["problem_label"] = prob_info.get("name", "?")
        run["team_name"] = team.get("name", f"Team {run['team']}")
        run["team_position"] = team.get("position", "??")
        run["team_section"] = team.get("section", "??")
        run["made"] = status.get(str(run["id"]), {}).get("made", False)
        run["sent"] = status.get(str(run["id"]), {}).get("sent", False)

    return jsonify({"success": True, "error": "Null", "data": yes_runs})

@app.route("/api/update_status", methods=["POST"])
@login_required
def update_status():
    run_id = str(request.json.get("id"))
    field = request.json.get("field")  # 'made' or 'sent'
    value = bool(request.json.get("value"))

    status = load_status()
    if run_id not in status:
        status[run_id] = {"made": False, "sent": False}
    if field == "made":
        status[run_id]["sent"] = False
    status[run_id][field] = value
    save_status(status)
    return jsonify({"success": True})

@app.route("/api/frozen", methods=["GET"])
@login_required
def frozen_status():
    global Frozen_flag
    return jsonify({"status": "True" if Frozen_flag else "False"})

@app.route("/api/frozen", methods=["POST"])
@login_required
def frozen():
    global Frozen_flag, scoreboard_cache
    Frozen_flag = request.json.get("frozen", True)
    scoreboard_cache["timestamp"] = -1
    return jsonify({"Success": "True", "status": "True" if Frozen_flag else "False"})


if __name__ == "__main__":
    try:
        load_config()
        load_accounts()
        load_runs()
        load_contest_metadata()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        exit(1)
    app.run(host="0.0.0.0", port=3001, debug=False)
