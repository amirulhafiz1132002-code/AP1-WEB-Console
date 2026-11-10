import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// GitHub API endpoints
export const githubAPI = {
  /**
   * Get GitHub user profile
   */
  getUser: async () => {
    try {
      const response = await apiClient.get('/github/user');
      return response.data;
    } catch (error) {
      console.error('Error fetching GitHub user:', error);
      throw error;
    }
  },

  /**
   * Get GitHub repositories
   * @param {string} category - Optional category filter (core, tools, research, backend, resources)
   */
  getRepositories: async (category = null) => {
    try {
      const params = category && category !== 'all' ? { category } : {};
      const response = await apiClient.get('/github/repositories', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching GitHub repositories:', error);
      throw error;
    }
  },

  /**
   * Get GitHub aggregated stats
   */
  getStats: async () => {
    try {
      const response = await apiClient.get('/github/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching GitHub stats:', error);
      throw error;
    }
  },

  /**
   * Health check for GitHub API
   */
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/github/health');
      return response.data;
    } catch (error) {
      console.error('GitHub API health check failed:', error);
      throw error;
    }
  }
};

// First-party, consent-gated site telemetry
export const telemetryAPI = {
  recordEvent: async (eventType) => {
    const response = await apiClient.post('/telemetry/event', { event_type: eventType });
    return response.data;
  },
  getPublicSummary: async () => {
    const response = await apiClient.get('/telemetry/public');
    return response.data;
  },
  getAdminSummary: async (token, days = 30) => {
    const response = await apiClient.get('/telemetry/admin', {
      params: { days },
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }
};

export default apiClient;
