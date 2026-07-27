<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Copy, Check, ChevronsLeft, Square, Camera, Loader2, AlertTriangle,
  X, ShieldCheck, ShieldX, Settings, Save, Eye, EyeOff,
} from '@lucide/vue'
import api from '@/services/api'

const props = defineProps({
  gate: {
    type: Object,
    required: true,
  },
  direction: {
    type: String,
    required: true, // "masuk" atau "keluar"
  },
})

const emit = defineEmits(['capture', 'refresh'])

const copied = ref(false)
const capturing = ref(false)
const relayLoading = ref(false)
const streamError = ref(false)
const streamSlowMode = ref(false)
const captureError = ref('')
const captureSuccess = ref('')
const relayError = ref('')
const cacheBuster = ref(0)
let streamTimer = null

// Settings modal
const showSettings = ref(false)
const settingsLoading = ref(false)
const settingsSaving = ref(false)
const settingsError = ref('')
const settingsSuccess = ref('')
const showPassword = ref(false)
const camForm = ref({})

const streamUrl = computed(() => {
  const base = api.getStreamUrl(props.direction)
  return `${base}?t=${cacheBuster.value}`
})

const startStreamTimer = (intervalMs) => {
  if (streamTimer) clearInterval(streamTimer)
  streamTimer = setInterval(() => {
    cacheBuster.value++
    streamError.value = false
  }, intervalMs)
}

