#!/usr/bin/env bash
# Despliegue SkillForge en EC2 desde tu máquina local.
# Uso: ./scripts/deploy-ec2.sh [usuario@host] [perfil]
# Ejemplo core (monolito+strangler): ./scripts/deploy-ec2.sh ec2-user@ec2-54-242-178-107.compute-1.amazonaws.com core
# Stack completo: ./scripts/deploy-ec2.sh ec2-user@ec2-54-242-178-107.compute-1.amazonaws.com microservices

set -euo pipefail

TARGET="${1:-ec2-user@ec2-54-242-178-107.compute-1.amazonaws.com}"
PROFILE="${2:-microservices}"
KEY="${SSH_KEY:-$HOME/.ssh/jeronimo.pem}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${TARGET#*@}"

SSH_OPTS=(-i "$KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new)

echo "==> Sync código a $TARGET"
rsync -avz --delete \
  -e "ssh ${SSH_OPTS[*]}" \
  --exclude '.git' --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'db.sqlite3' --exclude 'staticfiles' --exclude 'logs/*.log' \
  --exclude '.env' --exclude 'media/' \
  "$ROOT/" "$TARGET:~/skillforge/"

SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

echo "==> .env en servidor"
ssh "${SSH_OPTS[@]}" "$TARGET" "cat > ~/skillforge/.env << EOF
SECRET_KEY=${SECRET}
DEBUG=False
ALLOWED_HOSTS=${HOST},localhost,127.0.0.1,nginx,*
DATABASE_URL=postgres://skillforge:skillforge@db:5432/skillforge
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=false
ALLY_SERVICE_URL=
FRANKFURTER_API_URL=https://api.frankfurter.dev
EOF
mkdir -p ~/skillforge/logs"

echo "==> Nginx config (perfil: $PROFILE)"
if [[ "$PROFILE" == "core" ]]; then
  ssh "${SSH_OPTS[@]}" "$TARGET" "cp ~/skillforge/nginx.core.conf ~/skillforge/nginx.conf"
else
  ssh "${SSH_OPTS[@]}" "$TARGET" "test -f ~/skillforge/nginx.conf.bak || cp ~/skillforge/nginx.conf ~/skillforge/nginx.conf.bak 2>/dev/null; true"
fi

echo "==> Limpiar contenedores previos (evita OOM por stacks duplicados)"
ssh "${SSH_OPTS[@]}" "$TARGET" "cd ~/skillforge && sg docker -c 'docker compose -f docker-compose.yml -f docker-compose.aws.yml --profile core --profile microservices down --remove-orphans 2>/dev/null || true'"

echo "==> Docker Compose (perfil: $PROFILE)"
ssh "${SSH_OPTS[@]}" "$TARGET" "cd ~/skillforge && sg docker -c 'docker compose -f docker-compose.yml -f docker-compose.aws.yml --profile ${PROFILE} up -d --build'"

echo "==> Estado"
ssh "${SSH_OPTS[@]}" "$TARGET" "cd ~/skillforge && sg docker -c 'docker compose ps'"

echo "==> Smoke tests"
curl -sf "http://${HOST}/health" && echo " OK /health"
curl -sf "http://${HOST}/api/integration/skillforge/public/" | head -c 120 && echo "..."

echo "Listo: http://${HOST}/"
