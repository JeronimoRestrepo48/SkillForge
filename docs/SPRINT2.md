# Sprint 2 - SkillForge

## Alcance

Sprint 2 añade el flujo transaccional (carrito, checkout simulado, inscripción), la estructura de contenido (módulos y lecciones) y un frontend con componentes reutilizables.

### Entregables

- [x] App **transactions**: CarritoCompras, ItemCarrito, Orden, ItemOrden, Inscripcion
- [x] Carrito: agregar, ver, quitar, checkout con pago simulado
- [x] Modelos **Modulo**, **Leccion**, **ProgresoLeccion** en catalog
- [x] CRUD módulos y lecciones para instructores (gestionar contenido)
- [x] Vista "Aprender" para estudiantes inscritos (módulos/lecciones, marcar completada)
- [x] Mis inscripciones (/cursos/mis-inscripciones/)
- [x] Componentes reutilizables (card_curso, card_categoria, card_carrito, curso_card_mini)
- [x] CSS en static/css (base, components, pages)
- [x] Navbar: enlace carrito con badge, Mis cursos, Gestionar mis cursos (instructor)
- [x] Breadcrumbs en carrito, checkout, módulos/lecciones, aprender
- [x] Mensajes de feedback (añadir al carrito, compra exitosa)

### User Stories

| ID  | Historia                                                                 | Estado   |
|-----|--------------------------------------------------------------------------|----------|
| US7 | Como Estudiante quiero agregar cursos al carrito                         | Completado |
| US8 | Como Estudiante quiero ver mi carrito y proceder al pago                 | Completado |
| US9 | Como Estudiante quiero completar una compra (simulada)                   | Completado |
| US10| Como Instructor quiero estructurar mi curso en módulos y lecciones        | Completado |
| US11| Como Estudiante inscrito quiero ver el contenido del curso               | Completado |
| US12| Como visitante quiero una experiencia visual consistente                | Completado |

### Rutas principales

- `/carrito/` — Ver carrito
- `/carrito/agregar/<id>/` — Añadir curso al carrito (POST)
- `/carrito/quitar/<id>/` — Quitar del carrito (POST)
- `/checkout/` — Resumen y confirmar compra
- `/orden/<numero>/` — Confirmación de orden
- `/cursos/mis-inscripciones/` — Cursos inscritos
- `/cursos/<id>/aprender/` — Contenido del curso (módulos/lecciones)
- `/cursos/<id>/modulos/` — Gestionar módulos (instructor)
- `/cursos/<id>/modulos/<id>/lecciones/` — Gestionar lecciones (instructor)

### Fuera de alcance (Sprint 3+)

- Pago real (Stripe/PayPal)
- Cupones
- Calificaciones
- Certificados
