from flask import Flask, render_template, request, redirect, jsonify, session, url_for, abort
from functools import wraps
from flask_cors import CORS
import requests, json, os, re, hashlib, time
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/pdao_be/static')
CORS(app, resources={r"/pdao_be/api/*": {"origins": "*"}})
app.secret_key = hashlib.sha256("PDAOiiaioiiiai".encode('utf-8')).hexdigest()
app.permanent_session_lifetime = timedelta(minutes=10)

STATUS_FILE = "backend_file/status.json"
ACCOUNT_FILE = "backend_file/account.json"
CONFIG_PATH = "backend_file/scoreboard.json"
DATA_PATH = "backend_file/contest_data.json"

# config data
contest_data, problem_meta, team_info = None, None, None
sid, token = None, None

# 讀取配置檔案
def load_config():
    global sid, token, contest_data
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{CONFIG_PATH}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Configuration file '{CONFIG_PATH}' is not valid JSON.")
    if not config.get("sid") or not config.get("token"):
        raise ValueError("Invalid configuration: 'sid' and 'token' are required.")
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            contest_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Contest data file '{DATA_PATH}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Contest data file '{DATA_PATH}' is not valid JSON.")
    sid = config.get("sid")
    token = config.get("token")

# 載入封板狀態
def load_frozen():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("frozen", True)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{CONFIG_PATH}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Configuration file '{CONFIG_PATH}' is not valid JSON.")

def save_frozen(frozen):
    global sid, token
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config = {"sid": sid, "token": token, "frozen": frozen}
        json.dump(config, f, indent=2)

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
    global contest_data, problem_meta, team_info
    data = contest_data
    problem_meta = {
        p["id"]: {"name": p["name"], "color": p["color"], "title": p["title"]}
        for p in data.get("problems", [])
    }
    team_info = {
        t["id"]: {
            "name": re.sub(r"\s*\(.*?\)", "", t["name"]),
            "position": t.get("position","??"),
            "section": t.get("section","??"),
        }
        for t in data.get("teams", [])
    }

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f)

def load_runs():
    global sid, token
    try:
        url = f"https://be.pdogs.ntu.im/hardcode/team-contest-scoreboard/{sid}/runs"
        headers = {
            "auth-token": token,
            "Content-Type": "application/json"
        }
        res = requests.get(url, headers=headers, timeout=3)
        res.raise_for_status()
        data = res.json()
        if data["success"] == False:
            return {"success": False, "error": data["error"]}
        contestTime = data["data"]["time"]["contestTime"]
        timestamp = data["data"]["time"]["timestamp"]
        #if end and flag is frozen
        if load_frozen() and contestTime <= timestamp:
            left,right = -1, len(data["data"]["runs"])
            while left + 1 < right:
                mid = (left + right) // 2
                if data["data"]["runs"][mid]["submissionTime"] * 60 + 3600 > contestTime:
                    right = mid
                else:
                    left = mid
            for i in range(left+1, len(data["data"]["runs"])):
                data["data"]["runs"][i]["result"] = "Pending"
        return {"success": True, "data": data}
    except Exception as e:
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
        if not session.get('logged_in', False) or session.get('username', None) not in load_accounts():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in', False) or session.get('username', None) not in load_accounts():
            return (jsonify({"success": False, "error": "NoPermission"}))
        return f(*args, **kwargs)
    return decorated_function

# flask app routes

@app.route("/pdao_be/admin", endpoint="index")
@login_required
def balloon():
    contest_data = {"problems": problem_meta, "teams": team_info}
    return render_template("balloon/index.html", contest_data=contest_data, current_user=session.get("username"))

@app.route("/pdao_be/ballon/statistics", endpoint="stat")
@login_required
def statistics():
    sec = request.args.get("sec")
    if sec is None:
        sec = "pro"
    return render_template("balloon/stat.html", contest_data=contest_data, current_user=session.get("username"), req_sec = sec)

@app.route("/pdao_be/balloon/login", methods=["GET", "POST"], endpoint="login")
def login():
    error = False
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        accounts = load_accounts()

        if username in accounts and accounts[username] == hashlib.sha256(password.encode('utf-8')).hexdigest():
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("index"))  # 預設回首頁
        error = True
    return render_template("balloon/login.html", error=error)

@app.route("/pdao_be/balloon/logout", endpoint="logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/pdao_be/balloon/login_status", endpoint="login_status")
def login_status():
    status = session.get('logged_in', False) and session.get('username', None) in load_accounts()
    return jsonify({"logged_in": status, "username": session.get("username", None)})

@app.route("/pdao_be/api/contest_data", methods=["GET"], endpoint="api-contest_data")
def contest_data_api():
    global contest_data
    return jsonify(contest_data)

@app.route("/pdao_be/api/account_modify", methods=["POST"], endpoint="api-account_modify")
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

@app.route("/pdao_be/api/account_delete", methods=["POST"], endpoint="api-account_delete")
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

@app.route("/pdao_be/api/runs", methods=["GET"], endpoint="api-runs")
def get_runs():
    res = load_runs()
    if res.get("success", False):
        return jsonify(res.get("data"))
    else:
        return jsonify(res), 500

@app.route("/pdao_be/api/runs/balloon", methods=["GET"], endpoint="api-runs_balloon")
@login_required_error
def api_runs():
    global problem_meta, team_info
    first = {}
    res = load_runs()
    if res.get("success", False):
        data = res.get("data")
    else:
        return jsonify(res), 500
    runs = data["data"]["runs"]
    yes_runs = extract_first_yes_runs(runs)
    status = load_status()
    for run in yes_runs:
        prob_info = problem_meta.get(run["problem"], {})
        team = team_info.get(run["team"], {})
        if run["problem"] not in first:
            first[run["problem"]] = run.get("id")
            run["isFirst"] = True
        elif run["id"] == first[run["problem"]]:
            run["isFirst"] = True
        else:
            run["isFirst"] = False
        run["color"] = prob_info.get("color", "gray")
        run["problem_label"] = prob_info.get("name", "?")
        run["team_name"] = team.get("name", f"Team {run['team']}")
        run["team_position"] = team.get("position", "??")
        run["team_section"] = team.get("section", "??")
        run["made"] = status.get(str(run["id"]), {}).get("made", False)
        run["sent"] = status.get(str(run["id"]), {}).get("sent", False)
    
    return jsonify({"success": True, "error": "Null", "data": yes_runs, "time": data["data"]["time"]})

@app.route("/pdao_be/api/update_status", methods=["POST"], endpoint="api-update_status")
@login_required
def update_status():
    status = load_status()
    run_id = str(request.json.get("id"))
    field = request.json.get("field")  # 'made' or 'sent'
    value = bool(request.json.get("value"))
    if run_id not in status:
        status[run_id] = {"made": False, "sent": False}
    if field == "made":
        status[run_id]["sent"] = False
    status[run_id][field] = value
    save_status(status)
    return jsonify({"success": True})

@app.route("/pdao_be/api/frozen", methods=["GET"], endpoint="api-frozen_get")
@login_required
def frozen_status():
    Frozen_flag = load_frozen()
    return jsonify({"status": "True" if Frozen_flag else "False"})

@app.route("/pdao_be/api/frozen", methods=["POST"], endpoint="api-frozen_post")
@login_required
def frozen():
    Frozen_flag = request.json.get("frozen", True)
    save_frozen(Frozen_flag)
    return jsonify({"Success": "True", "status": "True" if Frozen_flag else "False"})

def Initialize():
    try:
        load_config()
        load_accounts()
        load_runs()
        load_contest_metadata()
        load_status()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        exit(1)

Initialize()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
