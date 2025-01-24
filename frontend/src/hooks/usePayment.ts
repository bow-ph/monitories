import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { SubscriptionResponse } from '../types/api';

interface CreateCustomerParams {
  name: string;
  email: string;
  metadata?: Record<string, any>;
}

interface CreateSubscriptionParams {
  customerId: string;
  amount: number;
  interval: string;
  description: string;
}

export function usePayment() {
  const createCustomer = useMutation({
    mutationFn: async (params: CreateCustomerParams) => {
      const response = await apiClient.post('/payments/customers', params);
      return response.data;
    },
  });

  const createSubscription = useMutation<SubscriptionResponse, Error, CreateSubscriptionParams>({
    mutationFn: async (params: CreateSubscriptionParams) => {
      const response = await apiClient.post(
        `/payments/subscriptions/${params.customerId}`,
        {
          amount: params.amount,
          interval: params.interval,
          description: params.description,
        }
      );
      return response.data;
    },
  });

  const cancelSubscription = useMutation({
    mutationFn: async ({
      customerId,
      subscriptionId,
    }: {
      customerId: string;
      subscriptionId: string;
    }) => {
      const response = await apiClient.delete(
        `/payments/subscriptions/${customerId}/${subscriptionId}`
      );
      return response.data;
    },
  });

  const getSubscriptions = (customerId: string) =>
    useQuery({
      queryKey: ['subscriptions', customerId],
      queryFn: async () => {
        const response = await apiClient.get(
          `/payments/subscriptions/${customerId}`
        );
        return response.data;
      },
      enabled: !!customerId,
    });

  return {
    createCustomer,
    createSubscription,
    cancelSubscription,
    getSubscriptions,
  };
}
