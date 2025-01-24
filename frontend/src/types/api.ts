// User Types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  subscription_type?: string;
  subscription_end_date?: string;
  client_type: 'private' | 'company';
  company_name?: string;
  vat_number?: string;
  billing_address?: string;
  shipping_address?: string;
  phone_number?: string;
  contact_person?: string;
  created_at: string;
  updated_at?: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  user_id: number;
  subscription_id: number;
  issue_date: string;
  total_amount: number;
  pdf_path: string;
  status: 'pending' | 'paid' | 'cancelled';
  created_at: string;
  updated_at?: string;
}

// Project Analysis Types
export interface Task {
  id?: number;
  description: string;
  estimated_hours: number;
  actual_hours?: number;
  status: 'pending' | 'in_progress' | 'completed';
  confidence_score: number;
  confidence_rationale?: string;
  complexity?: 'low' | 'medium' | 'high';
  requires_client_input?: boolean;
  technical_requirements?: string[];
  deliverables?: string[];
}

export interface PdfAnalysisResponse {
  status: string;
  document_analysis: {
    type: 'quote' | 'order' | 'proposal' | 'specification' | 'other';
    context: string;
    client_type: 'agency' | 'business' | 'individual';
    complexity_level: 'low' | 'medium' | 'high';
    clarity_score: number;
  };
  tasks: Task[];
  total_estimated_hours: number;
  risk_factors: string[];
  confidence_analysis: {
    overall_confidence: number;
    rationale: string;
    improvement_suggestions: string[];
    accuracy_factors: {
      document_clarity: number;
      technical_complexity: number;
      dependency_risk: number;
      client_input_risk: number;
    };
  };
}

export interface FinancialImpact {
  risk_level: 'low' | 'medium' | 'high';
  potential_cost_overrun: number;
  confidence: number;
}

export interface TimeImpact {
  risk_level: 'low' | 'medium' | 'high';
  potential_delay_hours: number;
  confidence: number;
}

export interface Recommendation {
  type: 'cost' | 'time' | 'resource';
  description: string;
  priority: 'low' | 'medium' | 'high';
}

export interface ProactiveHintsResponse {
  status: string;
  financial_impact: FinancialImpact;
  time_impact: TimeImpact;
  recommendations: Recommendation[];
  time_validation?: {
    validated_tasks: Array<{
      task_id: string;
      original_estimate: number;
      suggested_estimate: number;
      confidence: number;
      adjustment_reason: string;
    }>;
    overall_assessment: {
      estimation_quality: 'good' | 'needs_review' | 'poor';
      suggestions: string[];
    };
  };
}

// Package Types
export interface Package {
  id: number;
  name: string;
  description: string;
  price: number;
  interval: string;
  trial_days: number;
  max_projects: number;
  features: string[];
  button_text: string;
  sort_order: number;
  is_active: boolean;
}

export interface SubscriptionResponse {
  id: string;
  customerId: string;
  status: 'active' | 'pending' | 'canceled' | 'suspended';
  paymentUrl?: string;
  createdAt: string;
  startDate: string;
  nextPaymentDate?: string;
}

// CalDAV Types
export interface CalDAVTask {
  uid: string;
  description: string;
  start_date: string;
  end_date: string;
  estimated_hours: number;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
}

export interface CalDAVResponse {
  tasks: CalDAVTask[];
  caldav_url: string;
}
