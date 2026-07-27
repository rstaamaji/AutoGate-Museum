<script setup>
import { ref } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import DashboardView from '@/views/DashboardView.vue'
import SettingsView from '@/views/SettingsView.vue'

const currentView = ref('dashboard')

const views = {
  dashboard: DashboardView,
  settings: SettingsView,
}

const currentComponent = views[currentView] || DashboardView

const handleNavigate = (view) => {
  currentView.value = view
}
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 font-sans antialiased">
    <!-- Top Navigation Header -->
    <AppHeader :current-view="currentView" @navigate="handleNavigate" />

    <!-- Main View -->
    <main class="flex-1 overflow-y-auto">
      <component :is="views[currentView] || DashboardView" />
    </main>
  </div>
</template>
