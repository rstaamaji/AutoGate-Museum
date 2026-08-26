<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import JsBarcode from 'jsbarcode'
import api from '@/services/api'

const state = ref('waiting')
const message = ref('Menunggu kendaraan...')
const vehicle = ref(null)
const payment = ref(null)
const printData = ref(null)
const errorMessage = ref('')

let vehicleTimer = null
let paymentTimer = null
let lastEntryId = null

async function detectEntry() {
  if (state.value !== 'waiting') return

  try {
    const data = await api.getPlates({ direction: 'masuk', limit: 1 })
    const latest = data.items?.[0]
    if (!latest || latest.id === lastEntryId) return

    lastEntryId = latest.id
    vehicle.value = latest
    state.value = 'payment'
    message.value = 'Silakan bayar tarif masuk Rp5.000.'

    payment.value = await api.startEntryPayment(
      latest.plate_number,
      latest.event_id,
    )
    startPaymentPolling()
  } catch (error) {
    errorMessage.value = error.message
    state.value = 'error'
    message.value = 'Pembayaran belum dapat dimulai.'
  }
}

function startPaymentPolling() {
  clearInterval(paymentTimer)
  paymentTimer = setInterval(checkPayment, 3000)
}

async function checkPayment() {
  if (!payment.value?.ticket_code) return

  try {
    const status = await api.getPaymentStatus(payment.value.ticket_code)
    if (!status.can_open_gate) return

    clearInterval(paymentTimer)
    state.value = 'printing'
    message.value = 'Pembayaran berhasil. Menyiapkan karcis...'

    const result = await api.completeEntryPayment(payment.value.ticket_code)
    printData.value = result.ticket
    await nextTick()
    JsBarcode('#entry-barcode', printData.value.barcode_value, {
      format: 'CODE128',
      width: 2,
      height: 70,
      displayValue: false,
      margin: 10,
    })
    state.value = 'done'
    message.value = 'Karcis siap. Silakan masuk.'
  } catch (error) {
    errorMessage.value = error.message
    state.value = 'error'
    clearInterval(paymentTimer)
  }
}

function resetKiosk() {
  clearInterval(paymentTimer)
  state.value = 'waiting'
  message.value = 'Menunggu kendaraan...'
  vehicle.value = null
  payment.value = null
  printData.value = null
  errorMessage.value = ''
}

onMounted(() => {
  detectEntry()
  vehicleTimer = setInterval(detectEntry, 2000)
})

onUnmounted(() => {
  clearInterval(vehicleTimer)
  clearInterval(paymentTimer)
})
</script>

<template>
  <section class="rounded-xl border border-zinc-800 bg-zinc-900/90 p-6 shadow-xl shadow-black/30">
    <div class="flex items-center justify-between gap-4">
      <div>
        <p class="text-xs uppercase tracking-widest text-zinc-500">Pintu Masuk Otomatis</p>
        <h2 class="mt-1 text-xl font-bold text-white">{{ message }}</h2>
      </div>
      <span class="rounded-full border border-zinc-700 px-3 py-1 text-xs uppercase text-zinc-400">
        {{ state }}
      </span>
    </div>

    <div v-if="vehicle" class="mt-5 grid gap-2 text-sm text-zinc-300 sm:grid-cols-3">
      <span>Plat: <strong class="text-white">{{ vehicle.plate_number }}</strong></span>
      <span v-if="payment">Karcis: <strong class="text-white">{{ payment.ticket_code }}</strong></span>
      <span v-if="payment">Tarif: <strong class="text-white">Rp{{ payment.amount.toLocaleString('id-ID') }}</strong></span>
    </div>

    <a
      v-if="payment?.redirect_url && state === 'payment'"
      :href="payment.redirect_url"
      target="_blank"
      rel="noreferrer"
      class="mt-6 inline-flex rounded-lg bg-emerald-500 px-4 py-2 text-sm font-bold text-zinc-950"
    >
      Bayar Sekarang
    </a>

    <div v-if="printData" class="mt-6 rounded-lg bg-white p-4 text-center text-zinc-950">
      <p class="font-bold">Karcis Parkir Museum</p>
      <svg id="entry-barcode"></svg>
      <p class="mt-2 text-xs">{{ printData.ticket_code }}</p>
    </div>

    <p v-if="errorMessage" class="mt-4 text-sm text-red-400">{{ errorMessage }}</p>
    <button
      v-if="state === 'done' || state === 'error'"
      type="button"
      class="mt-5 rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-200"
      @click="resetKiosk"
    >
      Siap untuk kendaraan berikutnya
    </button>
  </section>
</template>
