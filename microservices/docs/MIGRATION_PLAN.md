# Migration plan: Django monolith -> Flask microservices

This branch now includes a full working migration for core backend API flows in `microservices/`.

## Domain split

- `auth-service`: users, profile, auth/session/JWT responsibilities.
- `catalog-service`: categories, courses, modules, ratings.
- `transactions-service`: cart, checkout, orders, invoices.
- `gateway`: single public entry point that routes to internal services.

## Implemented migration scope

- Flask apps, Dockerfiles, and service-level persistence for each service.
- Docker Compose orchestration for local development with 3 PostgreSQL databases.
- Gateway reverse proxy endpoints:
  - Auth: `POST /api/token`, `POST /api/token/refresh`, `GET /api/me`
  - Catalog: `GET /api/categories`, `GET /api/courses`, `GET /api/courses/<id>`, `GET /api/courses/<id>/modules`, `POST /api/courses/<id>/rate`
  - Transactions: `GET /api/cart`, `POST /api/cart/add`, `POST /api/cart/remove`, `POST /api/checkout/confirm`, `POST /api/checkout/return`, `GET /api/orders`
- Health checks:
  - `GET /health` on each service
  - `GET /health` on gateway with upstream checks
- JWT:
  - Issued/refresh in `auth-service`
  - Validated by gateway through `auth-service /api/auth/verify`
  - User identity propagated downstream through headers

## Pending optional improvements

1. Replace plain-text development credentials with password hashing (bcrypt/argon2) and secrets manager.
2. Add Alembic migration scripts (currently using SQLAlchemy `create_all` bootstrap for local development).
3. Add asynchronous domain events for cross-service workflows (enrollment, notifications, analytics).
4. Move remaining server-rendered web pages to a standalone frontend consuming gateway APIs.

## Run locally

```bash
cd microservices
docker compose up --build
```

Gateway base URL: `http://127.0.0.1:8001`
