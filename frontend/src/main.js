/**
 * BlogEngine - Vue.js 3 Application Entry Point
 *
 * Initializes the Vue app with router, store, and global configuration.
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Component:', instance)
  console.error('Info:', info)
}

// Global properties accessible in all components
app.config.globalProperties.$appName = 'BlogEngine'

app.use(router)
app.use(store)

// Restore auth state from localStorage on app initialization
const token = localStorage.getItem('access_token')
if (token) {
  store.dispatch('auth/initAuth')
}

app.mount('#app')
