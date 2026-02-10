"""Vistas del dominio Transacciones: carrito y checkout."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, ListView

from catalog.models import Curso
from catalog.services import course_service
from transactions.services import (
    obtener_o_crear_carrito,
    agregar_al_carrito,
    quitar_del_carrito,
    crear_orden_desde_carrito,
    aplicar_cupon,
    obtener_cupon_aplicado,
    limpiar_cupon,
)


class CarritoView(LoginRequiredMixin, TemplateView):
    """Vista del carrito: lista de items y total."""
    template_name = 'transactions/carrito.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = obtener_o_crear_carrito(self.request.user)
        context['carrito'] = carrito
        context['items'] = carrito.items.select_related('curso').all()
        context['subtotal'] = carrito.calcular_subtotal()
        context['total'] = carrito.calcular_total()
        context['cantidad_items'] = carrito.cantidad_items()
        return context


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
        messages.info(request, 'Curso eliminado del carrito.')
        return redirect('transactions:cart')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Resumen de compra y confirmación (pago simulado). Incluye cupón en sesión."""
    template_name = 'transactions/checkout.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = obtener_o_crear_carrito(self.request.user)
        items = carrito.items.select_related('curso').all()
        subtotal = carrito.calcular_subtotal()
        from decimal import Decimal
        cupon = obtener_cupon_aplicado(self.request)
        descuentos = cupon.aplicar_descuento(subtotal) if cupon else Decimal('0')
        total = subtotal - descuentos
        context['carrito'] = carrito
        context['items'] = items
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
        messages.info(request, 'Cupón eliminado.')
        return redirect('transactions:checkout')


class CheckoutConfirmarView(LoginRequiredMixin, View):
    """Procesa el pago simulado: crea Orden, Inscripciones y vacía el carrito."""
    login_url = '/'

    def post(self, request):
        carrito = obtener_o_crear_carrito(request.user)
        if carrito.cantidad_items() == 0:
            messages.warning(request, 'Tu carrito está vacío.')
            return redirect('transactions:cart')
        cupon = obtener_cupon_aplicado(request)
        orden = crear_orden_desde_carrito(carrito, cupon=cupon)
        if orden:
            limpiar_cupon(request)
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject=f'Orden confirmada - SkillForge ({orden.numero_orden})',
                message=f'Tu orden {orden.numero_orden} ha sido confirmada. Ya tienes acceso a tus cursos.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            messages.success(
                request,
                f'¡Compra realizada! Orden {orden.numero_orden}. Ya tienes acceso a tus cursos.'
            )
            return redirect('transactions:order_confirmed', numero=orden.numero_orden)
        messages.error(
            request,
            'No se pudo procesar la compra. Verifica que los cursos sigan disponibles.'
        )
        return redirect('transactions:cart')


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
            messages.error(request, 'Solo se pueden cancelar órdenes confirmadas.')
            return redirect('transactions:order_list')
        with transaction.atomic():
            orden.estado = EstadoOrden.CANCELADA
            orden.save(update_fields=['estado'])
            for item in orden.items.select_related('curso').all():
                item.curso.cupos_disponibles += item.cantidad
                item.curso.save(update_fields=['cupos_disponibles'])
            orden.inscripciones.all().update(estado=EstadoInscripcion.CANCELADA)
        messages.success(request, f'Orden {numero} cancelada. Los cupos han sido devueltos.')
        return redirect('transactions:order_list')
