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
  <header class="h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
    <div class="flex items-center gap-6">
      <div>
        <h2 class="text-lg font-bold text-white tracking-tight">
          Pos Satpam — Dashboard
        </h2>
        <p class="text-xs text-zinc-400">Kontrol gerbang & monitoring kamera</p>
      </div>

      <!-- Nav Tabs -->
      <nav class="flex items-center gap-1">
        <button
          @click="emit('navigate', 'dashboard')"
          :class="[
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition',
            currentView === 'dashboard'
              ? 'bg-zinc-100 text-zinc-950'
              : 'text-zinc-400 hover:text-white hover:bg-zinc-800',
          ]"
        >
          <LayoutDashboard class="w-3.5 h-3.5" />
          Dashboard
        </button>
        <button
          @click="emit('navigate', 'settings')"
          :class="[
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition',
            currentView === 'settings'
              ? 'bg-zinc-100 text-zinc-950'
              : 'text-zinc-400 hover:text-white hover:bg-zinc-800',
          ]"
        >
          <Settings class="w-3.5 h-3.5" />
          Settings
        </button>
      </nav>
    </div>

    <div class="flex items-center gap-4">
      <!-- Status Indicator -->
      <div v-if="nodeStatus" class="flex items-center gap-3 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs">
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
      <div class="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
        <Clock class="w-3.5 h-3.5 text-zinc-400" />
        <span>{{ currentTime }}</span>
      </div>
    </div>
  </header>
</template>
