import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import SubscriptionDetails from '../SubscriptionDetails';

describe('SubscriptionDetails', () => {
  const mockSubscription = {
    id: 1,
    userId: 1,
    mollieId: 'sub_test',
    customerId: 'cust_test',
    packageType: 'team',
    projectLimit: 10,
    status: 'active',
    amount: 119.0,
    interval: '3 months',
    startDate: '2024-01-01T00:00:00Z',
    endDate: '2024-04-01T00:00:00Z',
  };

  const mockProjectLimit = {
    can_create: true,
    current_count: 5,
    limit: 10,
  };

  const mockOnCancelClick = jest.fn();

  it('renders subscription details correctly', () => {
    render(
      <SubscriptionDetails
        subscription={mockSubscription}
        projectLimit={mockProjectLimit}
        onCancelClick={mockOnCancelClick}
      />
    );

    // Check package type and status
    expect(screen.getByText('Team Paket')).toBeInTheDocument();
    expect(screen.getByText('Aktiv')).toBeInTheDocument();

    // Check dates
    expect(screen.getByText('01.01.2024')).toBeInTheDocument(); // Start date
    expect(screen.getByText('01.04.2024')).toBeInTheDocument(); // End date

    // Check price and interval
    expect(screen.getByText('119.00 € / 3 months')).toBeInTheDocument();

    // Check project limit
    expect(screen.getByText('5 / 10')).toBeInTheDocument();
  });

  it('shows cancel button only for active subscriptions', () => {
    const activeSubscription = { ...mockSubscription, status: 'active' };
    const cancelledSubscription = { ...mockSubscription, status: 'cancelled' };

    // Test with active subscription
    const { rerender } = render(
      <SubscriptionDetails
        subscription={activeSubscription}
        projectLimit={mockProjectLimit}
        onCancelClick={mockOnCancelClick}
      />
    );
    expect(screen.getByText('Abonnement kündigen')).toBeInTheDocument();

    // Test with cancelled subscription
    rerender(
      <SubscriptionDetails
        subscription={cancelledSubscription}
        projectLimit={mockProjectLimit}
        onCancelClick={mockOnCancelClick}
      />
    );
    expect(screen.queryByText('Abonnement kündigen')).not.toBeInTheDocument();
  });

  it('handles cancel button click', () => {
    render(
      <SubscriptionDetails
        subscription={mockSubscription}
        projectLimit={mockProjectLimit}
        onCancelClick={mockOnCancelClick}
      />
    );

    fireEvent.click(screen.getByText('Abonnement kündigen'));
    expect(mockOnCancelClick).toHaveBeenCalledTimes(1);
  });

  it('displays unlimited projects for enterprise subscription without limit', () => {
    const enterpriseSubscription = {
      ...mockSubscription,
      packageType: 'enterprise',
      projectLimit: null,
    };

    const unlimitedProjectLimit = {
      can_create: true,
      current_count: 5,
      limit: null,
    };

    render(
      <SubscriptionDetails
        subscription={enterpriseSubscription}
        projectLimit={unlimitedProjectLimit}
        onCancelClick={mockOnCancelClick}
      />
    );

    expect(screen.getByText('5 / ∞')).toBeInTheDocument();
  });
});
