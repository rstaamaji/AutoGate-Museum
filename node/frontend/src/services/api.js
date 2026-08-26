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
    if (params.skip !== undefined) query.set('skip', params.skip)
    if (params.limit !== undefined) query.set('limit', params.limit)
    if (params.direction) query.set('direction', params.direction)
    if (params.search) query.set('search', params.search)
    if (params.start_date) query.set('start_date', params.start_date)
    if (params.end_date) query.set('end_date', params.end_date)
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

<<<<<<< Updated upstream
  // ── RFID ──

  async submitRfid(eventId, rfidUid = null) {
    return this.request('/api/rfid', {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId, rfid_uid: rfidUid }),
    })
  }

=======
  async startEntryPayment(plateNumber, entryEventId) {
    return this.request('/api/payment/start', {
      method: 'POST',
      body: JSON.stringify({
        plate_number: plateNumber,
        entry_event_id: entryEventId,
      }),
    })
  }

  async getPaymentStatus(ticketCode) {
    return this.request(`/api/payment/status/${encodeURIComponent(ticketCode)}`)
  }

  async completeEntryPayment(ticketCode) {
    return this.request(
      `/api/payment/complete-entry/${encodeURIComponent(ticketCode)}`,
      { method: 'POST' },
    )
  }

>>>>>>> Stashed changes
  // ── Relay/Gate ──

  async controlRelay(channel, status) {
    return this.request('/api/relay/control', {
      method: 'POST',
      body: JSON.stringify({ channel, status }),
    })
  }

  async validateExit(barcodeToken) {
    return this.request('/api/payment/validate-exit', {
      method: 'POST',
      body: JSON.stringify({ barcode_token: barcodeToken }),
    })
  }

  async completeExit(barcodeToken, exitEventId = null) {
    return this.request('/api/payment/complete-exit', {
      method: 'POST',
      body: JSON.stringify({
        barcode_token: barcodeToken,
        exit_event_id: exitEventId,
      }),
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
