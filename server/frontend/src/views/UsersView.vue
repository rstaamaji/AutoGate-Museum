<script setup>
import { ref, onMounted } from 'vue'
import { Users, Plus, Pencil, Trash2, X, Loader2, AlertTriangle, Check } from '@lucide/vue'
import api from '@/services/api'

const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingUser = ref(null)
const saving = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  username: '',
  password: '',
  name: '',
  role: 'admin',
  is_active: true,
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const data = await api.getUsers()
    users.value = data.items || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingUser.value = null
  form.value = { username: '', password: '', name: '', role: 'admin', is_active: true }
  error.value = ''
  showModal.value = true
}

const openEdit = (user) => {
  editingUser.value = user
  form.value = {
    username: user.username,
    password: '',
    name: user.name,
    role: user.role,
    is_active: user.is_active,
  }
  error.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
  error.value = ''
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    if (editingUser.value) {
      const data = {}
      if (form.value.username) data.username = form.value.username
      if (form.value.password) data.password = form.value.password
      if (form.value.name) data.name = form.value.name
      if (form.value.role) data.role = form.value.role
      data.is_active = form.value.is_active
      await api.updateUser(editingUser.value.id, data)
    } else {
      if (!form.value.password) {
        error.value = 'Password wajib diisi untuk user baru'
        saving.value = false
        return
      }
      await api.createUser(form.value)
    }
    closeModal()
    await fetchUsers()
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const handleDelete = async (user) => {
  if (!confirm(`Hapus user '${user.username}'?`)) return
  try {
    await api.deleteUser(user.id)
    await fetchUsers()
  } catch (err) {
    alert(err.message)
  }
}

const roleLabel = (role) => {
  const labels = { super_admin: 'Super Admin', admin: 'Admin', pimpinan: 'Pimpinan' }
  return labels[role] || role
}

const roleColor = (role) => {
  const colors = {
    super_admin: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    admin: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    pimpinan: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  }
  return colors[role] || 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
}

onMounted(fetchUsers)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <Users class="w-5 h-5 text-zinc-400" />
          Kelola User
        </h2>
        <p class="text-xs text-zinc-400 mt-1">Manajemen user dan role akses</p>
      </div>
      <button
        @click="openCreate"
        class="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg text-sm transition"
      >
        <Plus class="w-4 h-4" />
        Tambah User
      </button>
    </div>

    <!-- Table -->
    <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl shadow-xl shadow-black/40 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Username</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Nama</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Role</th>
              <th class="text-left py-3 px-4 text-zinc-500 font-medium">Status</th>
              <th class="text-right py-3 px-4 text-zinc-500 font-medium">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="u in users"
              :key="u.id"
              class="border-b border-zinc-800/50 hover:bg-zinc-800/30"
            >
              <td class="py-3 px-4 font-mono text-white">{{ u.username }}</td>
              <td class="py-3 px-4 text-zinc-300">{{ u.name }}</td>
              <td class="py-3 px-4">
                <span :class="['px-2 py-0.5 rounded text-[10px] font-bold border', roleColor(u.role)]">
                  {{ roleLabel(u.role) }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span
                  :class="[
                    'px-2 py-0.5 rounded text-[10px] font-bold border',
                    u.is_active
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-red-500/10 text-red-400 border-red-500/20',
                  ]"
                >
                  {{ u.is_active ? 'Aktif' : 'Nonaktif' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    @click="openEdit(u)"
                    class="p-1.5 rounded text-zinc-400 hover:text-blue-400 hover:bg-blue-950/50 transition"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    @click="handleDelete(u)"
                    class="p-1.5 rounded text-zinc-400 hover:text-red-400 hover:bg-red-950/50 transition"
                    title="Hapus"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!users.length && !loading">
              <td colspan="5" class="py-6 text-center text-zinc-500">Belum ada user</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="closeModal">
      <div class="bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/60 w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <h3 class="text-lg font-bold text-white">{{ editingUser ? 'Edit User' : 'Tambah User' }}</h3>
          <button @click="closeModal" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSave" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Username</label>
            <input v-model="form.username" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Password {{ editingUser ? '(kosongkan jika tidak diubah)' : '' }}</label>
            <input v-model="form.password" type="password" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Lengkap</label>
            <input v-model="form.name" type="text" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Role</label>
            <select v-model="form.role" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="pimpinan">Pimpinan</option>
            </select>
          </div>
          <div v-if="editingUser" class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" id="is_active" class="rounded" />
            <label for="is_active" class="text-xs text-zinc-400">User Aktif</label>
          </div>

          <div v-if="error" class="flex items-start gap-2 bg-red-950/80 border border-red-800/60 rounded-lg px-3 py-2">
            <AlertTriangle class="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            <p class="text-xs text-red-300">{{ error }}</p>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="closeModal" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-medium rounded-lg transition">Batal</button>
            <button type="submit" :disabled="saving" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition disabled:opacity-50">
              <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
              <Check v-else class="w-4 h-4" />
              {{ editingUser ? 'Simpan' : 'Buat' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
