# Sprint 1 - SkillForge

## Alcance

Sprint 1 establece los fundamentos del marketplace: usuarios, catálogo y experiencia de exploración.

### Entregables

- [x] Usuario con roles (Estudiante, Instructor, Administrador)
- [x] Registro, login, logout
- [x] Categorías y cursos (CRUD para instructores)
- [x] Listado público de cursos y detalle
- [x] Landing page y diseño responsivo

### User Stories

| ID | Historia | Criterios de aceptación | Estado |
|----|----------|-------------------------|--------|
| US1 | Como visitante quiero registrarme como Estudiante o Instructor | Formulario con selección de rol, creación de perfil asociado | Completado |
| US2 | Como usuario quiero iniciar y cerrar sesión | Login/Logout con redirección correcta | Completado |
| US3 | Como Instructor quiero crear y editar mis cursos | CRUD con validación de permisos | Completado |
| US4 | Como visitante quiero ver el catálogo de cursos publicados | Listado con filtro por categoría | Completado |
| US5 | Como visitante quiero ver el detalle de un curso | Página con descripción, precio, instructor | Completado |
| US6 | Como visitante quiero ver la landing page | Hero, categorías, cursos destacados | Completado |

### No incluido en Sprint 1

- Carrito de compras
- Proceso de pago
- Módulos y lecciones
- Calificaciones
- Certificados

### Criterios de aceptación técnicos

- Modelos alineados al diagrama de clases de dominio
- Servicios encapsulando lógica de negocio (user_service, course_service)
- Vistas restringidas por rol (InstructorRequiredMixin)
- Templates responsivos con Bootstrap 5
