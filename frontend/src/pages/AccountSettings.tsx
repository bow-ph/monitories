import React from 'react';
import { usePayment } from '../hooks/usePayment';
import { toast } from 'react-hot-toast';
import { SubscriptionResponse } from '../types/api';
import InvoiceList from '../components/Invoices/InvoiceList';

const AccountSettings: React.FC = () => {
  // TODO: Get actual customer ID from user context
  const customerId = "test-customer-id";
  
  const { getSubscriptions, cancelSubscription } = usePayment();
  const { data: subscriptions, isLoading, error } = getSubscriptions(customerId);

  const handleCancelSubscription = async (subscriptionId: string) => {
    if (window.confirm('Sind Sie sicher, dass Sie Ihr Abonnement kündigen möchten?')) {
      try {
        await cancelSubscription.mutateAsync({ customerId, subscriptionId });
        toast.success('Ihr Abonnement wurde erfolgreich gekündigt.');
      } catch (error) {
        toast.error('Fehler beim Kündigen des Abonnements. Bitte versuchen Sie es später erneut.');
        console.error('Error canceling subscription:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusBadgeColor = (status: SubscriptionResponse['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Mein Konto</h1>
        
        <div className="mt-6 space-y-8">
          <div>
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Aktive Abonnements</h2>
            
            <div className="mt-4 space-y-4">
              {subscriptions?.map((subscription: SubscriptionResponse) => (
              <div
                key={subscription.id}
                className="bg-white dark:bg-gray-800 shadow rounded-lg p-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(
                        subscription.status
                      )}`}
                    >
                      {subscription.status === 'active' ? 'Aktiv' :
                       subscription.status === 'pending' ? 'Ausstehend' :
                       subscription.status === 'canceled' ? 'Gekündigt' :
                       subscription.status}
                    </span>
                    
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Gestartet am {formatDate(subscription.startDate)}
                      </p>
                      {subscription.nextPaymentDate && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Nächste Zahlung am {formatDate(subscription.nextPaymentDate)}
                        </p>
                      )}
                    </div>
                  </div>

                  {subscription.status === 'active' && (
                    <button
                      onClick={() => handleCancelSubscription(subscription.id)}
                      className="ml-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:bg-red-900 dark:text-red-100 dark:hover:bg-red-800"
                      disabled={cancelSubscription.isPending}
                    >
                      {cancelSubscription.isPending ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-red-700 dark:text-red-100" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Wird gekündigt...
                        </>
                      ) : (
                        'Abonnement kündigen'
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {(!subscriptions || subscriptions.length === 0) && (
              <p className="text-gray-500 dark:text-gray-400">
                Sie haben derzeit keine aktiven Abonnements.
              </p>
            )}
          </div>
          </div>

          <div>
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Rechnungen</h2>
            <div className="mt-4">
              <InvoiceList />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountSettings;
