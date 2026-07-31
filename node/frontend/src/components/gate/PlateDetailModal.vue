<script setup>
import { onMounted, onUnmounted } from 'vue'
import { X, Car, ExternalLink, Nfc } from '@lucide/vue'

const props = defineProps({
  plate: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close'])

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

const handleClose = () => {
  emit('close')
}

const onKeydown = (e) => {
  if (e.key === 'Escape') handleClose()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
    @click.self="handleClose"
  >
    <div
      class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
        <div class="flex items-center gap-3">
          <Car class="w-5 h-5 text-zinc-400" />
          <h3 class="text-lg font-bold text-white tracking-tight">Detail Kendaraan</h3>
        </div>
        <button
          @click="handleClose"
          class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
          title="Tutup"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-6">
        <!-- Info Ringkas -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Plat</p>
            <p class="text-sm font-bold text-white font-mono mt-0.5">{{ plate.plate_number }}</p>
          </div>
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Arah</p>
            <span
              :class="[
                'inline-block mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                plate.direction === 'masuk'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
              ]"
            >
              {{ plate.direction }}
            </span>
          </div>
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Confidence</p>
            <p class="text-sm font-bold text-white font-mono mt-0.5">
              {{ plate.confidence ? `${plate.confidence.toFixed(1)}%` : '---' }}
            </p>
          </div>
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Waktu</p>
            <p class="text-xs font-mono text-zinc-300 mt-0.5">{{ formatTime(plate.captured_at || plate.created_at) }}</p>
          </div>
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Event ID</p>
            <p class="text-[10px] font-mono text-zinc-400 mt-0.5 break-all">{{ plate.event_id || '---' }}</p>
          </div>
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">RFID</p>
            <div class="flex items-center gap-1 mt-0.5">
              <Nfc v-if="plate.rfid_uid" class="w-3 h-3 text-violet-400" />
              <p class="text-sm font-bold font-mono" :class="plate.rfid_uid ? 'text-violet-300' : 'text-zinc-600'">
                {{ plate.rfid_uid || '---' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Gambar Plat -->
        <div v-if="plate.plate_image_url">
          <p class="text-xs font-medium text-zinc-400 mb-2">Gambar Plat</p>
          <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-950">
            <img
              :src="plate.plate_image_url"
              alt="Plat Nomor"
              class="w-full h-auto object-contain max-h-48"
            />
          </div>
        </div>

        <!-- Gambar Full Scene -->
        <div v-if="plate.scene_image_url">
          <p class="text-xs font-medium text-zinc-400 mb-2">Gambar Kendaraan</p>
          <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-950">
            <img
              :src="plate.scene_image_url"
              alt="Kendaraan"
              class="w-full h-auto object-contain max-h-80"
            />
          </div>
        </div>

        <div v-if="!plate.plate_image_url && !plate.scene_image_url" class="text-center py-8 text-zinc-500">
          <ExternalLink class="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p class="text-sm">Tidak ada gambar tersedia</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-3 border-t border-zinc-800 flex justify-end">
        <button
          @click="handleClose"
          class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-medium rounded-lg transition"
        >
          Tutup
        </button>
      </div>
    </div>
  </div>
</template>
