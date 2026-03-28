<template>
  <div id="blog-engine" :class="{ 'dark-mode': isDarkMode }">
    <Navbar v-if="showNavbar" />
    <div class="app-layout">
      <Sidebar v-if="showSidebar" />
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <Footer v-if="showFooter" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import Navbar from './components/common/Navbar.vue'
import Sidebar from './components/common/Sidebar.vue'
import Footer from './components/common/Footer.vue'

export default {
  name: 'App',
  components: { Navbar, Sidebar, Footer },
  setup() {
    const store = useStore()
    const route = useRoute()

    const isDarkMode = computed(() => store.state.darkMode || false)

    const showNavbar = computed(() => {
      return route.meta.hideNavbar !== true
    })

    const showSidebar = computed(() => {
      return route.meta.showSidebar === true && store.getters['auth/isAuthenticated']
    })

    const showFooter = computed(() => {
      return route.meta.hideFooter !== true
    })

    return { isDarkMode, showNavbar, showSidebar, showFooter }
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #3b82f6;
  --primary-dark: #2563eb;
  --secondary: #6366f1;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border: #e2e8f0;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
  --sidebar-width: 260px;
  --navbar-height: 64px;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-primary);
  background-color: var(--bg-secondary);
  line-height: 1.6;
}

#blog-engine {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout {
  display: flex;
  flex: 1;
  padding-top: var(--navbar-height);
}

.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.dark-mode {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --border: #334155;
}
</style>
