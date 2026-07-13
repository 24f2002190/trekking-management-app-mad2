import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://localhost:5000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user:  JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin:    (state) => state.user?.roles?.includes('admin'),
    isStaff:    (state) => state.user?.roles?.includes('trek_staff'),
    isTrekker:  (state) => state.user?.roles?.includes('trekker'),
  },

  actions: {
    async login(email, password) {
      const res = await axios.post(`${API}/auth/login`, { email, password })
      this.token = res.data.token
      this.user  = res.data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      return res.data.user
    },

    async register(data) {
      const res = await axios.post(`${API}/auth/register`, data)
      return res.data
    },

    logout() {
      this.token = null
      this.user  = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  }
})