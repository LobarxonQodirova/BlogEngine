/**
 * BlogEngine - Vuex Store Root
 *
 * Combines all store modules and provides global state.
 */

import { createStore } from 'vuex'
import auth from './modules/auth'
import posts from './modules/posts'
import media from './modules/media'

export default createStore({
  state() {
    return {
      darkMode: localStorage.getItem('darkMode') === 'true',
      sidebarOpen: true,
      globalLoading: false,
      toast: null, // { message, type: 'success'|'error'|'info', duration }
    }
  },

  mutations: {
    TOGGLE_DARK_MODE(state) {
      state.darkMode = !state.darkMode
      localStorage.setItem('darkMode', state.darkMode)
    },

    TOGGLE_SIDEBAR(state) {
      state.sidebarOpen = !state.sidebarOpen
    },

    SET_GLOBAL_LOADING(state, loading) {
      state.globalLoading = loading
    },

    SET_TOAST(state, toast) {
      state.toast = toast
    },

    CLEAR_TOAST(state) {
      state.toast = null
    },
  },

  actions: {
    toggleDarkMode({ commit }) {
      commit('TOGGLE_DARK_MODE')
    },

    toggleSidebar({ commit }) {
      commit('TOGGLE_SIDEBAR')
    },

    showToast({ commit }, { message, type = 'info', duration = 3000 }) {
      commit('SET_TOAST', { message, type, duration })
      setTimeout(() => commit('CLEAR_TOAST'), duration)
    },
  },

  getters: {
    isDarkMode: (state) => state.darkMode,
    isSidebarOpen: (state) => state.sidebarOpen,
    isGlobalLoading: (state) => state.globalLoading,
    activeToast: (state) => state.toast,
  },

  modules: {
    auth,
    posts,
    media,
  },
})
