import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Invoice } from '../../types/api';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

const InvoiceList: React.FC = () => {
  const { data: invoices, isLoading } = useQuery<Invoice[]>({
    queryKey: ['invoices'],
    queryFn: async () => {
      const response = await apiClient.get('/invoices');
      return response.data;
    },
  });

  const handleDownload = (invoiceId: number) => {
    window.open(`${process.env.REACT_APP_API_URL}/invoices/${invoiceId}/download`, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!invoices?.length) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        Keine Rechnungen verfügbar
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Rechnungsnummer
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Datum
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Betrag
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Aktion
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {invoices.map((invoice) => (
            <tr key={invoice.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                {invoice.invoice_number}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {format(new Date(invoice.issue_date), 'dd.MM.yyyy', { locale: de })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                €{invoice.total_amount.toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  invoice.status === 'paid'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : invoice.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {invoice.status === 'paid' ? 'Bezahlt' :
                   invoice.status === 'pending' ? 'Ausstehend' : 'Storniert'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => handleDownload(invoice.id)}
                  className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  PDF herunterladen
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InvoiceList;
