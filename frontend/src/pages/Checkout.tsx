import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartQuery } from '../hooks/useCart';
import { useConfirmCheckoutMutation } from '../hooks/useOrders';
import { transactionsApi } from '../api/transactions';

export const Checkout: React.FC = () => {
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Consulta del carrito
  const { data: cart, isLoading, error } = useCartQuery();

  // Recuperar cupón guardado
  const appliedCouponCode = sessionStorage.getItem('applied_coupon');
  const discountRate = appliedCouponCode === 'WELCOME10' ? 0.10 : appliedCouponCode === 'STUDENT15' ? 0.15 : 0.0;

  // Mutaciones de compra
  const confirmCheckoutMutation = useConfirmCheckoutMutation();

  const subtotal = cart?.total || 0;
  const discountAmount = roundToTwoDecimals(subtotal * discountRate);
  const total = Math.max(0, roundToTwoDecimals(subtotal - discountAmount));

  function roundToTwoDecimals(num: number): number {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  const handlePaymentWompi = async () => {
    setPaymentLoading(true);
    setPaymentError(null);

    try {
      // 1. Confirmar checkout en el backend para generar la orden en PENDING
      const order = await confirmCheckoutMutation.mutateAsync();

      // 2. MOCK: Simular pago exitoso automáticamente y notificar al backend
      await transactionsApi.returnCheckout({
        order_number: order.number,
        result: 'success'
      });

      // 3. Limpiar datos de cupones locales
      sessionStorage.removeItem('applied_coupon');

      // 4. Redirigir al usuario al dashboard
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Error al iniciar el checkout con Wompi', err);
      setPaymentError(
        err.response?.data?.detail || 'Ocurrió un error al conectar con Wompi. Intenta de nuevo.'
      );
      setPaymentLoading(false);
    }
  };

  if (isLoading || paymentLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary font-medium">
            {paymentLoading ? 'Conectando con pasarela y procesando pago...' : 'Cargando resumen...'}
          </p>
        </div>
      </div>
    );
  }

  if (error || !cart || cart.count === 0) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <p className="font-semibold text-lg">Tu carrito está vacío o no se pudo cargar</p>
        <Link to="/courses" className="mt-4 inline-block px-6 py-2 bg-zinc-800 text-white rounded-xl text-xs hover:bg-zinc-700">
          Explorar cursos
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 mt-4">
      {/* Título */}
      <div>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Checkout</h1>
        <p className="text-text-secondary mt-2">Confirma tu pedido y simula el pago con Wompi</p>
      </div>

      {paymentError && (
        <div className="bg-red-900/30 border border-red-500/50 text-red-200 text-sm p-4 rounded-xl flex items-start gap-2">
          <span>⚠️ Error: {paymentError}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Resumen del pedido */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-bold tracking-tight text-white mb-2">Cursos incluidos</h2>
          <div className="divide-y divide-zinc-850 border border-zinc-800 bg-background-card rounded-2xl overflow-hidden shadow-md">
            {(Array.isArray(cart?.results) ? cart.results : []).map((item) => (
              <div key={item.course_id} className="p-5 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-sm text-white">{item.course_title}</h3>
                  <span className="text-xs text-text-muted">Acceso digital ilimitado</span>
                </div>
                <span className="font-mono text-sm text-text-secondary">
                  ${item.unit_price.toLocaleString('es-CO')} COP
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Ficha de Pago */}
        <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card glass-effect space-y-6 shadow-xl relative">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-zinc-800/80">
            Detalle financiero
          </h3>

          <div className="space-y-3 text-sm text-text-secondary">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span className="font-mono text-white">${subtotal.toLocaleString('es-CO')} COP</span>
            </div>
            {appliedCouponCode && (
              <div className="flex justify-between text-primary-light">
                <span>Descuento ({appliedCouponCode})</span>
                <span className="font-mono">-${discountAmount.toLocaleString('es-CO')} COP</span>
              </div>
            )}
            <div className="flex justify-between text-base font-bold text-white pt-4 border-t border-zinc-800/50">
              <span>Total a pagar</span>
              <span className="font-mono text-primary-light">${total.toLocaleString('es-CO')} COP</span>
            </div>
          </div>

          <div className="pt-4 space-y-3">
            <button
              onClick={handlePaymentWompi}
              className="w-full py-3.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition duration-200 shadow-md text-sm flex justify-center items-center gap-2"
            >
              💳 Pagar con Wompi
            </button>
            <Link
              to="/cart"
              className="w-full block text-center py-2.5 bg-zinc-900 border border-zinc-800 text-text-secondary hover:text-white text-xs font-semibold rounded-xl transition"
            >
              Atrás al Carrito
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
