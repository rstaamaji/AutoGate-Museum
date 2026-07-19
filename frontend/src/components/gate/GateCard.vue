<script setup>
import { ref } from 'vue'
import { 
  Copy, 
  Check, 
  ChevronsLeft, 
  Square, 
  Pause, 
  Camera 
} from '@lucide/vue'

const props = defineProps({
  gate: {
    type: Object,
    required: true,
    default: () => ({
      id: 1,
      title: 'Gate 1 Masuk',
      lane: 'Lane 1',
      timestamp: '24/05/2025 10:24:36',
      image: '',
      plate: 'B 1234 ABC',
      rfidUid: 'E280 1160 1234 5678 90AB',
      validationStatus: 'GRANTED',
      barrierStatus: 'TERBUKA'
    })
  }
})

const copied = ref(false)

const handleCopy = () => {
  if (!props.gate.plate) return
  navigator.clipboard.writeText(props.gate.plate)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 hover:border-zinc-700/80 transition-all">
    <!-- 1. Header Card -->
    <div class="mb-4">
      <h3 class="text-xl font-bold text-white tracking-tight">{{ gate.title }}</h3>
    </div>

    <!-- 2. Content Grid: CCTV Preview (Left) + Details (Right) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-5">
      <!-- Left Column: Camera Preview Box (7 Cols) -->
      <div class="lg:col-span-7 relative rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800 shadow-inner group aspect-[4/3] flex items-center justify-center">
        <!-- Mock CCTV Image or Placeholder -->
        <img 
          v-if="gate.image" 
          :src="gate.image" 
          alt="CCTV Feed" 
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full bg-gradient-to-br from-zinc-900 via-zinc-950 to-black flex flex-col items-center justify-center p-6 text-center relative">
          <div class="absolute inset-0 bg-[radial-gradient(#27272a_1px,transparent_1px)] [background-size:16px_16px] opacity-40"></div>
          <Camera class="w-12 h-12 text-zinc-700 mb-2 relative z-10" />
          <p class="text-xs font-medium text-zinc-500 relative z-10">Live CCTV Feed</p>
        </div>

        <!-- Overlay: Top Left Timestamp -->
        <div class="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-[11px] font-mono text-zinc-200 border border-white/10 z-10">
          {{ gate.timestamp }}
        </div>

        <!-- Overlay: Bottom Left Lane Badge -->
        <div class="absolute bottom-3 left-3 bg-black/85 backdrop-blur-md px-3 py-1 rounded text-xs font-bold text-white border border-white/10 z-10">
          {{ gate.lane }}
        </div>

        <!-- Overlay: Bottom Right ANPR Indicator -->
        <div class="absolute bottom-3 right-3 bg-black/85 backdrop-blur-md px-2.5 py-1 rounded text-xs font-semibold text-emerald-400 flex items-center gap-1.5 border border-white/10 z-10">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          ANPR
        </div>
      </div>

      <!-- Right Column: Plate & Detection Details (5 Cols) - Aligned to Top -->
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

        <!-- Details List (Tightly Arranged at Top) -->
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
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
              {{ gate.barrierStatus }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Bottom Action Controls Bar (Darker Buttons & Slightly Sharper / Rounded-md) -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-3 border-t border-zinc-800">
      <!-- Buka Manual (Dark Emerald) -->
      <button class="flex items-center justify-center gap-2 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]">
        <ChevronsLeft class="w-4 h-4 text-emerald-400" />
        <span>Buka Manual</span>
      </button>

      <!-- Tutup Manual (Dark Rose/Red) -->
      <button class="flex items-center justify-center gap-2 bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800/70 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]">
        <Square class="w-4 h-4 text-rose-400" />
        <span>Tutup Manual</span>
      </button>

      <!-- Freeze -->
      <button class="flex items-center justify-center gap-2 bg-zinc-950 hover:bg-zinc-800 text-zinc-300 border border-zinc-700/80 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]">
        <Pause class="w-4 h-4 text-zinc-400" />
        <span>Freeze</span>
      </button>

      <!-- Snapshot -->
      <button class="flex items-center justify-center gap-2 bg-zinc-950 hover:bg-zinc-800 text-zinc-300 border border-zinc-700/80 font-semibold py-2 px-3 rounded-md text-xs transition active:scale-[0.98]">
        <Camera class="w-4 h-4 text-zinc-400" />
        <span>Snapshot</span>
      </button>
    </div>
  </div>
</template>
