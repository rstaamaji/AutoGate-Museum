<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Radio, Camera, Zap, Clock } from '@lucide/vue'
import api from '@/services/api'

const nodes = ref([])
const loading = ref(false)
let timer = null

const fetchNodes = async () => {
  loading.value = true
  try {
    nodes.value = await api.getNodes()
  } catch (err) {
    console.error('Gagal mengambil data node:', err)
  } finally {
    loading.value = false
  }
}

const formatTime = (iso) => {
  if (!iso) return '---'
  return new Date(iso).toLocaleString('id-ID')
}

onMounted(() => {
  fetchNodes()
  timer = setInterval(fetchNodes, 15000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl shadow-black/40">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-bold text-white tracking-tight flex items-center gap-2">
        <Radio class="w-4 h-4 text-zinc-400" />
        Status Pos Satpam
      </h3>
      <span class="text-xs text-zinc-500">{{ nodes.length }} node</span>
    </div>

    <div v-if="!nodes.length && !loading" class="text-center py-6 text-zinc-500 text-sm">
      Belum ada pos satpam terdaftar
    </div>

    <div class="space-y-3">
      <div
        v-for="node in nodes"
        :key="node.id"
        class="bg-zinc-950 border border-zinc-800 rounded-lg p-3 hover:border-zinc-700 transition"
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span
              :class="[
                'w-2.5 h-2.5 rounded-full',
                node.status === 'online' ? 'bg-emerald-400' : 'bg-red-400',
              ]"
            ></span>
            <span class="text-sm font-bold text-white">{{ node.name }}</span>
          </div>
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

        <!-- ID -->
        <p class="text-[10px] text-zinc-500 font-mono mb-2">{{ node.id }}</p>

        <!-- Device Status Grid -->
        <div class="grid grid-cols-2 gap-2 mb-2">
          <div class="flex items-center gap-2 text-xs">
            <Camera class="w-3.5 h-3.5 text-zinc-500" />
            <span class="text-zinc-400">Cam Masuk</span>
            <span
              :class="[
                'w-2 h-2 rounded-full ml-auto',
                node.camera_in_active ? 'bg-emerald-400' : 'bg-zinc-600',
              ]"
            ></span>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <Camera class="w-3.5 h-3.5 text-zinc-500" />
            <span class="text-zinc-400">Cam Keluar</span>
            <span
              :class="[
                'w-2 h-2 rounded-full ml-auto',
                node.camera_out_active ? 'bg-emerald-400' : 'bg-zinc-600',
              ]"
            ></span>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <Zap class="w-3.5 h-3.5 text-zinc-500" />
            <span class="text-zinc-400">Relay Masuk</span>
            <span
              :class="[
                'w-2 h-2 rounded-full ml-auto',
                node.relay_in_active ? 'bg-emerald-400' : 'bg-zinc-600',
              ]"
            ></span>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <Zap class="w-3.5 h-3.5 text-zinc-500" />
            <span class="text-zinc-400">Relay Keluar</span>
            <span
              :class="[
                'w-2 h-2 rounded-full ml-auto',
                node.relay_out_active ? 'bg-emerald-400' : 'bg-zinc-600',
              ]"
            ></span>
          </div>
        </div>

        <!-- Last Seen -->
        <div class="flex items-center gap-1.5 text-[10px] text-zinc-500">
          <Clock class="w-3 h-3" />
          <span>Terakhir terlihat: {{ formatTime(node.last_seen_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
