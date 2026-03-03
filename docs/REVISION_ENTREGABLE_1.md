# Revisión del proyecto frente al Entregable 1

**Documento de referencia:** Entregable_1.pdf — *Entrega No. 1: Núcleo de Negocio y Exposición de API Profesional*

---

## 1. Resumen de requisitos del documento

| Criterio | Peso | Requisito |
|----------|------|-----------|
| Dominio y avance | 1.0 | 50–60 % de clases del modelo implementadas; tipos y validaciones en modelo/entidad |
| SOLID y Service Layer | 1.5 | Desacoplamiento total; lógica en servicios inyectables; no Fat Views ni Fat Models |
| DRF y API Gateway | 1.0 | Serializers entrada/salida; APIView; códigos HTTP 201, 400, 404, 409 |
| Patrones creacionales | 1.0 | Builder (entidad más compleja); Factory (dependencia externa o variante) |
| Documentación (Wiki) | 0.5 | Justificación estructura, diagrama de secuencia, estrategia API Gateway |

**Advertencia del documento:** Cualquier lógica de negocio en `views.py` o en métodos de Model que no sean de persistencia penaliza SOLID en un 50 %.

---

## 2. Estado actual del código

### 2.1 Capa de dominio (50–60 % de clases)

**Cumple en gran medida.**

- **catalog:** Categoria, Curso, EstadoCurso, NivelDificultad, Modulo, Leccion, TipoLeccion, ProgresoLeccion, Calificacion, Certificado, CertificacionIndustria, SeccionMaterialCertificacion, ExamenCertificacion, PreguntaExamen, OpcionPregunta, AccesoCertificacion, DiplomaCertificacionIndustria.
- **transactions:** TipoCupon, Cupon, CarritoCompras, ItemCarrito, ItemCarritoCertificacion, EstadoOrden, Orden, ItemOrden, ItemOrdenCertificacion, EstadoInscripcion, Inscripcion, MetodoPago, EstadoPago, Pago, Factura.
- **users:** TipoUsuario, EstadoUsuario, NivelExperiencia, User, Estudiante, Instructor, UserProfile.

Hay muchos modelos con tipos adecuados (Decimal, TextChoices, FKs) y validaciones/reglas en modelo (p. ej. `Curso.calcular_precio_final()`, `esta_disponible()`, `Cupon.validar_vigencia()`, `aplicar_descuento()`). Para asegurar el “50–60 %” falta contrastar con el diagrama de clases original del proyecto; si ese diagrama tiene más entidades (p. ej. notificaciones, reportes), habría que indicar cuáles se consideran implementadas.

**Recomendación:** Incluir en la Wiki una tabla que relacione “clases del diagrama” vs “clases implementadas” para justificar el porcentaje.

---

### 2.2 Service Layer y SOLID

**Cumple en gran parte; hay puntos a ajustar.**

- **Bien:** Los flujos principales están orquestados por servicios:
  - `catalog/services`: `course_service`, `certificate_service`, `rating_service`.
  - `transactions/services`: `cart_service`, `order_service`, `coupon_service`.
- Las vistas de `catalog/views.py` y `transactions/views.py` delegan en estos servicios (obtener cursos, agregar al carrito, crear orden, confirmar pago, etc.).

**Riesgos de penalización:**

1. **catalog/views.py — CursoDetailView.get_context_data:**  
   Hay consultas directas en la vista:
   - `Inscripcion.objects.filter(user=..., curso=...).exclude(estado='CANCELADA').exists()` para `ya_inscrito`.
   - `Calificacion.objects.filter(user=..., curso=...).first()` para `mi_calificacion`.
   - `Leccion.objects.filter(modulo__curso=...).count()` para `total_lecciones`.  
   El documento considera “lógica de negocio” en views como penalizable. Lo más seguro es mover estas consultas a servicios (p. ej. `enrollment_service.esta_inscrito(user, curso)`, `course_service.total_lecciones_curso(curso)`) y que la vista solo llame a los servicios y arme el contexto.

2. **catalog/views.py — MisInscripcionesView.get_context_data:**  
   La consulta de inscripciones del usuario está en la vista. Recomendable llevarla a un servicio (p. ej. `enrollment_service.inscripciones_activas(user)`).

3. **transactions/views.py — CheckoutView.get_context_data:**  
   Se usa `cupon.aplicar_descuento(subtotal)` desde la vista. El cálculo en sí está en el modelo (Cupon), pero la orquestación “subtotal + cupón + total” podría vivir en un servicio (p. ej. `checkout_service.calcular_totales(carrito, cupon)`) para evitar cualquier duda de “lógica en la vista”.

**Recomendación:** Mover las consultas y cálculos anteriores a la capa de servicios y dejar en las vistas solo llamadas a servicios y asignación a `context`. Así se evita la penalización del 50 % en SOLID.

---

### 2.3 DRF (Serializers, APIView, códigos HTTP)

**No cumple por completo.**

