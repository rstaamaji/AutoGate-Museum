<script setup>
import { ref, watch, onMounted } from 'vue'
import { 
  RefreshCw, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Eye, 
  X,
  Car,
  Calendar,
  Layers,
  Sparkles
} from 'lucide-vue-next'

const props = defineProps({
  plates: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  page: {
    type: Number,
    default: 1
  },
  limit: {
    type: Number,
    default: 10
  },
  selectedDirection: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:page', 'update:selectedDirection', 'refresh'])

// Local state for modal image zoom
const activeImageModal = ref(null)

const openImageModal = (url, title) => {
  if (!url) return
  activeImageModal.value = { url, title }
}

const closeImageModal = () => {
  activeImageModal.value = null
}

const formatDate = (isoString) => {
  if (!isoString) return '-'
  try {
    const d = new Date(isoString)
    return new Intl.DateTimeFormat('id-ID', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(d)
  } catch (e) {
    return isoString
  }
}

const totalPages = ref(1)

watch([() => props.total, () => props.limit], () => {
  totalPages.value = Math.max(1, Math.ceil(props.total / props.limit))
})
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl shadow-black/40 mt-6">
    <!-- Header Controls -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
      <div>
        <h3 class="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Car class="w-5 h-5 text-emerald-400" />
          Riwayat Kendaraan (ANPR)
        </h3>
        <p class="text-xs text-zinc-400 mt-0.5">Daftar rekaman kendaraan masuk dan keluar dari kamera ANPR</p>
      </div>

      <div class="flex items-center gap-3">
        <!-- Filter Direction -->
        <select 
          :value="selectedDirection"
          @change="$emit('update:selectedDirection', $event.target.value)"
          class="bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-zinc-700 transition"
        >
          <option value="">Semua Arah</option>
          <option value="masuk">Gate Masuk</option>
          <option value="keluar">Gate Keluar</option>
        </select>

        <!-- Refresh Button -->
        <button 
          @click="$emit('refresh')"
          :disabled="loading"
          class="flex items-center gap-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-zinc-200 text-xs font-medium px-3 py-2 rounded-lg border border-zinc-700/60 transition active:scale-95"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Table Container -->
    <div class="overflow-x-auto rounded-lg border border-zinc-800/80 bg-zinc-950/60">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="border-b border-zinc-800 text-zinc-400 bg-zinc-900/80 uppercase tracking-wider font-semibold text-[11px]">
            <th class="py-3 px-4"># ID</th>
            <th class="py-3 px-4">Arah</th>
            <th class="py-3 px-4">Plat Nomor</th>
            <th class="py-3 px-4">Foto Plat</th>
            <th class="py-3 px-4">Foto Kendaraan</th>
            <th class="py-3 px-4">Akurasi</th>
            <th class="py-3 px-4">Waktu Rekam</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-800/60 text-zinc-300">
          <tr v-if="loading && plates.length === 0">
            <td colspan="7" class="py-12 text-center text-zinc-500">
              <div class="flex flex-col items-center justify-center gap-2">
                <RefreshCw class="w-6 h-6 animate-spin text-emerald-400" />
                <span>Memuat data riwayat plat...</span>
              </div>
            </td>
          </tr>

          <tr v-else-if="plates.length === 0">
            <td colspan="7" class="py-12 text-center text-zinc-500">
              Belum ada data riwayat plat kendaraan.
            </td>
          </tr>

          <tr 
            v-for="item in plates" 
            :key="item.id"
            class="hover:bg-zinc-900/50 transition-colors"
          >
            <!-- ID -->
            <td class="py-3 px-4 font-mono font-medium text-zinc-400">#{{ item.id }}</td>

            <!-- Arah Badge -->
            <td class="py-3 px-4">
              <span 
                class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border"
                :class="item.direction === 'masuk' 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/20'"
              >
                {{ item.direction }}
              </span>
            </td>

            <!-- Plat Nomor -->
            <td class="py-3 px-4">
              <span class="font-mono font-bold text-sm tracking-widest text-white px-2 py-1 bg-zinc-900 border border-zinc-700/80 rounded">
                {{ item.plate_number }}
              </span>
            </td>

            <!-- Foto Plat -->
            <td class="py-3 px-4">
              <div 
                v-if="item.plate_image_url"
                @click="openImageModal(item.plate_image_url, `Foto Plat - ${item.plate_number}`)"
                class="w-16 h-10 rounded overflow-hidden border border-zinc-700 bg-zinc-900 cursor-pointer hover:opacity-80 transition group relative"
              >
                <img :src="item.plate_image_url" alt="Foto Plat" class="w-full h-full object-cover" />
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
                  <Eye class="w-3.5 h-3.5 text-white" />
                </div>
              </div>
              <span v-else class="text-zinc-600 italic">-</span>
            </td>

            <!-- Foto Scene -->
            <td class="py-3 px-4">
              <div 
                v-if="item.scene_image_url"
                @click="openImageModal(item.scene_image_url, `Foto Kendaraan - ${item.plate_number}`)"
                class="w-20 h-10 rounded overflow-hidden border border-zinc-700 bg-zinc-900 cursor-pointer hover:opacity-80 transition group relative"
              >
                <img :src="item.scene_image_url" alt="Foto Scene" class="w-full h-full object-cover" />
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
                  <Eye class="w-3.5 h-3.5 text-white" />
                </div>
              </div>
              <span v-else class="text-zinc-600 italic">-</span>
            </td>

            <!-- Confidence -->
            <td class="py-3 px-4 font-mono">
              <span v-if="item.confidence !== null" class="text-zinc-200">
                {{ item.confidence.toFixed(1) }}%
              </span>
              <span v-else class="text-zinc-600">-</span>
            </td>

            <!-- Captured At -->
            <td class="py-3 px-4 font-mono text-zinc-400 text-[11px]">
              {{ formatDate(item.captured_at || item.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Controls -->
    <div class="flex items-center justify-between pt-4 text-xs text-zinc-400">
      <div>
        Menampilkan {{ plates.length }} dari {{ total }} data
      </div>

      <div class="flex items-center gap-2">
        <button 
          @click="$emit('update:page', Math.max(1, page - 1))"
          :disabled="page <= 1 || loading"
          class="p-1.5 rounded-lg border border-zinc-800 bg-zinc-950 hover:bg-zinc-900 disabled:opacity-40 transition"
        >
          <ChevronLeft class="w-4 h-4 text-zinc-300" />
        </button>

        <span class="px-2 font-mono text-zinc-300">
          {{ page }} / {{ totalPages }}
        </span>

        <button 
          @click="$emit('update:page', Math.min(totalPages, page + 1))"
          :disabled="page >= totalPages || loading"
          class="p-1.5 rounded-lg border border-zinc-800 bg-zinc-950 hover:bg-zinc-900 disabled:opacity-40 transition"
        >
          <ChevronRight class="w-4 h-4 text-zinc-300" />
        </button>
      </div>
    </div>

    <!-- Image Modal Viewer -->
    <div 
      v-if="activeImageModal"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      @click.self="closeImageModal"
    >
      <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-3xl w-full p-4 relative shadow-2xl">
        <div class="flex items-center justify-between mb-3 border-b border-zinc-800 pb-2">
          <h4 class="text-sm font-bold text-white">{{ activeImageModal.title }}</h4>
          <button @click="closeImageModal" class="p-1 text-zinc-400 hover:text-white rounded hover:bg-zinc-800">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="relative max-h-[75vh] flex items-center justify-center bg-black rounded-lg overflow-hidden">
          <img :src="activeImageModal.url" class="max-h-[70vh] object-contain w-full" />
        </div>
      </div>
    </div>
  </div>
</template>
