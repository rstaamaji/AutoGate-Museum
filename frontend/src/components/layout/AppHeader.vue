<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock, ShieldCheck, RefreshCw, Bell, Search } from '@lucide/vue'

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

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <header class="h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
    <!-- Left: Title & Subtitle -->
    <div class="flex items-center gap-4">
      <div>
        <h2 class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          Dashboard Monitoring CCTV Gate
        </h2>
        <p class="text-xs text-zinc-400">Live preview & kontrol otomatis gerbang kampus UNS</p>
      </div>
    </div>

    <!-- Right: Quick Status, Time, & Actions -->
    <div class="flex items-center gap-4">
      <!-- Time Display -->
      <div class="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
        <Clock class="w-3.5 h-3.5 text-zinc-400" />
        <span>{{ currentTime }}</span>
      </div>

      <!-- Quick Action Icons -->
      <div class="flex items-center gap-2">
        <button title="Refresh Status" class="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700 transition">
          <RefreshCw class="w-4 h-4" />
        </button>
        <button title="Notifikasi" class="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700 transition relative">
          <Bell class="w-4 h-4" />
          <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500"></span>
        </button>
      </div>
    </div>
  </header>
</template>
