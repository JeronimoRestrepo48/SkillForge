import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi } from '../api/transactions';
import { CheckoutReturnPayload } from '../types/transactions';

export const useOrdersQuery = () => {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => transactionsApi.getOrders(),
  });
};

export const useEnrollmentsQuery = (params?: { page?: number; page_size?: number }) => {
  return useQuery({
    queryKey: ['enrollments', params],
    queryFn: () => transactionsApi.getEnrollments(params),
  });
};

export const useConfirmCheckoutMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => transactionsApi.confirmCheckout(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
};

export const useReturnCheckoutMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CheckoutReturnPayload) => transactionsApi.returnCheckout(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['enrollments'] });
    },
  });
};
