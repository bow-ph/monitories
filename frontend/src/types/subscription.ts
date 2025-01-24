import { User } from './api';

export type SubscriptionTier = 'trial' | 'team' | 'enterprise';
export type SubscriptionStatus = 'active' | 'cancelled' | 'expired';

export interface SubscriptionPlan {
  id: number;
  name: string;
  tier: SubscriptionTier;
  price: number;
  interval: string;
  projectLimit: number;
  features: string[];
  buttonText: string;
  isActive: boolean;
}

export interface Subscription {
  id: number;
  userId: number;
  mollieId: string;
  customerId: string;
  packageId: number;
  packageType: SubscriptionTier;
  projectLimit: number;
  status: SubscriptionStatus;
  amount: number;
  interval: string;
  startDate: string;
  endDate?: string;
  lastPaymentDate?: string;
  nextPaymentDate?: string;
  createdAt: string;
}

export interface SubscriptionDetails extends Subscription {
  user: User;
  plan: SubscriptionPlan;
}

export interface CancellationRequest {
  subscriptionId: number;
  reason?: string;
  feedback?: string;
}

export interface SubscriptionUpdateRequest {
  status?: SubscriptionStatus;
  projectLimit?: number;
  endDate?: string;
}
