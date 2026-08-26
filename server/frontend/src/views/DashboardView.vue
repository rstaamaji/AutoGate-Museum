<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { BarChart3, Car, Radio, Wifi, WifiOff, History, ArrowRight } from '@lucide/vue'
import NodeStatusList from '@/components/node/NodeStatusList.vue'
import api from '@/services/api'

const emit = defineEmits(['navigate'])

const summary = ref({
  total_events: 0,
  today_events: 0,
  vehicles_inside: 0,
  total_nodes: 0,
  online_nodes: 0,
  offline_nodes: 0,
})

const recentHistory = ref([])
const loading = ref(false)
let refreshTimer = null

const fetchData = async () => {
  loading.value = true
  try {
    const [summaryData, historyData] = await Promise.all([
      api.getDashboardSummary(),
      api.getHistory({ limit: 10 }),
    ])
    summary.value = summaryData
    recentHistory.value = historyData.items || []
  } catch (err) {
    console.error('Gagal mengambil data:', err)
  } finally {
    loading.value = false
  }
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(() => {
  fetchData()
  refreshTimer = setInterval(fetchData, 15000)
})
onUnmounted(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<template>
  <div class="p-4 sm:p-6 space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
            <BarChart3 class="w-5 h-5 text-blue-400" />
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider truncate">Total Event</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.total_events }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <Car class="w-5 h-5 text-emerald-400" />
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider truncate">Hari Ini</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.today_events }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
            <Car class="w-5 h-5 text-amber-400" />
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider truncate">Di Dalam</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.vehicles_inside }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <Wifi class="w-5 h-5 text-emerald-400" />
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider truncate">Node Online</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.online_nodes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center shrink-0">
            <WifiOff class="w-5 h-5 text-red-400" />
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider truncate">Node Offline</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.offline_nodes }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- History -->
      <div class="xl:col-span-2 space-y-6 min-w-0">
        <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <History class="w-4 h-4 text-zinc-400" />
              Riwayat Terbaru
            </h3>
            <button
              @click="emit('navigate', 'history')"
              class="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 hover:bg-zinc-800/60 px-2.5 py-1 rounded-lg transition border border-transparent hover:border-zinc-700/60"
            >
              <span>Lihat Semua</span>
              <ArrowRight class="w-3.5 h-3.5" />
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-zinc-800">
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Plat</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Masuk</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Keluar</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="h in recentHistory"
                  :key="h.id"
                  class="border-b border-zinc-800/50 hover:bg-zinc-800/30 cursor-pointer"
                >
                  <td class="py-2 px-3 font-mono font-bold text-white">{{ h.plate_number }}</td>
                  <td class="py-2 px-3 text-zinc-300">
                    <div class="text-[10px] text-zinc-500">{{ h.entry_node_name || '---' }}</div>
                    <div>{{ formatTime(h.entry_at) }}</div>
                  </td>
                  <td class="py-2 px-3 text-zinc-300">
                    <div class="text-[10px] text-zinc-500">{{ h.exit_node_name || '---' }}</div>
                    <div>{{ formatTime(h.exit_at) }}</div>
                  </td>
                  <td class="py-2 px-3">
                    <span
                      :class="[
                        'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                        h.is_inside
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
                      ]"
                    >
                      {{ h.is_inside ? 'Di Dalam' : 'Keluar' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!recentHistory.length">
                  <td colspan="4" class="py-4 text-center text-zinc-500">Belum ada data</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Sidebar: Node Status -->
      <div class="space-y-6">
        <NodeStatusList />
      </div>
    </div>
  </div>
</template>
