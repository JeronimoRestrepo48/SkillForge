"""
Tests for transactions: cart service, order service, and views.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Curso, Categoria
from catalog.models import EstadoCurso
from users.models import TipoUsuario
from transactions.models import (
    CarritoCompras,
    ItemCarrito,
    Orden,
    ItemOrden,
    Inscripcion,
    EstadoInscripcion,
)
from transactions.services.cart_service import (
    obtener_o_crear_carrito,
    agregar_al_carrito,
    quitar_del_carrito,
    vaciar_carrito,
)
from transactions.services.order_service import crear_orden_desde_carrito

User = get_user_model()


def make_user(username, password, tipo=TipoUsuario.ESTUDIANTE):
    return User.objects.create_user(username=username, password=password, tipo=tipo)


class CartServiceTest(TestCase):
    """Tests for cart_service."""

    def setUp(self):
        self.user = make_user('student1', 'pass')
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=Decimal('100'),
            categoria=cat, instructor=inst, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10,
        )

    def test_obtener_o_crear_carrito_crea_uno_por_usuario(self):
        carrito = obtener_o_crear_carrito(self.user)
        self.assertIsInstance(carrito, CarritoCompras)
        self.assertEqual(carrito.user, self.user)
        carrito2 = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.pk, carrito2.pk)
        self.assertEqual(CarritoCompras.objects.filter(user=self.user).count(), 1)

    def test_agregar_al_carrito_curso_disponible(self):
        item, msg = agregar_al_carrito(self.user, self.curso, cantidad=1)
        self.assertIsNotNone(item)
        self.assertEqual(item.curso, self.curso)
        self.assertEqual(item.cantidad, 1)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.cantidad_items(), 1)
        self.assertEqual(carrito.calcular_subtotal(), Decimal('100'))

    def test_agregar_al_carrito_actualiza_cantidad_si_ya_existe(self):
        agregar_al_carrito(self.user, self.curso, cantidad=1)
        item, msg = agregar_al_carrito(self.user, self.curso, cantidad=2)
        self.assertIsNotNone(item)
        self.assertEqual(item.cantidad, 3)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.calcular_subtotal(), Decimal('300'))

    def test_agregar_al_carrito_curso_no_disponible_retorna_none(self):
        self.curso.cupos_disponibles = 0
        self.curso.save(update_fields=['cupos_disponibles'])
        item, msg = agregar_al_carrito(self.user, self.curso)
        self.assertIsNone(item)
        self.assertIn('no está disponible', msg)

    def test_quitar_del_carrito(self):
        agregar_al_carrito(self.user, self.curso)
        ok = quitar_del_carrito(self.user, self.curso.pk)
        self.assertTrue(ok)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.cantidad_items(), 0)
        ok2 = quitar_del_carrito(self.user, self.curso.pk)
        self.assertFalse(ok2)

    def test_vaciar_carrito(self):
        agregar_al_carrito(self.user, self.curso)
        vaciar_carrito(self.user)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.cantidad_items(), 0)
        self.assertEqual(carrito.calcular_subtotal(), Decimal('0'))

    def test_calcular_subtotal_y_total_coinciden_con_items(self):
        agregar_al_carrito(self.user, self.curso, cantidad=2)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.calcular_subtotal(), Decimal('200'))
        self.assertEqual(carrito.calcular_total(), Decimal('200'))


class OrderServiceTest(TestCase):
    """Tests for order_service."""

    def setUp(self):
        self.user = make_user('student1', 'pass')
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=Decimal('100'),
            categoria=cat, instructor=inst, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10,
        )

    def test_crear_orden_desde_carrito_vacio_retorna_none(self):
        carrito = obtener_o_crear_carrito(self.user)
        orden = crear_orden_desde_carrito(carrito)
        self.assertIsNone(orden)

    def test_crear_orden_desde_carrito_con_items_crea_orden_inscripcion_decrementa_cupos(self):
        agregar_al_carrito(self.user, self.curso, cantidad=1)
        carrito = obtener_o_crear_carrito(self.user)
        orden = crear_orden_desde_carrito(carrito)
        self.assertIsNotNone(orden)
        self.assertEqual(orden.user, self.user)
        self.assertEqual(orden.total, Decimal('100'))
        self.assertEqual(orden.items.count(), 1)
        self.assertTrue(orden.numero_orden.startswith('SF-'))
        self.assertTrue(Inscripcion.objects.filter(user=self.user, curso=self.curso).exists())
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.cupos_disponibles, 9)
        carrito.refresh_from_db()
        self.assertEqual(carrito.cantidad_items(), 0)

    def test_crear_orden_desde_carrito_sin_cupos_retorna_none_rollback(self):
        agregar_al_carrito(self.user, self.curso)
        self.curso.cupos_disponibles = 0
        self.curso.save(update_fields=['cupos_disponibles'])
        carrito = obtener_o_crear_carrito(self.user)
        orden = crear_orden_desde_carrito(carrito)
        self.assertIsNone(orden)
        self.assertFalse(Orden.objects.filter(user=self.user).exists())
        self.assertEqual(carrito.cantidad_items(), 1)


class TransactionsViewsTest(TestCase):
    """Tests for cart, checkout, order_confirmed views."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('student1', 'pass')
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=Decimal('100'),
            categoria=cat, instructor=inst, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10,
        )

    def test_cart_view_get_200_when_logged_in(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:cart'))
        self.assertEqual(r.status_code, 200)

    def test_cart_add_post_redirects_and_adds(self):
        self.client.login(username='student1', password='pass')
        r = self.client.post(reverse('transactions:cart_add', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 302)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.cantidad_items(), 1)

    def test_cart_remove_post_removes_and_redirects(self):
        agregar_al_carrito(self.user, self.curso)
        self.client.login(username='student1', password='pass')
        r = self.client.post(reverse('transactions:cart_remove', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 302)
        carrito = obtener_o_crear_carrito(self.user)
        self.assertEqual(carrito.cantidad_items(), 0)

    def test_checkout_view_get_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:checkout'))
        self.assertEqual(r.status_code, 200)

    def test_checkout_confirm_post_creates_order_redirects_to_order_confirmed(self):
        agregar_al_carrito(self.user, self.curso)
        self.client.login(username='student1', password='pass')
        r = self.client.post(reverse('transactions:checkout_confirm'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('order/', r.url)
        orden = Orden.objects.filter(user=self.user).first()
        self.assertIsNotNone(orden)
        self.assertTrue(r.url.endswith(orden.numero_orden + '/') or orden.numero_orden in r.url)

    def test_order_confirmed_get_200_for_own_order(self):
        agregar_al_carrito(self.user, self.curso)
        carrito = obtener_o_crear_carrito(self.user)
        orden = crear_orden_desde_carrito(carrito)
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:order_confirmed', args=[orden.numero_orden]))
        self.assertEqual(r.status_code, 200)

    def test_order_confirmed_get_404_for_other_user_order(self):
        other = make_user('other1', 'pass')
        orden = Orden.objects.create(
            user=other,
            numero_orden='SF-99999999999999-0000',
            total=Decimal('50'),
            subtotal=Decimal('50'),
            descuentos=Decimal('0'),
        )
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:order_confirmed', args=[orden.numero_orden]))
        self.assertEqual(r.status_code, 404)
