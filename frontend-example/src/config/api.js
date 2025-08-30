import axios from 'axios';

// Update this with your Railway app URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app-name.railway.app/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => apiClient.post('/token-auth/', credentials),
  getProfile: () => apiClient.get('/users/profile/'),
  getToken: () => apiClient.get('/users/token/'),
};

// Questions API
export const questionsAPI = {
  list: () => apiClient.get('/questions/'),
  get: (id) => apiClient.get(`/questions/${id}/`),
  create: (data) => apiClient.post('/questions/', data),
  update: (id, data) => apiClient.put(`/questions/${id}/`, data),
  delete: (id) => apiClient.delete(`/questions/${id}/`),
  getChoices: (id) => apiClient.get(`/questions/${id}/choices/`),
  getScoringModel: (id) => apiClient.get(`/questions/${id}/scoring_model/`),
  getRecommendation: (id) => apiClient.get(`/questions/${id}/recommendation/`),
};

// Choices API
export const choicesAPI = {
  list: () => apiClient.get('/choices/'),
  create: (data) => apiClient.post('/choices/', data),
  update: (id, data) => apiClient.put(`/choices/${id}/`, data),
  delete: (id) => apiClient.delete(`/choices/${id}/`),
};

// Scoring Models API
export const scoringModelsAPI = {
  list: () => apiClient.get('/scoring-models/'),
  get: (id) => apiClient.get(`/scoring-models/${id}/`),
  create: (data) => apiClient.post('/scoring-models/', data),
  update: (id, data) => apiClient.put(`/scoring-models/${id}/`, data),
  delete: (id) => apiClient.delete(`/scoring-models/${id}/`),
  getValueRanges: (id) => apiClient.get(`/scoring-models/${id}/value_ranges/`),
  getDatesRanges: (id) => apiClient.get(`/scoring-models/${id}/dates_ranges/`),
};

// Value Ranges API
export const valueRangesAPI = {
  list: () => apiClient.get('/value-ranges/'),
  create: (data) => apiClient.post('/value-ranges/', data),
  update: (id, data) => apiClient.put(`/value-ranges/${id}/`, data),
  delete: (id) => apiClient.delete(`/value-ranges/${id}/`),
};

// Date Ranges API
export const dateRangesAPI = {
  list: () => apiClient.get('/dates-ranges/'),
  create: (data) => apiClient.post('/dates-ranges/', data),
  update: (id, data) => apiClient.put(`/dates-ranges/${id}/`, data),
  delete: (id) => apiClient.delete(`/dates-ranges/${id}/`),
};

// Recommendations API
export const recommendationsAPI = {
  list: () => apiClient.get('/recommendations/'),
  get: (id) => apiClient.get(`/recommendations/${id}/`),
  create: (data) => apiClient.post('/recommendations/', data),
  update: (id, data) => apiClient.put(`/recommendations/${id}/`, data),
  delete: (id) => apiClient.delete(`/recommendations/${id}/`),
};

// Leads API
export const leadsAPI = {
  create: (data) => apiClient.post('/leads/', data),
  get: (id) => apiClient.get(`/leads/${id}/`),
};

// Analytics API
export const analyticsAPI = {
  getLeadSummary: () => apiClient.get('/analytics/lead_summary/'),
  getQuestionAnalytics: () => apiClient.get('/analytics/question_analytics/'),
  getRecommendationEffectiveness: () => apiClient.get('/analytics/recommendation_effectiveness/'),
};

export default apiClient;
