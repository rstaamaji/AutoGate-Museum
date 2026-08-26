<script setup>
import { ref, onMounted } from 'vue'
import { Car, Search, Loader2, ChevronLeft, ChevronRight, Pencil, X, Check, AlertTriangle } from '@lucide/vue'
import api from '@/services/api'

const vehicles = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(0)
const limit = 50
const searchQ = ref('')

// Modal edit
const showModal = ref(false)
const editingVehicle = ref(null)
const saving = ref(false)
const error = ref('')
const vehicleTypes = ref([])

const form = ref({
  vehicle_type: '',
  cc: null,
})

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

const fetchVehicleTypes = async () => {
  try {
    const data = await api.getVehicleTypes()
    vehicleTypes.value = data.items || []
  } catch {
    vehicleTypes.value = []
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

const openEdit = (v) => {
  editingVehicle.value = v
  form.value = {
    vehicle_type: v.vehicle_type || '',
    cc: v.cc ?? null,
  }
  error.value = ''
  showModal.value = true
  fetchVehicleTypes()
}

const closeModal = () => {
  showModal.value = false
  editingVehicle.value = null
  error.value = ''
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    const payload = {}
    if (form.value.vehicle_type !== (editingVehicle.value.vehicle_type || '')) {
      payload.vehicle_type = form.value.vehicle_type || null
    }
    if (form.value.cc !== (editingVehicle.value.cc ?? null)) {
      payload.cc = form.value.cc
    }
    if (Object.keys(payload).length === 0) {
      closeModal()
      return
    }
    await api.updateVehicle(editingVehicle.value.id, payload)
    closeModal()
    await fetchVehicles()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
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
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Tipe</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">CC</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Terdaftar</th>
              <th class="text-right py-3 px-4 text-zinc-500 font-medium">Aksi</th>
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
              <td class="py-3 px-4 text-zinc-400">{{ v.vehicle_type || '---' }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ v.cc ?? '---' }}</td>
              <td class="py-3 px-4 text-zinc-500 whitespace-nowrap">{{ formatTime(v.created_at) }}</td>
              <td class="py-3 px-4 text-right">
                <button @click="openEdit(v)" class="p-1.5 rounded text-zinc-400 hover:text-blue-400 hover:bg-blue-950/50 transition" title="Edit tipe &amp; CC">
                  <Pencil class="w-3.5 h-3.5" />
                </button>
              </td>
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

    <!-- Modal Edit -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeModal">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h3 class="text-lg font-bold text-white">Edit Kendaraan</h3>
          <button @click="closeModal" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSave" class="p-6 space-y-4">
          <!-- Plat Nomor (read-only) -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Plat Nomor</label>
            <div class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-400 font-mono">
              {{ editingVehicle?.plate_number }}
            </div>
          </div>

          <!-- Tipe Kendaraan (dropdown) -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Tipe Kendaraan</label>
            <select
              v-model="form.vehicle_type"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              <option value="" class="bg-zinc-900">-- Pilih tipe --</option>
              <option
                v-for="t in vehicleTypes"
                :key="t.id"
                :value="t.name"
                class="bg-zinc-900"
              >
                {{ t.name }}
              </option>
            </select>
            <p class="text-[10px] text-zinc-600 mt-1">Tipe diambil dari master data Tipe Kendaraan</p>
          </div>

          <!-- CC -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">CC</label>
            <input
              v-model.number="form.cc"
              type="number"
              min="0"
              max="9999"
              placeholder="misal: 1500"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div v-if="error" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
            <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            <p class="text-xs text-red-300">{{ error }}</p>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="closeModal" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-medium rounded-lg transition">Batal</button>
            <button type="submit" :disabled="saving" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition disabled:opacity-50">
              <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
              <Check v-else class="w-4 h-4" />
              Simpan
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
