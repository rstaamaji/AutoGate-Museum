<script setup>
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import UsersView from '@/views/UsersView.vue'
import NodesView from '@/views/NodesView.vue'
import PengunjungView from '@/views/PengunjungView.vue'
import api from '@/services/api'

// NOTE: VehicleOwnersView, VehiclesView, VehicleTypesView, HistoryView,
// EventsView TIDAK di-import langsung di sini lagi — sekarang dipakai
// LEWAT PengunjungView.vue sebagai tab. File-filenya TIDAK dihapus.

const user = ref(null)
const currentView = ref('dashboard')
const sidebarCollapsed = ref(false)

const isAuthenticated = computed(() => !!user.value)

const views = {
  dashboard: DashboardView,
  users: UsersView,
  nodes: NodesView,
  pengunjung: PengunjungView, // <-- SATU entry baru menggantikan 4 entry lama
}

const currentComponent = computed(() => views[currentView.value] || DashboardView)

const handleLoginSuccess = (userData) => {
  user.value = userData
}

const handleLogout = () => {
  api.logout()
  user.value = null
  currentView.value = 'dashboard'
}

const handleNavigate = (view) => {
  currentView.value = view
}

const handleToggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

onMounted(() => {
  const savedUser = api.getUser()
  const token = api.getToken()
  if (savedUser && token) {
    user.value = savedUser
  }
})
</script>

<template>
  <LoginView v-if="!isAuthenticated" @login-success="handleLoginSuccess" />

  <div v-else class="min-h-screen bg-zinc-950 text-zinc-100 flex font-sans antialiased">
    <AppSidebar
      :user="user"
      :current-view="currentView"
      :collapsed="sidebarCollapsed"
      @navigate="handleNavigate"
      @toggle="handleToggleSidebar"
    />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader :user="user" @logout="handleLogout" />
      <main class="flex-1 overflow-y-auto">
        <component :is="currentComponent" :user="user" @navigate="handleNavigate" />
      </main>
    </div>
  </div>
</template>