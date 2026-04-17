from flask import Flask, jsonify, request

app = Flask(__name__)


def _normalize_items(payload):
    items = payload.get("items", [])
    if not isinstance(items, list) or not items:
        raise ValueError("Field 'items' must be a non-empty array.")

    normalized = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"items[{idx}] must be an object.")

        qty = item.get("quantity")
        unit_price = item.get("unit_price")

        if not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"items[{idx}].quantity must be a positive integer.")
        if not isinstance(unit_price, (int, float)) or unit_price < 0:
            raise ValueError(f"items[{idx}].unit_price must be a non-negative number.")

        normalized.append({"quantity": qty, "unit_price": float(unit_price)})
    return normalized


def _apply_coupon(subtotal, coupon_code):
    if not coupon_code:
        return 0.0

    coupon_code = coupon_code.strip().upper()
    rules = {
        "WELCOME10": 0.10,
        "STUDENT15": 0.15,
    }
    percentage = rules.get(coupon_code)
    if percentage is None:
        raise ValueError("Coupon code is invalid.")
    return round(subtotal * percentage, 2)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/v2/checkout/quote", methods=["POST"])
def checkout_quote():
    try:
        payload = request.get_json(silent=True) or {}
        items = _normalize_items(payload)

        subtotal = round(sum(i["quantity"] * i["unit_price"] for i in items), 2)
        discounts = _apply_coupon(subtotal, payload.get("coupon_code"))
        total = round(max(subtotal - discounts, 0), 2)

        return (
            jsonify(
                {
                    "version": "v2",
                    "engine": "flask-microservice",
                    "items_count": len(items),
                    "subtotal": subtotal,
                    "discounts": discounts,
                    "total": total,
                    "currency": "COP",
                }
            ),
            200,
        )
    except ValueError as exc:
        return (
            jsonify(
                {
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": str(exc),
                    }
                }
            ),
            400,
        )
    except Exception:
        return (
            jsonify(
                {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error while calculating quote.",
                    }
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
