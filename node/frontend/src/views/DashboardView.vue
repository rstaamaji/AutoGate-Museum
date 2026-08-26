<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import GateCard from '@/components/gate/GateCard.vue'
import PlateDetailModal from '@/components/gate/PlateDetailModal.vue'
import RfidInputModal from '@/components/gate/RfidInputModal.vue'
import SyncStatus from '@/components/sync/SyncStatus.vue'
import { Nfc, Loader2 } from '@lucide/vue'
import api from '@/services/api'
import EntryKiosk from '@/components/payment/EntryKiosk.vue'

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
    confidence: null,
    barrierStatus: 'TERTUTUP',
  },
])

const recentPlates = ref([])
const loading = ref(false)
const selectedPlate = ref(null)
let refreshTimer = null
let fastPollTimer = null
const emit = defineEmits(['navigate'])

// ── RFID Modal State ──
const pendingRfid = ref(null) // { vehicle, direction }
const lastSeenIds = ref(new Set()) // id kendaraan yang sudah diketahui
const firstLoad = ref(true) // skip deteksi pada load pertama

// ── Vehicle menunggu RFID (untuk banner) ──
const waitingRfidPlates = computed(() => {
  return recentPlates.value.filter(v => v.rfid_uid === null)
})

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

    // Deteksi vehicle baru tanpa RFID (dari Hikvision push otomatis)
    const currentIds = new Set((data.items || []).map(v => v.id))

    if (!firstLoad.value && !pendingRfid.value) {
      for (const item of (data.items || [])) {
        if (item.rfid_uid === null && !lastSeenIds.value.has(item.id)) {
          // Vehicle baru tanpa RFID — tampilkan modal
          pendingRfid.value = {
            vehicle: item,
            direction: item.direction,
          }
          break
        }
      }
    }

    // Update lastSeenIds setelah deteksi
    lastSeenIds.value = currentIds
    firstLoad.value = false
  } catch (err) {
    console.error('Gagal mengambil data:', err)
  }
}

const handleCapture = (direction) => {
  fetchRecentPlates()
}

const handleRefresh = () => {
  fetchRecentPlates()
}

// Handle capture response dari GateCard (manual capture)
const handleCaptureResponse = (response) => {
  if (response.rfid_pending && response.vehicle) {
    lastSeenIds.value.add(response.vehicle.id)
    pendingRfid.value = {
      vehicle: response.vehicle,
      direction: response.vehicle.direction,
    }
  }
}

// Klik banner "menunggu RFID" → buka modal lagi
const reopenRfidModal = (item) => {
  if (!pendingRfid.value) {
    pendingRfid.value = {
      vehicle: item,
      direction: item.direction,
    }
  }
}

const handleRfidDone = ({ rfid_match }) => {
  // Bisa tambahkan notifikasi jika rfid_match === false
}

const handleRfidClose = () => {
  pendingRfid.value = null
  fetchRecentPlates()
}

onMounted(() => {
  fetchRecentPlates()
  // Polling utama: 15 detik
  refreshTimer = setInterval(fetchRecentPlates, 15000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div class="p-4 sm:p-6 space-y-6">
<<<<<<< Updated upstream
    <!-- Banner: Menunggu RFID -->
    <div
      v-if="waitingRfidPlates.length > 0 && !pendingRfid"
      class="bg-amber-950/80 border border-amber-700/60 rounded-xl p-4 shadow-lg shadow-black/30 animate-pulse"
    >
      <div class="flex items-center gap-3">
        <div class="p-2 bg-amber-500/20 rounded-lg">
          <Nfc class="w-5 h-5 text-amber-400 animate-bounce" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-bold text-amber-300">Menunggu Input RFID</p>
          <p class="text-xs text-amber-400/80">
            {{ waitingRfidPlates.length }} kendaraan menunggu RFID:
            <span v-for="(p, i) in waitingRfidPlates" :key="p.id">
              <button
                @click="reopenRfidModal(p)"
                class="font-mono font-bold text-amber-200 hover:text-white underline cursor-pointer"
              >{{ p.plate_number }}</button>{{ i < waitingRfidPlates.length - 1 ? ', ' : '' }}
            </span>
          </p>
        </div>
        <button
          v-if="waitingRfidPlates.length === 1"
          @click="reopenRfidModal(waitingRfidPlates[0])"
          class="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold rounded-lg transition"
        >
          Input RFID
        </button>
      </div>
    </div>
=======
    <EntryKiosk />
>>>>>>> Stashed changes

    <!-- Grid: Gate Cards + Sync Status -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Gate Cards (2 kolom) -->
      <div class="xl:col-span-2 space-y-6 min-w-0">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GateCard
            v-for="gate in gates"
            :key="gate.id"
            :gate="gate"
            :direction="gate.direction"
            @capture="handleCapture"
            @refresh="handleRefresh"
            @capture-response="handleCaptureResponse"
          />
        </div>

        <!-- Riwayat Terbaru -->
        <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-bold text-white tracking-tight">Riwayat Terbaru (10 Terakhir)</h3>
            <button
              @click="$emit('navigate', 'history')"
              class="text-xs font-semibold text-emerald-400 hover:text-emerald-300 hover:underline transition"
            >
              Lihat Selengkapnya →
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-zinc-800">
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Event ID</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Waktu</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Arah</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Gambar</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Plat</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">RFID</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Confidence</th>
                  <th class="text-left py-2 px-3 text-zinc-500 font-medium">Sync</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="plate in recentPlates"
                  :key="plate.id"
                  class="border-b border-zinc-800/50 hover:bg-zinc-800/30 cursor-pointer"
                  :class="{ 'bg-amber-950/20 border-amber-800/30': plate.rfid_uid === null }"
                  @click="selectedPlate = plate"
                >
                  <td class="py-2 px-3 font-mono text-[10px] text-zinc-500">
                    {{ plate.event_id ? plate.event_id.substring(0, 8) + '...' : '---' }}
                  </td>
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
                  <td class="py-2 px-3">
                    <span
                      v-if="plate.rfid_uid"
                      class="inline-flex items-center gap-1 font-mono text-[10px] text-violet-300 bg-violet-500/10 border border-violet-500/20 px-1.5 py-0.5 rounded"
                    >
                      <Nfc class="w-3 h-3" />
                      {{ plate.rfid_uid }}
                    </span>
                    <span v-else class="inline-flex items-center gap-1 text-amber-400 text-[10px] font-semibold">
                      <Loader2 class="w-3 h-3 animate-spin" />
                      Menunggu
                    </span>
                  </td>
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
                  <td colspan="8" class="py-4 text-center text-zinc-500">Belum ada data</td>
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

    <!-- Modal Detail -->
    <PlateDetailModal
      v-if="selectedPlate"
      :plate="selectedPlate"
      @close="selectedPlate = null"
    />

    <!-- Modal RFID Input -->
    <RfidInputModal
      v-if="pendingRfid"
      :vehicle="pendingRfid.vehicle"
      :direction="pendingRfid.direction"
      @done="handleRfidDone"
      @close="handleRfidClose"
    />
  </div>
</template>