- **Existente:**  
  - `users/api.py`: `MeView` (APIView), GET `/api/me/` con JWT.  
  - No se usan Serializers para entrada/salida; la respuesta se arma a mano en un diccionario.
- **Requisitos del documento:**  
  - “Implementación de Serializers para la entrada y salida de datos.”  
  - “Uso de APIView para el control total de la petición.”  
  - “Manejo correcto de códigos de estado HTTP (201, 400, 404, 409).”

**Falta:**

1. Definir al menos un **Serializer** (p. ej. `UserProfileSerializer` o `MeSerializer`) para la salida de `/api/me/` (y opcionalmente para entrada si se permite actualizar perfil).
2. Endpoints que devuelvan explícitamente **201** (creación), **400** (validación), **404** (recurso no encontrado), **409** (conflicto). Por ejemplo:
   - Un endpoint de creación (curso, inscripción, o recurso de catálogo) que devuelva 201 al crear y 400 si los datos son inválidos.
   - Un endpoint que devuelva 404 cuando un recurso no exista y 409 en caso de conflicto (p. ej. “ya inscrito”, “curso sin cupos”).

**Recomendación:** Añadir al menos un módulo `users/serializers.py` (o `api/serializers.py`) con un serializer para el perfil y usarlo en `MeView`; y al menos un endpoint adicional (o ampliar uno existente) que utilice Serializers y devuelva 201/400/404/409 según el caso.

---

### 2.4 Patrones creacionales (Builder y Factory)

**No implementados.**

- **Builder:** El documento exige usarlo para “la creación de la entidad más compleja del sistema”. En este proyecto candidatos claros son:
  - **Orden** (con ItemOrden, ItemOrdenCertificacion, y luego Pago, Factura, Inscripciones, AccesoCertificacion): es la entidad más rica en relaciones y efectos secundarios.
  - Alternativa: construcción paso a paso de un **Curso** con Módulos y Lecciones.
- **Factory:** Debe usarse para “gestionar al menos una dependencia externa o variante” (notificaciones, pasarelas de pago, generadores de reportes). Opciones coherentes con el código actual:
  - **Pasarela de pago:** una factory que devuelva una implementación “simulada” vs una futura “real” (Stripe, PayU, etc.).
  - **Notificaciones:** factory que devuelva envío por email vs consola vs cola.
  - **Generación de reportes/PDF:** factory que devuelva generador de certificado vs generador de factura vs generador de diploma (ya tienes `certificate_service` con PDFs).

**Recomendación:**  
1. Introducir un **OrderBuilder** (o similar) que construya una Orden con sus ítems, descuentos y, si aplica, Pago/Factura/Inscripciones en pasos claros, y usarlo desde `order_service`.  
2. Introducir una **PaymentGatewayFactory** (o **NotificationFactory**) que devuelva la implementación concreta (simulada vs real) y usarla donde hoy se crea el pago o se envía el correo.

---

## 3. Checklist rápido

| Requisito | Estado | Acción sugerida |
|-----------|--------|------------------|
| 50–60 % clases de dominio | ✅ | Documentar en Wiki el conteo vs diagrama |
| Tipos y validaciones en modelos | ✅ | Mantener; opcional revisar que no haya lógica pesada fuera de persistencia en modelos |
| Lógica solo en servicios | ✅ | Implementado: enrollment_service, checkout_service; vistas delegan |
| Serializers DRF | ✅ | UserMeSerializer, CalificacionCreateSerializer; MeView y CourseRateView |
| APIView | ✅ | MeView, CourseRateView |
| Códigos HTTP 201, 400, 404, 409 | ✅ | POST /api/courses/<id>/rate/ devuelve 201, 400, 404, 409 |
| Patrón Builder | ✅ | OrderBuilder en transactions/order_builder.py; usado en order_service |
| Patrón Factory | ✅ | PaymentGatewayFactory en transactions/payment_gateway_factory.py |
| Wiki: estructura de carpetas | ✅ | Contenido en docs/WIKI_ENTREGABLE_1.md |
| Wiki: diagrama de secuencia | ✅ | Contenido en docs/WIKI_ENTREGABLE_1.md |
| Wiki: API Gateway | ✅ | Contenido en docs/WIKI_ENTREGABLE_1.md |

---

## 4. Conclusión

**Implementación completada** (según última revisión):

1. **Vistas:** Toda la lógica de negocio se movió a servicios (`enrollment_service`, `checkout_service`, `course_service.total_lecciones_curso`, `rating_service.obtener_calificacion_usuario_curso`). Las vistas solo delegan.
2. **DRF:** Serializers (`UserMeSerializer`, `CalificacionCreateSerializer`) y endpoint `POST /api/courses/<id>/rate/` con códigos 201, 400, 404, 409.
3. **Patrones creacionales:** `OrderBuilder` para la creación de Orden; `PaymentGatewayFactory` para la pasarela de pago (simulada vs futura real).
4. **Wiki:** Contenido listo en `docs/WIKI_ENTREGABLE_1.md` para copiar a la Wiki del repositorio.
