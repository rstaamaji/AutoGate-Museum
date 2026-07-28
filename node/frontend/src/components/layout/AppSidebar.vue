<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  LayoutDashboard,
  Settings,
  ShieldCheck,
  PanelLeftClose,
  PanelLeftOpen,
  Clock,
  History,
} from '@lucide/vue'
import api from '@/services/api'

const props = defineProps({
  currentView: {
    type: String,
    default: 'dashboard',
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['navigate', 'toggle'])

const nodeStatus = ref(null)
const currentTime = ref('')
let timer = null
let statusTimer = null

const updateTime = () => {
  const now = new Date()
  const dateStr = now.toLocaleDateString('id-ID', { weekday: 'short', day: '2-digit', month: 'short' })
  const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
  currentTime.value = `${dateStr} - ${timeStr}`
}

const fetchStatus = async () => {
  try {
    nodeStatus.value = await api.getStatus()
  } catch (err) {
    nodeStatus.value = null
  }
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  fetchStatus()
  statusTimer = setInterval(fetchStatus, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (statusTimer) clearInterval(statusTimer)
})

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'history', label: 'Riwayat', icon: History },
  { id: 'settings', label: 'Settings', icon: Settings },
]
</script>

<template>
  <aside
    :class="[
      'bg-zinc-950 border-r border-zinc-800/80 flex flex-col justify-between h-screen sticky top-0 z-30 select-none transition-all duration-300 shrink-0',
      collapsed ? 'w-16 sm:w-20' : 'w-64'
    ]"
  >
    <!-- Top Section -->
    <div>
      <!-- Header / Logo & Collapse Button -->
      <div
        :class="[
          'px-4 py-4 flex items-center border-b border-zinc-800/60',
          collapsed ? 'justify-center' : 'justify-between'
        ]"
      >
        <div v-if="!collapsed" class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 shrink-0 rounded-lg bg-zinc-900 border border-zinc-700/60 flex items-center justify-center text-white shadow-md shadow-black/50">
            <ShieldCheck class="w-5 h-5 text-emerald-400" />
          </div>
          <div class="min-w-0">
            <h1 class="text-base font-bold text-white tracking-wider flex items-center gap-1.5 whitespace-nowrap">
              Pos Satpam
            </h1>
            <p class="text-[11px] text-zinc-400 font-medium whitespace-nowrap">AutoGate UNS</p>
          </div>
        </div>

        <button
          @click="emit('toggle')"
          class="p-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 border border-transparent hover:border-zinc-800 transition shrink-0"
          :title="collapsed ? 'Buka Sidebar' : 'Tutup Sidebar'"
        >
          <PanelLeftOpen v-if="collapsed" class="w-5 h-5 text-emerald-400" />
          <PanelLeftClose v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation -->
      <div class="p-3">
        <p v-if="!collapsed" class="px-3 text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-3">
          Menu Utama
        </p>

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

    <!-- Bottom Section: Status & Clock -->
    <div class="p-3 border-t border-zinc-800/60 space-y-2">
      <!-- Camera Status -->
      <div v-if="nodeStatus" :class="['bg-zinc-900 border border-zinc-800/80 rounded-lg p-2 text-xs', collapsed ? 'text-center' : '']">
        <div v-if="!collapsed" class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1.5">Status Kamera</div>
        <div :class="['flex items-center gap-2', collapsed ? 'flex-col gap-1.5 justify-center' : 'justify-between']">
          <div class="flex items-center gap-1.5" :title="nodeStatus.camera_in_active ? 'Kamera Masuk Aktif' : 'Kamera Masuk Nonaktif'">
            <span :class="['w-2 h-2 rounded-full shrink-0', nodeStatus.camera_in_active ? 'bg-emerald-400' : 'bg-red-400']"></span>
            <span v-if="!collapsed" class="text-[11px] text-zinc-400">Cam In</span>
          </div>
          <div class="flex items-center gap-1.5" :title="nodeStatus.camera_out_active ? 'Kamera Keluar Aktif' : 'Kamera Keluar Nonaktif'">
            <span :class="['w-2 h-2 rounded-full shrink-0', nodeStatus.camera_out_active ? 'bg-emerald-400' : 'bg-red-400']"></span>
            <span v-if="!collapsed" class="text-[11px] text-zinc-400">Cam Out</span>
          </div>
        </div>
      </div>

      <!-- Time Clock -->
      <div v-if="!collapsed" class="px-2 py-1 text-[11px] font-mono text-zinc-400 flex items-center gap-1.5">
        <Clock class="w-3.5 h-3.5 text-zinc-500 shrink-0" />
        <span class="truncate">{{ currentTime }}</span>
      </div>
    </div>
  </aside>
</template>
