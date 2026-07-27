<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock, Settings, LayoutDashboard, Wifi, WifiOff } from '@lucide/vue'
import api from '@/services/api'

const props = defineProps({
  currentView: String,
})

const emit = defineEmits(['navigate'])

const currentTime = ref('')
const nodeStatus = ref(null)
let timer = null
let statusTimer = null

const updateTime = () => {
  const now = new Date()
  const dateStr = now.toLocaleDateString('id-ID', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' })
  const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
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
  statusTimer = setInterval(fetchStatus, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (statusTimer) clearInterval(statusTimer)
})
</script>

<template>
  <header class="min-h-[4rem] border-b border-zinc-800 bg-zinc-950/90 backdrop-blur-md px-4 sm:px-6 py-2.5 sm:py-0 flex flex-wrap sm:flex-nowrap items-center justify-between gap-3 sticky top-0 z-20">
    <!-- Brand / Title & Nav Tabs -->
    <div class="flex items-center gap-3 sm:gap-6 min-w-0">
      <div class="min-w-0">
        <h2 class="text-base sm:text-lg font-bold text-white tracking-tight truncate">
          Pos Satpam
        </h2>
        <p class="text-[11px] text-zinc-400 hidden md:block">Kontrol gerbang & monitoring kamera</p>
      </div>

      <!-- Nav Tabs -->
      <nav class="flex items-center gap-1 shrink-0">
        <button
          @click="emit('navigate', 'dashboard')"
          :class="[
            'flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition',
            currentView === 'dashboard'
              ? 'bg-zinc-100 text-zinc-950 font-semibold'
              : 'text-zinc-400 hover:text-white hover:bg-zinc-800',
          ]"
        >
          <LayoutDashboard class="w-3.5 h-3.5" />
          <span>Dashboard</span>
        </button>
        <button
          @click="emit('navigate', 'settings')"
          :class="[
            'flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition',
            currentView === 'settings'
              ? 'bg-zinc-100 text-zinc-950 font-semibold'
              : 'text-zinc-400 hover:text-white hover:bg-zinc-800',
          ]"
        >
          <Settings class="w-3.5 h-3.5" />
          <span>Settings</span>
        </button>
      </nav>
    </div>

    <!-- Status & Time -->
    <div class="flex items-center gap-2 sm:gap-4 shrink-0 ml-auto sm:ml-0">
      <!-- Status Indicator -->
      <div v-if="nodeStatus" class="flex items-center gap-2 sm:gap-3 bg-zinc-900 border border-zinc-800 px-2.5 py-1.5 rounded-lg text-[11px] sm:text-xs">
        <div class="flex items-center gap-1.5" :title="nodeStatus.camera_in_active ? 'Kamera Masuk Aktif' : 'Kamera Masuk Nonaktif'">
          <span :class="['w-2 h-2 rounded-full', nodeStatus.camera_in_active ? 'bg-emerald-400' : 'bg-red-400']"></span>
          <span class="text-zinc-400">Cam In</span>
        </div>
        <div class="flex items-center gap-1.5" :title="nodeStatus.camera_out_active ? 'Kamera Keluar Aktif' : 'Kamera Keluar Nonaktif'">
          <span :class="['w-2 h-2 rounded-full', nodeStatus.camera_out_active ? 'bg-emerald-400' : 'bg-red-400']"></span>
          <span class="text-zinc-400">Cam Out</span>
        </div>
      </div>

      <!-- Time -->
      <div class="hidden lg:flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
        <Clock class="w-3.5 h-3.5 text-zinc-400" />
        <span>{{ currentTime }}</span>
      </div>
    </div>
  </header>
</template>
