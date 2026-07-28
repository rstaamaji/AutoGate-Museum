<script setup>
import { ref, onMounted } from 'vue'
import { Tag, Plus, Pencil, Trash2, X, Loader2, Check, AlertTriangle } from '@lucide/vue'
import api from '@/services/api'

const types = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingType = ref(null)
const saving = ref(false)
const error = ref('')

const form = ref({
  name: '',
})

const fetchTypes = async () => {
  loading.value = true
  try {
    const data = await api.getVehicleTypes()
    types.value = data.items || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingType.value = null
  form.value = { name: '' }
  error.value = ''
  showModal.value = true
}

const openEdit = (t) => {
  editingType.value = t
  form.value = {
    name: t.name,
  }
  error.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingType.value = null
  error.value = ''
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    if (editingType.value) {
      await api.updateVehicleType(editingType.value.id, form.value)
    } else {
      await api.createVehicleType(form.value)
    }
    closeModal()
    await fetchTypes()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const handleDelete = async (t) => {
  if (!confirm(`Hapus tipe kendaraan '${t.name}'?`)) return
  try {
    await api.deleteVehicleType(t.id)
    await fetchTypes()
  } catch (err) {
    alert(err.message)
  }
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(fetchTypes)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <Tag class="w-5 h-5 text-zinc-400" />
          Tipe Kendaraan
        </h2>
        <p class="text-xs text-zinc-400 mt-1">Master data tipe kendaraan</p>
      </div>
      <button
        @click="openCreate"
        class="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg text-sm transition"
      >
        <Plus class="w-4 h-4" />
        Tambah Tipe
      </button>
    </div>

    <!-- Table -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl shadow-xl shadow-black/40 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">ID</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Nama</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Dibuat</th>
              <th class="text-right py-3 px-4 text-zinc-500 font-medium">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="t in types"
              :key="t.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
            >
              <td class="py-3 px-4 text-zinc-500 font-mono">{{ t.id }}</td>
              <td class="py-3 px-4 font-semibold text-white">{{ t.name }}</td>
              <td class="py-3 px-4 text-zinc-500 whitespace-nowrap">{{ formatTime(t.created_at) }}</td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openEdit(t)" class="p-1.5 rounded text-zinc-400 hover:text-blue-400 hover:bg-blue-950/50 transition" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button @click="handleDelete(t)" class="p-1.5 rounded text-zinc-400 hover:text-red-400 hover:bg-red-950/50 transition" title="Hapus">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!types.length && !loading">
              <td colspan="4" class="py-6 text-center text-zinc-500">Belum ada tipe kendaraan</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-4 gap-2 text-zinc-500">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span class="text-xs">Memuat...</span>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeModal">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h3 class="text-lg font-bold text-white">{{ editingType ? 'Edit Tipe Kendaraan' : 'Tambah Tipe Kendaraan' }}</h3>
          <button @click="closeModal" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSave" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Tipe</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="misal: Mobil, Motor, Truk"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              required
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
              {{ editingType ? 'Simpan' : 'Buat' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
