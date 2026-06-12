import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi } from '../api/transactions';
import { CartItemAddPayload, CouponValidatePayload } from '../types/transactions';

export const useCartQuery = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['cart'],
    queryFn: () => transactionsApi.getCart(),
    enabled,
  });
};

export const useAddToCartMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CartItemAddPayload) => transactionsApi.addToCart(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
};

export const useRemoveFromCartMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (courseId: number) => transactionsApi.removeFromCart(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
};

export const useValidateCouponMutation = () => {
  return useMutation({
    mutationFn: (payload: CouponValidatePayload) => transactionsApi.validateCoupon(payload),
  });
};
