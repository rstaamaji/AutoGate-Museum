<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock, RefreshCw } from '@lucide/vue'

const currentTime = ref('')
let timer = null

const updateTime = () => {
  const now = new Date()
  const dateStr = now.toLocaleDateString('id-ID', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' })
  const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentTime.value = `${dateStr} - ${timeStr}`
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <header class="h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
    <div>
      <h2 class="text-lg font-bold text-white tracking-tight">Dashboard Monitoring Server</h2>
      <p class="text-xs text-zinc-400">Monitoring status pos satpam & riwayat kendaraan</p>
    </div>
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
        <Clock class="w-3.5 h-3.5 text-zinc-400" />
        <span>{{ currentTime }}</span>
      </div>
    </div>
  </header>
</template>
