"""
E2E Integration Test — SkillForge microservices
Flow: auth/token → auth/me → catalog/courses → catalog/categories → transactions/cart → transactions/orders
"""
import urllib.request
import json
import sys

AUTH_BASE = "http://auth-service:8000/api/auth"
CATALOG_BASE = "http://catalog-service:8000/api/catalog"
TRANS_BASE = "http://transactions-service:8000/api/transactions"

PASS = "✓"
FAIL = "✗"
results = []


def do_get(url, token=None):
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=hdrs)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()), resp.status


def do_post(url, data, token=None):
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers=hdrs)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()), resp.status


TOKEN = None

# ── 1. POST /auth/token ──────────────────────────────────
try:
    body = json.dumps({"username": "estudiante", "password": "estudiante123"}).encode()
    req = urllib.request.Request(
        f"{AUTH_BASE}/token", data=body, method="POST",
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    tokens = json.loads(resp.read())
    TOKEN = tokens["access"]
    print(f"[1] {PASS}  AUTH  POST /token        — JWT obtenido")
    results.append(True)
except Exception as e:
    print(f"[1] {FAIL}  AUTH  POST /token        — {e}")
    results.append(False)

# ── 2. GET /auth/me ───────────────────────────────────────
try:
    me, status = do_get(f"{AUTH_BASE}/me", TOKEN)
    print(f"[2] {PASS}  AUTH  GET  /me           — user={me['username']} role={me['role']}")
    results.append(True)
except Exception as e:
    print(f"[2] {FAIL}  AUTH  GET  /me           — {e}")
    results.append(False)

# ── 3. GET /catalog/courses/ ──────────────────────────────
try:
    data, _ = do_get(f"{CATALOG_BASE}/courses/", TOKEN)
    count = data.get("count", len(data))
    first = data["results"][0]["title"] if "results" in data else data[0]["title"]
    print(f"[3] {PASS}  CATALOG GET /courses/    — count={count} first='{first}'")
    results.append(True)
except Exception as e:
    print(f"[3] {FAIL}  CATALOG GET /courses/    — {e}")
    results.append(False)

# ── 4. GET /catalog/categories/ ───────────────────────────
try:
    cats, _ = do_get(f"{CATALOG_BASE}/categories/", TOKEN)
    n = len(cats)
    print(f"[4] {PASS}  CATALOG GET /categories/ — count={n}")
    results.append(True)
except Exception as e:
    print(f"[4] {FAIL}  CATALOG GET /categories/ — {e}")
    results.append(False)

# ── 5. GET /transactions/cart ─────────────────────────────
try:
    cart, _ = do_get(f"{TRANS_BASE}/cart", TOKEN)
    items = cart.get("items", cart) if isinstance(cart, dict) else cart
    n = len(items) if isinstance(items, list) else items
    print(f"[5] {PASS}  TRANS   GET /cart        — items={n}")
    results.append(True)
except Exception as e:
    print(f"[5] {FAIL}  TRANS   GET /cart        — {e}")
    results.append(False)

# ── 6. GET /transactions/orders ───────────────────────────
try:
    orders, _ = do_get(f"{TRANS_BASE}/orders", TOKEN)
    n = len(orders) if isinstance(orders, list) else orders.get("count", 0)
    print(f"[6] {PASS}  TRANS   GET /orders      — orders={n}")
    results.append(True)
except Exception as e:
    print(f"[6] {FAIL}  TRANS   GET /orders      — {e}")
    results.append(False)

# ── Resumen ───────────────────────────────────────────────
passed = sum(results)
total = len(results)
print()
print("=" * 55)
if passed == total:
    print(f"  E2E TEST PASSED  ✓  {passed}/{total} checks OK")
else:
    print(f"  E2E TEST FAILED  ✗  {passed}/{total} checks OK")
print("=" * 55)
sys.exit(0 if passed == total else 1)
