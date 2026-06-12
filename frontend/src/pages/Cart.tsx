import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCartQuery, useRemoveFromCartMutation, useValidateCouponMutation } from '../hooks/useCart';

export const Cart: React.FC = () => {
  const navigate = useNavigate();
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<{ code: string; discountPercentage: number } | null>(null);
  const [couponError, setCouponError] = useState<string | null>(null);

  // Consulta del carrito
  const { data: cart, isLoading, error } = useCartQuery();

  // Mutación para remover del carrito
  const removeMutation = useRemoveFromCartMutation();

  // Mutación para validar cupón
  const validateCouponMutation = useValidateCouponMutation();

  const handleRemove = (courseId: number) => {
    removeMutation.mutate(courseId);
  };

  const handleApplyCoupon = (e: React.FormEvent) => {
    e.preventDefault();
    setCouponError(null);

    if (!couponCode.trim()) {
      setCouponError('Por favor ingresa un código de cupón.');
      return;
    }

    validateCouponMutation.mutate(
      { coupon_code: couponCode },
      {
        onSuccess: (data) => {
          if (data.valid) {
            setAppliedCoupon({
              code: data.code,
              discountPercentage: data.discount_percentage,
            });
            // Guardar cupón en sessionStorage para usarlo en checkout
            sessionStorage.setItem('applied_coupon', data.code);
          } else {
            setCouponError('Cupón inválido.');
            setAppliedCoupon(null);
            sessionStorage.removeItem('applied_coupon');
          }
        },
        onError: (err: any) => {
          setCouponError(err.response?.data?.detail || 'El cupón ingresado no es válido.');
          setAppliedCoupon(null);
          sessionStorage.removeItem('applied_coupon');
        },
      }
    );
  };

  const handleClearCoupon = () => {
    setAppliedCoupon(null);
    setCouponCode('');
    setCouponError(null);
    sessionStorage.removeItem('applied_coupon');
  };

  // Calcular subtotales
  const subtotal = cart?.total || 0;
  const discountAmount = appliedCoupon ? roundToTwoDecimals(subtotal * (appliedCoupon.discountPercentage / 100)) : 0;
  const total = Math.max(0, roundToTwoDecimals(subtotal - discountAmount));

  function roundToTwoDecimals(num: number): number {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary">Cargando tu carrito...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <p className="font-semibold text-lg">Error al cargar el carrito</p>
        <p className="text-sm text-text-secondary mt-1">Intenta recargar la página.</p>
      </div>
    );
  }

  const isCartEmpty = !cart || cart.count === 0;

  return (
    <div className="space-y-8 mt-4">
      {/* Título */}
      <div>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Tu Carrito de Compras</h1>
        <p className="text-text-secondary mt-2">Revisa los cursos seleccionados antes de proceder al pago</p>
      </div>

      {isCartEmpty ? (
        <div className="text-center py-20 bg-background-card border border-zinc-800 rounded-2xl">
          <p className="text-2xl font-bold mb-4">🛒 Tu carrito está vacío</p>
          <p className="text-sm text-text-secondary mb-8">¡Explora nuestro catálogo y comienza a aprender hoy mismo!</p>
          <Link
            to="/courses"
            className="px-6 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition"
          >
            Explorar Cursos
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Listado de cursos */}
          <div className="lg:col-span-2 space-y-4">
            {(Array.isArray(cart?.results) ? cart.results : []).map((item) => (
              <div
                key={item.course_id}
                className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-5 rounded-2xl border border-zinc-800 bg-background-card gap-4 transition shadow-md"
              >
                <div>
                  <h3 className="font-bold text-base text-white">{item.course_title}</h3>
                  <p className="text-xs text-text-muted mt-1">Cantidad: {item.quantity}</p>
                </div>
                <div className="flex items-center justify-between w-full sm:w-auto gap-6 border-t border-zinc-800/50 sm:border-none pt-4 sm:pt-0">
                  <span className="font-mono font-bold text-white">
                    ${item.unit_price.toLocaleString('es-CO')} COP
                  </span>
                  <button
                    onClick={() => handleRemove(item.course_id)}
                    disabled={removeMutation.isPending}
                    className="text-xs text-red-400 hover:text-red-350 hover:underline transition"
                  >
                    {removeMutation.isPending ? 'Quitando...' : 'Remover'}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Resumen e Ingreso de Cupón */}
          <div className="space-y-6">
            {/* Formulario de Cupón */}
            <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">¿Tienes un cupón?</h3>
              {appliedCoupon ? (
                <div className="flex items-center justify-between p-3 rounded-xl bg-primary/15 border border-primary/30">
                  <div>
                    <span className="text-xs text-primary-light font-mono font-bold">{appliedCoupon.code}</span>
                    <span className="text-xs text-text-secondary block">
                      {appliedCoupon.discountPercentage}% de descuento aplicado
                    </span>
                  </div>
                  <button
                    onClick={handleClearCoupon}
                    className="text-text-muted hover:text-white transition text-xs font-semibold"
                  >
                    Quitar
                  </button>
                </div>
              ) : (
                <form onSubmit={handleApplyCoupon} className="flex gap-2">
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="Código (Ej. WELCOME10)"
                    className="flex-1 px-3 py-2 text-xs bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary placeholder-text-muted uppercase transition"
                    disabled={validateCouponMutation.isPending}
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-zinc-800 hover:bg-zinc-750 text-xs font-semibold rounded-xl transition text-white"
                    disabled={validateCouponMutation.isPending}
                  >
                    {validateCouponMutation.isPending ? '...' : 'Aplicar'}
                  </button>
                </form>
              )}
              {couponError && <p className="text-xs text-red-400">{couponError}</p>}
            </div>

            {/* Ficha de Total */}
            <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card glass-effect space-y-4 shadow-xl relative">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-zinc-800/80">
                Resumen del pedido
              </h3>

              <div className="space-y-2 text-sm text-text-secondary">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-mono text-white">${subtotal.toLocaleString('es-CO')} COP</span>
                </div>
                {appliedCoupon && (
                  <div className="flex justify-between text-primary-light">
                    <span>Descuento ({appliedCoupon.discountPercentage}%)</span>
                    <span className="font-mono">-${discountAmount.toLocaleString('es-CO')} COP</span>
                  </div>
                )}
                <div className="flex justify-between text-base font-bold text-white pt-4 border-t border-zinc-800/50">
                  <span>Total</span>
                  <span className="font-mono text-primary-light">${total.toLocaleString('es-CO')} COP</span>
                </div>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition duration-200 shadow-md text-sm mt-4"
              >
                Proceder al checkout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
