import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/api/v1/auth/login/', credentials),
  
  getProfile: () =>
    api.get('/api/v1/auth/profile/'),
  
  logout: () =>
    api.post('/api/v1/auth/logout/'),
};

// Analytics API
export const analyticsAPI = {
  getLeadSummary: () =>
    api.get('/api/v1/analytics/leads/summary/'),
  
  getLeadTrends: (params?: { days?: number }) =>
    api.get('/api/v1/analytics/leads/trends/', { params }),
  
  getScoreDistribution: () =>
    api.get('/api/v1/analytics/scores/distribution/'),
};

// Leads API
export const leadsAPI = {
  getLeads: (params?: { page?: number; limit?: number; search?: string }) =>
    api.get('/api/v1/leads/', { params }),
  
  getLead: (id: number) =>
    api.get(`/api/v1/leads/${id}/`),
  
  createLead: (data: any) =>
    api.post('/api/v1/leads/', data),
  
  updateLead: (id: number, data: any) =>
    api.put(`/api/v1/leads/${id}/`, data),
  
  deleteLead: (id: number) =>
    api.delete(`/api/v1/leads/${id}/`),
};

export default api;
