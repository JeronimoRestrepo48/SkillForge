# SkillForge

**Forja tu Futuro Profesional** — Marketplace de cursos en línea con roles Estudiante, Instructor y Administrador.

Esta plataforma ha sido refactorizada recientemente para migrar desde un monolito en Django hacia una **Arquitectura de Microservicios orientada a eventos** con un **Frontend moderno en React (Vite)**.

---

## Índice

- [Arquitectura Actual](#arquitectura-actual)
- [Tecnologías Principales](#tecnologías-principales)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Ejecución Rápida con Docker Compose](#ejecución-rápida-con-docker-compose)
- [Comandos Útiles](#comandos-útiles)
- [Documentación Adicional](#documentación-adicional)

---

## Arquitectura Actual

El sistema opera bajo un entorno completamente contenerizado orquestado por `docker-compose`. Cuenta con un **API Gateway (Nginx)** que enruta el tráfico entre el cliente web y los microservicios backend.

La comunicación asíncrona entre microservicios se maneja mediante un **Event Bus basado en Redis Streams**.

### Microservicios:
1. **Auth Service**: Autenticación, autorización (JWT), gestión de usuarios y roles.
2. **Catalog Service**: Gestión de cursos, módulos, lecciones, categorías y valoraciones.
3. **Transactions Service**: Carrito de compras, procesamiento de pagos (Wompi simulado), inscripciones de estudiantes.
4. **Certificate Service**: Generación asíncrona de diplomas en PDF usando **Celery**, reaccionando a eventos del bus.

---

## Tecnologías Principales

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query & Axios
- React Router DOM
- React Hook Form

**Backend:**
- Python 3.12 (imágenes slim)
- FastAPI
- SQLAlchemy + Alembic (PostgreSQL)
- Celery (Workers asíncronos)
- PyJWT

**Infraestructura:**
- Docker & Docker Compose
- Nginx (API Gateway)
- Redis (Caché, Event Bus y Broker para Celery)
- PostgreSQL (Una base de datos por microservicio)

---

## Estructura del Proyecto

```text
SkillForge/
├── frontend/                               # Aplicación React web
│   ├── src/
│   │   ├── api/                            # Clientes HTTP (Axios) para microservicios
│   │   ├── components/                     # Componentes reusables de UI
│   │   ├── pages/                          # Páginas y vistas principales
│   │   └── ...
├── microservices/
│   └── services/
│       ├── auth-service/                   # Servicio de autenticación
│       ├── catalog-service/                # Servicio de cursos y contenido
│       ├── transactions-service/           # Servicio de pagos y enrollments
│       └── certificate-service/            # Servicio generador de certificados
├── shared/                                 # Librerías compartidas (Event Bus, tareas)
├── nginx.conf                              # Reglas de enrutamiento del API Gateway
├── docker-compose.yml                      # Orquestación de infraestructura local
└── README.md                               # Este archivo
```

---

## Requisitos Previos

- **Docker** y **Docker Compose** instalados en tu sistema.
- Puertos `80` (HTTP), `5432` (PostgreSQL), y `6379` (Redis) disponibles en tu máquina local.

---

## Ejecución Rápida con Docker Compose

La forma más sencilla de levantar todo el ecosistema es mediante Docker Compose.

```bash
# Construir y levantar todos los contenedores en segundo plano
docker-compose up -d --build
```

Esto levantará:
- Bases de datos PostgreSQL individuales para cada servicio.
- El servidor Redis.
- Los microservicios (`auth-service`, `catalog-service`, `transactions-service`, `certificate-service`).
- Los workers asíncronos de Celery (`worker-documents`, `worker-notifications`).
- El frontend web.
- El API Gateway Nginx exponiendo el puerto `80`.

**Acceso a la plataforma:**
Una vez todo esté corriendo, abre tu navegador en:  
👉 **[http://localhost](http://localhost)**

### Inicialización de Bases de Datos (Seeds)

El repositorio incluye copias (dumps SQL) de las bases de datos en la carpeta `db_seeds/`. 
Si es la **primera vez** que clonas el proyecto o necesitas sincronizar tu base de datos con la versión del repositorio, asegúrate de destruir los volúmenes antiguos y volver a construir el entorno:

```bash
# 1. Detener servicios y eliminar bases de datos actuales en blanco/desactualizadas
docker-compose down -v

# 2. Volver a construir el entorno. Docker inyectará los archivos SQL automáticamente
docker-compose up -d --build
```

---

## Comandos Útiles

**Ver logs de los servicios:**
```bash
# Todos los logs
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f catalog-service
docker-compose logs -f worker-documents
```

**Reiniciar un servicio luego de aplicar cambios:**
```bash
docker-compose up -d --build frontend
docker-compose restart catalog-service
```

**Apagar el entorno:**
```bash
# Detiene los contenedores sin borrar las bases de datos (volúmenes)
docker-compose down

# Detiene todo y ELIMINA los datos (reset completo)
docker-compose down -v
```

---

## Documentación Adicional

- Las rutas de la API están prefijadas según el servicio. Puedes explorar la documentación interactiva (Swagger) de cada servicio en:
  - Auth: `http://localhost/api/auth/docs`
  - Catalog: `http://localhost/api/catalog/docs`
  - Transactions: `http://localhost/api/transactions/docs`
