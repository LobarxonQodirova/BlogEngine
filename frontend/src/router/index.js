/**
 * BlogEngine - Vue Router Configuration
 *
 * Defines all application routes with lazy loading, guards, and meta fields.
 */

import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: 'Home - BlogEngine' },
  },
  {
    path: '/posts/:slug',
    name: 'PostDetail',
    component: () => import('../views/PostView.vue'),
    meta: { title: 'Post - BlogEngine' },
    props: true,
  },
  {
    path: '/editor',
    name: 'NewPost',
    component: () => import('../views/EditorView.vue'),
    meta: {
      title: 'New Post - BlogEngine',
      requiresAuth: true,
      showSidebar: true,
    },
  },
  {
    path: '/editor/:slug',
    name: 'EditPost',
    component: () => import('../views/EditorView.vue'),
    meta: {
      title: 'Edit Post - BlogEngine',
      requiresAuth: true,
      showSidebar: true,
    },
    props: true,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      title: 'Dashboard - BlogEngine',
      requiresAuth: true,
      showSidebar: true,
    },
  },
  {
    path: '/media',
    name: 'Media',
    component: () => import('../views/MediaView.vue'),
    meta: {
      title: 'Media Library - BlogEngine',
      requiresAuth: true,
      showSidebar: true,
    },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: {
      title: 'Settings - BlogEngine',
      requiresAuth: true,
      showSidebar: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: `
        <div class="not-found">
          <h1>404</h1>
          <p>Page not found</p>
          <router-link to="/">Go Home</router-link>
        </div>
      `,
    },
    meta: { title: '404 - BlogEngine' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

// Navigation guard: auth check and page title
router.beforeEach((to, from, next) => {
  // Set page title
  document.title = to.meta.title || 'BlogEngine'

  // Auth guard
  if (to.meta.requiresAuth && !store.getters['auth/isAuthenticated']) {
    next({ name: 'Home', query: { redirect: to.fullPath, login: 'true' } })
    return
  }

  next()
})

export default router
