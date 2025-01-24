import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '../../api/client';
import { User, Invoice, Subscription } from '../../types/api';
import { toast } from 'react-hot-toast';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import InvoiceHistoryModal from '../../components/Admin/InvoiceHistoryModal';
import EditClientModal from '../../components/Admin/EditClientModal';

const AdminClients: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'private' | 'company'>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');
  const [selectedClient, setSelectedClient] = useState<User | null>(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  
  const queryClient = useQueryClient();

  const { data: clients, isLoading: clientsLoading, error } = useQuery<User[]>({
    queryKey: ['admin', 'clients'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/users');
      return response.data;
    },
  });

  const { data: subscriptions, isLoading: subscriptionsLoading } = useQuery<Subscription[]>({
    queryKey: ['admin', 'subscriptions'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/subscriptions');
      return response.data;
    },
  });

  const { data: invoices, isLoading: invoicesLoading } = useQuery<Invoice[]>({
    queryKey: ['admin', 'invoices'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/invoices');
      return response.data;
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({ userId, data }: { userId: number; data: Partial<User> }) => {
      const response = await apiClient.put(`/admin/users/${userId}`, data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Kunde erfolgreich aktualisiert');
    },
    onError: (error) => {
      toast.error(`Fehler beim Aktualisieren: ${error.message}`);
    },
  });

  const filteredClients = clients?.filter((client) => {
    const matchesSearch =
      client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (client.company_name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (client.contact_person?.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesType =
      filterType === 'all' || client.client_type === filterType;

    const matchesStatus =
      filterStatus === 'all' ||
      (filterStatus === 'active' ? client.is_active : !client.is_active);

    return matchesSearch && matchesType && matchesStatus;
  });

  if (error) {
    toast.error('Fehler beim Laden der Kunden');
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          Kundenverwaltung
        </h1>

        {/* Filters */}
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <input
              type="text"
              placeholder="Suche nach E-Mail, Firma oder Kontakt"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as 'all' | 'private' | 'company')}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
          >
            <option value="all">Alle Kundentypen</option>
            <option value="private">Privatkunden</option>
            <option value="company">Firmenkunden</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as 'all' | 'active' | 'inactive')}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
          >
            <option value="all">Alle Status</option>
            <option value="active">Aktiv</option>
            <option value="inactive">Inaktiv</option>
          </select>
        </div>

        {/* Clients Table */}
        <div className="mt-8 flex flex-col">
          <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Kunde
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Typ
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Status
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Abonnement
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                        Kontakt
                      </th>
                      <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                        <span className="sr-only">Aktionen</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
                    {clientsLoading || subscriptionsLoading || invoicesLoading ? (
                      <tr>
                        <td colSpan={6} className="text-center py-4">
                          <div className="flex justify-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                          </div>
                        </td>
                      </tr>
                    ) : filteredClients?.map((client) => (
                      <tr key={client.id}>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <div className="font-medium text-gray-900 dark:text-gray-100">
                            {client.company_name || client.email}
                          </div>
                          <div className="text-gray-500 dark:text-gray-400">
                            {client.company_name ? client.email : ''}
                          </div>
                          {client.billing_address && (
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {client.billing_address}
                            </div>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                          <div>{client.client_type === 'company' ? 'Firma' : 'Privat'}</div>
                          {client.vat_number && (
                            <div className="text-xs mt-1">USt-ID: {client.vat_number}</div>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <div className="flex flex-col space-y-2">
                            <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                              client.is_active
                                ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                                : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                            }`}>
                              {client.is_active ? 'Aktiv' : 'Inaktiv'}
                            </span>
                            <button
                              onClick={() => updateUserMutation.mutate({
                                userId: client.id,
                                data: { is_active: !client.is_active }
                              })}
                              className="text-xs text-blue-600 hover:text-blue-800"
                            >
                              {client.is_active ? 'Deaktivieren' : 'Aktivieren'}
                            </button>
                          </div>
                        </td>
                        <td className="px-3 py-4 text-sm">
                          {subscriptions?.find(s => s.user_id === client.id) ? (
                            <div className="space-y-2">
                              <div className="font-medium text-gray-900 dark:text-gray-100">
                                {subscriptions.find(s => s.user_id === client.id)?.package_type}
                              </div>
                              <div className="text-xs text-gray-500">
                                Start: {format(new Date(subscriptions.find(s => s.user_id === client.id)?.start_date || ''), 'dd.MM.yyyy', { locale: de })}
                              </div>
                              {subscriptions.find(s => s.user_id === client.id)?.end_date && (
                                <div className="text-xs text-gray-500">
                                  Ende: {format(new Date(subscriptions.find(s => s.user_id === client.id)?.end_date || ''), 'dd.MM.yyyy', { locale: de })}
                                </div>
                              )}
                              <div className="text-xs text-gray-500">
                                Status: {subscriptions.find(s => s.user_id === client.id)?.status}
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-500">Kein Abo</span>
                          )}
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <div className="space-y-2">
                            <div className="text-gray-900 dark:text-gray-100">
                              {client.phone_number || '-'}
                            </div>
                            {client.contact_person && (
                              <div className="text-xs text-gray-500">
                                Kontakt: {client.contact_person}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="relative py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                          <div className="space-y-2">
                            <button
                              onClick={() => {
                                setSelectedClient(client);
                                setShowEditModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 block"
                            >
                              Bearbeiten
                            </button>
                            <button
                              onClick={() => {
                                const invoiceList = invoices?.filter(i => i.user_id === client.id) || [];
                                if (invoiceList.length > 0) {
                                  setSelectedClient(client);
                                  setShowInvoiceModal(true);
                                } else {
                                  toast.info('Keine Rechnungen vorhanden');
                                }
                              }}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 block"
                            >
                              Rechnungen
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showInvoiceModal && selectedClient && (
        <InvoiceHistoryModal
          invoices={invoices?.filter(i => i.user_id === selectedClient.id) || []}
          onClose={() => {
            setShowInvoiceModal(false);
            setSelectedClient(null);
          }}
        />
      )}

      {showEditModal && selectedClient && (
        <EditClientModal
          client={selectedClient}
          onSave={async (data) => {
            try {
              await updateUserMutation.mutateAsync({
                userId: selectedClient.id,
                data
              });
              queryClient.invalidateQueries(['admin', 'clients']);
              setShowEditModal(false);
              setSelectedClient(null);
            } catch (error) {
              console.error('Error updating client:', error);
            }
          }}
          onClose={() => {
            setShowEditModal(false);
            setSelectedClient(null);
          }}
        />
      )}
    </div>
  );
};

export default AdminClients;
