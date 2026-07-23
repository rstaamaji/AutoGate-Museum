<script setup>
import { ref, computed } from 'vue'
import { Copy, Check, ChevronsLeft, Square, Pause, Camera, Loader2 } from '@lucide/vue'
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

const streamUrl = computed(() => api.getStreamUrl(props.direction))

const handleCopy = () => {
  if (!props.gate.plate) return
  navigator.clipboard.writeText(props.gate.plate)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

const handleCapture = async () => {
  capturing.value = true
  try {
    await api.capturePlate(props.direction)
    emit('capture', props.direction)
    emit('refresh')
  } catch (err) {
    console.error('Capture error:', err)
    alert(`Gagal capture: ${err.message}`)
  } finally {
    capturing.value = false
  }
}

const handleOpenGate = async () => {
  relayLoading.value = true
  try {
    const channel = props.direction === 'masuk' ? 1 : 2
    await api.controlRelay(channel, true)
    emit('refresh')
  } catch (err) {
    console.error('Relay error:', err)
    alert(`Gagal buka gate: ${err.message}`)
  } finally {
    relayLoading.value = false
  }
}

const handleCloseGate = async () => {
  relayLoading.value = true
  try {
    const channel = props.direction === 'masuk' ? 1 : 2
    await api.controlRelay(channel, false)
    emit('refresh')
  } catch (err) {
    console.error('Relay error:', err)
    alert(`Gagal tutup gate: ${err.message}`)
  } finally {
    relayLoading.value = false
  }
}

const onStreamError = () => {
  streamError.value = true
}
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 hover:border-zinc-700/80 transition-all">
    <!-- Header -->
    <div class="mb-4">
      <h3 class="text-xl font-bold text-white tracking-tight">{{ gate.title }}</h3>
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
        />
        <div v-else class="w-full h-full bg-gradient-to-br from-zinc-900 via-zinc-950 to-black flex flex-col items-center justify-center p-6 text-center">
          <Camera class="w-12 h-12 text-zinc-700 mb-2" />
          <p class="text-xs font-medium text-zinc-500">Kamera Tidak Terhubung</p>
        </div>

        <!-- Timestamp overlay -->
        <div class="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-[11px] font-mono text-zinc-200 border border-white/10 z-10">
          {{ gate.timestamp || '--' }}
        </div>

        <!-- Lane badge -->
        <div class="absolute bottom-3 left-3 bg-black/85 backdrop-blur-md px-3 py-1 rounded text-xs font-bold text-white border border-white/10 z-10">
          {{ gate.lane }}
        </div>

        <!-- ANPR indicator -->
        <div class="absolute bottom-3 right-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-xs font-semibold text-emerald-400 flex items-center gap-1.5 border border-white/10 z-10">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          ANPR
        </div>
      </div>

      <!-- Details -->
      <div class="lg:col-span-5 flex flex-col justify-start space-y-3">
        <!-- Plat -->
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

        <!-- Detail items -->
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

    <!-- Action Buttons -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-3 border-t border-zinc-800">
      <button
        @click="handleOpenGate"
        :disabled="relayLoading"
        class="flex items-center justify-center gap-2 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50"
      >
        <Loader2 v-if="relayLoading" class="w-4 h-4 animate-spin" />
        <ChevronsLeft v-else class="w-4 h-4 text-emerald-400" />
        <span>Buka Manual</span>
      </button>

      <button
        @click="handleCloseGate"
        :disabled="relayLoading"
        class="flex items-center justify-center gap-2 bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50"
      >
        <Square class="w-4 h-4 text-rose-400" />
        <span>Tutup Manual</span>
      </button>

      <button
        @click="handleCapture"
        :disabled="capturing"
        class="flex items-center justify-center gap-2 bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98] disabled:opacity-50"
      >
        <Loader2 v-if="capturing" class="w-4 h-4 animate-spin" />
        <Camera v-else class="w-4 h-4 text-blue-400" />
        <span>Capture</span>
      </button>
    </div>
  </div>
</template>
