/**
 * API Client untuk komunikasi dengan Server Backend (port 8000).
 * Mendukung JWT auth untuk user dan API key untuk node.
 */

const API_BASE = import.meta.env.VITE_API_URL || ''

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
    this.token = localStorage.getItem('token') || null
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }

  getToken() {
    if (!this.token) {
      this.token = localStorage.getItem('token') || null
    }
    return this.token
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`
    const headers = { 'Content-Type': 'application/json', ...options.headers }

    // Tambah JWT token jika ada
    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const config = { ...options, headers }

    try {
      const response = await fetch(url, config)
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }))

        // Hanya auto-logout jika 401 dari endpoint auth (bukan dari polling)
        if (response.status === 401 && path === '/api/auth/me') {
          this.clearToken()
          window.location.reload()
          throw new Error('Sesi berakhir, silakan login kembali')
        }

        throw new Error(error.detail || `HTTP ${response.status}`)
      }
      return await response.json()
    } catch (err) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        throw new Error('Tidak dapat terhubung ke server')
      }
      throw err
    }
  }

  // ══════════════════════════════════════════
  // AUTH
  // ══════════════════════════════════════════

  async login(username, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    this.setToken(data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  }

  async getMe() {
    return this.request('/api/auth/me')
  }

  logout() {
    this.clearToken()
  }

  getUser() {
    try {
      return JSON.parse(localStorage.getItem('user'))
    } catch {
      return null
    }
  }

  // ══════════════════════════════════════════
  // USERS (super_admin)
  // ══════════════════════════════════════════

  async getUsers() {
    return this.request('/api/users')
  }

  async createUser(data) {
    return this.request('/api/users', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateUser(userId, data) {
    return this.request(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteUser(userId) {
    return this.request(`/api/users/${userId}`, { method: 'DELETE' })
  }

  // ══════════════════════════════════════════
  // NODES (super_admin write, admin read)
  // ══════════════════════════════════════════

  async getNodes() {
    return this.request('/api/nodes')
  }

  async getNode(nodeId) {
    return this.request(`/api/nodes/${nodeId}`)
  }

  async createNode(data) {
    return this.request('/api/nodes', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateNode(nodeId, data) {
    return this.request(`/api/nodes/${nodeId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteNode(nodeId) {
    return this.request(`/api/nodes/${nodeId}`, { method: 'DELETE' })
  }

  // ══════════════════════════════════════════
  // VEHICLE OWNERS (admin, super_admin)
  // ══════════════════════════════════════════

  async getVehicleOwners(params = {}) {
    const query = new URLSearchParams()
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    if (params.plate_number) query.set('plate_number', params.plate_number)
    const qs = query.toString()
    return this.request(`/api/vehicle-owners${qs ? `?${qs}` : ''}`)
  }

  async createVehicleOwner(data) {
    return this.request('/api/vehicle-owners', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateVehicleOwner(ownerId, data) {
    return this.request(`/api/vehicle-owners/${ownerId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteVehicleOwner(ownerId) {
    return this.request(`/api/vehicle-owners/${ownerId}`, { method: 'DELETE' })
  }

  // ══════════════════════════════════════════
  // VEHICLES (search untuk dropdown)
  // ══════════════════════════════════════════

  async searchVehicles(q = '', limit = 20) {
    const query = new URLSearchParams()
    if (q) query.set('q', q)
    if (limit) query.set('limit', limit)
    const qs = query.toString()
    return this.request(`/api/vehicles${qs ? `?${qs}` : ''}`)
  }

  async getVehicles(params = {}) {
    const query = new URLSearchParams()
    if (params.q) query.set('q', params.q)
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    const qs = query.toString()
    return this.request(`/api/vehicles${qs ? `?${qs}` : ''}`)
  }

  // ══════════════════════════════════════════
  // VEHICLE EVENTS (all authenticated)
  // ══════════════════════════════════════════

  async getEvents(params = {}) {
    const query = new URLSearchParams()
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    if (params.direction) query.set('direction', params.direction)
    if (params.plate_number) query.set('plate_number', params.plate_number)
    if (params.node_id) query.set('node_id', params.node_id)
    const qs = query.toString()
    return this.request(`/api/vehicles/events${qs ? `?${qs}` : ''}`)
  }

  // ══════════════════════════════════════════
  // VEHICLE HISTORY (all authenticated)
  // ══════════════════════════════════════════

  async getHistory(params = {}) {
    const query = new URLSearchParams()
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    if (params.plate_number) query.set('plate_number', params.plate_number)
    if (params.node_id) query.set('node_id', params.node_id)
    if (params.is_inside !== undefined && params.is_inside !== null) query.set('is_inside', params.is_inside)
    if (params.date_from) query.set('date_from', params.date_from)
    if (params.date_to) query.set('date_to', params.date_to)
    const qs = query.toString()
    return this.request(`/api/vehicles/history${qs ? `?${qs}` : ''}`)
  }

  async getHistoryDetail(historyId) {
    return this.request(`/api/vehicles/history/${historyId}`)
  }

  // ══════════════════════════════════════════
  // DASHBOARD
  // ══════════════════════════════════════════

  async getDashboardSummary() {
    return this.request('/api/dashboard/summary')
  }
}

export const api = new ApiClient(API_BASE)
export default api
