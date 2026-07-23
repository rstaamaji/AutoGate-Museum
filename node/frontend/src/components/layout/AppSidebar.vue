<script setup>
import { ref } from 'vue'
import { 
  LayoutDashboard, 
  ShieldCheck, 
  PanelLeftClose, 
  PanelLeftOpen 
} from '@lucide/vue'

const isCollapsed = ref(false)

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside 
    :class="[
      'bg-zinc-950 border-r border-zinc-800/80 flex flex-col justify-between h-screen sticky top-0 z-30 select-none transition-all duration-300',
      isCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <!-- Top Section: Brand & Collapse Toggle & Dashboard Menu -->
    <div>
      <!-- Brand & Collapse Toggle Header -->
      <div 
        :class="[
          'px-4 py-5 flex items-center border-b border-zinc-800/60',
          isCollapsed ? 'justify-center' : 'justify-between'
        ]"
      >
        <!-- Logo & Brand Text (Hidden when collapsed to avoid overlap) -->
        <div v-if="!isCollapsed" class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 shrink-0 rounded-lg bg-zinc-900 border border-zinc-700/60 flex items-center justify-center text-white shadow-md shadow-black/50">
            <ShieldCheck class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 class="text-base font-bold text-white tracking-wider flex items-center gap-1.5 whitespace-nowrap">
              AutoGate <span class="text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 font-semibold">UNS</span>
            </h1>
            <p class="text-[11px] text-zinc-400 font-medium whitespace-nowrap">Monitoring System</p>
          </div>
        </div>

        <!-- Collapse Toggle Button -->
        <button 
          @click="toggleSidebar" 
          class="p-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 border border-transparent hover:border-zinc-800 transition shrink-0"
          :title="isCollapsed ? 'Buka Sidebar' : 'Tutup Sidebar'"
        >
          <PanelLeftOpen v-if="isCollapsed" class="w-5 h-5 text-emerald-400" />
          <PanelLeftClose v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation Section -->
      <div class="p-3">
        <p v-if="!isCollapsed" class="px-3 text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-3">
          Menu Utama
        </p>
        
        <nav class="space-y-1.5">
          <!-- Only Dashboard Button -->
          <button 
            :class="[
              'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-semibold bg-zinc-100 text-zinc-950 shadow-sm shadow-white/10 transition-all duration-150',
              isCollapsed ? 'justify-center px-0' : ''
            ]"
            title="Dashboard"
          >
            <LayoutDashboard class="w-5 h-5 text-zinc-950 shrink-0" />
            <span v-if="!isCollapsed" class="whitespace-nowrap">Dashboard</span>
          </button>
        </nav>
      </div>
    </div>
  </aside>
</template>
