<script setup>
import { ref, onMounted, watch } from 'vue'
import GateCard from '@/components/gate/GateCard.vue'
import PlatesTable from '@/components/gate/PlatesTable.vue'
import { getPlates } from '@/services/api'

// Gate cards definitions
const gates = ref([
  {
    id: 1,
    direction: 'masuk',
    channel: 1,
    title: 'Gate 1 Masuk',
    lane: 'Lane 1 (Masuk)',
    timestamp: '-',
    image: '',
    plate: '---',
    rfidUid: '-',
    validationStatus: 'READY',
    barrierStatus: 'TERTUTUP'
  },
  {
    id: 2,
    direction: 'keluar',
    channel: 2,
    title: 'Gate 1 Keluar',
    lane: 'Lane 2 (Keluar)',
    timestamp: '-',
    image: '',
    plate: '---',
    rfidUid: '-',
    validationStatus: 'READY',
    barrierStatus: 'TERTUTUP'
  }
])

// Plates table state
const plates = ref([])
const totalPlates = ref(0)
const loadingPlates = ref(false)
const page = ref(1)
const limit = ref(10)
const selectedDirection = ref('')

const loadPlates = async () => {
  loadingPlates.value = true
  try {
    const skip = (page.value - 1) * limit.value
    const data = await getPlates({
      skip,
      limit: limit.value,
      direction: selectedDirection.value || null
    })
    plates.value = data.items || []
    totalPlates.value = data.total || 0
  } catch (err) {
    console.error('Gagal memuat data plates:', err)
  } finally {
    loadingPlates.value = false
  }
}

watch([page, selectedDirection], () => {
  loadPlates()
})

onMounted(() => {
  loadPlates()
})

const handleGateCaptured = (result) => {
  // Reload table data when a capture occurs
  loadPlates()
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <!-- Main CCTV Gate Monitoring Cards Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <GateCard 
        v-for="gate in gates" 
        :key="gate.id" 
        :gate="gate" 
        @captured="handleGateCaptured"
      />
    </div>

    <!-- ANPR Plate History List Table -->
    <PlatesTable 
      :plates="plates"
      :total="totalPlates"
      :loading="loadingPlates"
      v-model:page="page"
      :limit="limit"
      v-model:selectedDirection="selectedDirection"
      @refresh="loadPlates"
    />
  </div>
</template>
