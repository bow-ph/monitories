
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Package } from '../../types/api';
import { toast } from 'react-hot-toast';

const PackageAdmin = () => {
  const queryClient = useQueryClient();
  const [newPackage, setNewPackage] = useState<Partial<Package>>({
    name: '',
    description: '',
    price: 0,
    interval: '3 months',
    trial_days: 0,
    max_projects: 1,
    features: [],
    button_text: '',
    sort_order: 0,
    is_active: true
  });

  const { data: packages, isLoading } = useQuery<Package[]>({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await apiClient.get('/packages');
      return response.data;
    },
  });

  const createPackageMutation = useMutation({
    mutationFn: async (newPackage: Partial<Package>) => {
      const response = await apiClient.post('/packages', newPackage);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      toast.success('Paket erfolgreich erstellt');
      setNewPackage({
        name: '',
        description: '',
        price: 0,
        interval: '3 months',
        trial_days: 0,
        max_projects: 1,
        features: [],
        button_text: '',
        sort_order: 0,
        is_active: true
      });
    },
    onError: (error: any) => {
      toast.error(`Fehler beim Erstellen: ${error.message}`);
    }
  });

  const updatePackageMutation = useMutation({
    mutationFn: async (updatedPackage: Package) => {
      const response = await apiClient.put(`/packages/${updatedPackage.id}`, updatedPackage);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      toast.success('Paket erfolgreich aktualisiert');
    },
    onError: (error: any) => {
      toast.error(`Fehler beim Aktualisieren: ${error.message}`);
    }
  });

  const deletePackageMutation = useMutation({
    mutationFn: async (packageId: number) => {
      const response = await apiClient.delete(`/packages/${packageId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      toast.success('Paket erfolgreich gelöscht');
    },
    onError: (error: any) => {
      toast.error(`Fehler beim Löschen: ${error.message}`);
    }
  });

  const handlePackageUpdate = (pkg: Package) => {
    updatePackageMutation.mutate(pkg);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const handleCreatePackage = () => {
    createPackageMutation.mutate(newPackage);
  };

  const handleDeletePackage = (packageId: number) => {
    if (window.confirm('Sind Sie sicher, dass Sie dieses Paket löschen möchten?')) {
      deletePackageMutation.mutate(packageId);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Paket Verwaltung</h1>
        
        {/* Create New Package Form */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Neues Paket erstellen</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                value={newPackage.name}
                onChange={(e) => setNewPackage({ ...newPackage, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Preis</label>
              <input
                type="number"
                value={newPackage.price}
                onChange={(e) => setNewPackage({ ...newPackage, price: Number(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Intervall</label>
              <select
                value={newPackage.interval}
                onChange={(e) => setNewPackage({ ...newPackage, interval: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="3 months">3 Monate</option>
                <option value="6 months">6 Monate</option>
                <option value="12 months">12 Monate</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Testtage</label>
              <input
                type="number"
                value={newPackage.trial_days}
                onChange={(e) => setNewPackage({ ...newPackage, trial_days: Number(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Max. Projekte</label>
              <input
                type="number"
                value={newPackage.max_projects}
                onChange={(e) => setNewPackage({ ...newPackage, max_projects: Number(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Button Text</label>
              <input
                type="text"
                value={newPackage.button_text}
                onChange={(e) => setNewPackage({ ...newPackage, button_text: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
              <textarea
                value={newPackage.description}
                onChange={(e) => setNewPackage({ ...newPackage, description: e.target.value })}
                rows={3}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={handleCreatePackage}
              disabled={createPackageMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {createPackageMutation.isPending ? 'Wird erstellt...' : 'Paket erstellen'}
            </button>
          </div>
        </div>

        {/* Existing Packages List */}
        <h2 className="text-lg font-medium text-gray-900 mb-4">Vorhandene Pakete</h2>
        <div className="space-y-6">
          {packages?.map((pkg) => (
            <div key={pkg.id} className="bg-white shadow rounded-lg p-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={pkg.name}
                    onChange={(e) => handlePackageUpdate({ ...pkg, name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Preis</label>
                  <input
                    type="number"
                    value={pkg.price}
                    onChange={(e) => handlePackageUpdate({ ...pkg, price: Number(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
                  <textarea
                    value={pkg.description}
                    onChange={(e) => handlePackageUpdate({ ...pkg, description: e.target.value })}
                    rows={3}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Button Text</label>
                  <input
                    type="text"
                    value={pkg.button_text}
                    onChange={(e) => handlePackageUpdate({ ...pkg, button_text: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Intervall</label>
                <select
                  value={pkg.interval}
                  onChange={(e) => handlePackageUpdate({ ...pkg, interval: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="3 months">3 Monate</option>
                  <option value="6 months">6 Monate</option>
                  <option value="12 months">12 Monate</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Testtage</label>
                <input
                  type="number"
                  value={pkg.trial_days}
                  onChange={(e) => handlePackageUpdate({ ...pkg, trial_days: Number(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Max. Projekte</label>
                <input
                  type="number"
                  value={pkg.max_projects}
                  onChange={(e) => handlePackageUpdate({ ...pkg, max_projects: Number(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>

              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700">Features</label>
                <div className="mt-2 space-y-2">
                  {pkg.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={feature}
                        onChange={(e) => {
                          const newFeatures = [...pkg.features];
                          newFeatures[index] = e.target.value;
                          handlePackageUpdate({ ...pkg, features: newFeatures });
                        }}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                      <button
                        onClick={() => {
                          const newFeatures = pkg.features.filter((_, i) => i !== index);
                          handlePackageUpdate({ ...pkg, features: newFeatures });
                        }}
                        className="p-2 text-red-600 hover:text-red-800"
                      >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      handlePackageUpdate({
                        ...pkg,
                        features: [...pkg.features, ''],
                      });
                    }}
                    className="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-full text-blue-600 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Feature hinzufügen
                  </button>
                </div>
              </div>

              <div className="mt-4 flex justify-between">
                <button
                  onClick={() => handleDeletePackage(pkg.id)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Paket löschen
                </button>
                <div className="flex items-center">
                  <span className="mr-2 text-sm text-gray-500">Aktiv</span>
                  <input
                    type="checkbox"
                    checked={pkg.is_active}
                    onChange={(e) => handlePackageUpdate({ ...pkg, is_active: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PackageAdmin;
