import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== 'undefined') {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const { state } = JSON.parse(authStorage);
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
          const { state } = JSON.parse(authStorage);
          if (state?.refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, null, {
              params: { refresh_token: state.refreshToken }
            });
            
            const newAuthState = {
              ...state,
              accessToken: response.data.access_token,
              refreshToken: response.data.refresh_token,
            };
            
            localStorage.setItem('auth-storage', JSON.stringify({ state: newAuthState }));
            
            originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Clear auth and redirect to login
        localStorage.removeItem('auth-storage');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', null, { params: { refresh_token: refreshToken } }),
};

// Users API
export const usersApi = {
  me: () => api.get('/users/me'),
  update: (data: { full_name?: string; email?: string }) => api.put('/users/me', data),
  updatePassword: (currentPassword: string, newPassword: string) =>
    api.put('/users/me/password', { current_password: currentPassword, new_password: newPassword }),
};

// Agents API
export const agentsApi = {
  list: (params?: { agent_type?: string; status?: string }) =>
    api.get('/agents/', { params }),
  get: (id: number) => api.get(`/agents/${id}`),
  create: (data: {
    agent_type: string;
    name: string;
    description?: string;
    config?: Record<string, unknown>;
    permissions?: Record<string, unknown>;
    can_execute_autonomously?: boolean;
    requires_approval?: boolean;
    max_daily_tasks?: number;
  }) => api.post('/agents/', data),
  update: (id: number, data: Partial<{
    name: string;
    description: string;
    config: Record<string, unknown>;
    permissions: Record<string, unknown>;
    can_execute_autonomously: boolean;
    requires_approval: boolean;
    max_daily_tasks: number;
  }>) => api.put(`/agents/${id}`, data),
  delete: (id: number) => api.delete(`/agents/${id}`),
  activate: (id: number) => api.post(`/agents/${id}/activate`),
  pause: (id: number) => api.post(`/agents/${id}/pause`),
};

// Tasks API
export const tasksApi = {
  list: (params?: { status?: string; priority?: string; agent_id?: number; limit?: number; offset?: number }) =>
    api.get('/tasks/', { params }),
  get: (id: number) => api.get(`/tasks/${id}`),
  create: (data: {
    agent_id: number;
    title: string;
    description?: string;
    task_type: string;
    priority?: string;
    input_data?: Record<string, unknown>;
    requires_approval?: boolean;
    scheduled_for?: string;
    deadline?: string;
  }) => api.post('/tasks/', data),
  update: (id: number, data: Partial<{
    title: string;
    description: string;
    priority: string;
    scheduled_for: string;
    deadline: string;
  }>) => api.put(`/tasks/${id}`, data),
  approve: (id: number) => api.post(`/tasks/${id}/approve`),
  reject: (id: number) => api.post(`/tasks/${id}/reject`),
  cancel: (id: number) => api.post(`/tasks/${id}/cancel`),
};

// Integrations API
export const integrationsApi = {
  list: () => api.get('/integrations/'),
  get: (id: number) => api.get(`/integrations/${id}`),
  create: (data: {
    integration_type: string;
    provider: string;
    name: string;
    config?: Record<string, unknown>;
  }) => api.post('/integrations/', data),
  update: (id: number, data: Partial<{
    name: string;
    config: Record<string, unknown>;
    status: string;
  }>) => api.put(`/integrations/${id}`, data),
  delete: (id: number) => api.delete(`/integrations/${id}`),
};

// Subscriptions API
export const subscriptionsApi = {
  current: () => api.get('/subscriptions/current'),
  upgrade: (tier: string) => api.post('/subscriptions/upgrade', { tier }),
  cancel: () => api.post('/subscriptions/cancel'),
  getBillingHistory: () => api.get('/subscriptions/billing-history'),
};

export default api;
