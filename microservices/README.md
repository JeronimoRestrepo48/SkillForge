# SkillForge microservices (Flask)

This folder contains the Flask-based microservices migration implementation.

## Services

- `gateway` (port 8001)
- `auth-service` (port 8101)
- `catalog-service` (port 8102)
- `transactions-service` (port 8103)
- `auth-db` (PostgreSQL)
- `catalog-db` (PostgreSQL)
- `transactions-db` (PostgreSQL)

## Migrated API endpoints (gateway)

- `POST /api/token`
- `POST /api/token/refresh`
- `GET /api/me`
- `GET /api/categories`
- `GET /api/courses`
- `GET /api/courses/<id>`
- `GET /api/courses/<id>/modules`
- `POST /api/courses/<id>/rate`
- `GET /api/cart`
- `POST /api/cart/add`
- `POST /api/cart/remove`
- `POST /api/checkout/confirm`
- `POST /api/checkout/return`
- `GET /api/orders`

## Run

```bash
cd microservices
docker compose up --build
```

## Smoke test

```bash
curl http://127.0.0.1:8001/health
ACCESS=$(curl -s -X POST http://127.0.0.1:8001/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"estudiante","password":"estudiante123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")
curl -H "Authorization: Bearer $ACCESS" "http://127.0.0.1:8001/api/me"
curl -H "Authorization: Bearer $ACCESS" "http://127.0.0.1:8001/api/courses?page=1&page_size=2"
curl -H "Authorization: Bearer $ACCESS" -X POST "http://127.0.0.1:8001/api/cart/add" \
  -H "Content-Type: application/json" -d '{"course_id":2,"quantity":1}'
curl -H "Authorization: Bearer $ACCESS" -X POST "http://127.0.0.1:8001/api/checkout/confirm" \
  -H "Content-Type: application/json" -d '{}'
```

## Notes

- The gateway validates JWT access tokens against `auth-service` before forwarding protected endpoints.
- Each domain has its own database (database-per-service pattern).
- This migration focuses on API and business flow parity (JWT, catalog list/detail/modules/rating, cart, checkout, orders).
