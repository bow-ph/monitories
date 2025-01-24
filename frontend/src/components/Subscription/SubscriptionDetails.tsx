import React from 'react';
import { Subscription } from '../../types/subscription';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

interface SubscriptionDetailsProps {
  subscription: Subscription;
  projectLimit?: {
    can_create: boolean;
    current_count: number;
    limit: number | null;
  };
  onCancelClick: () => void;
}

const SubscriptionDetails: React.FC<SubscriptionDetailsProps> = ({
  subscription,
  projectLimit,
  onCancelClick,
}) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {subscription.packageType === 'trial' ? 'Trial' :
               subscription.packageType === 'team' ? 'Team' : 'Enterprise'} Paket
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              {subscription.interval === '3 months' ? '3 Monate' : '12 Monate'}
            </p>
          </div>
          <span className={`px-2 py-1 text-sm rounded-full ${
            subscription.status === 'active'
              ? 'bg-green-100 text-green-800'
              : subscription.status === 'cancelled'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {subscription.status === 'active' ? 'Aktiv' :
             subscription.status === 'cancelled' ? 'Gekündigt' : 'Abgelaufen'}
          </span>
        </div>

        <div className="border-t border-gray-200 pt-4">
          <dl className="divide-y divide-gray-200">
            <div className="py-3 flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Startdatum</dt>
              <dd className="text-sm text-gray-900">
                {format(new Date(subscription.startDate), 'dd.MM.yyyy', { locale: de })}
              </dd>
            </div>
            {subscription.endDate && (
              <div className="py-3 flex justify-between">
                <dt className="text-sm font-medium text-gray-500">Enddatum</dt>
                <dd className="text-sm text-gray-900">
                  {format(new Date(subscription.endDate), 'dd.MM.yyyy', { locale: de })}
                </dd>
              </div>
            )}
            <div className="py-3 flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Preis</dt>
              <dd className="text-sm text-gray-900">
                {subscription.amount.toFixed(2)} € / {subscription.interval}
              </dd>
            </div>
            {projectLimit && (
              <div className="py-3 flex justify-between">
                <dt className="text-sm font-medium text-gray-500">Projekte</dt>
                <dd className="text-sm text-gray-900">
                  {projectLimit.current_count} / {projectLimit.limit || '∞'}
                </dd>
              </div>
            )}
          </dl>
        </div>

        {subscription.status === 'active' && (
          <div className="pt-4">
            <button
              onClick={onCancelClick}
              className="w-full px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Abonnement kündigen
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionDetails;
