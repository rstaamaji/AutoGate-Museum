<script setup>
import { computed } from 'vue'
import {
  LayoutDashboard,
  Server,
  PanelLeftClose,
  PanelLeftOpen,
  Users,
  Radio,
  Car,
  CarFront,
  History,
  List,
  LogOut,
} from '@lucide/vue'

const props = defineProps({
  user: Object,
  currentView: String,
  collapsed: Boolean,
})

const emit = defineEmits(['navigate', 'toggle'])

const isAdmin = computed(() => ['super_admin', 'admin'].includes(props.user?.role))
const isSuperAdmin = computed(() => props.user?.role === 'super_admin')

const navItems = computed(() => {
  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, show: true },
    { id: 'history', label: 'Riwayat Kendaraan', icon: History, show: true },
    { id: 'events', label: 'Event Kendaraan', icon: List, show: true },
    { id: 'vehicles', label: 'Kendaraan', icon: CarFront, show: isAdmin.value },
    { id: 'vehicle-owners', label: 'Pemilik Kendaraan', icon: Car, show: isAdmin.value },
    { id: 'nodes', label: 'Kelola Node', icon: Radio, show: isAdmin.value },
    { id: 'users', label: 'Kelola User', icon: Users, show: isSuperAdmin.value },
  ]
  return items.filter(i => i.show)
})
</script>

<template>
  <aside
    :class="[
      'bg-zinc-950 border-r border-zinc-800/80 flex flex-col justify-between h-screen sticky top-0 z-30 select-none transition-all duration-300',
      collapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div>
      <!-- Header -->
      <div
        :class="[
          'px-4 py-5 flex items-center border-b border-zinc-800/60',
          collapsed ? 'justify-center' : 'justify-between'
        ]"
      >
        <div v-if="!collapsed" class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 shrink-0 rounded-lg bg-zinc-900 border border-zinc-700/60 flex items-center justify-center text-white shadow-md shadow-black/50">
            <Server class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 class="text-base font-bold text-white tracking-wider flex items-center gap-1.5 whitespace-nowrap">
              AutoGate <span class="text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 font-semibold">Server</span>
            </h1>
            <p class="text-[11px] text-zinc-400 font-medium whitespace-nowrap">Monitoring</p>
          </div>
        </div>
        <button
          @click="emit('toggle')"
          class="p-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 border border-transparent hover:border-zinc-800 transition shrink-0"
        >
          <PanelLeftOpen v-if="collapsed" class="w-5 h-5 text-blue-400" />
          <PanelLeftClose v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation -->
      <div class="p-3">
        <p v-if="!collapsed" class="px-3 text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-3">Menu</p>
        <nav class="space-y-1.5">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="emit('navigate', item.id)"
            :class="[
              'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-semibold transition-all duration-150',
              collapsed ? 'justify-center px-0' : '',
              currentView === item.id
                ? 'bg-zinc-100 text-zinc-950 shadow-sm shadow-white/10'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-900',
            ]"
            :title="item.label"
          >
            <component :is="item.icon" class="w-5 h-5 shrink-0" />
            <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- User Info -->
    <div class="p-3 border-t border-zinc-800/60">
      <div v-if="!collapsed" class="px-3 py-2">
        <p class="text-xs font-medium text-white truncate">{{ user?.name }}</p>
        <p class="text-[10px] text-zinc-500 uppercase tracking-wider">{{ user?.role }}</p>
      </div>
    </div>
  </aside>
</template>
