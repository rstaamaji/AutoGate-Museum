<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock, LogOut, User } from '@lucide/vue'

const props = defineProps({
  user: Object,
})

const emit = defineEmits(['logout'])

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
  <header class="h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
    <div class="min-w-0">
      <h2 class="text-base sm:text-lg font-bold text-white tracking-tight truncate">Dashboard Monitoring Server</h2>
      <p class="text-xs text-zinc-400 hidden sm:block">Monitoring status pos satpam & riwayat kendaraan</p>
    </div>
    <div class="flex items-center gap-2 sm:gap-4 shrink-0">
      <!-- Clock -->
      <div class="hidden md:flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
        <Clock class="w-3.5 h-3.5 text-zinc-400" />
        <span>{{ currentTime }}</span>
      </div>

      <!-- User Info + Logout -->
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-2.5 py-1.5 rounded-lg text-xs">
          <User class="w-3.5 h-3.5 text-zinc-400" />
          <span class="text-zinc-300 font-medium hidden xs:inline">{{ user?.name }}</span>
          <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-zinc-800 text-zinc-400 uppercase">{{ user?.role }}</span>
        </div>
        <button
          @click="emit('logout')"
          class="p-2 rounded-lg text-zinc-400 hover:text-red-400 hover:bg-red-950/50 border border-transparent hover:border-red-800/50 transition"
          title="Logout"
        >
          <LogOut class="w-4 h-4" />
        </button>
      </div>
    </div>
  </header>
</template>
