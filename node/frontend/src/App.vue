<script setup>
import { ref } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import DashboardView from '@/views/DashboardView.vue'
import HistoryView from '@/views/HistoryView.vue'
import SettingsView from '@/views/SettingsView.vue'

const currentView = ref('dashboard')
const sidebarCollapsed = ref(false)

const views = {
  dashboard: DashboardView,
  history: HistoryView,
  settings: SettingsView,
}

const handleNavigate = (view) => {
  currentView.value = view
}

const handleToggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 flex font-sans antialiased">
    <!-- Collapsible Sidebar Navigation -->
    <AppSidebar
      :current-view="currentView"
      :collapsed="sidebarCollapsed"
      @navigate="handleNavigate"
      @toggle="handleToggleSidebar"
    />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
      <main class="flex-1">
        <component :is="views[currentView] || DashboardView" @navigate="handleNavigate" />
      </main>
    </div>
  </div>
</template>
