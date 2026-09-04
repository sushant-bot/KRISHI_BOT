/**
 * AgroVisor Edge — API Client
 * Wraps fetch() calls to the FastAPI backend.
 */

const API_BASE = '/api';

/** Build request headers */
function headers(extra = {}) {
  return {
    'Content-Type': 'application/json',
    ...extra,
  };
}

/** Generic GET */
async function get(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: headers() });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body?.error?.message || res.statusText);
  }
  return res.json();
}

/** Generic POST */
async function post(path, payload) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body?.error?.message || res.statusText);
  }
  return res.json();
}

/** Generic PATCH */
async function patch(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    headers: headers(),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body?.error?.message || res.statusText);
  }
  return res.json();
}

/** Custom error class */
export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// ──────────── Health ────────────

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new ApiError(res.status, 'Backend unreachable');
  return res.json();
}

// ──────────── Farms ────────────

export async function getFarms() {
  return get('/farms');
}

export async function getFarm(farmId) {
  return get(`/farms/${farmId}`);
}

export async function createFarm(payload) {
  return post('/farms', payload);
}

// ──────────── Zones ────────────

export async function getZones(farmId) {
  return get(`/farms/${farmId}/zones`);
}

export async function getZone(zoneId) {
  return get(`/zones/${zoneId}`);
}

export async function createZone(farmId, payload) {
  return post(`/farms/${farmId}/zones`, payload);
}

// ──────────── Sensor Readings ────────────

export async function getReadings(zoneId, limit = 100) {
  return get(`/zones/${zoneId}/readings?limit=${limit}`);
}

export async function createReading(payload) {
  return post('/sensors/readings', payload);
}

// ──────────── Irrigation ────────────

export async function issueIrrigationCommand(payload) {
  return post('/irrigation/command', payload);
}

export async function getIrrigationStatus(zoneId) {
  return get(`/irrigation/status?zone_id=${zoneId}`);
}

export async function getIrrigationHistory(zoneId = null, limit = 100) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (zoneId) params.set('zone_id', String(zoneId));
  return get(`/irrigation/history?${params}`);
}

export async function recordFlow(payload) {
  return post('/irrigation/flow', payload);
}

// ──────────── Images ────────────

export async function getZoneImages(zoneId, limit = 100) {
  return get(`/zones/${zoneId}/images?limit=${limit}`);
}

// ──────────── AI Results ────────────

export async function getAiResults(zoneId, limit = 100) {
  return get(`/zones/${zoneId}/ai-results?limit=${limit}`);
}

// ──────────── Decisions ────────────

export async function getDecisionContext(zoneId) {
  return get(`/zones/${zoneId}/decision-context`);
}

export async function getZoneRisks(zoneId, limit = 100) {
  return get(`/zones/${zoneId}/risks?limit=${limit}`);
}

export async function getZoneHealth(zoneId) {
  return get(`/zones/${zoneId}/health`);
}

// ──────────── Alerts ────────────

export async function getAlerts(farmId = null, zoneId = null, unreadOnly = false, limit = 100) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (farmId) params.set('farm_id', String(farmId));
  if (zoneId) params.set('zone_id', String(zoneId));
  if (unreadOnly) params.set('unread_only', 'true');
  return get(`/alerts?${params}`);
}

export async function markAlertRead(alertId) {
  return patch(`/alerts/${alertId}/read`);
}

// ──────────── Digital Twin ────────────

export async function getDigitalTwin() {
  return get('/digital-twin');
}

export async function getZoneTwins() {
  return get('/digital-twin/zones');
}

export async function getZoneTwin(zoneId) {
  return get(`/digital-twin/zones/${zoneId}`);
}
