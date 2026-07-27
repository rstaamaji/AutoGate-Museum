<script setup>
import { ref, onMounted } from 'vue'
import { Car, Search, Loader2, ChevronLeft, ChevronRight } from '@lucide/vue'
import api from '@/services/api'

const vehicles = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(0)
const limit = 50
const searchQ = ref('')

const fetchVehicles = async () => {
  loading.value = true
  try {
    const data = await api.getVehicles({ q: searchQ.value, skip: page.value * limit, limit })
    vehicles.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 0
  fetchVehicles()
}

const nextPage = () => {
  if ((page.value + 1) * limit < total.value) {
    page.value++
    fetchVehicles()
  }
}

const prevPage = () => {
  if (page.value > 0) {
    page.value--
    fetchVehicles()
  }
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(fetchVehicles)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <Car class="w-5 h-5 text-zinc-400" />
          Kendaraan
        </h2>
        <p class="text-xs text-zinc-400 mt-1">Daftar kendaraan yang tercatat dari semua node</p>
      </div>
      <span class="text-xs text-zinc-500">{{ total }} kendaraan</span>
    </div>

    <!-- Search -->
    <div class="mb-4">
      <div class="flex gap-2 max-w-sm">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            v-model="searchQ"
            type="text"
            placeholder="Cari plat nomor..."
            @keyup.enter="handleSearch"
            class="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>
        <button @click="handleSearch" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm rounded-lg transition">
          Cari
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl shadow-xl shadow-black/40 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="text-left py-3 px-4 text-zinc-500 font-medium w-16">ID</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Plat Nomor</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Pemilik</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Tipe</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">CC</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Terdaftar</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="v in vehicles"
              :key="v.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
            >
              <td class="py-3 px-4 text-zinc-500 font-mono">{{ v.id }}</td>
              <td class="py-3 px-4 font-mono font-bold text-white">{{ v.plate_number }}</td>
              <td class="py-3 px-4 text-zinc-300">{{ v.owner_name || '---' }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ v.vehicle_type || '---' }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ v.cc || '---' }}</td>
              <td class="py-3 px-4 text-zinc-500 whitespace-nowrap">{{ formatTime(v.created_at) }}</td>
            </tr>
            <tr v-if="!vehicles.length && !loading">
              <td colspan="6" class="py-6 text-center text-zinc-500">Belum ada kendaraan tercatat</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-4 gap-2 text-zinc-500">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span class="text-xs">Memuat...</span>
      </div>

      <!-- Pagination -->
      <div v-if="total > limit" class="flex items-center justify-between px-4 py-3 border-t border-zinc-800">
        <span class="text-xs text-zinc-500">
          {{ page * limit + 1 }}–{{ Math.min((page + 1) * limit, total) }} dari {{ total }}
        </span>
        <div class="flex gap-1">
          <button
            @click="prevPage"
            :disabled="page === 0"
            class="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 disabled:opacity-30 transition"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <button
            @click="nextPage"
            :disabled="(page + 1) * limit >= total"
            class="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 disabled:opacity-30 transition"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
