import subprocess, time, requests, sys, os

# 清理旧数据
for f in ["users.json", "sessions.json", "devices.json", "logs.json"]:
    path = os.path.join("data", f)
    if os.path.exists(path):
        os.remove(path)

proc = subprocess.Popen(["python", "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
base = "http://127.0.0.1:5000"
passes = 0

def check(name, cond):
    global passes
    print(f"{'✅' if cond else '❌'} {name}")
    if cond:
        passes += 1

try:
    r = requests.post(f"{base}/api/login", json={"username": "小猪猪", "password": "wrong", "duration": 30})
    check("错误密码拦截", r.status_code == 401)

    r = requests.post(f"{base}/api/login", json={"username": "小猪猪", "password": "ZhuZhu@2026", "duration": 60})
    check("正确登录", r.status_code == 200 and r.json().get("ok"))
    token = r.json()["token"]

    r = requests.post(f"{base}/api/check", json={"token": token})
    check("会话校验", r.json().get("ok"))

    expire_before = r.json()["expire"]
    time.sleep(1)
    r = requests.post(f"{base}/api/renew", json={"token": token, "extra": 10})
    check("续期 +10 分钟", r.json().get("ok") and r.json()["expire"] > expire_before)

    r = requests.post(f"{base}/api/login", json={"username": "小猪猪", "password": "ZhuZhu@2026", "duration": 0})
    check("非法时长(0) 拦截", r.status_code == 400)

    r = requests.get(f"{base}/api/admin/sessions")
    check("管理员接口鉴权", r.status_code == 403)

    s = requests.Session()
    r = s.post(f"{base}/api/admin/login", json={"password": "Parent@2026"})
    check("管理员登录", r.json().get("ok"))

    r = s.get(f"{base}/api/admin/logs")
    check("查看操作日志", r.status_code == 200 and len(r.json()) >= 1)

    r = requests.post(f"{base}/api/logout", json={"token": token})
    check("注销", r.json().get("ok"))

    print(f"\n通过 {passes}/9")
    sys.exit(0 if passes == 9 else 1)
finally:
    proc.terminate()
