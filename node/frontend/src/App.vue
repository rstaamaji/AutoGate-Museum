<script setup>
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import DashboardView from '@/views/DashboardView.vue'
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 flex font-sans antialiased">
    <!-- Sidebar Navigation -->
    <AppSidebar />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top Navigation Header -->
      <AppHeader />

      <!-- Main Dashboard View -->
      <main class="flex-1 overflow-y-auto">
        <DashboardView />
      </main>
    </div>
  </div>
</template>
