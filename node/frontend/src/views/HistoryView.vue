<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Search, Calendar, Filter, ChevronLeft, ChevronRight,
  RefreshCw, Loader2, History, X, Nfc,
} from '@lucide/vue'
import PlateDetailModal from '@/components/gate/PlateDetailModal.vue'
import api from '@/services/api'

const items = ref([])
const total = ref(0)
const loading = ref(false)
const selectedPlate = ref(null)

// Filters & Pagination
const search = ref('')
const direction = ref('')
const startDate = ref('')
const endDate = ref('')
const page = ref(1)
const perPage = 20

// Search debouncer
let searchTimeout = null

const totalPages = computed(() => Math.ceil(total.value / perPage) || 1)

const fetchHistory = async () => {
  loading.value = true
  try {
    const skip = (page.value - 1) * perPage
    const data = await api.getPlates({
      skip,
      limit: perPage,
      direction: direction.value || undefined,
      search: search.value.trim() || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
    })
    items.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    console.error('Gagal mengambil data riwayat:', err)
  } finally {
    loading.value = false
  }
}

const handleSearchInput = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchHistory()
  }, 400)
}

const handleFilterChange = () => {
  page.value = 1
  fetchHistory()
}

const resetFilters = () => {
  search.value = ''
  direction.value = ''
  startDate.value = ''
  endDate.value = ''
  page.value = 1
  fetchHistory()
}

