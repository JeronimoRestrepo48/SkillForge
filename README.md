# SkillForge — Desarrollo

**Forja tu Futuro Profesional** — Marketplace de cursos en línea con roles Estudiante, Instructor y Administrador.

---

## Índice

- [Requisitos](#requisitos)
- [Instalación rápida](#instalación-rápida)
- [Variables de entorno y configuración](#variables-de-entorno-y-configuración)
- [Credenciales por defecto](#credenciales-por-defecto)
- [Ejecución](#ejecución)
- [Rutas principales (URLs)](#rutas-principales-urls)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Comandos de gestión](#comandos-de-gestión)
- [Tests](#tests)
- [Documentación adicional](#documentación-adicional)
- [Producción](#producción)

---

## Requisitos

- **Python** 3.10 o superior
- **pip** (gestor de paquetes)
- Opcional: **venv** o **virtualenv** para entorno virtual

---

## Instalación rápida

```bash
# 1. Clonar o entrar en la carpeta del proyecto
cd desarrollo

# 2. Crear y activar entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar variables de entorno y ajustar si hace falta
cp .env.example .env
# Editar .env: al menos SECRET_KEY en producción (en desarrollo puede quedarse el de ejemplo)

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear datos iniciales (categorías, cursos, usuarios de prueba)
python manage.py crear_datos_iniciales

# 7. Arrancar el servidor
python manage.py runserver
```

Abre **http://127.0.0.1:8000**. La ruta raíz (`/`) es la pantalla de **login**; necesitas autenticarte para acceder al resto de la aplicación.

---

## Variables de entorno y configuración

Todas las variables se definen en el archivo **`.env`** en la raíz de `desarrollo/`. Puedes copiar **`.env.example`** como plantilla:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por defecto (si no se usa .env) |
|----------|-------------|--------------------------------------|
| `SECRET_KEY` | Clave secreta de Django (sesiones, CSRF, etc.) | `dev-key-change-in-production` |
| `DEBUG` | Modo debug (no usar `True` en producción) | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL de base de datos | SQLite: `sqlite:///db.sqlite3` |
| `DEFAULT_FROM_EMAIL` | Remitente por defecto de correos | `noreply@skillforge.local` |

- **Desarrollo**: el módulo de settings por defecto es `config.settings.development` (definido en `manage.py` y `config/wsgi.py`). En desarrollo el correo se envía a consola (`EMAIL_BACKEND = console`).
- **Generar una SECRET_KEY segura** (producción):
  ```bash
  python -c "import secrets; print(secrets.token_hex(50))"
  ```
- Detalle de cada variable y ejemplos para PostgreSQL están en **`.env.example`** y en ** [docs/CONFIGURACION.md](docs/CONFIGURACION.md)**.

---

## Credenciales por defecto

Después de ejecutar **`python manage.py crear_datos_iniciales`** quedan creados los siguientes usuarios. **No uses estas contraseñas en producción.**

### Usuarios principales (3 roles)

| Usuario      | Contraseña     | Rol            | Uso |
|--------------|----------------|----------------|-----|
| **estudiante** | `estudiante123` | Estudiante     | Home, Cursos, Mis cursos, Certificaciones, Carrito, Checkout, Mis pedidos |
| **instructor** | `instructor123` | Instructor     | Home, Gestionar cursos, Crear/editar curso, Módulos y lecciones |
| **admin**      | `admin123`      | Administrador  | Home, Panel de administración en `/panel/` |

### Instructores de ejemplo (con cursos asignados)

| Usuario      | Contraseña      |
|--------------|-----------------|
| **instructor1** | `instructor1123` |
| **instructor2** | `instructor2123` |
| **instructor3** | `instructor3123` |

El comando `crear_datos_iniciales` también crea categorías, cursos publicados y al menos un módulo con lecciones por curso. El **admin** puede acceder al panel Django en **http://127.0.0.1:8000/admin/** (mismo usuario/contraseña: `admin` / `admin123`).

---

## Ejecución

```bash
python manage.py runserver
```

- URL local: **http://127.0.0.1:8000**
- La raíz **`/`** muestra el **login**. Tras iniciar sesión se redirige a **`/home/`**.
- Archivos estáticos y media se sirven en modo DEBUG; en producción hay que usar un servidor de archivos estáticos y configurar `STATIC_ROOT` / `MEDIA_ROOT`.

---

## Rutas principales (URLs)

Prefijo base: `http://127.0.0.1:8000`.

### Core (login, home, panel)

| Ruta | Nombre | Descripción |
|------|--------|-------------|
| `/` | Login | Inicio de sesión |
| `/register/` | Registro | Alta Estudiante/Instructor |
| `/logout/` | Cierre de sesión | |
| `/home/` | Landing | Página principal tras login |
| `/panel/` | Panel admin | Solo administradores |
| `/health/` | Health check | Comprobación de servicio |

### Catálogo (`/courses/`)

| Ruta | Descripción |
|------|-------------|
| `/courses/` | Listado de cursos |
| `/courses/<id>/` | Detalle del curso |
| `/courses/my-courses/` | Mis inscripciones |
| `/courses/my-certificates/` | Mis certificados |
| `/courses/<id>/learn/` | Aprender (módulos/lecciones) |
| `/courses/<id>/learn/lesson/<id_leccion>/` | Detalle de lección, marcar completada |
| `/courses/create/` | Crear curso (instructor) |
| `/courses/manage/` | Gestionar mis cursos (instructor) |
| `/courses/<id>/modules/` | Módulos del curso |
| `/courses/certificaciones-industria/` | Certificaciones de industria |
| `/courses/certificaciones-industria/<slug>/` | Detalle certificación, comprar acceso, examen, diploma |

### Carrito y transacciones (`/cart/`)

| Ruta | Descripción |
|------|-------------|
| `/cart/` | Ver carrito |
| `/cart/add/<curso_id>/` | Añadir curso al carrito |
| `/cart/remove/<curso_id>/` | Quitar curso del carrito |
| `/cart/add-certificacion/<slug>/` | Añadir certificación al carrito |
| `/cart/remove-certificacion/<slug>/` | Quitar certificación del carrito |
| `/cart/checkout/` | Resumen y datos de pago |
| `/cart/checkout/confirm/` | Crear orden pendiente y redirigir a pasarela |
| `/cart/checkout/gateway/` | Pasarela de pago simulada (Pagar / Fallar / Cancelar) |
| `/cart/checkout/return/` | Retorno desde pasarela (éxito/fallo/cancelado) |
| `/cart/checkout/continue/<numero>/` | Completar pago de una orden pendiente (“Complete payment”) |
| `/cart/orders/` | Mis pedidos |
| `/cart/order/<numero>/` | Detalle de orden confirmada |
| `/cart/order/<numero>/invoice/` | Factura PDF |
| `/cart/order/<numero>/cancel/` | Cancelar orden |

### Usuario (`/my-account/`)

| Ruta | Descripción |
|------|-------------|
| `/my-account/` | Mi cuenta / perfil |
| `/my-account/edit/` | Editar perfil |

### API (JWT)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/api/token/` | POST | Obtener access + refresh (body: `username`, `password`) |
| `/api/token/refresh/` | POST | Refrescar access (body: `refresh`) |
| `/api/me/` | GET | Perfil del usuario autenticado (cabecera: `Authorization: Bearer <access>`) |

### Django Admin

| Ruta | Descripción |
|------|-------------|
| `/admin/` | Panel de administración Django |

---

## Estructura del proyecto

```
desarrollo/
├── config/                 # Configuración Django
│   ├── settings/
│   │   ├── base.py         # Configuración común
│   │   └── development.py  # Desarrollo (DEBUG, email consola)
│   ├── urls.py             # URLs raíz
│   └── wsgi.py
├── core/                   # App compartida
│   ├── templates/          # Plantillas base, landing
│   ├── management/commands/
│   │   ├── crear_datos_iniciales.py
│   │   ├── crear_certificaciones_industria.py
│   │   ├── expandir_contenido_cursos.py
│   │   └── asignar_imagen_cursos_marketing.py
│   └── context_processors  # Carrito en navbar, etc.
├── users/                  # Usuarios, auth, perfiles, API JWT
│   ├── services/
│   ├── api.py              # /api/me/
│   └── templates/
├── catalog/                # Catálogo: cursos, módulos, lecciones, certificados, certificaciones industria
│   ├── services/
│   ├── templates/
│   └── tests/
├── transactions/           # Carrito, checkout, órdenes, pasarela simulada, factura
│   ├── services/
│   ├── payment_token.py   # Token firmado para retorno pasarela
│   └── templates/
├── static/                 # CSS, imágenes (favicon, curso-default)
├── media/                  # Subidas (imágenes de cursos, etc.)
├── docs/                   # Documentación (flujos, sprints, configuración)
├── .env.example            # Plantilla de variables de entorno
├── .env                    # No versionado; copiar desde .env.example
├── requirements.txt
├── manage.py
└── README.md               # Este archivo
```

---

## Comandos de gestión

| Comando | Descripción |
|---------|-------------|
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py crear_datos_iniciales` | Categorías, instructores, cursos de ejemplo y usuarios por defecto (estudiante, instructor, admin, instructor1–3) |
| `python manage.py crear_certificaciones_industria` | Crear certificaciones de industria y preguntas de examen (si aplica) |
| `python manage.py expandir_contenido_cursos` | Añadir más módulos/lecciones a cursos existentes |
| `python manage.py asignar_imagen_cursos_marketing` | Asignar imágenes a cursos (media) |
| `python manage.py makemessages -l es` | Generar ficheros de traducción (i18n) |
| `python manage.py compilemessages` | Compilar mensajes de traducción |
| `python manage.py createsuperuser` | Crear otro superusuario (admin) |
| `python manage.py runserver` | Servidor de desarrollo |

---

## Tests

```bash
# Todos los tests
python manage.py test

# Por app
python manage.py test catalog
python manage.py test transactions
python manage.py test users
```

Si usas **pytest** y **pytest-django** (no incluidos por defecto en `requirements.txt`):

```bash
pip install pytest pytest-django
pytest
```

---

## Documentación adicional

- **[docs/FLUJOS.md](docs/FLUJOS.md)** — Flujos principales: inscripción, aprendizaje, certificados, carrito, checkout, pasarela simulada, API.
- **[docs/CONFIGURACION.md](docs/CONFIGURACION.md)** — Detalle de variables de entorno, base de datos, email y despliegue.
- **Sprints**: [SPRINT1.md](docs/SPRINT1.md), [SPRINT2.md](docs/SPRINT2.md), [SPRINT3.md](docs/SPRINT3.md), [SPRINT4.md](docs/SPRINT4.md) — Alcance y entregables por iteración.

---

## Producción

- Usar **`DEBUG=False`** y una **`SECRET_KEY`** generada de forma segura.
- Configurar **`ALLOWED_HOSTS`** con el dominio real.
- Servir estáticos con **WhiteNoise** o un servidor web (Nginx/Apache); recoger `STATIC_ROOT` con `collectstatic`.
- Base de datos: usar **PostgreSQL** (o MySQL) y `DATABASE_URL` en `.env`.
- Configurar un **EMAIL_BACKEND** real (SMTP) y `DEFAULT_FROM_EMAIL`.
- Crear un módulo `config.settings.production` y definir `DJANGO_SETTINGS_MODULE=config.settings.production` en el entorno de producción.

Más detalles en [docs/CONFIGURACION.md](docs/CONFIGURACION.md).
