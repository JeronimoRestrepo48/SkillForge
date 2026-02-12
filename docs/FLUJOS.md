# Flujos principales de SkillForge

Este documento describe los flujos de usuario más importantes del sistema. Las rutas usan los prefijos definidos en `config/urls.py`: **`/courses/`** (catálogo) y **`/cart/`** (transacciones).

---

## 1. Inscripción a un curso

1. El **estudiante** navega al catálogo (**`/courses/`**) y ve los cursos publicados.
2. Entra al **detalle del curso** (**`/courses/<id>/`**), donde puede ver descripción, instructor, precio y botón para añadir al carrito o inscribirse según el flujo.
3. Para cursos de pago: añade al **carrito**, pasa por **checkout** y **pasarela de pago**. Tras confirmar el pago se crea la **Orden** y las **Inscripciones** asociadas.
4. El estudiante puede acceder a **Mis cursos** (**`/courses/my-courses/`**) y desde ahí entrar a **Aprender** (**`/courses/<id>/learn/`**).

---

## 2. Aprendizaje y progreso

1. En **Aprender** (**`/courses/<curso_id>/learn/`**) el estudiante ve los **módulos** y **lecciones** en acordeón.
2. Cada lección puede ser de tipo **TEXTO**, **VIDEO**, **QUIZ** o **PRACTICA**. El contenido se muestra en la **vista de lección** (**`/courses/<curso_id>/learn/lesson/<leccion_id>/`**).
3. En la vista de lección hay **navegación anterior/siguiente** y botón **Marcar como completada**.
4. Al marcar una lección completada se crea/actualiza un **ProgresoLeccion**. El **porcentaje de progreso** se calcula como (lecciones completadas / total) × 100.
5. Cuando el progreso llega al **100%**, al marcar la última lección el sistema genera el **Certificado** de completitud y la inscripción pasa a estado `COMPLETADA`.
6. El usuario puede ver y descargar el certificado desde **Mis certificados** (**`/courses/my-certificates/`**).

---

## 3. Certificados

- **Certificado de completitud de curso**: se genera al completar el 100% de las lecciones. Vista previa y descarga PDF desde **Mis certificados** (**`/courses/my-certificates/`**).
- **Diplomas de certificaciones de industria**: independientes de cursos. El estudiante **compra acceso** desde **Certificaciones de industria** (**`/courses/certificaciones-industria/<slug>/`**), lo añade al carrito y paga por el flujo normal; luego puede presentar el **examen** (**`/courses/certificaciones-industria/<slug>/examen/`**). Al aprobar se emite el diploma PDF.

---

## 4. Carrito, checkout y pasarela de pago

1. El estudiante añade **cursos** o **certificaciones** al **carrito** (**`/cart/`**). Puede añadir/quitar ítems desde el detalle del curso o de la certificación.
2. En **Checkout** (**`/cart/checkout/`**) revisa el resumen, puede aplicar un **cupón** (apply/remove) y pulsa confirmar.
3. Al **confirmar** (**`/cart/checkout/confirm/`**) se crea una **Orden** en estado **PENDIENTE** y se redirige a la **pasarela de pago simulada** (**`/cart/checkout/gateway/`**) con un token firmado.
4. En la **pasarela simulada** el usuario puede elegir:
   - **Pagar**: simula pago correcto y redirige a **retorno** con éxito.
   - **Fallar**: simula rechazo y redirige a retorno con fallo.
   - **Cancelar**: redirige a retorno cancelado.
5. En **retorno** (**`/cart/checkout/return/`**) se valida el token, se confirma o se marca fallida la orden y se crean las **Inscripciones** en caso de éxito. El usuario ve la **orden confirmada** (**`/cart/order/<numero>/`**) o un mensaje de error/cancelación.
6. **Órdenes pendientes**: desde **Mis pedidos** (**`/cart/orders/`**) el usuario ve todas sus órdenes. Para una orden en estado **PENDIENTE** aparece el enlace **Complete payment**, que lleva a **`/cart/checkout/continue/<numero>/`** y de ahí de nuevo a la pasarela para completar el pago.

---

## 5. API (autenticación JWT)

- **Login JWT**: POST **`/api/token/`** con `username` y `password` en el body devuelve `access` y `refresh`.
- **Refresh**: POST **`/api/token/refresh/`** con `refresh` en el body devuelve un nuevo `access`.
- **Perfil**: GET **`/api/me/`** con cabecera `Authorization: Bearer <access>` devuelve los datos del usuario (id, username, email, tipo, perfil si existe).

Para más detalle de endpoints, ver `config/urls.py` y `users/api.py`.
