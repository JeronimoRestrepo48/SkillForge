export interface CartItem {
  course_id: number;
  course_title: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Cart {
  count: number;
  results: CartItem[];
  total: number;
}

export interface CartItemAddPayload {
  course_id: number;
  quantity: number;
}

export interface CouponValidatePayload {
  coupon_code: string;
}

export interface CouponValidationResult {
  valid: boolean;
  code: string;
  discount_percentage: number;
  description: string;
}

export interface Order {
  id: number;
  number: string;
  user_id: number;
  status: 'PENDING' | 'CONFIRMED' | 'CANCELLED';
  total: number;
}

export interface CheckoutReturnPayload {
  order_number: string;
  result: 'success' | 'fail' | 'cancel';
}

export interface Enrollment {
  id: number;
  user_id: number;
  course_id: number;
  order_id: number | null;
  status: string; // 'ACTIVA', etc.
  enrolled_at: string;
}
