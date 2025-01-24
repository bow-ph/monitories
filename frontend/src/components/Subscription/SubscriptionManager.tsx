import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '../../api/client';
import { Subscription, CancellationRequest } from '../../types/subscription';
import SubscriptionDetails from './SubscriptionDetails';
import CancelSubscriptionModal from './CancelSubscriptionModal';
import { toast } from 'react-hot-toast';

const SubscriptionManager: React.FC = () => {
  const [showCancelModal, setShowCancelModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: subscription, isLoading } = useQuery<Subscription>({
    queryKey: ['subscription', 'me'],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getMySubscription());
      return response.data;
    },
  });

  const { data: projectLimit } = useQuery({
    queryKey: ['subscription', 'project-limit'],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.checkProjectLimit());
      return response.data;
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async (data: CancellationRequest) => {
      const response = await apiClient.post(endpoints.cancelSubscription(), data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Abonnement erfolgreich gekündigt');
      queryClient.invalidateQueries(['subscription']);
      setShowCancelModal(false);
    },
    onError: (error) => {
      toast.error(`Fehler beim Kündigen: ${error.message}`);
    },
  });

  const handleCancel = (reason?: string) => {
    if (!subscription) return;
    
    cancelMutation.mutate({
      subscriptionId: subscription.id,
      reason,
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Kein aktives Abonnement gefunden</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <SubscriptionDetails
        subscription={subscription}
        projectLimit={projectLimit}
        onCancelClick={() => setShowCancelModal(true)}
      />

      {showCancelModal && (
        <CancelSubscriptionModal
          onCancel={handleCancel}
          onClose={() => setShowCancelModal(false)}
        />
      )}
    </div>
  );
};

export default SubscriptionManager;
