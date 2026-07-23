<script setup>
import { ref, computed } from 'vue'
import { Camera, Wifi, WifiOff } from '@lucide/vue'

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  direction: {
    type: String,
    required: true, // "masuk" atau "keluar"
  },
})

const streamUrl = computed(() => {
  // Server tidak punya akses kamera langsung, jadi tidak ada stream
  return null
})

const cameraActive = computed(() => {
  return props.direction === 'masuk'
    ? props.node.camera_in_active
    : props.node.camera_out_active
})

const relayActive = computed(() => {
  return props.direction === 'masuk'
    ? props.node.relay_in_active
    : props.node.relay_out_active
})
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 hover:border-zinc-700/80 transition-all">
    <!-- Header -->
    <div class="mb-4">
      <h3 class="text-xl font-bold text-white tracking-tight">{{ node.name }} — {{ direction === 'masuk' ? 'Masuk' : 'Keluar' }}</h3>
      <p class="text-[10px] text-zinc-500 font-mono mt-0.5">{{ node.id }}</p>
    </div>

    <!-- Camera Preview Placeholder -->
    <div class="relative rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800 shadow-inner aspect-[4/3] flex items-center justify-center mb-4">
      <div class="flex flex-col items-center justify-center p-6 text-center">
        <Camera class="w-12 h-12 mb-2" :class="cameraActive ? 'text-emerald-600' : 'text-zinc-700'" />
        <p class="text-xs font-medium" :class="cameraActive ? 'text-emerald-500' : 'text-zinc-500'">
          {{ cameraActive ? 'Kamera Aktif' : 'Kamera Nonaktif' }}
        </p>
        <p class="text-[10px] text-zinc-600 mt-1">Live view hanya di pos satpam</p>
      </div>

      <!-- Status badges -->
      <div class="absolute top-3 right-3 flex items-center gap-1.5">
        <div
          :class="[
            'flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border',
            cameraActive
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-red-500/10 text-red-400 border-red-500/20',
          ]"
        >
          <span :class="['w-1.5 h-1.5 rounded-full', cameraActive ? 'bg-emerald-400' : 'bg-red-400']"></span>
          ANPR
        </div>
      </div>
    </div>

    <!-- Status Info -->
    <div class="space-y-2 text-xs">
      <div class="flex items-center justify-between py-1 border-b border-zinc-800/80">
        <span class="text-zinc-400 font-medium">Node</span>
        <span
          :class="[
            'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
            node.status === 'online'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-red-500/10 text-red-400 border border-red-500/20',
          ]"
        >
          {{ node.status }}
        </span>
      </div>

      <div class="flex items-center justify-between py-1 border-b border-zinc-800/80">
        <span class="text-zinc-400 font-medium">Kamera</span>
        <span
          :class="[
            'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
            cameraActive
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-zinc-500/10 text-zinc-400 border border-zinc-500/20',
          ]"
        >
          {{ cameraActive ? 'AKTIF' : 'NONAKTIF' }}
        </span>
      </div>

      <div class="flex items-center justify-between py-1">
        <span class="text-zinc-400 font-medium">Barrier</span>
        <span
          :class="[
            'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
            relayActive
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-zinc-500/10 text-zinc-400 border border-zinc-500/20',
          ]"
        >
          {{ relayActive ? 'TERBUKA' : 'TERTUTUP' }}
        </span>
      </div>
    </div>
  </div>
</template>
