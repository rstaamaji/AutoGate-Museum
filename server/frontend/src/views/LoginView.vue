<script setup>
import { ref } from 'vue'
import { Lock, User, Loader2, AlertTriangle, Server } from '@lucide/vue'
import api from '@/services/api'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Username dan password wajib diisi'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const data = await api.login(username.value, password.value)
    emit('login-success', data.user)
  } catch (err) {
    error.value = err.message || 'Login gagal'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-zinc-900 border border-zinc-700/60 flex items-center justify-center mb-4 shadow-xl shadow-black/50">
          <Server class="w-8 h-8 text-blue-400" />
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight">AutoGate UNS</h1>
        <p class="text-sm text-zinc-400 mt-1">Server Monitoring — Login</p>
      </div>

      <!-- Form -->
      <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-6 shadow-xl shadow-black/40">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1.5">Username</label>
            <div class="relative">
              <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                v-model="username"
                type="text"
                placeholder="Masukkan username"
                autocomplete="username"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1.5">Password</label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                v-model="password"
                type="password"
                placeholder="Masukkan password"
                autocomplete="current-password"
                class="w-full bg-zinc-950 border border-zinc-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition"
              />
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
            <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            <p class="text-xs text-red-300">{{ error }}</p>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 px-4 rounded-lg text-sm transition active:scale-[0.98] disabled:opacity-50"
          >
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            <Lock v-else class="w-4 h-4" />
            <span>{{ loading ? 'Masuk...' : 'Masuk' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-[11px] text-zinc-600 mt-6">
        AutoGate UNS — Universitas Sebelas Maret
      </p>
    </div>
  </div>
</template>
