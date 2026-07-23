/**
 * API Client untuk komunikasi dengan Server Backend (port 8000).
 */

const API_BASE = import.meta.env.VITE_API_URL || ''

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`
    const config = {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }))
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

  // ── Vehicles ──

  async getVehicles(params = {}) {
    const query = new URLSearchParams()
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    if (params.direction) query.set('direction', params.direction)
    if (params.node_id) query.set('node_id', params.node_id)
    const qs = query.toString()
    return this.request(`/api/vehicles${qs ? `?${qs}` : ''}`)
  }

  // ── Nodes ──

  async getNodes() {
    return this.request('/api/nodes')
  }

  async getNode(nodeId) {
    return this.request(`/api/nodes/${nodeId}`)
  }

  // ── Dashboard ──

  async getDashboardSummary() {
    return this.request('/api/dashboard/summary')
  }
}

export const api = new ApiClient(API_BASE)
export default api
