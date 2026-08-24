import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Bearer token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('coinsy_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor for 401 handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('coinsy_token');
      localStorage.removeItem('coinsy_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (email, password) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },
  signup: async (email, password, full_name) => {
    const res = await apiClient.post('/auth/signup', { email, password, full_name });
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};

export const analyticsApi = {
  getSpend: async (timeframe = 'monthly', userId = null) => {
    const params = { timeframe };
    if (userId) params.user_id = userId;
    const res = await apiClient.get('/analytics/spend', { params });
    return res.data;
  },
  getComparison: async (period = 'mom', userId = null) => {
    const params = { period };
    if (userId) params.user_id = userId;
    const res = await apiClient.get('/analytics/comparison', { params });
    return res.data;
  },
  getSummary: async (period = 'mom', userId = null) => {
    const params = { period };
    if (userId) params.user_id = userId;
    const res = await apiClient.get('/analytics/summary', { params });
    return res.data;
  },
  getHeatmap: async (userId, daysBack = 90) => {
    const params = { user_id: userId, days_back: daysBack };
    const res = await apiClient.get('/analytics/heatmap', { params });
    return res.data;
  },
  getCashFlow: async (userId, timeframe = 'monthly') => {
    const params = { user_id: userId, timeframe };
    const res = await apiClient.get('/analytics/cashflow', { params });
    return res.data;
  },
  getRecap: async (userId, month = null, year = null) => {
    const params = { user_id: userId };
    if (month) params.month = month;
    if (year) params.year = year;
    const res = await apiClient.get('/analytics/recap', { params });
    return res.data;
  },
};

export const insightsApi = {
  getPrediction: async (userId, forceRefresh = false) => {
    const params = { user_id: userId, force_refresh: forceRefresh };
    const res = await apiClient.get('/insights/prediction', { params });
    return res.data;
  },
  getDailyTip: async (userId, forceRefresh = false) => {
    const params = { user_id: userId, force_refresh: forceRefresh };
    const res = await apiClient.get('/insights/daily-tip', { params });
    return res.data;
  },
};

export const personalityApi = {
  getPersonality: async (userId, roastMode = false) => {
    const params = { user_id: userId, roast_mode: roastMode };
    const res = await apiClient.get('/personality', { params });
    return res.data;
  },
  getTip: async (userId, roastMode = false) => {
    const params = { user_id: userId, roast_mode: roastMode };
    const res = await apiClient.get('/personality/tip', { params });
    return res.data;
  },
};

export const budgetsApi = {
  getBudgets: async (userId, month = null, year = null) => {
    const params = { user_id: userId };
    if (month) params.month = month;
    if (year) params.year = year;
    const res = await apiClient.get('/budgets', { params });
    return res.data;
  },
  setBudget: async (userId, budgetData) => {
    const params = { user_id: userId };
    const res = await apiClient.post('/budgets', budgetData, { params });
    return res.data;
  },
  deleteBudget: async (userId, budgetId) => {
    const params = { user_id: userId };
    const res = await apiClient.delete(`/budgets/${budgetId}`, { params });
    return res.data;
  },
  getCoinsyWidget: async (userId) => {
    const params = { user_id: userId };
    const res = await apiClient.get('/budgets/coinsy-widget', { params });
    return res.data;
  },
};

export const jobsApi = {
  listJobs: async (userId, statusFilter = null) => {
    const params = { user_id: userId };
    if (statusFilter) params.status_filter = statusFilter;
    const res = await apiClient.get('/jobs', { params });
    return res.data;
  },
  createJob: async (userId, jobData) => {
    const params = { user_id: userId };
    const res = await apiClient.post('/jobs', jobData, { params });
    return res.data;
  },
  getJob: async (userId, jobId) => {
    const params = { user_id: userId };
    const res = await apiClient.get(`/jobs/${jobId}`, { params });
    return res.data;
  },
  updateJob: async (userId, jobId, jobData) => {
    const params = { user_id: userId };
    const res = await apiClient.put(`/jobs/${jobId}`, jobData, { params });
    return res.data;
  },
  deleteJob: async (userId, jobId) => {
    const params = { user_id: userId };
    const res = await apiClient.delete(`/jobs/${jobId}`, { params });
    return res.data;
  },
};

export const interviewPrepApi = {
  generatePrepPack: async (userId, jobId) => {
    const params = { user_id: userId };
    const res = await apiClient.post(`/interview-prep/generate/${jobId}`, {}, { params });
    return res.data;
  },
  getPrepPack: async (userId, jobId) => {
    const params = { user_id: userId };
    const res = await apiClient.get(`/interview-prep/${jobId}`, { params });
    return res.data;
  },
  updateItem: async (userId, itemId, updateData) => {
    const params = { user_id: userId };
    const res = await apiClient.patch(`/interview-prep/items/${itemId}`, updateData, { params });
    return res.data;
  },
  getResume: async (userId) => {
    const params = { user_id: userId };
    const res = await apiClient.get('/interview-prep/resume/me', { params });
    return res.data;
  },
  saveResume: async (userId, resumeData) => {
    const params = { user_id: userId };
    const res = await apiClient.post('/interview-prep/resume/me', resumeData, { params });
    return res.data;
  },
};

export const transactionsApi = {
  listTransactions: async (params = {}) => {
    const res = await apiClient.get('/transactions', { params });
    return res.data;
  },
  createTransaction: async (data) => {
    const res = await apiClient.post('/transactions', data);
    return res.data;
  },
};

export const statementsApi = {
  uploadCSV: async (file, userId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    const res = await apiClient.post('/statements/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  uploadPDF: async (file, password, userId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (password) formData.append('pdf_password', password);
    formData.append('user_id', userId);
    const res = await apiClient.post('/statements/upload-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

export const categoriesApi = {
  listCategories: async (userId = null) => {
    const params = userId ? { user_id: userId } : {};
    const res = await apiClient.get('/categories', { params });
    return res.data;
  },
};

export default apiClient;
