"""Vistas del dominio Transacciones: carrito y checkout."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from urllib.parse import quote
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, ListView

from catalog.models import Curso, CertificacionIndustria
from catalog.services import course_service
from transactions.services import (
    obtener_o_crear_carrito,
    agregar_al_carrito,
    agregar_certificacion_al_carrito,
    quitar_del_carrito,
    quitar_certificacion_del_carrito,
    crear_orden_desde_carrito,
    crear_orden_pendiente_desde_carrito,
    confirmar_pago_orden,
    marcar_pago_fallido_orden,
    aplicar_cupon,
    obtener_cupon_aplicado,
    limpiar_cupon,
)
from transactions.payment_token import generate_payment_token, validate_payment_token
from transactions.models import Orden, EstadoOrden


class CarritoView(LoginRequiredMixin, TemplateView):
    """Vista del carrito: lista de items y total."""
    template_name = 'transactions/carrito.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = obtener_o_crear_carrito(self.request.user)
        context['carrito'] = carrito
        context['items'] = carrito.items.select_related('curso', 'curso__categoria').all()
        context['items_certificacion'] = carrito.items_certificacion.select_related('certificacion').all()
        context['subtotal'] = carrito.calcular_subtotal()
        context['total'] = carrito.calcular_total()
        context['cantidad_items'] = carrito.cantidad_items()
        return context


class CarritoAgregarCertificacionView(LoginRequiredMixin, View):
    """Adds certification access to cart. Redirects to certification detail or cart."""
    login_url = '/'

    def post(self, request, slug):
        certificacion = get_object_or_404(CertificacionIndustria, slug=slug, activa=True)
        item, msg = agregar_certificacion_al_carrito(request.user, certificacion, cantidad=1)
        if item:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('catalog:certificacion_industria_detail', args=[slug])
        return redirect(next_url)


class CarritoQuitarCertificacionView(LoginRequiredMixin, View):
    """Removes certification from cart."""
    login_url = '/'

    def post(self, request, slug):
        quitar_certificacion_del_carrito(request.user, slug)
        messages.info(request, 'Certification removed from cart.')
        return redirect('transactions:cart')


class CarritoAgregarView(LoginRequiredMixin, View):
    """Agrega un curso al carrito. Redirige al detalle del curso o al carrito."""
    login_url = '/'

    def post(self, request, curso_id):
        curso = get_object_or_404(
            Curso,
            pk=curso_id,
            estado='PUBLICADO',
        )
        item, msg = agregar_al_carrito(request.user, curso, cantidad=1)
        if item:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('catalog:course_detail', args=[curso_id])
        return redirect(next_url)


class CarritoQuitarView(LoginRequiredMixin, View):
    """Quita un curso del carrito."""
    login_url = '/'

    def post(self, request, curso_id):
        quitar_del_carrito(request.user, curso_id)
        messages.info(request, 'Course removed from cart.')
        return redirect('transactions:cart')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Resumen de compra y confirmación (pago simulado). Incluye cupón en sesión."""
    template_name = 'transactions/checkout.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = obtener_o_crear_carrito(self.request.user)
        items = carrito.items.select_related('curso', 'curso__categoria').all()
        items_certificacion = carrito.items_certificacion.select_related('certificacion').all()
        subtotal = carrito.calcular_subtotal()
        from decimal import Decimal
        cupon = obtener_cupon_aplicado(self.request)
        descuentos = cupon.aplicar_descuento(subtotal) if cupon else Decimal('0')
        total = subtotal - descuentos
        context['carrito'] = carrito
        context['items'] = items
        context['items_certificacion'] = items_certificacion
        context['subtotal'] = subtotal
        context['descuentos'] = descuentos
        context['total'] = total
        context['cupon_aplicado'] = cupon
        return context


class CheckoutApplyCouponView(LoginRequiredMixin, View):
    """Aplica un cupón por código (POST). Redirige al checkout."""
    login_url = '/'

    def post(self, request):
        codigo = request.POST.get('codigo', '').strip()
        ok, msg, cupon = aplicar_cupon(request, codigo)
        if ok:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect('transactions:checkout')


class CheckoutRemoveCouponView(LoginRequiredMixin, View):
    """Quita el cupón aplicado (POST). Redirige al checkout."""
    login_url = '/'

    def post(self, request):
        limpiar_cupon(request)
        messages.info(request, 'Coupon removed.')
        return redirect('transactions:checkout')


class CheckoutConfirmarView(LoginRequiredMixin, View):
    """Inicia pago: crea Orden PENDIENTE y redirige a la pasarela simulada."""
    login_url = '/'

    def post(self, request):
        carrito = obtener_o_crear_carrito(request.user)
        if carrito.cantidad_items() == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('transactions:cart')
        cupon = obtener_cupon_aplicado(request)
        orden = crear_orden_pendiente_desde_carrito(carrito, cupon=cupon)
        if orden:
            limpiar_cupon(request)
            token = generate_payment_token(orden.numero_orden, request.user.pk)
            return_url = request.build_absolute_uri(
                reverse('transactions:checkout_return') + '?token=' + token
            )
            gateway_url = reverse('transactions:checkout_gateway')
            params = f'?numero_orden={orden.numero_orden}&return_url={quote(return_url, safe="")}&total={orden.total}&token={quote(token, safe="")}'
            return redirect(gateway_url + params)
        messages.error(
            request,
            'Could not process the purchase. Please check that the courses are still available.'
        )
        return redirect('transactions:cart')


