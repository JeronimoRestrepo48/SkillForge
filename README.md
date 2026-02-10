# SkillForge - Desarrollo

**Forja tu Futuro Profesional** - Marketplace de Cursos Online

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env y ajustar SECRET_KEY si es necesario

# Aplicar migraciones
python manage.py migrate

# Crear datos iniciales (categorías, cursos y usuarios por defecto para los 3 roles)
python manage.py crear_datos_iniciales
```

## Ejecución

```bash
python manage.py runserver
```

Abrir http://127.0.0.1:8000 (la ruta `/` es el login; hace falta autenticarse para acceder al resto).

## Credenciales por defecto (3 paneles)

Tras ejecutar `python manage.py crear_datos_iniciales` puedes acceder con:

| Usuario     | Contraseña    | Rol            | Acceso |
|-------------|---------------|----------------|--------|
| **estudiante** | estudiante123 | Estudiante     | Home, Cursos, Mis cursos, Certificaciones, Carrito |
| **instructor** | instructor123 | Instructor     | Home, Gestionar cursos, Crear curso |
| **admin**      | admin123      | Administrador  | Home, Panel de administración (`/panel/`) |

Además, el comando crea instructores `instructor1`, `instructor2`, `instructor3` (contraseñas: `instructor1123`, `instructor2123`, `instructor3123`) con cursos de ejemplo asignados.

## Estructura del proyecto

```
desarrollo/
├── config/           # Configuración Django
│   └── settings/
├── core/             # App compartida (landing, mixins)
├── users/            # Dominio: Usuarios, autenticación
│   └── services/
├── catalog/          # Dominio: Catálogo de cursos
│   └── services/
└── manage.py
```

## Sprint 1 - Alcance

- Registro e inicio de sesión (Estudiante/Instructor)
- CRUD de cursos para instructores
- Listado público y detalle de cursos
- Landing page y navegación

Ver [docs/SPRINT1.md](docs/SPRINT1.md) para detalles.
