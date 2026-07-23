<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { BarChart3, Car, Radio, Wifi, WifiOff } from '@lucide/vue'
import NodeStatusList from '@/components/node/NodeStatusList.vue'
import PlateDetailModal from '@/components/gate/PlateDetailModal.vue'
import api from '@/services/api'

const summary = ref({
  total_vehicles: 0,
  today_vehicles: 0,
  total_nodes: 0,
  online_nodes: 0,
  offline_nodes: 0,
})

const nodes = ref([])
const recentPlates = ref([])
const loading = ref(false)
const selectedPlate = ref(null)
let refreshTimer = null

const fetchData = async () => {
  loading.value = true
  try {
    const [summaryData, nodesData, platesData] = await Promise.all([
      api.getDashboardSummary(),
      api.getNodes(),
      api.getVehicles({ limit: 15 }),
    ])
    summary.value = summaryData
    nodes.value = nodesData
    recentPlates.value = platesData.items || []
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
  <div class="p-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Car class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Total Kendaraan</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.total_vehicles }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <Car class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Hari Ini</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.today_vehicles }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <Wifi class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Node Online</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.online_nodes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center">
            <WifiOff class="w-5 h-5 text-red-400" />
          </div>
          <div>
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Node Offline</p>
            <p class="text-2xl font-bold text-white font-mono">{{ summary.offline_nodes }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Gate Status Cards + Riwayat -->
      <div class="xl:col-span-2 space-y-6">
        <!-- Riwayat Kendaraan -->
        <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
          <h3 class="text-sm font-bold text-white tracking-tight mb-3 flex items-center gap-2">
            <BarChart3 class="w-4 h-4 text-zinc-400" />
            Riwayat Kendaraan
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-zinc-800">
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Waktu</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Node</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Arah</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Gambar</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Plat</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="plate in recentPlates"
                  :key="plate.id"
                  class="border-b border-zinc-800/50 hover:bg-zinc-800/30 cursor-pointer"
                  @click="selectedPlate = plate"
                >
                  <td class="py-2 px-3 font-mono text-zinc-300">{{ formatTime(plate.created_at) }}</td>
                  <td class="py-2 px-3">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-800 text-zinc-300 font-mono">
                      {{ plate.node_id }}
                    </span>
                  </td>
                  <td class="py-2 px-3">
                    <span
                      :class="[
                        'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                        plate.direction === 'masuk'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
                      ]"
                    >
                      {{ plate.direction }}
                    </span>
                  </td>
                  <td class="py-2 px-3">
                    <img
                      v-if="plate.plate_image_url"
                      :src="plate.plate_image_url"
                      alt="Plat"
                      class="w-16 h-10 object-contain rounded border border-zinc-700 bg-zinc-950"
                    />
                    <span v-else class="text-zinc-600">---</span>
                  </td>
                  <td class="py-2 px-3 font-mono font-bold text-white">{{ plate.plate_number }}</td>
                  <td class="py-2 px-3 text-zinc-300">
                    {{ plate.confidence ? `${plate.confidence.toFixed(1)}%` : '---' }}
                  </td>
                </tr>
                <tr v-if="!recentPlates.length">
                  <td colspan="6" class="py-4 text-center text-zinc-500">Belum ada data</td>
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
    <!-- Modal Detail -->
    <PlateDetailModal
      v-if="selectedPlate"
      :plate="selectedPlate"
      @close="selectedPlate = null"
    />
  </div>
</template>
