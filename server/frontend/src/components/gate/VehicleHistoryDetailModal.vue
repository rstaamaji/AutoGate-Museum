<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { X, Car, ArrowDownRight, ArrowUpRight, Loader2, Image as ImageIcon } from '@lucide/vue'
import api from '@/services/api'

const props = defineProps({
  history: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close'])

const loading = ref(false)
const entryEvent = ref(null)
const exitEvent = ref(null)

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

const handleClose = () => {
  emit('close')
}

const fetchEventsForHistory = async () => {
  if (!props.history || !props.history.plate_number) return
  loading.value = true
  entryEvent.value = null
  exitEvent.value = null
  try {
    const data = await api.getEvents({ plate_number: props.history.plate_number, limit: 100 })
    const items = data.items || []

    if (props.history.entry_event_id) {
      entryEvent.value = items.find(e => e.event_id === props.history.entry_event_id)
    }
    if (!entryEvent.value && props.history.entry_at) {
      entryEvent.value = items.find(e => e.direction === 'masuk')
    }

    if (props.history.exit_event_id) {
      exitEvent.value = items.find(e => e.event_id === props.history.exit_event_id)
    }
    if (!exitEvent.value && props.history.exit_at) {
      exitEvent.value = items.find(e => e.direction === 'keluar')
    }
  } catch (err) {
    console.error('Gagal mengambil event detail:', err)
  } finally {
    loading.value = false
  }
}

const onKeydown = (e) => {
  if (e.key === 'Escape') handleClose()
}

onMounted(() => {
  fetchEventsForHistory()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})

watch(() => props.history, () => {
  fetchEventsForHistory()
})
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
    @click.self="handleClose"
  >
    <div
      class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-3xl max-h-[90vh] overflow-y-auto"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
        <div class="flex items-center gap-3">
          <Car class="w-5 h-5 text-zinc-400" />
          <h3 class="text-lg font-bold text-white tracking-tight">Detail Riwayat Kendaraan</h3>
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
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Plat Nomor</p>
            <p class="text-base font-extrabold text-white font-mono mt-0.5">{{ history.plate_number }}</p>
          </div>

          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Status</p>
            <span
              :class="[
                'inline-block mt-1 px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                history.is_inside
                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
              ]"
            >
              {{ history.is_inside ? 'Di Dalam' : 'Sudah Keluar' }}
            </span>
          </div>

          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Pemilik</p>
            <p class="text-xs font-semibold text-zinc-200 mt-1 truncate">{{ history.owner_name || '---' }}</p>
          </div>

          <div class="bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2.5">
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">History ID</p>
            <p class="text-xs font-mono text-zinc-400 mt-1">#{{ history.id }}</p>
          </div>
        </div>

        <!-- Detail Node & Waktu -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-zinc-950/60 border border-zinc-800/80 rounded-xl p-4">
          <!-- Masuk -->
          <div class="space-y-1.5 border-b sm:border-b-0 sm:border-r border-zinc-800 pb-3 sm:pb-0 sm:pr-4">
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase tracking-wider">
              <ArrowDownRight class="w-4 h-4" />
              <span>Gate Masuk</span>
            </div>
            <p class="text-xs text-zinc-300 font-mono"><span class="text-zinc-500">Waktu:</span> {{ formatTime(history.entry_at) }}</p>
            <p class="text-xs text-zinc-300"><span class="text-zinc-500">Pos/Node:</span> {{ history.entry_node_name || '---' }}</p>
          </div>

          <!-- Keluar -->
          <div class="space-y-1.5 pt-1 sm:pt-0 sm:pl-2">
            <div class="flex items-center gap-1.5 text-xs font-bold text-blue-400 uppercase tracking-wider">
              <ArrowUpRight class="w-4 h-4" />
              <span>Gate Keluar</span>
            </div>
            <p class="text-xs text-zinc-300 font-mono"><span class="text-zinc-500">Waktu:</span> {{ formatTime(history.exit_at) }}</p>
            <p class="text-xs text-zinc-300"><span class="text-zinc-500">Pos/Node:</span> {{ history.exit_node_name || '---' }}</p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-10">
          <Loader2 class="w-8 h-8 text-zinc-500 animate-spin mb-2" />
          <p class="text-xs text-zinc-500">Memuat gambar kendaraan...</p>
        </div>

        <!-- Image Sections -->
        <div v-else class="space-y-6">
          <!-- Gambar Masuk -->
          <div class="bg-zinc-950 border border-zinc-800 rounded-xl p-4">
            <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowDownRight class="w-4 h-4" />
              Gambar Saat Masuk
            </h4>
            <div v-if="entryEvent && (entryEvent.plate_image_url || entryEvent.scene_image_url)" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-if="entryEvent.plate_image_url">
                <p class="text-[11px] font-medium text-zinc-400 mb-1.5">Plat Masuk</p>
                <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-900 flex items-center justify-center">
                  <img :src="entryEvent.plate_image_url" alt="Plat Masuk" class="w-full h-40 object-contain" />
                </div>
              </div>
              <div v-if="entryEvent.scene_image_url">
                <p class="text-[11px] font-medium text-zinc-400 mb-1.5">Kendaraan Masuk</p>
                <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-900 flex items-center justify-center">
                  <img :src="entryEvent.scene_image_url" alt="Kendaraan Masuk" class="w-full h-40 object-contain" />
                </div>
              </div>
            </div>
            <div v-else class="text-center py-6 text-zinc-600 text-xs">
              <ImageIcon class="w-8 h-8 mx-auto mb-1 opacity-40" />
              Tidak ada gambar saat masuk
            </div>
          </div>

          <!-- Gambar Keluar -->
          <div class="bg-zinc-950 border border-zinc-800 rounded-xl p-4">
            <h4 class="text-xs font-bold text-blue-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <ArrowUpRight class="w-4 h-4" />
              Gambar Saat Keluar
            </h4>
            <div v-if="exitEvent && (exitEvent.plate_image_url || exitEvent.scene_image_url)" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-if="exitEvent.plate_image_url">
                <p class="text-[11px] font-medium text-zinc-400 mb-1.5">Plat Keluar</p>
                <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-900 flex items-center justify-center">
                  <img :src="exitEvent.plate_image_url" alt="Plat Keluar" class="w-full h-40 object-contain" />
                </div>
              </div>
              <div v-if="exitEvent.scene_image_url">
                <p class="text-[11px] font-medium text-zinc-400 mb-1.5">Kendaraan Keluar</p>
                <div class="rounded-lg overflow-hidden border border-zinc-800 bg-zinc-900 flex items-center justify-center">
                  <img :src="exitEvent.scene_image_url" alt="Kendaraan Keluar" class="w-full h-40 object-contain" />
                </div>
              </div>
            </div>
            <div v-else class="text-center py-6 text-zinc-600 text-xs">
              <ImageIcon class="w-8 h-8 mx-auto mb-1 opacity-40" />
              <span v-if="history.is_inside">Kendaraan masih di dalam (belum ada gambar keluar)</span>
              <span v-else>Tidak ada gambar saat keluar</span>
            </div>
          </div>
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
