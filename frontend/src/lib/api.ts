/**
 * API client for backend endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<{ data: T }> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return { data };
}

export const authAPI = {
  async getProfile() {
    return request('/v1/auth/profile/');
  },
  
  async login(email: string, password: string) {
    return request('/v1/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
  
  async logout() {
    return request('/v1/auth/logout/', {
      method: 'POST',
    });
  },
};

export const analyticsAPI = {
  async getLeadSummary() {
    return request('/v1/analytics/leads/summary/');
  },
  
  async getScoreDistribution() {
    return request('/v1/analytics/scores/distribution/');
  },
};
