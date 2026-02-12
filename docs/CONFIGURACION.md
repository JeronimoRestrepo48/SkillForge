# Configuración — SkillForge

Este documento detalla la configuración del proyecto: variables de entorno, base de datos, correo y consideraciones para producción.

---

## Variables de entorno

El proyecto usa **django-environ**. Las variables se leen desde el archivo **`.env`** en la raíz de `desarrollo/`. Puedes copiar **`.env.example`** como plantilla.

### Resumen de variables

| Variable | Tipo | Por defecto (si no existe .env) | Descripción |
|----------|------|---------------------------------|-------------|
| `SECRET_KEY` | string | `dev-key-change-in-production` | Clave secreta de Django. En producción debe ser única y segura. |
| `DEBUG` | bool | `False` | Modo debug. En producción debe ser `False`. |
| `ALLOWED_HOSTS` | list (coma) | `localhost`, `127.0.0.1` | Hosts permitidos en `Host` de las peticiones. |
| `DATABASE_URL` | string | SQLite en `db.sqlite3` | URL de conexión a la base de datos. |
| `DEFAULT_FROM_EMAIL` | string | `noreply@skillforge.local` | Remitente por defecto de los correos. |

### Cómo se cargan

- En **`config/settings/base.py`** se usa `environ.Env` y se lee el archivo `.env` si existe.
- Los valores por defecto del `Env` se aplican cuando la variable no está definida en el entorno ni en `.env`.

### Generar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(50))"
```

Copia el resultado en `SECRET_KEY` en tu `.env` de producción.

---

## Módulo de configuración (settings)

- **Desarrollo**: por defecto se usa **`config.settings.development`** (definido en `manage.py` y `config/wsgi.py`).
- **Producción**: se debe crear un módulo `config.settings.production` y definir en el entorno:
  ```bash
  export DJANGO_SETTINGS_MODULE=config.settings.production
  ```

En **development**:
- `DEBUG = True`
- `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` (los correos se imprimen en consola).
- `ALLOWED_HOSTS` incluye `localhost`, `127.0.0.1`, `[::1]`.

---

## Base de datos

- **Desarrollo**: SQLite (`db.sqlite3`). No requiere instalación adicional.
- **Producción**: se recomienda PostgreSQL. Ejemplo en `.env`:
  ```env
  DATABASE_URL=postgres://usuario:contraseña@localhost:5432/skillforge
  ```
  El formato depende de cómo `django-environ` parsee `env.db()`. Para MySQL:
  ```env
  DATABASE_URL=mysql://usuario:contraseña@localhost:3306/skillforge
  ```

Después de cambiar `DATABASE_URL`, ejecutar:
```bash
python manage.py migrate
```

---

## Archivos estáticos y media

- **STATIC_URL**: `static/`
- **STATICFILES_DIRS**: `static/` en la raíz del proyecto.
- **STATIC_ROOT**: `staticfiles/` (para `collectstatic` en producción).
- **MEDIA_URL**: `media/`
- **MEDIA_ROOT**: `media/` (subidas: imágenes de cursos, etc.).

En desarrollo, con `DEBUG=True`, Django sirve estáticos y media desde las URLs configuradas. En producción hay que:
- Ejecutar `python manage.py collectstatic`.
- Servir los archivos con WhiteNoise, Nginx, Apache o el servidor que uses.

---

## Correo

- En **desarrollo** el backend es **consola**: los correos no se envían, se muestran en la salida del proceso.
- En **producción** hay que configurar un backend real (SMTP). Las variables típicas serían (si se implementan en `config.settings.production`):
  - `EMAIL_HOST`
  - `EMAIL_PORT`
  - `EMAIL_USE_TLS`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
  - `DEFAULT_FROM_EMAIL`

---

## Internacionalización

- **LANGUAGE_CODE**: `en` (base).
- **TIME_ZONE**: `America/Bogota`.
- **USE_I18N**: `True`.
- **LOCALE_PATHS**: `locale/` en la raíz.

Para generar y compilar mensajes en español:
```bash
python manage.py makemessages -l es
python manage.py compilemessages
```

---

## Autenticación y JWT

- **AUTH_USER_MODEL**: `users.User`
- **LOGIN_REDIRECT_URL**: `core:home`
- **LOGOUT_REDIRECT_URL**: `/`
- **LOGIN_URL**: `/`

JWT (Simple JWT) está configurado en `base.py`:
- **ACCESS_TOKEN_LIFETIME**: 60 minutos.
- **REFRESH_TOKEN_LIFETIME**: 7 días.

Los endpoints son `/api/token/` y `/api/token/refresh/`; el perfil en `/api/me/`.

---

## Checklist producción

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única y segura, no la por defecto
- [ ] `ALLOWED_HOSTS` con el/los dominio(s) real(es)
- [ ] `DATABASE_URL` apuntando a base de datos de producción (PostgreSQL recomendado)
- [ ] Servir estáticos (collectstatic + WhiteNoise o servidor web)
- [ ] Configurar EMAIL_BACKEND y variables SMTP si se envían correos
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production` (o el módulo que definas)
- [ ] No versionar `.env` (debe estar en `.gitignore`)
