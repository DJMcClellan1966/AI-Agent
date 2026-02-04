// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  subscription_tier: 'free' | 'pro' | 'premium';
  subscription_status: 'active' | 'cancelled' | 'expired';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

// Agent types
export type AgentType = 'email' | 'scheduler' | 'finance' | 'planning' | 'coordinator';
export type AgentStatus = 'active' | 'paused' | 'inactive';

export interface Agent {
  id: number;
  user_id: number;
  agent_type: AgentType;
  name: string;
  description?: string;
  status: AgentStatus;
  config: Record<string, unknown>;
  permissions: Record<string, unknown>;
  can_execute_autonomously: boolean;
  requires_approval: boolean;
  max_daily_tasks: number;
  created_at: string;
  updated_at: string;
}

// Task types
export type TaskStatus = 
  | 'pending'
  | 'awaiting_approval'
  | 'approved'
  | 'rejected'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type TaskPriority = 'urgent' | 'high' | 'medium' | 'low';

export interface Task {
  id: number;
  user_id: number;
  agent_id: number;
  title: string;
  description?: string;
  task_type: string;
  status: TaskStatus;
  priority: TaskPriority;
  input_data: Record<string, unknown>;
  result?: Record<string, unknown>;
  error?: string;
  requires_approval: boolean;
  scheduled_for?: string;
  deadline?: string;
  approved_at?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

// Integration types
export type IntegrationType = 
  | 'gmail'
  | 'outlook'
  | 'google_calendar'
  | 'outlook_calendar'
  | 'stripe'
  | 'plaid'
  | 'slack'
  | 'zapier';

export interface Integration {
  id: number;
  user_id: number;
  integration_type: IntegrationType;
  name: string;
  is_active: boolean;
  config: Record<string, unknown>;
  last_sync?: string;
  created_at: string;
  updated_at: string;
}

// Subscription types
export interface Subscription {
  id: number;
  user_id: number;
  tier: 'free' | 'pro' | 'premium';
  status: 'active' | 'cancelled' | 'expired' | 'trial';
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiError {
  detail: string;
  type?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Auth types
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}
