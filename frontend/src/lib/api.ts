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
    api.post('/api/token-auth/', credentials),
  
  getProfile: () =>
    api.get('/api/v1/users/profile/'),
  
  getToken: () =>
    api.get('/api/v1/users/token/'),
};

// Analytics API
export const analyticsAPI = {
  getLeadSummary: () =>
    api.get('/api/v1/analytics/lead_summary/'),
  
  getQuestionAnalytics: () =>
    api.get('/api/v1/analytics/question_analytics/'),
  
  getRecommendationEffectiveness: () =>
    api.get('/api/v1/analytics/recommendation_effectiveness/'),
};

// Questions API
export const questionsAPI = {
  getQuestions: () =>
    api.get('/api/v1/questions/'),
  
  getQuestion: (id: number) =>
    api.get(`/api/v1/questions/${id}/`),
  
  createQuestion: (data: any) =>
    api.post('/api/v1/questions/', data),
  
  updateQuestion: (id: number, data: any) =>
    api.put(`/api/v1/questions/${id}/`, data),
  
  deleteQuestion: (id: number) =>
    api.delete(`/api/v1/questions/${id}/`),
};

// Choices API
export const choicesAPI = {
  getChoices: () =>
    api.get('/api/v1/choices/'),
  
  getChoice: (id: number) =>
    api.get(`/api/v1/choices/${id}/`),
  
  createChoice: (data: any) =>
    api.post('/api/v1/choices/', data),
  
  updateChoice: (id: number, data: any) =>
    api.put(`/api/v1/choices/${id}/`, data),
  
  deleteChoice: (id: number) =>
    api.delete(`/api/v1/choices/${id}/`),
};

// Scoring Models API
export const scoringModelsAPI = {
  getScoringModels: () =>
    api.get('/api/v1/scoring-models/'),
  
  getScoringModel: (id: number) =>
    api.get(`/api/v1/scoring-models/${id}/`),
  
  createScoringModel: (data: any) =>
    api.post('/api/v1/scoring-models/', data),
  
  updateScoringModel: (id: number, data: any) =>
    api.put(`/api/v1/scoring-models/${id}/`, data),
  
  deleteScoringModel: (id: number) =>
    api.delete(`/api/v1/scoring-models/${id}/`),
};

// Value Ranges API
export const valueRangesAPI = {
  getValueRanges: () =>
    api.get('/api/v1/value-ranges/'),
  
  getValueRange: (id: number) =>
    api.get(`/api/v1/value-ranges/${id}/`),
  
  createValueRange: (data: any) =>
    api.post('/api/v1/value-ranges/', data),
  
  updateValueRange: (id: number, data: any) =>
    api.put(`/api/v1/value-ranges/${id}/`, data),
  
  deleteValueRange: (id: number) =>
    api.delete(`/api/v1/value-ranges/${id}/`),
};

// Date Ranges API
export const dateRangesAPI = {
  getDateRanges: () =>
    api.get('/api/v1/dates-ranges/'),
  
  getDateRange: (id: number) =>
    api.get(`/api/v1/dates-ranges/${id}/`),
  
  createDateRange: (data: any) =>
    api.post('/api/v1/dates-ranges/', data),
  
  updateDateRange: (id: number, data: any) =>
    api.put(`/api/v1/dates-ranges/${id}/`, data),
  
  deleteDateRange: (id: number) =>
    api.delete(`/api/v1/dates-ranges/${id}/`),
};

// Recommendations API
export const recommendationsAPI = {
  getRecommendations: () =>
    api.get('/api/v1/recommendations/'),
  
  getRecommendation: (id: number) =>
    api.get(`/api/v1/recommendations/${id}/`),
  
  createRecommendation: (data: any) =>
    api.post('/api/v1/recommendations/', data),
  
  updateRecommendation: (id: number, data: any) =>
    api.put(`/api/v1/recommendations/${id}/`, data),
  
  deleteRecommendation: (id: number) =>
    api.delete(`/api/v1/recommendations/${id}/`),
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
