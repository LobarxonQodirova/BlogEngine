/**
 * BlogEngine - Auth Vuex Module
 *
 * Manages authentication state, JWT tokens, and user profile.
 */

import api from '../../api/axiosConfig'

export default {
  namespaced: true,

  state() {
    return {
      user: null,
      accessToken: localStorage.getItem('access_token') || null,
      refreshToken: localStorage.getItem('refresh_token') || null,
      loading: false,
      error: null,
    }
  },

  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKENS(state, { access, refresh }) {
      state.accessToken = access
      state.refreshToken = refresh
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
    },
    CLEAR_AUTH(state) {
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
  },

  actions: {
    async register({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await api.post('/auth/register/', credentials)
        commit('SET_TOKENS', response.data.tokens)
        commit('SET_USER', response.data.user)
        return response.data
      } catch (error) {
        const msg = error.response?.data?.detail || 'Registration failed.'
        commit('SET_ERROR', msg)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async login({ commit, dispatch }, { email, password }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await api.post('/auth/login/', { email, password })
        commit('SET_TOKENS', {
          access: response.data.access,
          refresh: response.data.refresh,
        })
        await dispatch('fetchProfile')
        return response.data
      } catch (error) {
        const msg = error.response?.data?.detail || 'Invalid credentials.'
        commit('SET_ERROR', msg)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async logout({ commit, state }) {
      try {
        if (state.refreshToken) {
          await api.post('/auth/logout/', { refresh: state.refreshToken })
        }
      } catch {
        // Ignore errors during logout
      } finally {
        commit('CLEAR_AUTH')
      }
    },

    async fetchProfile({ commit }) {
      try {
        const response = await api.get('/auth/profile/')
        commit('SET_USER', response.data)
        return response.data
      } catch (error) {
        commit('CLEAR_AUTH')
        throw error
      }
    },

    async updateProfile({ commit }, profileData) {
      const response = await api.put('/auth/profile/', profileData)
      commit('SET_USER', response.data)
      return response.data
    },

    async refreshAccessToken({ commit, state }) {
      if (!state.refreshToken) {
        commit('CLEAR_AUTH')
        throw new Error('No refresh token available')
      }
      try {
        const response = await api.post('/auth/token/refresh/', {
          refresh: state.refreshToken,
        })
        commit('SET_TOKENS', {
          access: response.data.access,
          refresh: response.data.refresh || state.refreshToken,
        })
        return response.data.access
      } catch {
        commit('CLEAR_AUTH')
        throw new Error('Token refresh failed')
      }
    },

    async initAuth({ commit, dispatch, state }) {
      if (state.accessToken) {
        try {
          await dispatch('fetchProfile')
        } catch {
          try {
            await dispatch('refreshAccessToken')
            await dispatch('fetchProfile')
          } catch {
            commit('CLEAR_AUTH')
          }
        }
      }
    },
  },

  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    currentUser: (state) => state.user,
    userRole: (state) => state.user?.role || null,
    isAuthor: (state) => ['author', 'editor', 'admin'].includes(state.user?.role),
    isEditor: (state) => ['editor', 'admin'].includes(state.user?.role),
    isAdmin: (state) => state.user?.role === 'admin',
    authError: (state) => state.error,
    authLoading: (state) => state.loading,
  },
}
