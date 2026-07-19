<script setup>
import { ref } from 'vue'
import GateCard from '@/components/gate/GateCard.vue'

const gates = ref([
  {
    id: 1,
    title: 'Gate 1 Masuk',
    lane: 'Lane 1',
    timestamp: '24/05/2025 10:24:36',
    image: '',
    plate: 'B 1234 ABC',
    rfidUid: 'E280 1160 1234 5678 90AB',
    validationStatus: 'GRANTED',
    barrierStatus: 'TERBUKA'
  },
  {
    id: 2,
    title: 'Gate 1 Keluar',
    lane: 'Lane 2',
    timestamp: '24/05/2025 10:24:36',
    image: '',
    plate: 'B 5678 DEF',
    rfidUid: 'E280 1160 9876 5432 10CD',
    validationStatus: 'GRANTED',
    barrierStatus: 'TERBUKA'
  }
])
</script>

<template>
  <div class="p-6">
    <!-- Main CCTV Gate Monitoring Cards Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <GateCard 
        v-for="gate in gates" 
        :key="gate.id" 
        :gate="gate" 
      />
    </div>
  </div>
</template>
