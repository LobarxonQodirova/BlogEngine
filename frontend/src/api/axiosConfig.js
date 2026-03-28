/**
 * BlogEngine - Axios Configuration
 *
 * Configures a shared Axios instance with base URL, interceptors for
 * JWT authentication, and automatic token refresh on 401 responses.
 */

import axios from 'axios'
import store from '../store'
import router from '../router'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Track whether a token refresh is already in progress
let isRefreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

// Request interceptor: attach access token
api.interceptors.request.use(
  (config) => {
    const token = store.state.auth.accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 and refresh tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for the ongoing refresh to complete
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await store.dispatch('auth/refreshAccessToken')
        isRefreshing = false
        onTokenRefreshed(newToken)

        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch {
        isRefreshing = false
        refreshSubscribers = []
        await store.dispatch('auth/logout')
        router.push({ name: 'Home', query: { login: 'true' } })
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default api
