<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import GateCard from '@/components/gate/GateCard.vue'
import SyncStatus from '@/components/sync/SyncStatus.vue'
import api from '@/services/api'

const gates = ref([
  {
    id: 1,
    title: 'Gate Masuk',
    lane: 'Lane 1',
    direction: 'masuk',
    timestamp: '',
    image: '',
    plate: '',
    confidence: null,
    barrierStatus: 'TERTUTUP',
  },
  {
    id: 2,
    title: 'Gate Keluar',
    lane: 'Lane 2',
    direction: 'keluar',
    timestamp: '',
    image: '',
    plate: '',
    confidence: null,
    barrierStatus: 'TERTUTUP',
  },
])

const recentPlates = ref([])
const loading = ref(false)
let refreshTimer = null

const fetchRecentPlates = async () => {
  try {
    const data = await api.getPlates({ limit: 10 })
    recentPlates.value = data.items || []

    // Update gate cards dengan data terbaru
    for (const dir of ['masuk', 'keluar']) {
      const latest = data.items?.find(v => v.direction === dir)
      if (latest) {
        const gate = gates.value.find(g => g.direction === dir)
        if (gate) {
          gate.plate = latest.plate_number
          gate.confidence = latest.confidence
          gate.timestamp = latest.captured_at
            ? new Date(latest.captured_at).toLocaleString('id-ID')
            : ''
        }
      }
    }
  } catch (err) {
    console.error('Gagal mengambil data:', err)
  }
}

const handleCapture = (direction) => {
  // Refresh data setelah capture
  fetchRecentPlates()
}

const handleRefresh = () => {
  fetchRecentPlates()
}

onMounted(() => {
  fetchRecentPlates()
  refreshTimer = setInterval(fetchRecentPlates, 15000) // refresh setiap 15 detik
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div class="p-6">
    <!-- Grid: Gate Cards + Sync Status -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Gate Cards (2 kolom) -->
      <div class="xl:col-span-2 space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GateCard
            v-for="gate in gates"
            :key="gate.id"
            :gate="gate"
            :direction="gate.direction"
            @capture="handleCapture"
            @refresh="handleRefresh"
          />
        </div>

        <!-- Riwayat Terbaru -->
        <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
          <h3 class="text-sm font-bold text-white tracking-tight mb-3">Riwayat Terbaru</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-zinc-800">
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Waktu</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Arah</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Plat</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Confidence</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Sync</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="plate in recentPlates"
                  :key="plate.id"
                  class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
                >
                  <td class="py-2 px-3 font-mono text-zinc-300">
                    {{ plate.created_at ? new Date(plate.created_at).toLocaleString('id-ID') : '---' }}
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
                  <td class="py-2 px-3 font-mono font-bold text-white">{{ plate.plate_number }}</td>
                  <td class="py-2 px-3 text-zinc-300">
                    {{ plate.confidence ? `${plate.confidence.toFixed(1)}%` : '---' }}
                  </td>
                  <td class="py-2 px-3">
                    <span
                      :class="[
                        'w-2 h-2 inline-block rounded-full',
                        plate.synced ? 'bg-emerald-400' : 'bg-amber-400',
                      ]"
                      :title="plate.synced ? 'Terkirim' : 'Menunggu sync'"
                    ></span>
                  </td>
                </tr>
                <tr v-if="!recentPlates.length">
                  <td colspan="5" class="py-4 text-center text-zinc-500">Belum ada data</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Sidebar: Sync Status -->
      <div class="space-y-6">
        <SyncStatus />
      </div>
    </div>
  </div>
</template>
