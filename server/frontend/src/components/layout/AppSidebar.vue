<script setup>
import { computed } from 'vue'
import {
  LayoutDashboard,
  Server,
  PanelLeftClose,
  PanelLeftOpen,
  Users,
  Radio,
  IdCard,
  LogOut,
} from '@lucide/vue'
// NOTE: Car, CarFront, Tag, History, List sudah tidak dipakai di sini,
// tapi JANGAN dihapus dari file lain yang mungkin masih pakai (misal
// kalau ada modal/komponen lain yang import icon yang sama).

const props = defineProps({
  user: Object,
  currentView: String,
  collapsed: Boolean,
})

const emit = defineEmits(['navigate', 'toggle'])

const isAdmin = computed(() => ['super_admin', 'admin'].includes(props.user?.role))
const isSuperAdmin = computed(() => props.user?.role === 'super_admin')

const navItems = computed(() => {
  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, show: true },
    { id: 'pengunjung', label: 'Pengunjung & Transaksi', icon: IdCard, show: true },
    { id: 'nodes', label: 'Kelola Node', icon: Radio, show: isAdmin.value },
    { id: 'users', label: 'Kelola User', icon: Users, show: isSuperAdmin.value },
  ]
  return items.filter(i => i.show)
})
</script>

<template>
  <aside
    :class="[
      'bg-[var(--bg-panel)] border-r border-[var(--border)] flex flex-col justify-between h-screen sticky top-0 z-30 select-none transition-all duration-300',
      collapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div>
      <!-- Header -->
      <div
        :class="[
          'px-4 py-5 flex items-center border-b border-[var(--border)]',
          collapsed ? 'justify-center' : 'justify-between'
        ]"
      >
        <div v-if="!collapsed" class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 shrink-0 rounded-lg bg-[var(--bg-panel-alt)] border border-[var(--border-hover)] flex items-center justify-center text-white shadow-md shadow-black/50">
            <Server class="w-5 h-5 text-[var(--accent)]" />
          </div>
          <div>
            <h1 class="text-base font-bold text-white tracking-wider flex items-center gap-1.5 whitespace-nowrap">
              AutoGate <span class="text-xs px-1.5 py-0.5 rounded bg-[var(--bg-panel-alt)] text-[var(--text-muted)] font-semibold">Server</span>
            </h1>
            <p class="text-[11px] text-[var(--text-muted)] font-medium whitespace-nowrap">Monitoring</p>
          </div>
        </div>
        <button
          @click="emit('toggle')"
          class="p-2 rounded-md text-[var(--text-muted)] hover:text-white hover:bg-[var(--bg-panel-alt)] border border-transparent hover:border-[var(--border)] transition shrink-0"
        >
          <PanelLeftOpen v-if="collapsed" class="w-5 h-5 text-[var(--accent)]" />
          <PanelLeftClose v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation -->
      <div class="p-3">
        <p v-if="!collapsed" class="px-3 text-[10px] font-bold text-[var(--text-muted-dark)] uppercase tracking-widest mb-3">Menu</p>
        <nav class="space-y-1.5">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="emit('navigate', item.id)"
            :class="[
              'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-semibold transition-all duration-150',
              collapsed ? 'justify-center px-0' : '',
              currentView === item.id
                ? 'bg-[var(--active-bg)] text-[var(--active-text)] shadow-sm shadow-black/20'
                : 'text-[var(--text-muted)] hover:text-white hover:bg-[var(--bg-panel-alt)]',
            ]"
            :title="item.label"
          >
            <component :is="item.icon" class="w-5 h-5 shrink-0" />
            <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- User Info -->
    <div class="p-3 border-t border-[var(--border)]">
      <div v-if="!collapsed" class="px-3 py-2">
        <p class="text-xs font-medium text-white truncate">{{ user?.name }}</p>
        <p class="text-[10px] text-[var(--text-muted-dark)] uppercase tracking-wider">{{ user?.role }}</p>
      </div>
    </div>
  </aside>
</template>