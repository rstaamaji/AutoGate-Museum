<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { 
  Copy, 
  Check, 
  ChevronsLeft, 
  Square, 
  Camera,
  RefreshCw,
  AlertCircle
} from 'lucide-vue-next'
import { controlRelay, capturePlate, getStreamUrl } from '@/services/api'

const props = defineProps({
  gate: {
    type: Object,
    required: true,
    default: () => ({
      id: 1,
      direction: 'masuk',
      channel: 1,
      title: 'Gate 1 Masuk',
      lane: 'Lane 1',
      timestamp: '24/05/2025 10:24:36',
      image: '',
      plate: '---',
      rfidUid: '-',
      validationStatus: 'READY',
      barrierStatus: 'TERTUTUP'
    })
  }
})

const emit = defineEmits(['captured'])

// Local reactive state
const copied = ref(false)
const liveImageUrl = ref('')
const liveTimestamp = ref('')
const isCapturing = ref(false)
const captureMessage = ref(null)
const isStreamError = ref(false)
const capturedSceneUrl = ref('')

// Cooldown state for relay buttons (3 seconds)
const cooldownSeconds = ref(0)
let cooldownTimer = null

const isCoolingDown = computed(() => cooldownSeconds.value > 0)

// Stream polling interval (3s)
let streamInterval = null

const updateStream = () => {
  if (!props.gate || !props.gate.direction) return
  // Pause stream requests while capturing or showing captured scene preview to prevent collision
  if (isCapturing.value || capturedSceneUrl.value) return

  liveImageUrl.value = getStreamUrl(props.gate.direction)
  const d = new Date()
  liveTimestamp.value = d.toLocaleDateString('id-ID') + ' ' + d.toLocaleTimeString('id-ID')
}

const handleImageError = () => {
  isStreamError.value = true
}

const handleImageLoad = () => {
  // Auto-recover stream error state as soon as an image loads cleanly
  isStreamError.value = false
}

onMounted(() => {
  updateStream()
  // Refresh camera stream every 3 seconds (3000ms) to prevent Hikvision ISAPI overload
  streamInterval = setInterval(updateStream, 3000)
})

onUnmounted(() => {
  if (streamInterval) clearInterval(streamInterval)
  if (cooldownTimer) clearInterval(cooldownTimer)
})

