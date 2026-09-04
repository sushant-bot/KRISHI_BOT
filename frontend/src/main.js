/**
 * AgroVisor Edge — Main Application
 * Initializes the dashboard, fetches data, and renders all sections.
 */

import {
  setApiKey,
  checkHealth,
  getFarms,
  getZones,
  getReadings,
  getAlerts,
  issueIrrigationCommand,
  getDecisionContext,
  getZoneTwins,
  markAlertRead,
  ApiError,
} from './api.js';

// ──────────── State ────────────
let state = {
  connected: false,
  farms: [],
  zones: [],                // zones for the first farm
  readings: {},             // { zoneId: [readings] }
  alerts: [],
  decisionContext: null,
  zoneTwins: [],
  selectedFarmId: null,
  selectedZoneId: null,
  refreshTimer: null,
};

// ──────────── Initialise ────────────
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initApiKeyInput();
  initIrrigationForm();
  loadDashboard();
});

// ──────────── Navigation Scroll Effect ────────────
function initNav() {
  const nav = document.getElementById('main-nav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });
}

// ──────────── API Key Input ────────────
function initApiKeyInput() {
  const input = document.getElementById('api-key-input');
  const saved = localStorage.getItem('agrovisor_api_key') || '';
  if (saved) input.value = saved;

  input.addEventListener('change', () => {
    setApiKey(input.value.trim());
    showToast('API key updated', 'success');
    loadDashboard();
  });
}

// ──────────── Load Dashboard Data ────────────
async function loadDashboard() {
  await checkConnection();

  if (!state.connected) return;

  try {
    await Promise.all([
      loadFarms(),
      loadAlerts(),
      loadZoneTwins(),
    ]);
  } catch (err) {
    console.error('Dashboard load error:', err);
  }

  // Auto-refresh sensor readings every 30s
  if (state.refreshTimer) clearInterval(state.refreshTimer);
  state.refreshTimer = setInterval(async () => {
    if (state.zones.length > 0) {
      await loadAllReadings();
      renderZoneCards();
    }
  }, 30000);
}

// ──────────── Connection Check ────────────
async function checkConnection() {
  const dot = document.getElementById('connection-dot');
  const label = document.getElementById('connection-label');

  try {
    await checkHealth();
    state.connected = true;
    dot.className = 'connection-dot connected';
    label.textContent = 'Connected';
  } catch {
    state.connected = false;
    dot.className = 'connection-dot error';
    label.textContent = 'Offline';
    showToast('Cannot reach AgroVisor backend', 'error');
  }
}

// ──────────── Farms ────────────
async function loadFarms() {
  try {
    state.farms = await getFarms();
    renderFarmFeature();

    if (state.farms.length > 0) {
      state.selectedFarmId = state.farms[0].id;
      await loadZonesForFarm(state.selectedFarmId);
    } else {
      renderEmptyFarms();
    }
  } catch (err) {
    if (err instanceof ApiError && err.status === 403) {
      showToast('Invalid API key — enter your DEV_API_KEY in the nav bar', 'error');
    }
    renderEmptyFarms();
  }
}

function renderFarmFeature() {
  const container = document.getElementById('farm-feature');
  if (!state.farms.length) {
    renderEmptyFarms();
    return;
  }

  const farm = state.farms[0];
  container.innerHTML = `
    <div class="feature-card-content">
      <div>
        <span class="text-label-sm" style="color: var(--outline-variant); letter-spacing: 0.1em; display: block; margin-bottom: 1rem;">PRIMARY FARM</span>
        <h3 class="text-headline-md" style="color: var(--primary); margin-bottom: 1rem;">${escapeHtml(farm.name)}</h3>
        <p class="text-body-md" style="color: var(--on-surface-variant); margin-bottom: 1.5rem;">
          ${farm.location ? escapeHtml(farm.location) : 'Location not set'}<br/>
          <span style="font-size: 0.8125rem; color: var(--outline);">Created ${formatDate(farm.created_at)}</span>
        </p>
      </div>
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <button class="btn-outline" onclick="document.getElementById('zone-cards').scrollIntoView({behavior:'smooth'})">
          View Zones
        </button>
        ${state.farms.length > 1 ? `<span class="text-label-sm" style="color: var(--outline); align-self: center;">+${state.farms.length - 1} more farm${state.farms.length > 2 ? 's' : ''}</span>` : ''}
      </div>
    </div>
    <div class="feature-card-visual">
      <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&q=80" alt="${escapeHtml(farm.name)}" />
    </div>
  `;
}

function renderEmptyFarms() {
  const container = document.getElementById('farm-feature');
  container.innerHTML = `
    <div class="empty-state" style="width: 100%; padding: 4rem;">
      <span class="material-symbols-outlined">agriculture</span>
      <p>No farms found. Create a farm via <code>POST /api/farms</code> or check your API key.</p>
    </div>
  `;
}

// ──────────── Zones ────────────
async function loadZonesForFarm(farmId) {
  try {
    state.zones = await getZones(farmId);
    await loadAllReadings();
    renderZoneCards();
    populateZoneSelector();

    if (state.zones.length > 0) {
      state.selectedZoneId = state.zones[0].id;
      await loadDecisionContext(state.selectedZoneId);
    }
  } catch (err) {
    console.error('Zone load error:', err);
    state.zones = [];
    renderZoneCards();
  }
}

async function loadAllReadings() {
  const promises = state.zones.map(async (zone) => {
    try {
      state.readings[zone.id] = await getReadings(zone.id, 5);
    } catch {
      state.readings[zone.id] = [];
    }
  });
  await Promise.all(promises);
}

function renderZoneCards() {
  const container = document.getElementById('zone-cards');

  if (state.zones.length === 0) {
    container.innerHTML = `
      <div class="bento-card bento-col-8 stat-card">
        <div class="empty-state">
          <span class="material-symbols-outlined">grid_view</span>
          <p>No zones configured for this farm yet.</p>
        </div>
      </div>
    `;
    return;
  }

  // Render up to 2 zone cards in the bento grid
  const zonesHtml = state.zones.slice(0, 2).map((zone, idx) => {
    const readings = state.readings[zone.id] || [];
    const latest = readings[0] || null;

    const moisture = latest ? latest.soil_moisture : 0;
    const moisturePct = Math.min(moisture, 100);
    const temp = latest ? latest.soil_temperature.toFixed(1) : '--';
    const light = latest ? latest.light_intensity.toFixed(0) : '--';

    const moistureColor = moisturePct > 60 ? 'green' : moisturePct > 30 ? 'amber' : 'red';

    return `
      <div class="bento-card bento-col-4 stat-card animate-in animate-delay-${idx + 2}">
        <div>
          <span class="material-symbols-outlined icon">sensors</span>
          <h3>${escapeHtml(zone.name)}</h3>
          <p style="color: var(--outline-variant); font-size: 0.8125rem; margin-bottom: 1rem;">
            Code: ${escapeHtml(zone.code)}
          </p>
          ${latest ? `
            <div class="reveal-data" style="margin-top: 0;">
              <div class="reveal-datum">
                <div class="reveal-datum-label">Soil Moisture</div>
                <div class="reveal-datum-value ${moistureColor}">${moisture.toFixed(1)}%</div>
              </div>
              <div class="reveal-datum">
                <div class="reveal-datum-label">Temperature</div>
                <div class="reveal-datum-value">${temp}°C</div>
              </div>
              <div class="reveal-datum">
                <div class="reveal-datum-label">Light</div>
                <div class="reveal-datum-value">${light} lux</div>
              </div>
              <div class="reveal-datum">
                <div class="reveal-datum-label">Readings</div>
                <div class="reveal-datum-value blue">${readings.length}</div>
              </div>
            </div>
          ` : `
            <p style="color: var(--outline-variant); font-size: 0.875rem;">No sensor data yet</p>
          `}
        </div>
        <div style="margin-top: 1.5rem;">
          <div class="progress-track">
            <div class="progress-fill ${moistureColor}" style="width: ${moisturePct}%"></div>
          </div>
          <span class="text-label-sm" style="color: var(--outline-variant);">Soil Moisture ${moisturePct.toFixed(0)}%</span>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = zonesHtml;
}

// ──────────── Alerts ────────────
async function loadAlerts() {
  try {
    state.alerts = await getAlerts(null, null, false, 20);
    renderAlertQuote();
  } catch {
    state.alerts = [];
    renderAlertQuote();
  }
}

function renderAlertQuote() {
  const container = document.getElementById('alert-quote');
  const unread = state.alerts.filter(a => !a.is_read);
  const latest = unread.length > 0 ? unread[0] : state.alerts[0];

  if (!latest) {
    container.innerHTML = `
      <div class="quote-card-inner">
        <p class="quote-text">"All systems nominal. Your farm is thriving."</p>
        <span class="quote-source">— AgroVisor Edge</span>
      </div>
    `;
    return;
  }

  const severityIcon = latest.severity === 'CRITICAL' ? 'error' :
    latest.severity === 'WARNING' ? 'warning' : 'info';
  const severityColor = latest.severity === 'CRITICAL' ? 'var(--agro-red)' :
    latest.severity === 'WARNING' ? 'var(--agro-amber)' : 'var(--agro-blue)';

  container.innerHTML = `
    <div class="quote-card-inner" style="border-left-color: ${severityColor};">
      <p class="quote-text" style="font-style: normal; font-size: 1.25rem;">
        <span class="material-symbols-outlined" style="font-size: 1.5rem; vertical-align: middle; margin-right: 0.5rem; color: ${severityColor};">${severityIcon}</span>
        ${escapeHtml(latest.message)}
      </p>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="quote-source">${escapeHtml(latest.type)} · ${escapeHtml(latest.severity)} · ${formatDate(latest.created_at)}</span>
        ${!latest.is_read ? `<button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.625rem;" onclick="handleMarkRead(${latest.id})">Mark Read</button>` : ''}
      </div>
      ${unread.length > 1 ? `<span class="text-label-sm" style="color: var(--outline); display: block; margin-top: 0.75rem;">${unread.length} unread alerts total</span>` : ''}
    </div>
  `;
}

// Mark alert read handler (global for onclick)
window.handleMarkRead = async function(alertId) {
  try {
    await markAlertRead(alertId);
    showToast('Alert marked as read', 'success');
    await loadAlerts();
  } catch (err) {
    showToast('Failed to mark alert: ' + err.message, 'error');
  }
};

// ──────────── Irrigation Form ────────────
function populateZoneSelector() {
  const select = document.getElementById('irrigation-zone-select');
  if (!select) return;

  select.innerHTML = state.zones.map(z =>
    `<option value="${z.id}">${escapeHtml(z.name)} (${escapeHtml(z.code)})</option>`
  ).join('');

  if (state.zones.length === 0) {
    select.innerHTML = '<option value="">No zones available</option>';
  }
}

function initIrrigationForm() {
  const form = document.getElementById('irrigation-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const zoneId = parseInt(document.getElementById('irrigation-zone-select').value);
    const action = document.getElementById('irrigation-action-select').value;
    const targetWater = document.getElementById('irrigation-target-input').value;

    if (!zoneId) {
      showToast('Select a zone first', 'error');
      return;
    }

    const payload = {
      zone_id: zoneId,
      action: action,
    };
    if (targetWater && parseFloat(targetWater) > 0) {
      payload.target_water_liters = parseFloat(targetWater);
    }

    const submitBtn = document.getElementById('irrigation-submit-btn');
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;

    try {
      await issueIrrigationCommand(payload);
      showToast(`Irrigation ${action} command sent to zone ${zoneId}`, 'success');
      document.getElementById('irrigation-target-input').value = '';
    } catch (err) {
      showToast('Irrigation error: ' + err.message, 'error');
    } finally {
      submitBtn.textContent = 'Send Command';
      submitBtn.disabled = false;
    }
  });
}

// ──────────── Decision Context ────────────
async function loadDecisionContext(zoneId) {
  try {
    state.decisionContext = await getDecisionContext(zoneId);
    renderRevealList();
  } catch {
    state.decisionContext = null;
    renderRevealList();
  }
}

function renderRevealList() {
  const ctx = state.decisionContext;

  // Sensor
  const sensorEl = document.getElementById('reveal-sensor-data');
  if (ctx?.latest_sensor) {
    const s = ctx.latest_sensor;
    sensorEl.innerHTML = `
      <div class="reveal-data">
        <div class="reveal-datum">
          <div class="reveal-datum-label">Moisture</div>
          <div class="reveal-datum-value">${s.soil_moisture.toFixed(1)}%</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Temperature</div>
          <div class="reveal-datum-value">${s.soil_temperature.toFixed(1)}°C</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Light</div>
          <div class="reveal-datum-value">${s.light_intensity.toFixed(0)} lux</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Timestamp</div>
          <div class="reveal-datum-value" style="font-size: 0.75rem;">${formatDate(s.timestamp)}</div>
        </div>
      </div>
    `;
  } else {
    sensorEl.innerHTML = '<p>No sensor data available for this zone.</p>';
  }

  // AI
  const aiEl = document.getElementById('reveal-ai-data');
  if (ctx?.latest_ai_result) {
    const a = ctx.latest_ai_result;
    aiEl.innerHTML = `
      <div class="reveal-data">
        <div class="reveal-datum">
          <div class="reveal-datum-label">Crop Health</div>
          <div class="reveal-datum-value ${a.crop_health === 'healthy' ? 'green' : 'amber'}">${a.crop_health || 'N/A'}</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Disease</div>
          <div class="reveal-datum-value ${a.disease ? 'red' : 'green'}">${a.disease || 'None'}</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Confidence</div>
          <div class="reveal-datum-value">${a.confidence ? (a.confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Growth Stage</div>
          <div class="reveal-datum-value">${a.growth_stage || 'N/A'}</div>
        </div>
      </div>
    `;
  } else {
    aiEl.innerHTML = '<p>No AI analysis results for this zone.</p>';
  }

  // Irrigation
  const irrigEl = document.getElementById('reveal-irrigation-data');
  if (ctx?.active_irrigation) {
    const i = ctx.active_irrigation;
    irrigEl.innerHTML = `
      <div class="reveal-data">
        <div class="reveal-datum">
          <div class="reveal-datum-label">Status</div>
          <div class="reveal-datum-value ${i.status === 'ACTIVE' ? 'green' : 'amber'}">${i.status}</div>
        </div>
        <div class="reveal-datum">
          <div class="reveal-datum-label">Water Delivered</div>
          <div class="reveal-datum-value blue">${i.water_delivered_liters.toFixed(1)}L</div>
        </div>
      </div>
    `;
  } else {
    irrigEl.innerHTML = '<p>No active irrigation event for this zone.</p>';
  }
}

// ──────────── Zone Twins ────────────
async function loadZoneTwins() {
  try {
    state.zoneTwins = await getZoneTwins();
    renderZoneTwins();
  } catch {
    state.zoneTwins = [];
    renderZoneTwins();
  }
}

function renderZoneTwins() {
  const container = document.getElementById('twin-cards');

  if (state.zoneTwins.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1/-1;">
        <span class="material-symbols-outlined">hub</span>
        <p>No Digital Twin data available. Add farms and zones to see aggregated views.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.zoneTwins.map((twin, idx) => {
    const healthScore = twin.health_score?.farm_health_score;
    const badgeClass = healthScore != null ? (healthScore >= 70 ? 'healthy' : healthScore >= 40 ? 'warning' : 'critical') : '';
    const badgeText = healthScore != null ? `Score: ${healthScore}` : 'No Score';

    const sensor = twin.current;
    const alertCount = twin.alerts?.length || 0;
    const unreadAlerts = twin.alerts?.filter(a => !a.is_read).length || 0;
    const riskCount = twin.risks?.length || 0;

    const irrigStatus = twin.irrigation?.status || 'N/A';
    const irrigColor = irrigStatus === 'ACTIVE' ? 'green' : 'amber';

    return `
      <div class="twin-card animate-in animate-delay-${(idx % 4) + 1}">
        <div class="twin-card-header">
          <h3>Zone ${twin.zone_id}</h3>
          <span class="twin-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="twin-card-stats">
          <div class="twin-stat">
            <div class="twin-stat-label">Moisture</div>
            <div class="twin-stat-value ${sensor ? (sensor.soil_moisture > 60 ? 'green' : sensor.soil_moisture > 30 ? 'amber' : 'red') : ''}">
              ${sensor ? sensor.soil_moisture.toFixed(1) + '%' : '--'}
            </div>
          </div>
          <div class="twin-stat">
            <div class="twin-stat-label">Temperature</div>
            <div class="twin-stat-value">${sensor ? sensor.soil_temperature.toFixed(1) + '°C' : '--'}</div>
          </div>
          <div class="twin-stat">
            <div class="twin-stat-label">Irrigation</div>
            <div class="twin-stat-value ${irrigColor}">${irrigStatus}</div>
          </div>
          <div class="twin-stat">
            <div class="twin-stat-label">Risks</div>
            <div class="twin-stat-value ${riskCount > 0 ? 'red' : 'green'}">${riskCount}</div>
          </div>
        </div>
        ${alertCount > 0 ? `
          <div class="twin-alerts">
            ${twin.alerts.slice(0, 3).map(a => `
              <div class="twin-alert-row ${!a.is_read ? 'unread' : ''}">
                <span class="material-symbols-outlined">${a.severity === 'CRITICAL' ? 'error' : a.severity === 'WARNING' ? 'warning' : 'info'}</span>
                <span>${escapeHtml(a.message.length > 50 ? a.message.substring(0, 50) + '...' : a.message)}</span>
              </div>
            `).join('')}
            ${alertCount > 3 ? `<div class="twin-alert-row"><span style="color: var(--outline);">+${alertCount - 3} more</span></div>` : ''}
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

// ──────────── Toast Notifications ────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
  toast.innerHTML = `<span class="material-symbols-outlined" style="font-size: 1rem;">${icon}</span> ${escapeHtml(message)}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(1rem)';
    toast.style.transition = 'all 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ──────────── Utilities ────────────
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}
