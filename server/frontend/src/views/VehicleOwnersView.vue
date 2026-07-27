<script setup>
import { ref, onMounted, watch } from 'vue'
import { Car, Plus, Pencil, Trash2, X, Loader2, AlertTriangle, Check, Search, ChevronDown } from '@lucide/vue'
import api from '@/services/api'

const owners = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingOwner = ref(null)
const saving = ref(false)
const error = ref('')
const searchPlate = ref('')

// Dropdown plat
const vehicleOptions = ref([])
const dropdownOpen = ref(false)
const dropdownLoading = ref(false)
const plateSearch = ref('')
let searchTimeout = null

const form = ref({
  plate_number: '',
  owner_name: '',
  owner_address: '',
  owner_phone: '',
  notes: '',
})

const fetchOwners = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchPlate.value) params.plate_number = searchPlate.value
    const data = await api.getVehicleOwners(params)
    owners.value = data.items || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchOwners()
}

// Fetch vehicles untuk dropdown
const fetchVehicles = async (q = '') => {
  dropdownLoading.value = true
  try {
    const data = await api.searchVehicles(q, 20)
    vehicleOptions.value = data.items || data || []
  } catch {
    vehicleOptions.value = []
  } finally {
    dropdownLoading.value = false
  }
}

// Debounce search
const onPlateSearch = (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchVehicles(val)
  }, 300)
}

const selectPlate = (plate) => {
  form.value.plate_number = plate
  dropdownOpen.value = false
  plateSearch.value = ''
}

const onPlateInput = (e) => {
  form.value.plate_number = e.target.value
  plateSearch.value = e.target.value
  dropdownOpen.value = true
  onPlateSearch(e.target.value)
}

const openDropdown = () => {
  dropdownOpen.value = true
  plateSearch.value = form.value.plate_number
  fetchVehicles(form.value.plate_number)
}

const openCreate = () => {
  editingOwner.value = null
  form.value = { plate_number: '', owner_name: '', owner_address: '', owner_phone: '', notes: '' }
  error.value = ''
  plateSearch.value = ''
  dropdownOpen.value = false
  showModal.value = true
  fetchVehicles()
}

const openEdit = (owner) => {
  editingOwner.value = owner
  form.value = {
    plate_number: owner.plate_number,
    owner_name: owner.owner_name,
    owner_address: owner.owner_address || '',
    owner_phone: owner.owner_phone || '',
    notes: owner.notes || '',
  }
  error.value = ''
  plateSearch.value = ''
  dropdownOpen.value = false
  showModal.value = true
  fetchVehicles(owner.plate_number)
}

const closeModal = () => {
  showModal.value = false
  editingOwner.value = null
  dropdownOpen.value = false
  error.value = ''
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    if (editingOwner.value) {
      await api.updateVehicleOwner(editingOwner.value.id, form.value)
    } else {
      await api.createVehicleOwner(form.value)
    }
    closeModal()
    await fetchOwners()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const handleDelete = async (owner) => {
  if (!confirm(`Hapus pemilik plat '${owner.plate_number}'?`)) return
  try {
    await api.deleteVehicleOwner(owner.id)
    await fetchOwners()
  } catch (err) {
    alert(err.message)
  }
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(fetchOwners)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <Car class="w-5 h-5 text-zinc-400" />
          Pemilik Kendaraan
        </h2>
        <p class="text-xs text-zinc-400 mt-1">Data pemilik berdasarkan plat nomor</p>
      </div>
      <button
        @click="openCreate"
        class="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg text-sm transition"
      >
        <Plus class="w-4 h-4" />
        Tambah Pemilik
      </button>
    </div>

    <!-- Search -->
    <div class="mb-4">
      <div class="flex gap-2">
        <div class="relative flex-1 max-w-sm">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            v-model="searchPlate"
            type="text"
            placeholder="Cari plat nomor..."
            @keyup.enter="handleSearch"
            class="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500"
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
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Plat Nomor</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Nama Pemilik</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Alamat</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Telepon</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Catatan</th>
              <th class="text-right py-3 px-4 text-zinc-500 font-medium">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="o in owners"
              :key="o.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
            >
              <td class="py-3 px-4 font-mono font-bold text-white">{{ o.plate_number }}</td>
              <td class="py-3 px-4 text-zinc-300">{{ o.owner_name }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ o.owner_address || '---' }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ o.owner_phone || '---' }}</td>
              <td class="py-3 px-4 text-zinc-400">{{ o.notes || '---' }}</td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openEdit(o)" class="p-1.5 rounded text-zinc-400 hover:text-blue-400 hover:bg-blue-950/50 transition" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button @click="handleDelete(o)" class="p-1.5 rounded text-zinc-400 hover:text-red-400 hover:bg-red-950/50 transition" title="Hapus">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!owners.length && !loading">
              <td colspan="6" class="py-6 text-center text-zinc-500">Belum ada data pemilik</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeModal">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h3 class="text-lg font-bold text-white">{{ editingOwner ? 'Edit Pemilik' : 'Tambah Pemilik' }}</h3>
          <button @click="closeModal" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSave" class="p-6 space-y-4">
          <!-- Dropdown Plat Nomor -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Plat Nomor</label>
            <div class="relative">
              <input
                :value="form.plate_number"
                @input="onPlateInput"
                @focus="openDropdown"
                @blur="setTimeout(() => dropdownOpen = false, 200)"
                type="text"
                placeholder="Ketik atau pilih plat..."
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 pr-8 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 font-mono"
                autocomplete="off"
              />
              <ChevronDown class="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />

              <!-- Dropdown -->
              <div
                v-if="dropdownOpen"
                class="absolute z-10 w-full mt-1 bg-zinc-950 border border-zinc-700 rounded-lg shadow-xl max-h-48 overflow-y-auto"
              >
                <div v-if="dropdownLoading" class="px-3 py-2 text-xs text-zinc-500 flex items-center gap-2">
                  <Loader2 class="w-3 h-3 animate-spin" />
                  Mencari...
                </div>
                <div
                  v-for="v in vehicleOptions"
                  :key="v.id"
                  @mousedown.prevent="selectPlate(v.plate_number)"
                  class="px-3 py-2 text-sm font-mono text-zinc-300 hover:bg-zinc-800 cursor-pointer transition"
                >
                  {{ v.plate_number }}
                  <span v-if="v.vehicle_type" class="text-zinc-500 text-xs ml-2">({{ v.vehicle_type }})</span>
                </div>
                <div v-if="!vehicleOptions.length && !dropdownLoading" class="px-3 py-2 text-xs text-zinc-500">
                  Tidak ditemukan — ketik plat baru
                </div>
              </div>
            </div>
            <p class="text-[10px] text-zinc-600 mt-1">Pilih dari kendaraan yang sudah terdaftar, atau ketik plat baru</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Pemilik</label>
            <input v-model="form.owner_name" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Alamat</label>
            <input v-model="form.owner_address" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Telepon</label>
            <input v-model="form.owner_phone" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Catatan</label>
            <input v-model="form.notes" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
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
              {{ editingOwner ? 'Simpan' : 'Buat' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
