# Flujos principales de SkillForge

Este documento describe los flujos de usuario más importantes del sistema.

## 1. Inscripción a un curso

1. El **estudiante** navega al catálogo (`/catalog/`) y ve los cursos publicados.
2. Entra al **detalle del curso** (`/catalog/<id>/`), donde puede ver descripción, instructor, precio y botón "Inscribirse" (si hay cupos).
3. Al inscribirse se crea una **Inscripción** en estado `ACTIVA` y, en el flujo actual, suele asociarse a una **Orden** (carrito/checkout) o a una inscripción directa según la implementación.
4. El estudiante puede acceder a **Mis cursos** (`/catalog/my-courses/`) y desde ahí entrar a **Aprender** (`/catalog/<id>/learn/`).

## 2. Aprendizaje y progreso

1. En **Aprender** (`/catalog/<curso_id>/learn/`) el estudiante ve los **módulos** y **lecciones** en acordeón.
2. Cada lección puede ser de tipo **TEXTO**, **VIDEO**, **QUIZ** o **PRACTICA**. El contenido se muestra en la misma página o en la **vista de lección** (`/catalog/<curso_id>/learn/lesson/<leccion_id>/`).
3. En la vista de lección hay **navegación anterior/siguiente** y botón **Marcar como completada**.
4. Al marcar una lección completada se crea/actualiza un **ProgresoLeccion**. El **porcentaje de progreso** se calcula como (lecciones completadas / total) × 100.
5. Cuando el progreso llega al **100%**, al marcar la última lección el sistema llama a `crear_certificado_si_completo`: se crea el **Certificado** de completitud y la inscripción pasa a estado `COMPLETADA`.
6. El usuario ve un mensaje de éxito indicando que el certificado está en **Mis certificados** (`/catalog/my-certificates/`).

## 3. Certificados

- **Certificado de completitud de curso**: se genera al completar el 100% de las lecciones. El estudiante puede ver la vista previa y descargar el PDF desde Mis certificados.
- **Diplomas de certificaciones de industria**: son independientes de cursos. El estudiante debe **comprar acceso** a una certificación (pago simulado), estudiar el material y aprobar el **examen** (cuestionario). Al aprobar se emite un diploma PDF.

## 4. Carrito y pago (transacciones)

1. El estudiante añade cursos al **carrito** (`/transactions/cart/`).
2. En **Checkout** (`/transactions/checkout/`) se confirma la orden; se puede aplicar un **cupón** si existe.
3. Tras el pago simulado se crea la **Orden** y las **Inscripciones** asociadas a los ítems comprados.
4. El estudiante ve la **orden confirmada** y puede ir a **Mis cursos** o directamente a **Aprender** de cada curso comprado.

## 5. API (autenticación JWT)

- **Login JWT**: POST a la ruta configurada con Simple JWT (p. ej. `/api/token/`) con `username` y `password` devuelve `access` y `refresh`.
- **Perfil**: GET `/api/me/` con el token en cabecera `Authorization: Bearer <access>` devuelve los datos del usuario (id, username, email, tipo, perfil si existe).

Para más detalle de endpoints REST, ver la configuración en `config/urls.py` y las apps `users` (api.py) y, si existe, documentación OpenAPI/Swagger.