const goToPage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchHistory()
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="p-4 sm:p-6 space-y-6">
    <!-- Header Page -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40">
      <div>
        <div class="flex items-center gap-2">
          <History class="w-5 h-5 text-emerald-400" />
          <h2 class="text-xl font-bold text-white tracking-tight">Riwayat Kendaraan Lengkap</h2>
        </div>
        <p class="text-xs text-zinc-400 mt-1">Daftar seluruh kendaraan yang tercatat di Pos Satpam</p>
      </div>

      <button
        @click="fetchHistory"
        :disabled="loading"
        class="flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold px-4 py-2.5 rounded-lg border border-zinc-700/60 transition disabled:opacity-50"
      >
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        <RefreshCw v-else class="w-4 h-4 text-emerald-400" />
        <span>Refresh Data</span>
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Search Plat -->
        <div>
          <label class="block text-[11px] font-medium text-zinc-400 mb-1">Cari Plat Nomor</label>
          <div class="relative">
            <input
              v-model="search"
              @input="handleSearchInput"
              type="text"
              placeholder="Contoh: AD1234AB..."
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white uppercase font-mono placeholder:normal-case placeholder:font-sans focus:outline-none focus:border-emerald-500"
            />
            <Search class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          </div>
        </div>

        <!-- Filter Arah -->
        <div>
          <label class="block text-[11px] font-medium text-zinc-400 mb-1">Arah Pintu</label>
          <div class="relative">
            <select
              v-model="direction"
              @change="handleFilterChange"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="">Semua Arah</option>
              <option value="masuk">Masuk</option>
              <option value="keluar">Keluar</option>
            </select>
            <Filter class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          </div>
        </div>

        <!-- Tanggal Mulai -->
        <div>
          <label class="block text-[11px] font-medium text-zinc-400 mb-1">Dari Tanggal</label>
          <div class="relative cursor-pointer" @click="$refs.startDateInput?.showPicker()">
            <input
              ref="startDateInput"
              v-model="startDate"
              @change="handleFilterChange"
              @focus="$event.target.showPicker && $event.target.showPicker()"
              type="date"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 cursor-pointer [color-scheme:dark]"
            />
            <Calendar class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>

        <!-- Tanggal Akhir -->
        <div>
          <label class="block text-[11px] font-medium text-zinc-400 mb-1">Sampai Tanggal</label>
          <div class="relative cursor-pointer" @click="$refs.endDateInput?.showPicker()">
            <input
              ref="endDateInput"
              v-model="endDate"
              @change="handleFilterChange"
              @focus="$event.target.showPicker && $event.target.showPicker()"
              type="date"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 cursor-pointer [color-scheme:dark]"
            />
            <Calendar class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </div>

      <!-- Active Filters Reset -->
      <div v-if="search || direction || startDate || endDate" class="flex items-center justify-between pt-2 border-t border-zinc-800/60 text-xs">
        <span class="text-zinc-400">Filter aktif diterapkan</span>
        <button
          @click="resetFilters"
          class="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-medium"
        >
          <X class="w-3.5 h-3.5" />
          <span>Reset Filter</span>
        </button>
      </div>
    </div>

    <!-- Table Section -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40 space-y-4">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Event ID</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Waktu Capture</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Arah</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Foto Plat</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Plat Nomor</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">RFID</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Confidence</th>
              <th class="text-left py-3 px-3 text-zinc-400 font-semibold">Status Sync</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="item.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/40 cursor-pointer transition"
              @click="selectedPlate = item"
            >
              <td class="py-2.5 px-3 font-mono text-[10px] text-zinc-500">
                {{ item.event_id ? item.event_id.substring(0, 8) + '...' : '---' }}
              </td>
              <td class="py-2.5 px-3 font-mono text-zinc-300">
                {{ item.created_at ? new Date(item.created_at).toLocaleString('id-ID') : '---' }}
              </td>
              <td class="py-2.5 px-3">
                <span
                  :class="[
                    'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                    item.direction === 'masuk'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
                  ]"
                >
                  {{ item.direction }}
                </span>
              </td>
              <td class="py-2.5 px-3">
                <img
                  v-if="item.plate_image_url"
                  :src="item.plate_image_url"
                  alt="Plat"
                  class="w-16 h-10 object-contain rounded border border-zinc-700 bg-zinc-950"
                />
                <span v-else class="text-zinc-600">---</span>
              </td>
              <td class="py-2.5 px-3 font-mono font-bold text-white text-sm tracking-wider">
                {{ item.plate_number }}
              </td>
              <td class="py-2.5 px-3">
                <span
                  v-if="item.rfid_uid"
                  class="inline-flex items-center gap-1 font-mono text-[10px] text-violet-300 bg-violet-500/10 border border-violet-500/20 px-1.5 py-0.5 rounded"
                >
                  <Nfc class="w-3 h-3" />
                  {{ item.rfid_uid }}
                </span>
                <span v-else class="text-zinc-600">---</span>
              </td>
              <td class="py-2.5 px-3 text-zinc-300">
                {{ item.confidence ? `${item.confidence.toFixed(1)}%` : '---' }}
              </td>
              <td class="py-2.5 px-3">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold',
                    item.synced
                      ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                      : 'bg-amber-950/80 text-amber-400 border border-amber-800',
                  ]"
                >
                  <span :class="['w-1.5 h-1.5 rounded-full', item.synced ? 'bg-emerald-400' : 'bg-amber-400']"></span>
                  {{ item.synced ? 'Synced' : 'Pending' }}
                </span>
              </td>
            </tr>
            <tr v-if="!loading && !items.length">
              <td colspan="8" class="py-8 text-center text-zinc-500">
                Tidak ada data riwayat yang ditemukan.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Bar (20 item per halaman) -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-zinc-800 text-xs">
        <div class="text-zinc-400 font-medium">
          Menampilkan <span class="text-white font-bold">{{ items.length ? (page - 1) * perPage + 1 : 0 }}</span> - 
          <span class="text-white font-bold">{{ Math.min(page * perPage, total) }}</span> dari 
          <span class="text-white font-bold">{{ total }}</span> riwayat
        </div>

        <div class="flex items-center gap-1.5">
          <button
            @click="goToPage(page - 1)"
            :disabled="page <= 1 || loading"
            class="p-2 rounded-lg bg-zinc-950 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 disabled:opacity-30 disabled:hover:bg-zinc-950 transition"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="px-3 py-1.5 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 font-mono">
            {{ page }} / {{ totalPages }}
          </span>
          <button
            @click="goToPage(page + 1)"
            :disabled="page >= totalPages || loading"
            class="p-2 rounded-lg bg-zinc-950 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 disabled:opacity-30 disabled:hover:bg-zinc-950 transition"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
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
