<script setup>
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import DashboardView from '@/views/DashboardView.vue'
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 flex font-sans antialiased">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader />
      <main class="flex-1 overflow-y-auto">
        <DashboardView />
      </main>
    </div>
  </div>
</template>
