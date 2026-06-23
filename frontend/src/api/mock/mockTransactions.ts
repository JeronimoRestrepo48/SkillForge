// Mock implementation of transactionsApi for demo mode
import { DEMO_ENROLLMENTS } from '../../data/mockData';
import type { Cart, Order, Enrollment } from '../../types/transactions';
import type { PaginatedResponse } from '../../types/catalog';

const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

export const mockTransactionsApi = {
  getCart: async (): Promise<Cart> => {
    await delay(100);
    return { count: 0, results: [], total: 0 };
  },

  addToCart: async (_payload: any): Promise<{ detail: string }> => {
    await delay();
    return { detail: 'Curso agregado al carrito (demo)' };
  },

  removeFromCart: async (_courseId: number): Promise<void> => {
    await delay();
  },

  validateCoupon: async (_payload: any): Promise<any> => {
    await delay();
    return { valid: true, code: 'DEMO2026', discount_percentage: 20, description: 'Cupón demo 20% off' };
  },

  confirmCheckout: async (): Promise<Order> => {
    await delay();
    return { id: 1, number: 'ORD-DEMO-001', user_id: 1, status: 'CONFIRMED', total: 89000 };
  },

  returnCheckout: async (_payload: any): Promise<Order> => {
    await delay();
    return { id: 1, number: 'ORD-DEMO-001', user_id: 1, status: 'CONFIRMED', total: 89000 };
  },

  getWompiParams: async (_orderNumber: string): Promise<any> => {
    await delay();
    return {
      public_key: 'pub_test_demo',
      signature: 'demo_signature',
      amount_in_cents: 8900000,
      reference: _orderNumber,
      currency: 'COP',
      redirect_url: '/payment/confirmation',
    };
  },

  getOrders: async (): Promise<Order[]> => {
    await delay();
    return [
      { id: 1, number: 'ORD-2026-001', user_id: 1, status: 'CONFIRMED', total: 89000 },
      { id: 2, number: 'ORD-2026-002', user_id: 1, status: 'CONFIRMED', total: 129000 },
      { id: 3, number: 'ORD-2026-003', user_id: 1, status: 'CONFIRMED', total: 150000 },
    ];
  },

  getEnrollments: async (_params?: any): Promise<PaginatedResponse<Enrollment>> => {
    await delay(200);
    return {
      count: DEMO_ENROLLMENTS.length,
      next: null,
      previous: null,
      results: DEMO_ENROLLMENTS,
    };
  },
};
