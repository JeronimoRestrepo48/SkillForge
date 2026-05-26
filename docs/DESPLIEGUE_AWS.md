# Despliegue en AWS Academy (Entregable 2)

Guía para desplegar el ecosistema híbrido SkillForge en una instancia **EC2** de AWS Academy usando **Docker Compose** y **Nginx** como API Gateway.

## Arquitectura desplegada

| Componente | Rol |
|------------|-----|
| **nginx** (puerto 80) | API Gateway / reverse proxy |
| **web_django** | Monolito (UI + integración + `/api/v1`, `/api/integration`) |
| **checkout_flask** | Strangler: cotización `/api/v2/checkout/quote` |
| **gateway** + microservicios | API migrada (`/api/token`, `/api/courses`, carrito, checkout, órdenes) |
| **PostgreSQL** | BD monolito + 3 BD por microservicio |
| **Redis** | Broker Celery + caché |
| **celery_worker** | Notificaciones y reportes asíncronos |

## 1. Preparar la instancia EC2 (AWS Academy)

1. Inicia sesión en **AWS Academy Learner Lab** y abre la consola EC2.
2. Lanza una instancia **Amazon Linux 2023** o **Ubuntu 22.04** (t2.medium o superior recomendado).
3. Security Group: permite **SSH (22)** y **HTTP (80)** desde `0.0.0.0/0` (o el rango que indique el profesor).
4. Asocia una **Elastic IP** y anótala (la entregarás en la plataforma institucional).

## 2. Instalar Docker en la EC2

**Amazon Linux 2023:**

```bash
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
```

Cierra sesión SSH y vuelve a entrar para aplicar el grupo `docker`.

Instala Docker Compose plugin:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version
```

## 3. Clonar el repositorio

```bash
cd ~
git clone <URL_DE_TU_REPOSITORIO> skillforge
cd skillforge/Proyecto/desarrollo
```

Usa la rama **main** que indique la entrega.

## 4. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` (o exporta variables antes de `docker compose up`):

```bash
# Obligatorio en AWS: dominio o IP elástica
ALLOWED_HOSTS=localhost,127.0.0.1,<TU_ELASTIC_IP>,nginx

# Clave segura (generar con python -c "import secrets; print(secrets.token_hex(50))")
SECRET_KEY=<clave-generada>

# Equipo aliado (IP elástica del otro equipo, sin barra final)
ALLY_SERVICE_URL=http://<IP_ALIADO>
ALLY_SERVICE_PUBLIC_PATH=api/integration/skillforge/public/
```

En `docker-compose.yml` ya están definidos `REDIS_URL`, `CELERY_BROKER_URL` y `DATABASE_URL` para los contenedores.

## 5. Levantar el stack

```bash
docker compose up -d --build
```

La primera ejecución puede tardar varios minutos (build de imágenes + migraciones).

Verifica contenedores:

```bash
docker compose ps
docker compose logs -f nginx
```

## 6. Pruebas de humo (desde tu PC o la EC2)

Sustituye `<IP>` por tu Elastic IP.

```bash
# Salud del monolito (vía Nginx)
curl http://<IP>/health

# Servicio a proveer (JSON público)
curl http://<IP>/api/integration/skillforge/public/

# Strangler Flask v2
curl -X POST http://<IP>/api/v2/checkout/quote \
  -H "Content-Type: application/json" \
  -d '{"items":[{"quantity":1,"unit_price":100000}],"coupon_code":"WELCOME10"}'

# Microservicios (JWT)
ACCESS=$(curl -s -X POST http://<IP>/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"estudiante","password":"estudiante123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")
curl -H "Authorization: Bearer $ACCESS" http://<IP>/api/me
curl -H "Authorization: Bearer $ACCESS" "http://<IP>/api/courses?page=1&page_size=2"

# Tipo de cambio (Adapter + API terceros)
curl "http://<IP>/api/integration/exchange-rate/?base=USD&target=COP"
```

**UI:** `http://<IP>/` — login `estudiante` / `estudiante123`. Hub de integración: `http://<IP>/integration/hub/`.

## 7. Celery (tareas asíncronas)

Tras confirmar un pago, el worker encola notificaciones y reportes:

```bash
docker compose logs -f celery_worker
```

## 8. Entrega institucional

1. Repositorio (rama **main**) en la plataforma del curso.
2. **Elastic IP** de la EC2 con la instancia **encendida** para la sustentación.
3. Cada integrante debe tener **commits** visibles en el historial.

## 9. Solución de problemas

| Síntoma | Acción |
|---------|--------|
| 502 Bad Gateway | `docker compose ps` — espera healthchecks de `auth-service`, `catalog-service`, `gateway`. |
| DisallowedHost | Añade la Elastic IP a `ALLOWED_HOSTS` y reinicia: `docker compose up -d web_django`. |
| Ally mock en hub | Configura `ALLY_SERVICE_URL` con la IP del equipo aliado y reinicia Django. |
| API 401 en microservicios | Usuarios seed: `estudiante`/`estudiante123` (creados en auth-service al arrancar). |

## 10. Detener / actualizar

```bash
docker compose down
git pull
docker compose up -d --build
```

Para liberar volúmenes (borra datos): `docker compose down -v` (solo en entornos de prueba).
