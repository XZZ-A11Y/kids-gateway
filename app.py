import json, os, hashlib, time, uuid
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "kids-gateway-2026"

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
DEVICES_FILE = os.path.join(DATA_DIR, "devices.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")


def init_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for f in [USERS_FILE, SESSIONS_FILE, DEVICES_FILE, LOGS_FILE]:
        if not os.path.exists(f):
            with open(f, "w") as fp:
                json.dump({}, fp)


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def now_ts():
    return int(time.time())


def today_str():
    return date.today().isoformat()


def device_fingerprint():
    ua = request.headers.get("User-Agent", "")
    ip = request.remote_addr or ""
    return hashlib.md5(f"{ua}|{ip}".encode()).hexdigest()[:12]


def log_action(action, detail="", user="unknown"):
    logs = load_json(LOGS_FILE)
    logs[str(uuid.uuid4())[:8]] = {
        "ts": now_ts(), "action": action, "detail": detail,
        "user": user, "ip": request.remote_addr,
    }
    if len(logs) > 500:
        keys = sorted(logs.keys(), key=lambda k: logs[k]["ts"])
        for k in keys[:len(logs) - 500]:
            del logs[k]
    save_json(LOGS_FILE, logs)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    init_files()
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    try:
        duration = int(data.get("duration", 60))
    except (ValueError, TypeError):
        return jsonify({"ok": False, "msg": "请输入有效的分钟数"}), 400
    if duration <= 0:
        return jsonify({"ok": False, "msg": "请输入大于 0 的分钟数"}), 400

    users = load_json(USERS_FILE)
    if not users:
        users["小猪猪"] = {"password": "ZhuZhu@2026", "daily_quota": 180,
                          "used_today": 0, "last_date": today_str()}
        save_json(USERS_FILE, users)

    if username not in users or users[username]["password"] != password:
        log_action("login_failed", f"user={username}", username)
        return jsonify({"ok": False, "msg": "账号或密码错误"}), 401

    user = users[username]
    if user.get("last_date") != today_str():
        user["used_today"] = 0
        user["last_date"] = today_str()
    if user["used_today"] >= user.get("daily_quota", 180):
        return jsonify({"ok": False, "msg": "今日上网时长已用完，明天再来吧！"}), 403

    sessions = load_json(SESSIONS_FILE)
    dev_id = device_fingerprint()
    token = str(uuid.uuid4())
    expire = now_ts() + duration * 60
    sessions[token] = {"user": username, "expire": expire,
                       "device_id": dev_id, "created": now_ts()}
    save_json(SESSIONS_FILE, sessions)

    devices = load_json(DEVICES_FILE)
    devices[dev_id] = {"user": username,
                       "ua": request.headers.get("User-Agent", ""),
                       "ip": request.remote_addr, "last_seen": now_ts()}
    save_json(DEVICES_FILE, devices)

    log_action("login_success", f"duration={duration}min", username)
    return jsonify({"ok": True, "token": token, "expire": expire})


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.json or {}
    token = data.get("token", "")
    sess = load_json(SESSIONS_FILE).get(token)
    if not sess or sess["expire"] < now_ts():
        return jsonify({"ok": False, "msg": "会话已过期"})
    return jsonify({"ok": True, "expire": sess["expire"], "user": sess["user"]})


@app.route("/api/renew", methods=["POST"])
def api_renew():
    data = request.json or {}
    token = data.get("token", "")
    try:
        extra = int(data.get("extra", 10))
    except (ValueError, TypeError):
        return jsonify({"ok": False, "msg": "请输入有效的分钟数"}), 400
    if extra <= 0:
        return jsonify({"ok": False, "msg": "请输入大于 0 的分钟数"}), 400
    sessions = load_json(SESSIONS_FILE)
    if token not in sessions:
        return jsonify({"ok": False, "msg": "无效会话"}), 404
    sessions[token]["expire"] += extra * 60
    save_json(SESSIONS_FILE, sessions)
    log_action("renew", f"+{extra}min", sessions[token]["user"])
    return jsonify({"ok": True, "expire": sessions[token]["expire"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    data = request.json or {}
    token = data.get("token", "")
    user = load_json(SESSIONS_FILE).get(token, {}).get("user", "unknown")
    sessions = load_json(SESSIONS_FILE)
    if token in sessions:
        del sessions[token]
        save_json(SESSIONS_FILE, sessions)
    log_action("logout", "", user)
    return jsonify({"ok": True})


ADMIN_PASS = "Parent@2026"


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    if (request.json or {}).get("password") == ADMIN_PASS:
        session["admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401


def admin_required():
    return session.get("admin")


@app.route("/api/admin/sessions")
def admin_sessions():
    if not admin_required():
        return jsonify({"ok": False}), 403
    return jsonify(load_json(SESSIONS_FILE))


@app.route("/api/admin/devices")
def admin_devices():
    if not admin_required():
        return jsonify({"ok": False}), 403
    return jsonify(load_json(DEVICES_FILE))


@app.route("/api/admin/logs")
def admin_logs():
    if not admin_required():
        return jsonify({"ok": False}), 403
    return jsonify(load_json(LOGS_FILE))


@app.route("/api/admin/kick", methods=["POST"])
def admin_kick():
    if not admin_required():
        return jsonify({"ok": False}), 403
    token = (request.json or {}).get("token", "")
    sessions = load_json(SESSIONS_FILE)
    if token in sessions:
        del sessions[token]
        save_json(SESSIONS_FILE, sessions)
        log_action("admin_kick", f"token={token[:8]}")
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_files()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
