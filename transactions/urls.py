from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.CarritoView.as_view(), name='cart'),
    path('add/<int:curso_id>/', views.CarritoAgregarView.as_view(), name='cart_add'),
    path('remove/<int:curso_id>/', views.CarritoQuitarView.as_view(), name='cart_remove'),
    path('add-certificacion/<slug:slug>/', views.CarritoAgregarCertificacionView.as_view(), name='cart_add_certificacion'),
    path('remove-certificacion/<slug:slug>/', views.CarritoQuitarCertificacionView.as_view(), name='cart_remove_certificacion'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/apply-coupon/', views.CheckoutApplyCouponView.as_view(), name='checkout_apply_coupon'),
    path('checkout/remove-coupon/', views.CheckoutRemoveCouponView.as_view(), name='checkout_remove_coupon'),
    path('checkout/confirm/', views.CheckoutConfirmarView.as_view(), name='checkout_confirm'),
    path('checkout/gateway/', views.GatewaySimuladaView.as_view(), name='checkout_gateway'),
    path('checkout/return/', views.CheckoutReturnView.as_view(), name='checkout_return'),
    path('checkout/continue/<str:numero>/', views.CheckoutContinuePaymentView.as_view(), name='checkout_continue'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<str:numero>/', views.OrdenConfirmadaView.as_view(), name='order_confirmed'),
    path('order/<str:numero>/invoice/', views.OrderInvoiceView.as_view(), name='order_invoice'),
    path('order/<str:numero>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
]
