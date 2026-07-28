<script setup>
import { ref, onMounted } from 'vue'
import {
  Settings, Server, Radio, Loader2, Check, AlertTriangle,
  Eye, EyeOff, Save,
} from '@lucide/vue'
import api from '@/services/api'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const showPasswords = ref({})

const serverForm = ref({})
const relayForm = ref({})

const fetchSettings = async () => {
  loading.value = true
  try {
    const data = await api.getSettings()
    serverForm.value = { ...data.server }
    relayForm.value = { ...data.relay }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const handleSave = async (section) => {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    let updates = {}
    if (section === 'server') updates = { ...serverForm.value }
    if (section === 'relay') updates = { ...relayForm.value }

    const result = await api.updateSettings(updates)
    success.value = result.message || 'Berhasil disimpan'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const togglePassword = (field) => {
  showPasswords.value[field] = !showPasswords.value[field]
}

onMounted(fetchSettings)
</script>

<template>
  <div class="p-6 space-y-6">
    <div>
      <h2 class="text-xl font-bold text-white flex items-center gap-2">
        <Settings class="w-5 h-5 text-zinc-400" />
        Pengaturan Node
      </h2>
      <p class="text-xs text-zinc-400 mt-1">Konfigurasi server dan relay. Kamera diatur dari masing-masing gate card.</p>
    </div>

    <!-- Notifications -->
    <div v-if="success" class="flex items-start gap-2 bg-emerald-950/80 border border-emerald-800/60 rounded-lg px-3 py-2">
      <Check class="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
      <p class="text-xs text-emerald-300">{{ success }}</p>
    </div>
    <div v-if="error" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
      <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
      <p class="text-xs text-red-300">{{ error }}</p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 class="w-6 h-6 text-zinc-400 animate-spin" />
    </div>

    <template v-else>
      <!-- Server Sync -->
      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Server class="w-4 h-4 text-blue-400" />
            <h3 class="text-sm font-bold text-white">Server & Sinkronisasi</h3>
          </div>
          <button @click="handleSave('server')" :disabled="saving"
            class="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-1.5 px-3 rounded-lg text-xs transition disabled:opacity-50">
            <Loader2 v-if="saving" class="w-3.5 h-3.5 animate-spin" />
            <Save v-else class="w-3.5 h-3.5" />
            Simpan
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Server URL</label>
            <input v-model="serverForm.SERVER_URL" type="text"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Server API Key</label>
            <div class="relative">
              <input v-model="serverForm.SERVER_API_KEY"
                :type="showPasswords.SERVER_API_KEY ? 'text' : 'password'"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 pr-10 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
              <button @click="togglePassword('SERVER_API_KEY')" class="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300">
                <Eye v-if="!showPasswords.SERVER_API_KEY" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Sync Interval (detik)</label>
            <input v-model="serverForm.SYNC_INTERVAL" type="number"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
          </div>
        </div>
      </div>

      <!-- Relay -->
      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Radio class="w-4 h-4 text-amber-400" />
            <h3 class="text-sm font-bold text-white">Modbus Relay</h3>
          </div>
          <button @click="handleSave('relay')" :disabled="saving"
            class="flex items-center gap-1.5 bg-amber-600 hover:bg-amber-500 text-white font-semibold py-1.5 px-3 rounded-lg text-xs transition disabled:opacity-50">
            <Loader2 v-if="saving" class="w-3.5 h-3.5 animate-spin" />
            <Save v-else class="w-3.5 h-3.5" />
            Simpan
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Modbus Host</label>
            <input v-model="relayForm.MODBUS_HOST" type="text"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Modbus Port</label>
            <input v-model="relayForm.MODBUS_PORT" type="number"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
