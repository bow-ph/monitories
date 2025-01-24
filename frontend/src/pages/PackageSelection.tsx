import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Package } from '../types/api';
import PackageCard from '../components/Packages/PackageCard';
import { usePayment } from '../hooks/usePayment';
import { toast } from 'react-hot-toast';

const PackageSelection = () => {
  const [selectedPackage, setSelectedPackage] = useState<number | null>(null);

  const { data: packages, isLoading } = useQuery<Package[]>({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await apiClient.get('/packages');
      return response.data;
    },
  });

  const { createCustomer, createSubscription } = usePayment();

  const handlePackageSelect = async (packageId: number) => {
    setSelectedPackage(packageId);
  };

  const handleCheckout = async () => {
    if (!selectedPackage) return;

    const selectedPkg = packages?.find(pkg => pkg.id === selectedPackage);
    if (!selectedPkg) return;

    try {
      toast.loading('Erstelle Kundenkonto...');
      const customer = await createCustomer.mutateAsync({
        name: "Test Customer", // TODO: Get from user context
        email: "test@example.com", // TODO: Get from user context
      });

      toast.loading('Erstelle Abonnement...');
      const subscription = await createSubscription.mutateAsync({
        customerId: customer.id,
        amount: selectedPkg.price,
        interval: "3 months", // Based on package requirements
        description: `Subscription for ${selectedPkg.name} package`,
      });

      if (subscription.paymentUrl) {
        toast.success('Weiterleitung zur Zahlung...');
        window.location.href = subscription.paymentUrl;
      } else {
        toast.error('Fehler bei der Zahlungsabwicklung');
      }
    } catch (error) {
      toast.error('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.');
      console.error('Error creating subscription:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Wählen Sie Ihr Paket
        </h2>
        <p className="mt-4 text-lg text-gray-500">
          Wählen Sie das passende Paket für Ihre Bedürfnisse
        </p>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-3">
        {packages?.map((pkg) => (
          <PackageCard
            key={pkg.id}
            package={pkg}
            isSelected={selectedPackage === pkg.id}
            onSelect={() => handlePackageSelect(pkg.id)}
          />
        ))}
      </div>

      {selectedPackage && (
        <div className="mt-8 text-center">
          <button
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleCheckout}
            disabled={createCustomer.isPending || createSubscription.isPending}
          >
            {createCustomer.isPending || createSubscription.isPending ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Verarbeitung...
              </>
            ) : (
              'Weiter zur Zahlung'
            )}
          </button>
          {(createCustomer.isError || createSubscription.isError) && (
            <p className="mt-2 text-sm text-red-600">
              Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default PackageSelection;
