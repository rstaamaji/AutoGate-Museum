<script setup>
import { ref } from 'vue'
import HistoryView from '@/views/HistoryView.vue'
import EventsView from '@/views/EventsView.vue'
import VehiclesView from '@/views/VehiclesView.vue'
import VehicleOwnersView from '@/views/VehicleOwnersView.vue'
// VehicleTypesView SENGAJA tidak di-import di sini (dihilangkan dari UI)

defineProps({
  user: Object,
})

const tabs = [
  { id: 'history', label: 'Riwayat Transaksi', component: HistoryView },
  { id: 'events', label: 'Event Masuk/Keluar', component: EventsView },
  { id: 'owners', label: 'Data Pengunjung', component: VehicleOwnersView },
  { id: 'vehicles', label: 'Kartu Terdaftar', component: VehiclesView },
]

const activeTab = ref('history')
</script>

<template>
  <div class="p-6">
    <h2 class="text-xl font-bold text-white mb-4">Pengunjung & Transaksi</h2>

    <div class="flex gap-2 border-b border-zinc-800 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-4 py-2 text-sm font-semibold border-b-2 transition-colors',
          activeTab === tab.id
            ? 'border-blue-400 text-white'
            : 'border-transparent text-zinc-500 hover:text-zinc-300'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <component
      :is="tabs.find(t => t.id === activeTab)?.component"
      :user="user"
    />
  </div>
</template>
