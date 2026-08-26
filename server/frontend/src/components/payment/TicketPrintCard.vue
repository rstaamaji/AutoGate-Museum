<script setup>
import { nextTick, ref } from 'vue'
import JsBarcode from 'jsbarcode'
import api from '@/services/api'

const ticketCode = ref('')
const nodeApiKey = ref('')
const ticket = ref(null)
const errorMessage = ref('')
const loading = ref(false)

async function loadTicket() {
  errorMessage.value = ''
  ticket.value = null

  if (!ticketCode.value || !nodeApiKey.value) {
    errorMessage.value = 'Ticket code dan API key node wajib diisi.'
    return
  }

  loading.value = true

  try {
    ticket.value = await api.getTicketPrintData(
      ticketCode.value,
      nodeApiKey.value,
    )

    await nextTick()

    JsBarcode('#ticket-barcode', ticket.value.barcode_value, {
      format: 'CODE128',
      width: 2,
      height: 70,
      displayValue: false,
      margin: 10,
    })
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

function printTicket() {
  window.print()
}
</script>

<template>
  <section class="ticket-panel">
    <h2>Print Karcis</h2>

    <input
      v-model="ticketCode"
      placeholder="Contoh: TKT-1792727496"
    />

    <input
      v-model="nodeApiKey"
      type="password"
      placeholder="API key node"
    />

    <button type="button" @click="loadTicket">
      Ambil Data Karcis
    </button>

    <p v-if="loading">Memuat data...</p>
    <p v-if="errorMessage">{{ errorMessage }}</p>

    <article v-if="ticket" class="printed-ticket">
      <h3>Karcis Parkir Museum</h3>
      <p>Plat: {{ ticket.plate_number }}</p>
      <p>Tarif: Rp{{ ticket.amount.toLocaleString('id-ID') }}</p>

      <svg id="ticket-barcode"></svg>

      <p>Kode: {{ ticket.ticket_code }}</p>

      <button type="button" @click="printTicket">
        Cetak Karcis
      </button>
    </article>
  </section>
</template>