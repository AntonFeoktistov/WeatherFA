import { defineStore } from 'pinia';
import { authApi } from '@/api/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(credentials) {
      try {
        const response = await authApi.login(credentials);
        this.token = response.data.access_token;
        localStorage.setItem('access_token', this.token);
        return true; 
      } catch (error) {
        console.error('Login failed:', error);
        throw error; 
      }
    },
    async register(userData) {
  try {
    const response = await authApi.register(userData);
    return true;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;  
  }
},
    logout() {
      this.token = null;
      localStorage.removeItem('access_token');
    },
  },
});