class GatewaySimuladaView(LoginRequiredMixin, TemplateView):
    """Página simulada de pasarela de pago: formulario tipo tarjeta y botones Pay / Fail / Cancel."""
    template_name = 'transactions/gateway_simulada.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['numero_orden'] = self.request.GET.get('numero_orden', '')
        context['return_url'] = self.request.GET.get('return_url', '')
        context['total'] = self.request.GET.get('total', '0')
        context['token'] = self.request.GET.get('token', '')
        return context


class CheckoutContinuePaymentView(LoginRequiredMixin, View):
    """Redirige a la pasarela simulada con un token nuevo para una orden PENDIENTE (ej. desde Mis pedidos)."""
    login_url = '/'

    def get(self, request, numero):
        orden = get_object_or_404(Orden, numero_orden=numero, user=request.user)
        if orden.estado != EstadoOrden.PENDIENTE:
            messages.info(request, 'This order is no longer pending payment.')
            return redirect('transactions:order_confirmed', numero=numero)
        token = generate_payment_token(orden.numero_orden, request.user.pk)
        return_url = request.build_absolute_uri(
            reverse('transactions:checkout_return') + '?token=' + quote(token, safe='')
        )
        gateway_url = reverse('transactions:checkout_gateway')
        params = f'?numero_orden={orden.numero_orden}&return_url={quote(return_url, safe="")}&total={orden.total}&token={quote(token, safe="")}'
        return redirect(gateway_url + params)


class CheckoutReturnView(LoginRequiredMixin, View):
    """Recibe el retorno desde la pasarela simulada (result=success|fail|cancel) y actualiza la orden."""
    login_url = '/'

    def get(self, request):
        result = request.GET.get('result', '').lower()
        token = request.GET.get('token', '')
        if result not in ('success', 'fail', 'cancel') or not token:
            messages.error(request, 'Invalid return from payment.')
            return redirect('transactions:order_list')

        parsed = validate_payment_token(token)
        if not parsed:
            messages.error(request, 'Payment link expired or invalid.')
            return redirect('transactions:order_list')

        numero_orden, user_id = parsed
        if request.user.pk != user_id:
            messages.error(request, 'Invalid payment session.')
            return redirect('transactions:order_list')

        orden = get_object_or_404(Orden, numero_orden=numero_orden, user=request.user)
        if orden.estado != EstadoOrden.PENDIENTE:
            messages.info(request, f'Order {numero_orden} was already processed.')
            return redirect('transactions:order_confirmed', numero=numero_orden)

        if result == 'success':
            if confirmar_pago_orden(orden):
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    subject=f'Order confirmed - SkillForge ({orden.numero_orden})',
                    message=f'Your order {orden.numero_orden} has been confirmed. You now have access to your courses.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
                messages.success(
                    request,
                    f'Purchase complete! Order {orden.numero_orden}. You now have access to your courses.'
                )
                return redirect('transactions:order_confirmed', numero=numero_orden)
            messages.error(request, 'Could not confirm payment.')
            return redirect('transactions:order_list')

        if result == 'fail':
            marcar_pago_fallido_orden(orden)
            messages.error(request, 'Payment failed. You can try again from your cart.')
            return redirect('transactions:checkout')

        # result == 'cancel'
        orden.estado = EstadoOrden.CANCELADA
        orden.save(update_fields=['estado'])
        messages.info(request, 'Payment cancelled. Your cart is unchanged.')
        return redirect('transactions:checkout')


class OrdenConfirmadaView(LoginRequiredMixin, TemplateView):
    """Página de confirmación tras compra exitosa."""
    template_name = 'transactions/orden_confirmada.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from transactions.models import Orden
        orden = get_object_or_404(
            Orden,
            numero_orden=self.kwargs['numero'],
            user=self.request.user,
        )
        context['orden'] = orden
        context['items'] = orden.items.select_related('curso').all()
        return context


class OrderInvoiceView(LoginRequiredMixin, TemplateView):
    """Vista 'Ver factura' (simulada): HTML con datos de orden y usuario."""
    template_name = 'transactions/factura.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from transactions.models import Orden
        orden = get_object_or_404(
            Orden,
            numero_orden=self.kwargs['numero'],
            user=self.request.user,
        )
        context['orden'] = orden
        context['items'] = orden.items.select_related('curso').all()
        context['factura'] = getattr(orden, 'factura', None)
        context['pago'] = getattr(orden, 'pago', None)
        return context


class OrderListView(LoginRequiredMixin, ListView):
    """Lista de pedidos del usuario (Mis pedidos)."""
    template_name = 'transactions/mis_pedidos.html'
    context_object_name = 'ordenes'
    login_url = '/'

    def get_queryset(self):
        from transactions.models import Orden
        return Orden.objects.filter(user=self.request.user).order_by('-fecha_creacion')


class OrderCancelView(LoginRequiredMixin, View):
    """Cancela una orden (solo CONFIRMADA, solo dueño). Devuelve cupos y cancela inscripciones."""
    login_url = '/'

    def post(self, request, numero):
        from transactions.models import Orden, EstadoOrden, EstadoInscripcion
        orden = get_object_or_404(Orden, numero_orden=numero, user=request.user)
        if orden.estado != EstadoOrden.CONFIRMADA:
            messages.error(request, 'Only confirmed orders can be cancelled.')
            return redirect('transactions:order_list')
        with transaction.atomic():
            orden.estado = EstadoOrden.CANCELADA
            orden.save(update_fields=['estado'])
            for item in orden.items.select_related('curso').all():
                item.curso.cupos_disponibles += item.cantidad
                item.curso.save(update_fields=['cupos_disponibles'])
            orden.inscripciones.all().update(estado=EstadoInscripcion.CANCELADA)
        messages.success(request, f'Order {numero} cancelled. Slots have been returned.')
        return redirect('transactions:order_list')
