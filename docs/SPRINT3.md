# Sprint 3 - SkillForge

## Alcance

Sprint 3 incorpora **certificados** (generación al completar curso, preview y verificación por código), **calificaciones** (solo estudiantes que completaron pueden valorar), **roles diferenciados** (navbar y redirección post-login por rol, panel de administración), mejoras de **lógica de negocio** (completitud de curso, inscripción COMPLETADA) y un **frontend unificado** alineado con la identidad SkillForge (forja y fuego). Incluye tests unitarios e integración para servicios y vistas críticas.

### Entregables

- [x] Modelos **Certificado** y **Calificacion** en catalog; migraciones
- [x] Servicio `certificate_service`: crear certificado solo si progreso 100%; marcar Inscripcion COMPLETADA
- [x] Servicio `rating_service`: validar inscripción completada para crear/actualizar calificación; promedio y total por curso
- [x] Integración en flujo “completar lección”: al 100% → Inscripcion COMPLETADA + generación de certificado
- [x] Vistas: preview de certificado, verificación pública por código, Mis certificados
- [x] Formulario de valoración en detalle de curso; sección Reseñas con “Compra verificada”
- [x] Detalle de curso con pestañas: Descripción, Contenido (módulos/lecciones), Reseñas
- [x] **Roles**: `AdminRequiredMixin`; redirección post-login por rol (Estudiante → landing, Instructor → mis cursos, Administrador → panel admin)
- [x] Navbar por rol: Panel Admin para admin; badge de rol y “Mis certificados” en dropdown
- [x] Panel de administración (`/panel-admin/`): resumen (usuarios por tipo, cursos publicados, órdenes recientes); enlaces al Django admin
- [x] Diseño: login y registro amplios; navbar más grande y visible
- [x] **Frontend “SkillForge”**: paleta fuego/forja (amber, naranja, coral sobre metal oscuro); gradientes, sombras y componentes alineados; hero y cards con identidad de marca
- [x] Tests: certificate_service, rating_service, acceso al panel admin por rol, mixins

### User Stories

| ID   | Historia                                                                 | Estado    |
|------|---------------------------------------------------------------------------|-----------|
| US13 | Como Estudiante quiero obtener un certificado al completar un curso      | Completado |
| US14 | Como Estudiante quiero ver y verificar mis certificados                   | Completado |
| US15 | Como Estudiante que completó un curso quiero valorarlo con estrellas      | Completado |
| US16 | Como visitante quiero ver reseñas y valoración media en el detalle del curso | Completado |
| US17 | Como Administrador quiero acceder a un panel de resumen                   | Completado |
| US18 | Como usuario quiero ser redirigido según mi rol al iniciar sesión         | Completado |
| US19 | Como visitante quiero una interfaz con identidad visual SkillForge       | Completado |

### Rutas principales

- `/cursos/mis-certificados/` — Mis certificados (estudiante)
- `/cursos/<id>/certificado/` — Preview del certificado (dueño)
- `/certificado/verificar/<codigo>/` — Verificación pública por código
- `/cursos/<id>/` — Detalle de curso (con pestañas y reseñas)
- `/cursos/calificar/<id>/` — POST: crear/actualizar calificación
- `/panel-admin/` — Panel de administración (solo Admin/staff)
- Login → redirección por rol (landing / mis cursos / panel admin)

### Identidad visual (frontend)

- **Paleta**: llama/ámbar (`#f59e0b`), naranja (`#ea580c`), coral (`#f43f5e`), metal oscuro (`#0f172a`, `#1e293b`), fondos cálidos (`#fffbf7`, `#fff7ed`).
- **Gradientes**: botones y acentos con gradiente amber → naranja → coral; navbar con franja inferior en gradiente de marca; hero con degradado oscuro y toque ámbar.
- **Componentes**: cards con borde/sombra alineados a la marca; tabs activos con subrayado en color fuego; breadcrumbs y paginación en tonos naranja/ámbar.
- **Archivos**: `static/css/base.css` (variables y paleta), `static/css/components.css` (navbar, botones, cards, footer, tabs), `static/css/pages.css` (hero, section-card, auth, empty-state, certificado, panel admin).

### Fuera de alcance (Sprint 4+)

- Pago real (Stripe)
- Cupones
- Generación de PDF de certificados (WeasyPrint)
- Notificaciones por email