const handleCopy = () => {
  if (!props.gate.plate) return
  navigator.clipboard.writeText(props.gate.plate)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

const handleCapture = async () => {
  capturing.value = true
  captureError.value = ''
  captureSuccess.value = ''
  try {
    const result = await api.capturePlate(props.direction)
    if (props.direction === 'keluar' && result.validated === true) {
      captureSuccess.value = `Plat terverifikasi — gate dibuka`
    } else if (props.direction === 'keluar' && result.validated === false) {
      captureError.value = result.reason || 'Plat tidak valid untuk keluar — gate tetap tertutup'
    } else if (result.ignored) {
      captureError.value = result.reason || 'Plat tidak terbaca'
    } else {
      captureSuccess.value = 'Capture berhasil — gate dibuka'
    }
    emit('capture', props.direction)
    emit('refresh')
  } catch (err) {
    captureError.value = err.message || 'Gagal capture'
  } finally {
    capturing.value = false
  }
}

const handleOpenGate = async () => {
  relayLoading.value = true
  relayError.value = ''
  try {
    const channel = props.direction === 'masuk' ? 1 : 4
    await api.controlRelay(channel, true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    await api.controlRelay(channel, false)
    emit('refresh')
  } catch (err) {
    relayError.value = err.message || 'Gagal buka gate'
  } finally {
    relayLoading.value = false
  }
}

const handleCloseGate = async () => {
  relayLoading.value = true
  relayError.value = ''
  try {
    const channel = props.direction === 'masuk' ? 2 : 5
    await api.controlRelay(channel, true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    await api.controlRelay(channel, false)
    emit('refresh')
  } catch (err) {
    relayError.value = err.message || 'Gagal tutup gate'
  } finally {
    relayLoading.value = false
  }
}

// Settings
const openSettings = async () => {
  showSettings.value = true
  settingsLoading.value = true
  settingsError.value = ''
  settingsSuccess.value = ''
  try {
    const data = await api.getSettings()
    const section = props.direction === 'masuk' ? 'camera_in' : 'camera_out'
    camForm.value = { ...data[section] }
  } catch (err) {
    settingsError.value = err.message
  } finally {
    settingsLoading.value = false
  }
}

const closeSettings = () => {
  showSettings.value = false
  settingsError.value = ''
  settingsSuccess.value = ''
}

const saveSettings = async () => {
  settingsSaving.value = true
  settingsError.value = ''
  settingsSuccess.value = ''
  try {
    const result = await api.updateSettings(camForm.value)
    settingsSuccess.value = result.message || 'Berhasil disimpan'
    setTimeout(() => { settingsSuccess.value = '' }, 2000)
  } catch (err) {
    settingsError.value = err.message
  } finally {
    settingsSaving.value = false
  }
}

const onStreamError = () => {
  streamError.value = true
  if (!streamSlowMode.value) {
    streamSlowMode.value = true
    startStreamTimer(5000)
  }
}

const onStreamLoad = () => {
  streamError.value = false
  if (streamSlowMode.value) {
    streamSlowMode.value = false
    startStreamTimer(1000)
  }
}

onMounted(() => { startStreamTimer(1000) })
onUnmounted(() => { if (streamTimer) clearInterval(streamTimer) })
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 hover:border-zinc-700/80 transition-all">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xl font-bold text-white tracking-tight">{{ gate.title }}</h3>
      <button
        @click="openSettings"
        class="p-2 rounded-lg text-zinc-500 hover:text-white hover:bg-zinc-800 transition"
        :title="`Settings Kamera ${direction}`"
      >
        <Settings class="w-4 h-4" />
      </button>
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-5">
      <!-- Camera Preview -->
      <div class="lg:col-span-7 relative rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800 shadow-inner group aspect-[4/3] flex items-center justify-center">
        <img
          v-if="!streamError"
          :src="streamUrl"
          alt="CCTV Feed"
          class="w-full h-full object-cover"
          @error="onStreamError"
          @load="onStreamLoad"
        />
        <div v-else class="w-full h-full bg-gradient-to-br from-zinc-900 via-zinc-950 to-black flex flex-col items-center justify-center p-6 text-center">
          <Camera class="w-12 h-12 text-zinc-700 mb-2" />
          <p class="text-xs font-medium text-zinc-500">Kamera Tidak Terhubung</p>
          <p class="text-[10px] text-zinc-600 mt-2">Mencoba lagi otomatis...</p>
        </div>

        <div class="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-[11px] font-mono text-zinc-200 border border-white/10 z-10">
          {{ gate.timestamp || '--' }}
        </div>
        <div class="absolute bottom-3 left-3 bg-black/85 backdrop-blur-md px-3 py-1 rounded text-xs font-bold text-white border border-white/10 z-10">
          {{ gate.lane }}
        </div>
        <div class="absolute bottom-3 right-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-xs font-semibold text-emerald-400 flex items-center gap-1.5 border border-white/10 z-10">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          ANPR
        </div>
      </div>

      <!-- Details -->
      <div class="lg:col-span-5 flex flex-col justify-start space-y-3">
        <div>
          <p class="text-xs font-medium text-zinc-400 mb-1">Plat Terbaca</p>
          <div class="flex items-center justify-between bg-zinc-950 border border-zinc-700/80 px-3.5 py-2 rounded-lg shadow-inner">
            <span class="text-lg font-extrabold text-white tracking-widest font-mono">
              {{ gate.plate || '---' }}
            </span>
            <button @click="handleCopy" class="p-1 text-zinc-400 hover:text-white rounded hover:bg-zinc-800 transition" title="Salin">
              <Check v-if="copied" class="w-4 h-4 text-emerald-400" />
              <Copy v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="space-y-2 text-xs">
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/80">
            <span class="text-zinc-400 font-medium">Confidence</span>
            <span class="font-mono text-zinc-200 font-semibold">
              {{ gate.confidence ? `${gate.confidence.toFixed(1)}%` : '---' }}
            </span>
          </div>
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/80">
            <span class="text-zinc-400 font-medium">Arah</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
              {{ direction }}
            </span>
          </div>
          <div class="flex items-center justify-between py-1">
            <span class="text-zinc-400 font-medium">Barrier</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
              {{ gate.barrierStatus || 'TERTUTUP' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div v-if="captureError || captureSuccess || relayError" class="mb-3 space-y-2">
      <div v-if="captureSuccess" class="flex items-start gap-2 bg-emerald-950/80 border border-emerald-800/60 rounded-lg px-3 py-2">
        <ShieldCheck class="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
        <p class="text-xs text-emerald-300 flex-1">{{ captureSuccess }}</p>
        <button @click="captureSuccess = ''" class="p-0.5 text-emerald-400 hover:text-emerald-300"><X class="w-3.5 h-3.5" /></button>
      </div>
      <div v-if="captureError" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
        <ShieldX v-if="direction === 'keluar'" class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
        <AlertTriangle v-else class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
        <p class="text-xs text-red-300 flex-1">{{ captureError }}</p>
        <button @click="captureError = ''" class="p-0.5 text-red-400 hover:text-red-300"><X class="w-3.5 h-3.5" /></button>
      </div>
      <div v-if="relayError" class="flex items-start gap-2 bg-amber-950/80 border border-amber-800/60 rounded-lg px-3 py-2">
        <AlertTriangle class="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
        <p class="text-xs text-amber-300 flex-1">{{ relayError }}</p>
        <button @click="relayError = ''" class="p-0.5 text-amber-400 hover:text-amber-300"><X class="w-3.5 h-3.5" /></button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-3 border-t border-zinc-800">
      <button @click="handleOpenGate" :disabled="relayLoading"
        class="flex items-center justify-center gap-2 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50">
        <Loader2 v-if="relayLoading" class="w-4 h-4 animate-spin" />
        <ChevronsLeft v-else class="w-4 h-4 text-emerald-400" />
        <span>Buka Manual</span>
      </button>
      <button @click="handleCloseGate" :disabled="relayLoading"
        class="flex items-center justify-center gap-2 bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50">
        <Square class="w-4 h-4 text-rose-400" />
        <span>Tutup Manual</span>
      </button>
      <button @click="handleCapture" :disabled="capturing"
        class="flex items-center justify-center gap-2 bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50">
        <Loader2 v-if="capturing" class="w-4 h-4 animate-spin" />
        <Camera v-else class="w-4 h-4 text-blue-400" />
        <span>Capture</span>
      </button>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeSettings">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <div class="flex items-center gap-2">
            <Camera class="w-4 h-4 text-zinc-400" />
            <h3 class="text-lg font-bold text-white">Settings Kamera {{ direction === 'masuk' ? 'Masuk' : 'Keluar' }}</h3>
          </div>
          <button @click="closeSettings" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="settingsLoading" class="flex items-center justify-center py-12">
          <Loader2 class="w-6 h-6 text-zinc-400 animate-spin" />
        </div>

        <form v-else @submit.prevent="saveSettings" class="p-6 space-y-4">
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">IP Camera</label>
            <input v-model="camForm[`CAMERA_${direction === 'masuk' ? 'IN' : 'OUT'}_HOST`]" type="text"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Username</label>
            <input v-model="camForm[`CAMERA_${direction === 'masuk' ? 'IN' : 'OUT'}_USER`]" type="text"
              class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1">Password</label>
            <div class="relative">
              <input v-model="camForm[`CAMERA_${direction === 'masuk' ? 'IN' : 'OUT'}_PASSWORD`]"
                :type="showPassword ? 'text' : 'password'"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 pr-10 text-sm text-white focus:outline-none focus:border-blue-500" />
              <button type="button" @click="showPassword = !showPassword" class="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300">
                <Eye v-if="!showPassword" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] text-zinc-500 font-medium mb-1">Channel</label>
              <input v-model="camForm[`CAMERA_${direction === 'masuk' ? 'IN' : 'OUT'}_CHANNEL`]" type="number"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-[11px] text-zinc-500 font-medium mb-1">HTTPS</label>
              <select v-model="camForm[`CAMERA_${direction === 'masuk' ? 'IN' : 'OUT'}_USE_HTTPS`]"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                <option value="false">Tidak</option>
                <option value="true">Ya</option>
              </select>
            </div>
          </div>

          <div v-if="settingsSuccess" class="flex items-start gap-2 bg-emerald-950/80 border border-emerald-800/60 rounded-lg px-3 py-2">
            <Check class="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
            <p class="text-xs text-emerald-300">{{ settingsSuccess }}</p>
          </div>
          <div v-if="settingsError" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
            <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            <p class="text-xs text-red-300">{{ settingsError }}</p>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="closeSettings" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-medium rounded-lg transition">Batal</button>
            <button type="submit" :disabled="settingsSaving"
              class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition disabled:opacity-50">
              <Loader2 v-if="settingsSaving" class="w-4 h-4 animate-spin" />
              <Save v-else class="w-4 h-4" />
              Simpan
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
