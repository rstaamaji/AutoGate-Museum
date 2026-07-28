<script setup>
import { ref, onMounted } from 'vue'
import { Radio, Plus, Pencil, Trash2, X, Loader2, AlertTriangle, Check, Copy, Eye, EyeOff } from '@lucide/vue'
import api from '@/services/api'

const nodes = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingNode = ref(null)
const saving = ref(false)
const error = ref('')
const showApiKey = ref({})
const copiedKey = ref(null)

const form = ref({
  name: '',
  location: '',
})

const fetchNodes = async () => {
  loading.value = true
  try {
    const data = await api.getNodes()
    nodes.value = data.items || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingNode.value = null
  form.value = { name: '', location: '' }
  error.value = ''
  showModal.value = true
}

const openEdit = (node) => {
  editingNode.value = node
  form.value = { name: node.name, location: node.location || '' }
  error.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingNode.value = null
  error.value = ''
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    if (editingNode.value) {
      await api.updateNode(editingNode.value.id, form.value)
    } else {
      await api.createNode(form.value)
    }
    closeModal()
    await fetchNodes()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const handleDelete = async (node) => {
  if (!confirm(`Hapus node '${node.name}'?`)) return
  try {
    await api.deleteNode(node.id)
    await fetchNodes()
  } catch (err) {
    alert(err.message)
  }
}

const copyApiKey = (nodeId, apiKey) => {
  navigator.clipboard.writeText(apiKey)
  copiedKey.value = nodeId
  setTimeout(() => { copiedKey.value = null }, 2000)
}

const toggleApiKey = (nodeId) => {
  showApiKey.value[nodeId] = !showApiKey.value[nodeId]
}

const maskKey = (key) => {
  if (!key) return ''
  return key.substring(0, 8) + '...' + key.substring(key.length - 4)
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(fetchNodes)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <Radio class="w-5 h-5 text-zinc-400" />
          Kelola Node
        </h2>
        <p class="text-xs text-zinc-400 mt-1">Manajemen pos satpam dan API key</p>
      </div>
      <button
        @click="openCreate"
        class="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg text-sm transition"
      >
        <Plus class="w-4 h-4" />
        Tambah Node
      </button>
    </div>

    <!-- Table -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl shadow-xl shadow-black/40 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Nama</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">ID</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">API Key</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Lokasi</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Status</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Terakhir</th>
              <th class="text-right py-3 px-4 text-zinc-500 font-medium">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="n in nodes"
              :key="n.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
            >
              <td class="py-3 px-4 font-medium text-white">{{ n.name }}</td>
              <td class="py-3 px-4 font-mono text-zinc-500 text-[10px]">{{ n.id.substring(0, 8) }}...</td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-1">
                  <code class="text-[10px] text-zinc-400 font-mono">
                    {{ showApiKey[n.id] ? n.api_key : maskKey(n.api_key) }}
                  </code>
                  <button @click="toggleApiKey(n.id)" class="p-1 text-zinc-500 hover:text-zinc-300 transition">
                    <Eye v-if="!showApiKey[n.id]" class="w-3 h-3" />
                    <EyeOff v-else class="w-3 h-3" />
                  </button>
                  <button
                    @click="copyApiKey(n.id, n.api_key)"
                    class="p-1 transition"
                    :class="copiedKey === n.id ? 'text-emerald-400' : 'text-zinc-500 hover:text-zinc-300'"
                    title="Copy API Key"
                  >
                    <Check v-if="copiedKey === n.id" class="w-3 h-3" />
                    <Copy v-else class="w-3 h-3" />
                  </button>
                </div>
              </td>
              <td class="py-3 px-4 text-zinc-400">{{ n.location || '---' }}</td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-1.5">
                  <span :class="['w-2 h-2 rounded-full', n.status === 'online' ? 'bg-emerald-400' : 'bg-red-400']"></span>
                  <span class="text-zinc-300">{{ n.status }}</span>
                </div>
              </td>
              <td class="py-3 px-4 text-zinc-400 font-mono text-[10px]">{{ formatTime(n.last_seen_at) }}</td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openEdit(n)" class="p-1.5 rounded text-zinc-400 hover:text-blue-400 hover:bg-blue-950/50 transition" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button @click="handleDelete(n)" class="p-1.5 rounded text-zinc-400 hover:text-red-400 hover:bg-red-950/50 transition" title="Hapus">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!nodes.length && !loading">
              <td colspan="7" class="py-6 text-center text-zinc-500">Belum ada node</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeModal">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h3 class="text-lg font-bold text-white">{{ editingNode ? 'Edit Node' : 'Tambah Node' }}</h3>
          <button @click="closeModal" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSave" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Node</label>
            <input v-model="form.name" type="text" placeholder="Contoh: Gerbang Depan" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Lokasi (opsional)</label>
            <input v-model="form.location" type="text" placeholder="Contoh: Depan Fakultas MIPA" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500" />
          </div>

          <div v-if="!editingNode" class="bg-blue-950/50 border border-blue-800/50 rounded-lg px-3 py-2">
            <p class="text-xs text-blue-300">UUID dan API key akan di-generate otomatis oleh server.</p>
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
              {{ editingNode ? 'Simpan' : 'Buat' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