const handleCopy = () => {
  if (!props.gate.plate || props.gate.plate === '---') return
  navigator.clipboard.writeText(props.gate.plate)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

// Start 3-second cooldown timer for relay buttons
const startCooldown = () => {
  cooldownSeconds.value = 3
  if (cooldownTimer) clearInterval(cooldownTimer)

  cooldownTimer = setInterval(() => {
    if (cooldownSeconds.value > 1) {
      cooldownSeconds.value -= 1
    } else {
      cooldownSeconds.value = 0
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

// Trigger Modbus Relay control (Buka / Tutup Manual)
const handleRelayControl = async (openStatus) => {
  if (isCoolingDown.value) return

  // Start cooldown immediately
  startCooldown()

  try {
    const channel = props.gate.channel || (props.gate.direction === 'masuk' ? 1 : 2)
    await controlRelay(channel, openStatus)
    
    // Update local barrier status label
    props.gate.barrierStatus = openStatus ? 'TERBUKA' : 'TERTUTUP'
  } catch (err) {
    console.error('Relay error:', err)
    captureMessage.value = { type: 'error', text: err.message || 'Gagal mengontrol relay' }
    setTimeout(() => { captureMessage.value = null }, 4000)
  }
}

// Trigger ANPR capture via POST /api/plates/{direction}
const handleCapture = async () => {
  if (isCapturing.value) return
  isCapturing.value = true
  captureMessage.value = null

  try {
    const result = await capturePlate(props.gate.direction)
    
    if (result.ignored) {
      captureMessage.value = { 
        type: 'warning', 
        text: result.reason || 'Plat tidak terbaca (unknown), diabaikan.' 
      }
    } else if (result.vehicle) {
      props.gate.plate = result.vehicle.plate_number
      props.gate.validationStatus = 'GRANTED'
      props.gate.barrierStatus = 'TERBUKA'

      if (result.vehicle.scene_image_url) {
        capturedSceneUrl.value = result.vehicle.scene_image_url
        // Show captured scene preview for 4 seconds then return to live stream
        setTimeout(() => {
          capturedSceneUrl.value = ''
        }, 4000)
      }

      captureMessage.value = { 
        type: 'success', 
        text: `Plat ${result.vehicle.plate_number} berhasil dibaca & disimpan!` 
      }
    }

    emit('captured', result)
  } catch (err) {
    console.error('Capture error:', err)
    captureMessage.value = { 
      type: 'error', 
      text: err.message || 'Gagal terhubung ke kamera' 
    }
  } finally {
    isCapturing.value = false
    setTimeout(() => { captureMessage.value = null }, 5000)
  }
}
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 hover:border-zinc-700/80 transition-all relative">
    <!-- 1. Header Card -->
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-xl font-bold text-white tracking-tight">{{ gate.title }}</h3>
      <span 
        class="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border"
        :class="gate.direction === 'masuk' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'"
      >
        {{ gate.direction }}
      </span>
    </div>

    <!-- Toast Notification Message -->
    <div 
      v-if="captureMessage" 
      class="mb-3 px-3 py-2 rounded-lg text-xs flex items-center gap-2 border transition-all"
      :class="{
        'bg-rose-500/10 text-rose-300 border-rose-500/20': captureMessage.type === 'error',
        'bg-amber-500/10 text-amber-300 border-amber-500/20': captureMessage.type === 'warning',
        'bg-emerald-500/10 text-emerald-300 border-emerald-500/20': captureMessage.type === 'success'
      }"
    >
      <AlertCircle class="w-4 h-4 shrink-0" />
      <span>{{ captureMessage.text }}</span>
    </div>

    <!-- 2. Content Grid: CCTV Preview (Left) + Details (Right) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-5">
      <!-- Left Column: Camera Live Preview Box (7 Cols) -->
      <div class="lg:col-span-7 relative rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800 shadow-inner group aspect-[4/3] flex items-center justify-center">
        
        <!-- Opsi A: Tampilkan Foto Scene Hasil Capture Terbaru (selama 4 detik setelah capture) -->
        <img 
          v-if="capturedSceneUrl" 
          :src="capturedSceneUrl" 
          alt="Captured Scene" 
          class="w-full h-full object-cover z-0"
        />

        <!-- Opsi B: Tampilkan Live Stream Gambar Kamera (di-refresh tiap 3s) -->
        <img 
          v-else-if="liveImageUrl && !isStreamError" 
          :src="liveImageUrl" 
          alt="Live CCTV Feed" 
          class="w-full h-full object-cover z-0"
          @error="handleImageError"
          @load="handleImageLoad"
        />

        <!-- Placeholder jika stream error / kamera offline -->
        <div v-else class="w-full h-full bg-gradient-to-br from-zinc-900 via-zinc-950 to-black flex flex-col items-center justify-center p-6 text-center relative z-0">
          <div class="absolute inset-0 bg-[radial-gradient(#27272a_1px,transparent_1px)] [background-size:16px_16px] opacity-40"></div>
          <Camera class="w-12 h-12 text-zinc-700 mb-2 relative z-10" />
          <p class="text-xs font-medium text-zinc-500 relative z-10">
            {{ isStreamError ? 'Kamera Offline / Gagal Terhubung' : 'Live CCTV Feed' }}
          </p>
        </div>

        <!-- Overlay: Top Left Timestamp -->
        <div class="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-[11px] font-mono text-zinc-200 border border-white/10 z-10">
          {{ liveTimestamp || gate.timestamp }}
        </div>

        <!-- Overlay: Bottom Left Lane Badge -->
        <div class="absolute bottom-3 left-3 bg-black/85 backdrop-blur-md px-3 py-1 rounded text-xs font-bold text-white border border-white/10 z-10">
          {{ gate.lane }}
        </div>

        <!-- Overlay: Bottom Right ANPR Indicator -->
        <div class="absolute bottom-3 right-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-xs font-semibold text-emerald-400 flex items-center gap-1.5 border border-white/10 z-10">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          ANPR
        </div>
      </div>

      <!-- Right Column: Plate & Detection Details (5 Cols) -->
      <div class="lg:col-span-5 flex flex-col justify-start space-y-3">
        <!-- Plat Terbaca Section -->
        <div>
          <p class="text-xs font-medium text-zinc-400 mb-1">Plat Terbaca</p>
          <div class="flex items-center justify-between bg-zinc-950 border border-zinc-700/80 px-3.5 py-2 rounded-lg shadow-inner">
            <span class="text-lg font-extrabold text-white tracking-widest font-mono">
              {{ gate.plate || '---' }}
            </span>
            <button 
              @click="handleCopy" 
              class="p-1 text-zinc-400 hover:text-white rounded hover:bg-zinc-800 transition"
              title="Salin Plat Nomor"
            >
              <Check v-if="copied" class="w-4 h-4 text-emerald-400" />
              <Copy v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Details List -->
        <div class="space-y-2 text-xs">
          <!-- RFID UID -->
          <div class="py-1 border-b border-zinc-800/80">
            <p class="text-zinc-400 font-medium text-[11px] mb-0.5">RFID UID</p>
            <p class="font-mono text-zinc-200 font-semibold tracking-wider text-[11px] truncate">
              {{ gate.rfidUid }}
            </p>
          </div>

          <!-- Validasi -->
          <div class="flex items-center justify-between py-1 border-b border-zinc-800/80">
            <span class="text-zinc-400 font-medium">Validasi</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
              {{ gate.validationStatus }}
            </span>
          </div>

          <!-- Barrier Gate -->
          <div class="flex items-center justify-between py-1">
            <span class="text-zinc-400 font-medium">Barrier</span>
            <span 
              class="px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider"
              :class="gate.barrierStatus === 'TERBUKA' 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'"
            >
              {{ gate.barrierStatus }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Bottom Action Controls Bar (Buka Manual, Tutup Manual, Capture) -->
    <div class="grid grid-cols-3 gap-2.5 pt-3 border-t border-zinc-800">
      <!-- Buka Manual (Dark Emerald) with 3s Cooldown -->
      <button 
        @click="handleRelayControl(true)"
        :disabled="isCoolingDown"
        class="flex items-center justify-center gap-2 bg-emerald-950 hover:bg-emerald-900 disabled:opacity-50 disabled:cursor-not-allowed text-emerald-300 border border-emerald-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]"
      >
        <ChevronsLeft class="w-4 h-4 text-emerald-400" />
        <span>Buka Manual</span>
        <span v-if="isCoolingDown" class="text-[10px] bg-emerald-900/80 text-emerald-300 px-1.5 py-0.2 rounded">
          {{ cooldownSeconds }}s
        </span>
      </button>

      <!-- Tutup Manual (Dark Rose/Red) with 3s Cooldown -->
      <button 
        @click="handleRelayControl(false)"
        :disabled="isCoolingDown"
        class="flex items-center justify-center gap-2 bg-rose-950 hover:bg-rose-900 disabled:opacity-50 disabled:cursor-not-allowed text-rose-300 border border-rose-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]"
      >
        <Square class="w-4 h-4 text-rose-400" />
        <span>Tutup Manual</span>
        <span v-if="isCoolingDown" class="text-[10px] bg-rose-900/80 text-rose-300 px-1.5 py-0.2 rounded">
          {{ cooldownSeconds }}s
        </span>
      </button>

      <!-- Capture Button (Trigger POST /api/plates/{direction}) -->
      <button 
        @click="handleCapture"
        :disabled="isCapturing"
        class="flex items-center justify-center gap-2 bg-zinc-950 hover:bg-zinc-800 disabled:opacity-50 text-zinc-300 border border-zinc-700/80 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]"
      >
        <RefreshCw v-if="isCapturing" class="w-4 h-4 text-zinc-400 animate-spin" />
        <Camera v-else class="w-4 h-4 text-zinc-400" />
        <span>{{ isCapturing ? 'Capturing...' : 'Capture' }}</span>
      </button>
    </div>
  </div>
</template>
