import requests, sys

B = "http://localhost:8000"
S = "http://localhost:8002"
M = "http://localhost:8001"

errors = []


def check(name, condition, msg=""):
    if condition:
        print(f"  OK  {name}")
    else:
        print(f"  FAIL {name}: {msg}")
        errors.append(name)


# Health checks
for url, name in [(B, "Backend"), (S, "Simulator"), (M, "ML Service")]:
    try:
        r = requests.get(f"{url}/health", timeout=5)
        check(f"{name} /health", r.status_code == 200, r.status_code)
    except Exception as e:
        check(f"{name} /health", False, str(e))

# Auth
try:
    r = requests.post(f"{B}/auth/login", json={"username":"admin","password":"homeiq2026"})
    check("Auth login", r.status_code == 200, r.text)
    token = r.json().get("access_token", "")
    H = {"Authorization": f"Bearer {token}"}
except Exception as e:
    check("Auth login", False, str(e))
    token, H = "", {}

# Devices
if token:
    r = requests.get(f"{B}/devices", headers=H)
    check("GET /devices", r.status_code == 200, r.text[:100])

# ML classify
try:
    fv = {"hour_of_day":14,"weekday":1,"motion_hall":1,"motion_living":0,
          "temperature":22.0,"light_level":80.0,"tv_on":0,"minutes_idle":5}
    r = requests.post(f"{M}/classify", json=fv, timeout=10)
    check("ML /classify", r.status_code == 200 and r.json().get("scenario") in ["day","night","away","movie"], r.text[:100])
except Exception as e:
    check("ML /classify", False, str(e))

# Simulator devices
try:
    r = requests.get(f"{S}/devices")
    check("Simulator /devices", r.status_code == 200, r.text[:100])
except Exception as e:
    check("Simulator /devices", False, str(e))

print()
if errors:
    print(f"FAILED: {errors}")
    sys.exit(1)
else:
    print("ALL SMOKE TESTS PASSED")
