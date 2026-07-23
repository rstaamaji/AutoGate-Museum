/**
 * API Service for AutoGateUNS Frontend
 * Handles HTTP requests to the FastAPI backend.
 */

const BASE_URL = ''

/**
 * Fetch list of captured plates from backend
 * @param {Object} options - { skip, limit, direction }
 * @returns {Promise<{total: number, items: Array}>}
 */
export async function getPlates({ skip = 0, limit = 50, direction = null } = {}) {
  const params = new URLSearchParams({ skip, limit })
  if (direction) {
    params.append('direction', direction)
  }

  const response = await fetch(`${BASE_URL}/api/plates?${params.toString()}`)
  if (!response.ok) {
    throw new Error(`Gagal mengambil data plat: ${response.statusText}`)
  }
  return await response.json()
}

/**
 * Trigger ANPR capture on camera for given direction ('masuk' | 'keluar')
 * @param {string} direction - 'masuk' or 'keluar'
 * @param {number|null} channel - optional channel override
 * @returns {Promise<{ignored: boolean, reason: string|null, vehicle: Object|null}>}
 */
export async function capturePlate(direction, channel = null) {
  const payload = channel ? { channel } : {}
  const response = await fetch(`${BASE_URL}/api/plates/${direction}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Gagal melakukan capture: ${response.statusText}`)
  }
  return await response.json()
}

/**
 * Control Modbus Relay (Open/Close barrier)
 * @param {number} channel - 1 for Gate Masuk, 2 for Gate Keluar (or custom)
 * @param {boolean} status - true = ON (Open), false = OFF (Close)
 * @returns {Promise<{success: boolean, message: string, channel: number, status: boolean}>}
 */
export async function controlRelay(channel, status) {
  const response = await fetch(`${BASE_URL}/api/relay/control`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ channel, status }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Gagal mengontrol relay: ${response.statusText}`)
  }
  return await response.json()
}

/**
 * Get image URL for live camera snapshot with cache busting
 * @param {string} direction - 'masuk' or 'keluar'
 * @returns {string} Image stream URL with timestamp query param
 */
export function getStreamUrl(direction) {
  return `${BASE_URL}/api/stream/${direction}?t=${Date.now()}`
}
