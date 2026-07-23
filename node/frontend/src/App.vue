<script setup>
import AppHeader from '@/components/layout/AppHeader.vue'
import DashboardView from '@/views/DashboardView.vue'
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 font-sans antialiased">
    <!-- Top Navigation Header -->
    <AppHeader />

    <!-- Main Dashboard View -->
    <main class="flex-1 overflow-y-auto">
      <DashboardView />
    </main>
  </div>
</template>
