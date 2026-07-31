<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Nfc, Loader2, AlertTriangle, CheckCircle2, ArrowRight } from '@lucide/vue'
import api from '@/services/api'

const props = defineProps({
  vehicle: { type: Object, required: true },
  direction: { type: String, required: true }, // "masuk" atau "keluar"
})

const emit = defineEmits(['close', 'done'])

const rfidInput = ref('')
const rfidRef = ref(null)
const submitting = ref(false)
const submitError = ref('')
const rfidMatchResult = ref(null) // true, false, null
const submitted = ref(false)

const isMasuk = props.direction === 'masuk'
const title = isMasuk ? 'RFID untuk Masuk' : 'RFID untuk Keluar'
const accentColor = isMasuk ? 'emerald' : 'blue'

const handleSubmit = async () => {
  if (submitting.value) return
  submitting.value = true
  submitError.value = ''

  try {
    const rfidUid = rfidInput.value.trim() || null
    const result = await api.submitRfid(props.vehicle.event_id, rfidUid)

    if (!result.success) {
      submitError.value = result.message || 'Gagal menyimpan RFID'
      return
    }

    rfidMatchResult.value = result.rfid_match
    submitted.value = true

    // Auto-close setelah 2 detik (atau 4 detik jika ada warning mismatch)
    const delay = result.rfid_match === false ? 4000 : 2000
    setTimeout(() => {
      emit('done', { rfid_match: result.rfid_match })
      emit('close')
    }, delay)
  } catch (err) {
    submitError.value = err.message || 'Gagal mengirim RFID'
  } finally {
    submitting.value = false
  }
}

const handleLanjutkan = () => {
  rfidInput.value = ''
  handleSubmit()
}

const handleKeydown = (e) => {
  // Blokir Escape — modal wajib diisi atau "Lanjutkan" ditekan
  if (e.key === 'Escape') {
    e.preventDefault()
    e.stopPropagation()
  }
}

onMounted(async () => {
  document.addEventListener('keydown', handleKeydown, true) // capture phase
  await nextTick()
  rfidRef.value?.focus()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown, true)
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
      <!-- Header -->
      <div class="flex items-center gap-3 px-6 py-4 border-b border-zinc-800">
        <div
          :class="[
            'p-2 rounded-lg',
            isMasuk ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400',
          ]"
        >
          <Nfc class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-white">{{ title }}</h3>
          <p class="text-xs text-zinc-500">Tap kartu RFID atau tekan Enter</p>
        </div>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-4">
        <!-- Info kendaraan -->
        <div class="flex items-center gap-3 bg-zinc-950 rounded-lg p-3 border border-zinc-800">
          <img
            v-if="vehicle.plate_image_url"
            :src="vehicle.plate_image_url"
            alt="Plat"
            class="w-20 h-12 object-contain rounded border border-zinc-700 bg-zinc-900"
          />
          <div class="flex-1 min-w-0">
            <p class="font-mono font-bold text-white text-lg">{{ vehicle.plate_number }}</p>
            <p class="text-xs text-zinc-500">
              Confidence: {{ vehicle.confidence ? `${vehicle.confidence.toFixed(1)}%` : '---' }}
            </p>
          </div>
          <span
            :class="[
              'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
              isMasuk
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
            ]"
          >
            {{ direction }}
          </span>
        </div>

        <!-- Sudah submit -->
        <div v-if="submitted" class="space-y-3">
          <div class="flex items-center gap-2 bg-emerald-950/80 border border-emerald-800/60 rounded-lg px-3 py-3">
            <CheckCircle2 class="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <p class="text-sm font-semibold text-emerald-300">RFID tersimpan</p>
              <p class="text-xs text-emerald-400/70">Gate sedang dibuka...</p>
            </div>
          </div>

          <!-- Warning RFID mismatch (keluar) -->
          <div v-if="rfidMatchResult === false" class="flex items-start gap-2 bg-amber-950/80 border border-amber-800/60 rounded-lg px-3 py-3">
            <AlertTriangle class="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
            <div>
              <p class="text-sm font-semibold text-amber-300">RFID Berbeda</p>
              <p class="text-xs text-amber-400/70">RFID tidak cocok dengan data entry. Gate tetap dibuka.</p>
            </div>
          </div>
        </div>

        <!-- Form input RFID -->
        <div v-else class="space-y-4">
          <div>
            <label class="block text-[11px] text-zinc-500 font-medium mb-1.5">UID RFID</label>
            <input
              ref="rfidRef"
              v-model="rfidInput"
              @keydown.enter.prevent="handleSubmit"
              type="text"
              placeholder="Scan kartu RFID..."
              autocomplete="off"
              :disabled="submitting"
              :class="[
                'w-full bg-zinc-950 border rounded-lg px-3 py-3 text-lg font-mono text-white focus:outline-none transition disabled:opacity-50',
                isMasuk ? 'border-zinc-700 focus:border-emerald-500' : 'border-zinc-700 focus:border-blue-500',
              ]"
            />
            <p class="text-[10px] text-zinc-600 mt-1">Scanner RFID akan mengetik otomatis di sini, lalu tekan Enter.</p>
          </div>

          <!-- Error -->
          <div v-if="submitError" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
            <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            <p class="text-xs text-red-300">{{ submitError }}</p>
          </div>

          <!-- Buttons -->
          <div class="flex gap-3 pt-2">
            <button
              @click="handleLanjutkan"
              :disabled="submitting"
              class="flex-1 flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 font-semibold py-2.5 px-4 rounded-lg text-sm transition active:scale-[0.98] disabled:opacity-50"
            >
              <ArrowRight class="w-4 h-4" />
              Lanjutkan Tanpa RFID
            </button>
            <button
              @click="handleSubmit"
              :disabled="submitting || !rfidInput.trim()"
              :class="[
                'flex-1 flex items-center justify-center gap-2 border font-semibold py-2.5 px-4 rounded-lg text-sm transition active:scale-[0.98] disabled:opacity-50',
                isMasuk
                  ? 'bg-emerald-600 hover:bg-emerald-500 text-white border-emerald-500'
                  : 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500',
              ]"
            >
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              <Nfc v-else class="w-4 h-4" />
              Submit RFID
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
