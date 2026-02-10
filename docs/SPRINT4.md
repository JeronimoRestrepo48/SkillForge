# Sprint 4 - Mejoras (sistema simulado) - SkillForge

## Principio rector

**Sin integraciones externas:** pago, factura, envío de correo y generación de PDF son **simulados** (backend local, consola, archivos). No se usan Stripe, PayPal, SMTP real ni APIs de facturación.

---

## Alcance

Sprint 4 añade **tests del dominio Transacciones** (carrito, orden, vistas), **cupones** (modelo y aplicación en checkout vía sesión), **pago y factura simulados** (modelos Pago/Factura creados al confirmar orden, vista "Ver factura" en HTML), **certificado en PDF** (generación local con reportlab), **emails simulados** (backend consola: orden confirmada y certificado obtenido), **Mis pedidos** (lista de órdenes del usuario) y **cancelación de orden** (solo CONFIRMADA; devolución de cupos y cancelación de inscripciones). Incluye documentación de rutas y user stories.

### Entregables

- [x] **Tests transacciones:** Cart service (obtener/crear carrito, agregar, quitar, vaciar, subtotal/total); Order service (crear orden desde carrito vacío/ítems/cupos agotados); vistas (carrito, agregar, quitar, checkout, confirmar, orden confirmada 200/404).
- [x] **Cupones:** Modelo Cupon (código, descuento %, fijo, vigencia, usos); validar vigencia y uso; aplicar en checkout vía sesión; aplicar_cupon / obtener_cupon_aplicado / limpiar_cupon; CheckoutView con subtotal, descuentos, total y cupon_aplicado; apply-coupon y remove-coupon; CheckoutConfirmarView pasa cupón a crear_orden_desde_carrito y limpia sesión.
- [x] **Pago y factura simulados:** Modelos Pago y Factura; creación en crear_orden_desde_carrito (Pago COMPLETADO, referencia SIM-…; Factura con numero_factura, subtotal, descuentos, total); vista "Ver factura" (`order/<numero>/invoice/`) con plantilla HTML.
- [x] **Certificado PDF:** reportlab en requirements; servicio generar_pdf_certificado(certificado); vista descarga PDF (`courses/<pk>/certificate/pdf/`) con Content-Disposition attachment.
- [x] **Emails simulados:** EMAIL_BACKEND console en development; DEFAULT_FROM_EMAIL en base; send_mail tras confirmar orden y al crear certificado (100%).
- [x] **Mis pedidos:** OrderListView (`cart/orders/`), template mis_pedidos.html con tabla y enlace a detalle y factura.
- [x] **Cancelación de orden:** POST `order/<numero>/cancel/`; solo orden CONFIRMADA y dueño; estado CANCELADA, devolver cupos, Inscripciones CANCELADA; botón "Cancelar" en lista solo si CONFIRMADA.
- [x] **Navbar:** Enlace "My orders" / "Mis pedidos" para usuarios autenticados (junto a Cart y en dropdown).
- [x] Documentación SPRINT4.md y rutas nuevas.

### User Stories

| ID   | Historia                                                                 | Estado     |
|------|---------------------------------------------------------------------------|------------|
| US20 | Como Estudiante quiero aplicar un cupón en el checkout para obtener descuento | Completado |
| US21 | Como Estudiante quiero ver mis pedidos y cancelar uno si está confirmado  | Completado |
| US22 | Como sistema registro pago y factura simulados al confirmar la compra    | Completado |
| US23 | Como Estudiante quiero descargar mi certificado en PDF                   | Completado |
| US24 | Como Estudiante recibo un email simulado al confirmar orden y al obtener certificado | Completado |

### Rutas nuevas

- `cart/orders/` — Lista de pedidos del usuario (Mis pedidos).
- `cart/order/<numero>/` — Detalle de orden confirmada (ya existente).
- `cart/order/<numero>/invoice/` — Ver factura (HTML simulado).
- `cart/order/<numero>/cancel/` — POST: cancelar orden (solo CONFIRMADA).
- `cart/checkout/apply-coupon/` — POST: aplicar código de cupón.
- `cart/checkout/remove-coupon/` — POST: quitar cupón.
- `cursos/<curso_pk>/certificate/pdf/` — Descarga del certificado en PDF.

### Aclaración

**Todo es simulado:** no hay integración con pasarelas de pago, proveedores de facturación, servidores SMTP ni servicios externos. Los correos se imprimen en consola (o se escriben en archivo si se configura `FileBased`). El PDF del certificado se genera en el servidor con reportlab.

---

## Fuera de alcance (futuro)

- Stripe / PayPal u otra pasarela real.
- Facturación electrónica con proveedor externo.
- Envío real de correos (SMTP/API).
- Integración con servicios de verificación de certificados externos.
