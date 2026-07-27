/**
 * API Client untuk komunikasi dengan backend Pos Satpam (port 3000).
 */

const API_BASE = import.meta.env.VITE_API_URL || ''

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
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

  // ── Kendaraan ──

  async getPlates(params = {}) {
    const query = new URLSearchParams()
    if (params.skip) query.set('skip', params.skip)
    if (params.limit) query.set('limit', params.limit)
    if (params.direction) query.set('direction', params.direction)
    const qs = query.toString()
    return this.request(`/api/plates${qs ? `?${qs}` : ''}`)
  }

  async capturePlate(direction, channel = null) {
    const body = channel ? { channel } : {}
    return this.request(`/api/plates/${direction}`, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  // ── Relay/Gate ──

  async controlRelay(channel, status) {
    return this.request('/api/relay/control', {
      method: 'POST',
      body: JSON.stringify({ channel, status }),
    })
  }

  // ── Stream ──

  getStreamUrl(direction) {
    return `${this.baseUrl}/api/stream/${direction}`
  }

  // ── Status ──

  async getStatus() {
    return this.request('/api/status')
  }

  // ── Sync ──

  async getSyncStatus() {
    return this.request('/api/sync/status')
  }

  async manualSync() {
    return this.request('/api/sync/manual', { method: 'POST' })
  }

  // ── Settings ──

  async getSettings() {
    return this.request('/api/settings')
  }

  async updateSettings(updates) {
    return this.request('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(updates),
    })
  }
}

export const api = new ApiClient(API_BASE)
export default api
