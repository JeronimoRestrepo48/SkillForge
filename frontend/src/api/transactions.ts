import api from './axios';
import { 
  Cart, 
  CartItemAddPayload, 
  CouponValidatePayload, 
  CouponValidationResult, 
  Order, 
  CheckoutReturnPayload, 
  Enrollment 
} from '../types/transactions';
import { PaginatedResponse } from '../types/catalog';

export const transactionsApi = {
  // Obtener el estado actual del carrito
  getCart: async (): Promise<Cart> => {
    const response = await api.get<Cart>('/transactions/cart');
    return response.data;
  },

  // Agregar un curso al carrito
  addToCart: async (payload: CartItemAddPayload): Promise<{ detail: string }> => {
    const response = await api.post<{ detail: string }>('/transactions/cart/items', payload);
    return response.data;
  },

  // Eliminar un curso del carrito
  removeFromCart: async (courseId: number): Promise<void> => {
    await api.delete(`/transactions/cart/items/${courseId}`);
  },

  // Validar un cupón de descuento
  validateCoupon: async (payload: CouponValidatePayload): Promise<CouponValidationResult> => {
    const response = await api.post<CouponValidationResult>('/transactions/coupons/validate', payload);
    return response.data;
  },

  // Crear una nueva orden (Checkout Confirm)
  confirmCheckout: async (): Promise<Order> => {
    const response = await api.post<Order>('/transactions/checkout/confirm');
    return response.data;
  },

  // Confirmar el pago simulado de la orden (Checkout Return)
  returnCheckout: async (payload: CheckoutReturnPayload): Promise<Order> => {
    const response = await api.post<Order>('/transactions/checkout/return', payload);
    return response.data;
  },

  // Obtener parámetros firmados para Wompi
  getWompiParams: async (orderNumber: string): Promise<{
    public_key: string;
    signature: string;
    amount_in_cents: number;
    reference: string;
    currency: string;
    redirect_url: string;
  }> => {
    const response = await api.get<{
      public_key: string;
      signature: string;
      amount_in_cents: number;
      reference: string;
      currency: string;
      redirect_url: string;
    }>(`/transactions/checkout/wompi-params/${orderNumber}`);
    return response.data;
  },

  // Listar órdenes del estudiante
  getOrders: async (): Promise<Order[]> => {
    const response = await api.get<Order[]>('/transactions/orders');
    return response.data;
  },

  // Listar las inscripciones del estudiante logueado (cursos activos)
  getEnrollments: async (params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<Enrollment>> => {
    const response = await api.get<PaginatedResponse<Enrollment>>('/transactions/enrollments', { params });
    return response.data;
  },
};
