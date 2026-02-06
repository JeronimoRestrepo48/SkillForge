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

# Crear datos iniciales (categorías, usuario admin e instructor de prueba)
python manage.py crear_datos_iniciales
```

## Ejecución

```bash
python manage.py runserver
```

Abrir http://127.0.0.1:8000

## Usuarios de prueba

Tras ejecutar `crear_datos_iniciales`:

| Usuario     | Contraseña   | Rol           |
|-------------|--------------|---------------|
| admin       | admin123     | Administrador |
| instructor1 | instructor123| Instructor    |

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
