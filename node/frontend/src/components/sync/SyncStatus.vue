<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Cloud, CloudOff, RefreshCw, Check, AlertTriangle, Loader2 } from '@lucide/vue'
import api from '@/services/api'

const syncStatus = ref({
  server_online: false,
  pending: 0,
  sent: 0,
  failed: 0,
})
const loading = ref(false)
const syncing = ref(false)
let timer = null

const fetchStatus = async () => {
  try {
    syncStatus.value = await api.getSyncStatus()
  } catch (err) {
    syncStatus.value.server_online = false
  }
}

const handleManualSync = async () => {
  syncing.value = true
  try {
    await api.manualSync()
    await fetchStatus()
  } catch (err) {
    console.error('Manual sync failed:', err)
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchStatus()
  timer = setInterval(fetchStatus, 10000) // refresh setiap 10 detik
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-bold text-white tracking-tight flex items-center gap-2">
        <Cloud class="w-4 h-4 text-zinc-400" />
        Status Sinkronisasi
      </h3>
      <button
        @click="handleManualSync"
        :disabled="syncing"
        class="p-1.5 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 transition disabled:opacity-50"
        title="Sync Manual"
      >
        <Loader2 v-if="syncing" class="w-4 h-4 animate-spin" />
        <RefreshCw v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Server Status -->
    <div class="flex items-center gap-2 mb-3">
      <span
        :class="[
          'w-2.5 h-2.5 rounded-full',
          syncStatus.server_online ? 'bg-emerald-400' : 'bg-red-400',
        ]"
      ></span>
      <span class="text-xs font-medium" :class="syncStatus.server_online ? 'text-emerald-400' : 'text-red-400'">
        {{ syncStatus.server_online ? 'Server Online' : 'Server Offline' }}
      </span>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-2">
      <div class="bg-zinc-950 rounded-lg p-2 text-center border border-zinc-800">
        <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Pending</p>
        <p class="text-lg font-bold text-amber-400 font-mono">{{ syncStatus.pending }}</p>
      </div>
      <div class="bg-zinc-950 rounded-lg p-2 text-center border border-zinc-800">
        <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Terkirim</p>
        <p class="text-lg font-bold text-emerald-400 font-mono">{{ syncStatus.sent }}</p>
      </div>
      <div class="bg-zinc-950 rounded-lg p-2 text-center border border-zinc-800">
        <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Gagal</p>
        <p class="text-lg font-bold text-red-400 font-mono">{{ syncStatus.failed }}</p>
      </div>
    </div>
  </div>
</template>
