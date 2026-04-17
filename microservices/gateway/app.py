import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8101")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8102")
TRANSACTIONS_SERVICE_URL = os.getenv("TRANSACTIONS_SERVICE_URL", "http://localhost:8103")


def _verify_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"detail": "Authentication credentials were not provided."}), 401)
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL.rstrip('/')}/api/auth/verify",
            headers={"Authorization": auth_header},
            timeout=5,
        )
    except requests.RequestException:
        return None, (jsonify({"detail": "Auth service unavailable"}), 503)
    if response.status_code != 200:
        return None, (jsonify(response.json()), response.status_code)
    return response.json(), None


def _proxy(base_url: str, endpoint: str, method: str = "GET", require_auth: bool = True):
    upstream = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    upstream_headers = {}
    if require_auth:
        claims, error = _verify_token()
        if error is not None:
            return error
        upstream_headers["X-User-Id"] = str(claims["user_id"])
        upstream_headers["X-Username"] = str(claims["username"])
        upstream_headers["X-Role"] = str(claims["role"])
    elif request.headers.get("Authorization"):
        upstream_headers["Authorization"] = request.headers.get("Authorization")
    kwargs = {"timeout": 10}
    if method == "GET":
        kwargs["params"] = request.args
        kwargs["headers"] = upstream_headers
        resp = requests.get(upstream, **kwargs)
    else:
        kwargs["params"] = request.args
        kwargs["json"] = request.get_json(silent=True) or {}
        kwargs["headers"] = upstream_headers
        resp = requests.post(upstream, **kwargs)
    return jsonify(resp.json()), resp.status_code


@app.get("/health")
def health():
    checks = {}
    status_code = 200
    for name, url in {
        "auth": AUTH_SERVICE_URL,
        "catalog": CATALOG_SERVICE_URL,
        "transactions": TRANSACTIONS_SERVICE_URL,
    }.items():
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            checks[name] = "ok" if resp.status_code == 200 else "error"
            if resp.status_code != 200:
                status_code = 503
        except requests.RequestException:
            checks[name] = "down"
            status_code = 503

    return jsonify({"status": "ok" if status_code == 200 else "degraded", "checks": checks}), status_code


@app.get("/api/me")
def api_me():
    return _proxy(AUTH_SERVICE_URL, "/api/me", require_auth=False)


@app.post("/api/token")
def api_token():
    return _proxy(AUTH_SERVICE_URL, "/api/token", method="POST", require_auth=False)


@app.post("/api/token/refresh")
def api_token_refresh():
    return _proxy(AUTH_SERVICE_URL, "/api/token/refresh", method="POST", require_auth=False)


@app.get("/api/courses")
def api_courses():
    return _proxy(CATALOG_SERVICE_URL, "/api/courses")


@app.get("/api/categories")
def api_categories():
    return _proxy(CATALOG_SERVICE_URL, "/api/categories")


@app.get("/api/courses/<int:course_id>")
def api_course_detail(course_id: int):
    return _proxy(CATALOG_SERVICE_URL, f"/api/courses/{course_id}")


@app.get("/api/courses/<int:course_id>/modules")
def api_course_modules(course_id: int):
    return _proxy(CATALOG_SERVICE_URL, f"/api/courses/{course_id}/modules")


@app.post("/api/courses/<int:course_id>/rate")
def api_course_rate(course_id: int):
    return _proxy(CATALOG_SERVICE_URL, f"/api/courses/{course_id}/rate", method="POST")


@app.get("/api/orders")
def api_orders():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/orders")


@app.get("/api/cart")
def api_cart():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/cart")


@app.post("/api/cart/add")
def api_cart_add():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/cart/add", method="POST")


@app.post("/api/cart/remove")
def api_cart_remove():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/cart/remove", method="POST")


@app.post("/api/checkout/confirm")
def api_checkout_confirm():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/checkout/confirm", method="POST")


@app.post("/api/checkout/return")
def api_checkout_return():
    return _proxy(TRANSACTIONS_SERVICE_URL, "/api/checkout/return", method="POST")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
