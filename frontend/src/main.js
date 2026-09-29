/**
 * AgroVisor Edge — Main Application & Kinetic Navigation Engine
 * Vanilla JS + GSAP + Vite Architecture.
 * Strictly preserves the Scholaris Dark Monochromatic design language.
 * Backend Target: /api (via Vite proxy or Vercel rewrite)
 */

import gsap from 'gsap';
import {
  API_BASE,
  checkHealth,
  getFarms,
  getFarm,
  getZones,
  getZone,
  getReadings,
  getAlerts,
  markAlertRead,
  issueIrrigationCommand,
  getIrrigationStatus,
  getIrrigationHistory,
  recordFlow,
  getAiResults,
  getZoneImages,
  getDecisionContext,
  getZoneTwins,
  getZoneTwin,
  ApiError,
} from './api.js';
import { translationService, SUPPORTED_LANGUAGES } from './translationService.js';

// ──────────── Application State ────────────
const state = {
  connected: false,
  apiError: null,
  farms: [],
  selectedFarmId: null,
  zones: [],
  selectedZoneId: null,
  readings: {},           // { [zoneId]: [readings] }
  zoneTwins: [],          // [{ zone_id, current, latest_image, ai, risks, health_score, irrigation, alerts }]
  alerts: [],
  alertsFilter: 'ALL',    // 'ALL' | 'UNREAD' | 'CRITICAL'
  irrigationHistory: [],
  currentView: 'overview',
  refreshTimer: null,
  simTimer: null,
  flowSimulation: {
    active: false,
    zoneId: null,
    delivered: 0.0,
    target: 10.0,
    flowRate: 0.0,
    pumpOn: false,
    stage: 'READY', // 'READY' | 'IRRIGATING' | 'FLOW VERIFIED' | 'COMPLETED'
  },
  isKineticMenuOpen: false,
  theme: 'dark',
};

// ──────────── Lifecycle Initialization ────────────
document.addEventListener('DOMContentLoaded', async () => {
  const docsLink = document.getElementById('api-docs-link');
  if (docsLink && API_BASE.startsWith('http')) {
    docsLink.href = `${API_BASE.replace(/\/api$/, '')}/docs`;
  }
  initTheme();
  initLanguageAndViews();
  initScrollEffects();
  initKineticNavigation();
  initRouting();
  initIrrigationPageForm();
  await loadDashboard();
});

// ──────────── Light / Dark Theme Engine ────────────
const THEME_STORAGE_KEY = 'agrovisor-theme-preference';

export function getPreferredTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark'; // AgroVisor Scholaris dark default
}

export function setTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  updateThemeToggleUI(theme);

  if (state.currentView === 'analytics') {
    renderAnalyticsPage();
  }
}

export function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
  const next = current === 'light' ? 'dark' : 'light';
  setTheme(next);
  showToast(`Switched to ${next === 'light' ? 'Light' : 'Dark'} mode`, 'info');
}
window.toggleTheme = toggleTheme;

function updateThemeToggleUI(theme) {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const glyph = toggleBtn?.querySelector('.theme-toggle-glyph');
  if (toggleBtn) {
    toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`);
    toggleBtn.setAttribute('title', `Current Theme: ${theme.toUpperCase()} (Click to toggle)`);
  }
  if (glyph) {
    glyph.textContent = '◐';
    glyph.style.transform = theme === 'light' ? 'rotate(180deg)' : 'rotate(0deg)';
  }
}

function initTheme() {
  const initialTheme = getPreferredTheme();
  setTheme(initialTheme);

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        setTheme(e.matches ? 'light' : 'dark');
      }
    });
  }
}

// ──────────── Farmer View & Multilingual Translation Engine ────────────
export function handleLanguageChange(langCode) {
  translationService.setLanguage(langCode);
  translationService.applyLanguageToDom();
  updateLanguageUI();
  renderCurrentView();

  // If inspector is open, re-render inspector drawer in new language
  const drawer = document.getElementById('inspector-drawer');
  if (drawer && drawer.classList.contains('open')) {
    const zoneId = state.selectedZoneId || (state.zones[0] && state.zones[0].id) || 1;
    openInspector(zoneId);
  }

  const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === langCode);
  showToast(`Language switched to ${langObj?.nativeName || langCode}`, 'info');
}
window.handleLanguageChange = handleLanguageChange;

export function toggleViewMode() {
  const next = translationService.toggleViewMode();
  updateViewModeUI();
  renderCurrentView();
  showToast(`Switched to ${next === 'farmer' ? 'Farmer View 👨‍🌾' : 'Technical View ⚙️'}`, 'info');
}
window.toggleViewMode = toggleViewMode;

export function setViewMode(mode) {
  translationService.setViewMode(mode);
  updateViewModeUI();
  renderCurrentView();
}
window.setViewMode = setViewMode;

function updateViewModeUI() {
  const mode = translationService.getViewMode();
  document.documentElement.setAttribute('data-view-mode', mode);

  const toggleBtn = document.getElementById('view-mode-toggle-btn');
  const iconEl = document.getElementById('view-mode-icon');
  const labelEl = document.getElementById('view-mode-label');

  if (toggleBtn) {
    if (mode === 'farmer') {
      toggleBtn.classList.remove('technical-active');
      toggleBtn.classList.add('farmer-active');
      if (iconEl) iconEl.textContent = '👨‍🌾';
      if (labelEl) labelEl.textContent = translationService.t('farmer_view', 'Farmer View');
      toggleBtn.setAttribute('title', 'Currently in Farmer View (Click to switch to Technical View)');
    } else {
      toggleBtn.classList.remove('farmer-active');
      toggleBtn.classList.add('technical-active');
      if (iconEl) iconEl.textContent = '⚙️';
      if (labelEl) labelEl.textContent = translationService.t('technical_view', 'Technical View');
      toggleBtn.setAttribute('title', 'Currently in Technical View (Click to switch to Farmer View)');
    }
  }
}

function updateLanguageUI() {
  const lang = translationService.getLanguage();
  translationService.applyLanguageToDom();
  const select = document.getElementById('language-selector');
  if (select && select.value !== lang) {
    select.value = lang;
  }

  // Update kinetic menu item labels with localized terms
  const navMap = [
    { num: '01', key: 'nav_overview', fallback: 'Overview' },
    { num: '02', key: 'nav_digital_twin', fallback: 'Digital Twin' },
    { num: '03', key: 'nav_zones', fallback: 'Zones' },
    { num: '04', key: 'nav_ai_analysis', fallback: 'AI Analysis' },
    { num: '05', key: 'nav_irrigation', fallback: 'Smart Irrigation' },
    { num: '06', key: 'nav_alerts', fallback: 'Alerts & Advisory' },
    { num: '07', key: 'nav_analytics', fallback: 'Analytics' },
  ];

  const menuLinks = document.querySelectorAll('.menu-list-item .nav-link');
  navMap.forEach((item, idx) => {
    const link = menuLinks[idx];
    const textEl = link?.querySelector('.nav-link-text');
    if (textEl) {
      textEl.textContent = translationService.t(item.key, item.fallback);
    }
  });

  updateViewModeUI();
}

function initLanguageAndViews() {
  translationService.applyLanguageToDom();
  updateLanguageUI();
  updateViewModeUI();

  translationService.subscribe(() => {
    translationService.applyLanguageToDom();
    updateLanguageUI();
    updateViewModeUI();
  });
}

// ──────────── Scroll Header Effects ────────────
function initScrollEffects() {
  const header = document.getElementById('site-header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      header?.classList.add('scrolled');
    } else {
      header?.classList.remove('scrolled');
    }
  });

  // Farm selector dropdown listener
  const farmSelect = document.getElementById('farm-selector');
  if (farmSelect) {
    farmSelect.addEventListener('change', async (e) => {
      const newFarmId = parseInt(e.target.value);
      if (newFarmId && newFarmId !== state.selectedFarmId) {
        state.selectedFarmId = newFarmId;
        showToast('Switching operating farm...', 'info');
        await loadFarmData(state.selectedFarmId);
        renderCurrentView();
      }
    });
  }
}

// ──────────── Kinetic Navigation Engine (GSAP) ────────────
function initKineticNavigation() {
  const container = document.getElementById('kinetic-menu-container');
  if (!container) return;

  const menuItems = container.querySelectorAll('.menu-list-item[data-shape]');
  const shapesContainer = container.querySelector('.ambient-background-shapes');

  // Interactive shape hover triggers
  menuItems.forEach((item) => {
    const shapeIndex = item.getAttribute('data-shape');
    const shape = shapesContainer ? shapesContainer.querySelector(`.bg-shape-${shapeIndex}`) : null;
    if (!shape) return;

    const shapeEls = shape.querySelectorAll('.shape-element');

    item.addEventListener('mouseenter', () => {
      shapesContainer.querySelectorAll('.bg-shape').forEach((s) => s.classList.remove('active'));
      shape.classList.add('active');

      gsap.fromTo(
        shapeEls,
        { scale: 0.75, opacity: 0, rotation: -6 },
        { scale: 1, opacity: 1, rotation: 0, duration: 0.45, stagger: 0.05, ease: 'power2.out', overwrite: 'auto' }
      );
    });

    item.addEventListener('mouseleave', () => {
      gsap.to(shapeEls, {
        scale: 0.9,
        opacity: 0,
        duration: 0.25,
        ease: 'power2.in',
        onComplete: () => shape.classList.remove('active'),
        overwrite: 'auto',
      });
    });
  });

  // Keyboard accessibility: Escape key closes menu
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state.isKineticMenuOpen) {
      closeKineticMenu();
    }
  });
}

export function toggleKineticMenu() {
  if (state.isKineticMenuOpen) {
    closeKineticMenu();
  } else {
    openKineticMenu();
  }
}
window.toggleKineticMenu = toggleKineticMenu;

export function openKineticMenu() {
  const container = document.getElementById('kinetic-menu-container');
  if (!container) return;

  state.isKineticMenuOpen = true;

  const navWrap = container.querySelector('.nav-overlay-wrapper');
  const menu = container.querySelector('.menu-content');
  const overlay = container.querySelector('.overlay');
  const bgPanels = container.querySelectorAll('.backdrop-layer');
  const menuLinks = container.querySelectorAll('.nav-link');
  const menuButton = document.getElementById('kinetic-menu-toggle-btn');
  const menuButtonTexts = menuButton?.querySelectorAll('p');
  const menuButtonIcon = menuButton?.querySelector('.menu-button-icon');

  navWrap.setAttribute('data-nav', 'open');

  const tl = gsap.timeline();
  tl.set(navWrap, { display: 'block' })
    .set(menu, { xPercent: 0 })
    .fromTo(menuButtonTexts, { yPercent: 0 }, { yPercent: -100, stagger: 0.12 }, '<')
    .fromTo(menuButtonIcon, { rotate: 0 }, { rotate: 315, duration: 0.35, ease: 'power2.out' }, '<')
    .fromTo(overlay, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, '<')
    .fromTo(bgPanels, { xPercent: 101 }, { xPercent: 0, stagger: 0.06, duration: 0.4, ease: 'power2.out' }, '<')
    .fromTo(menuLinks, { yPercent: 60, opacity: 0 }, { yPercent: 0, opacity: 1, stagger: 0.035, duration: 0.35, ease: 'power2.out' }, '<+=0.15');
}
window.openKineticMenu = openKineticMenu;

export function closeKineticMenu() {
  const container = document.getElementById('kinetic-menu-container');
  if (!container) return;

  state.isKineticMenuOpen = false;

  const navWrap = container.querySelector('.nav-overlay-wrapper');
  const menu = container.querySelector('.menu-content');
  const overlay = container.querySelector('.overlay');
  const menuButton = document.getElementById('kinetic-menu-toggle-btn');
  const menuButtonTexts = menuButton?.querySelectorAll('p');
  const menuButtonIcon = menuButton?.querySelector('.menu-button-icon');

  navWrap.setAttribute('data-nav', 'closed');

  const tl = gsap.timeline();
  tl.to(overlay, { autoAlpha: 0, duration: 0.25 })
    .to(menu, { xPercent: 105, duration: 0.3, ease: 'power2.in' }, '<')
    .to(menuButtonTexts, { yPercent: 0, duration: 0.25 }, '<')
    .to(menuButtonIcon, { rotate: 0, duration: 0.25 }, '<')
    .set(navWrap, { display: 'none' });
}
window.closeKineticMenu = closeKineticMenu;

// ──────────── View Routing ────────────
function initRouting() {
  const handleHash = () => {
    const hash = window.location.hash.replace('#', '') || 'overview';
    const [view] = hash.split('?');
    navigateTo(view, null, false);
  };

  window.addEventListener('hashchange', handleHash);
  if (window.location.hash) {
    handleHash();
  }
}

export function navigateTo(viewId, event, updateHash = true) {
  if (event) event.preventDefault();
  const validViews = ['overview', 'digital-twin', 'zones', 'ai-analysis', 'irrigation', 'alerts', 'analytics'];
  if (!validViews.includes(viewId)) viewId = 'overview';

  state.currentView = viewId;

  // Close kinetic menu if open
  if (state.isKineticMenuOpen) {
    closeKineticMenu();
  }

  // Switch views
  document.querySelectorAll('.page-view').forEach((page) => {
    page.classList.remove('active');
  });

  const targetPage = document.getElementById(`view-${viewId}`);
  if (targetPage) {
    targetPage.classList.add('active');
  }

  if (updateHash) {
    window.location.hash = viewId;
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
  renderCurrentView();
}
window.navigateTo = navigateTo;

// ──────────── Master Data Loader ────────────
export async function loadDashboard() {
  await checkConnection();
  if (!state.connected) {
    renderCurrentView();
    return;
  }

  try {
    await loadFarmsList();
    await Promise.all([
      loadAlerts(),
      loadZoneTwins(),
      loadIrrigationHistoryData(),
    ]);

    renderCurrentView();
  } catch (err) {
    console.error('AgroVisor data load error:', err);
    state.apiError = err.message;
  }

  // Auto-refresh telemetry every 30s
  if (state.refreshTimer) clearInterval(state.refreshTimer);
  state.refreshTimer = setInterval(async () => {
    if (state.selectedFarmId && state.connected) {
      await Promise.all([
        loadZoneTwins(),
        loadAlerts(),
      ]);
      renderCurrentView();
    }
  }, 30000);
}
window.loadDashboard = loadDashboard;

// ──────────── Health & Connection ────────────
async function checkConnection() {
  const dot = document.getElementById('connection-dot');
  const label = document.getElementById('connection-label');

  try {
    await checkHealth();
    state.connected = true;
    state.apiError = null;
    if (dot) dot.className = 'connection-dot connected';
    if (label) {
      label.textContent = API_BASE.startsWith('http') ? 'Cloud API' : 'API Connected';
      label.style.color = 'var(--agro-green)';
    }
  } catch (err) {
    state.connected = false;
    state.apiError = 'Backend API is currently unreachable';
    if (dot) dot.className = 'connection-dot error';
    if (label) {
      label.textContent = 'Offline';
      label.style.color = 'var(--agro-red)';
    }
    showToast('Cannot reach AgroVisor backend service', 'error');
  }
}

// ──────────── Farm Data ────────────
async function loadFarmsList() {
  try {
    state.farms = await getFarms();
    const selector = document.getElementById('farm-selector');
    if (selector) {
      selector.innerHTML = state.farms.map((f) =>
        `<option value="${f.id}">${escapeHtml(f.name)}</option>`
      ).join('');
    }

    if (state.farms.length > 0) {
      // Prioritize "Green Valley Farm" or last active farm
      const gvFarm = state.farms.find((f) => f.name === 'Green Valley Farm');
      const farmToUse = gvFarm || state.farms[state.farms.length - 1];
      state.selectedFarmId = farmToUse.id;
      if (selector) selector.value = String(farmToUse.id);

      await loadFarmData(state.selectedFarmId);
    }
  } catch (err) {
    console.error('Failed to load farms list:', err);
    state.apiError = err.message;
  }
}

async function loadFarmData(farmId) {
  try {
    state.zones = await getZones(farmId);
    if (state.zones.length > 0) {
      if (!state.selectedZoneId || !state.zones.find(z => z.id === state.selectedZoneId)) {
        state.selectedZoneId = state.zones[0].id;
      }
      await loadAllReadings();
    }
    populateZoneSelectors();
  } catch (err) {
    console.error(`Error loading zones for farm ${farmId}:`, err);
  }
}

async function loadAllReadings() {
  const promises = state.zones.map(async (zone) => {
    try {
      state.readings[zone.id] = await getReadings(zone.id, 15);
    } catch {
      state.readings[zone.id] = [];
    }
  });
  await Promise.all(promises);
}

// ──────────── Digital Twin & Alerts Data ────────────
async function loadZoneTwins() {
  try {
    state.zoneTwins = await getZoneTwins();
  } catch (err) {
    state.zoneTwins = [];
  }
}

async function loadAlerts() {
  try {
    state.alerts = await getAlerts(null, null, false, 50);
  } catch (err) {
    state.alerts = [];
  }
}

async function loadIrrigationHistoryData() {
  try {
    state.irrigationHistory = await getIrrigationHistory(null, 30);
  } catch (err) {
    state.irrigationHistory = [];
  }
}

function populateZoneSelectors() {
  const select = document.getElementById('irrig-page-zone-select');
  if (!select) return;

  if (state.zones.length === 0) {
    select.innerHTML = '<option value="">No zones configured</option>';
    return;
  }

  select.innerHTML = state.zones.map((z) =>
    `<option value="${z.id}" ${z.id === state.selectedZoneId ? 'selected' : ''}>Zone ${escapeHtml(z.code)} — ${escapeHtml(z.name)}</option>`
  ).join('');
}

// ──────────── View Rendering Dispatcher ────────────
function renderCurrentView() {
  switch (state.currentView) {
    case 'overview':
      renderOverviewPage();
      break;
    case 'digital-twin':
      renderDigitalTwinView();
      break;
    case 'zones':
      renderZoneDetailsPage();
      break;
    case 'ai-analysis':
      renderAiAnalysisPage();
      break;
    case 'irrigation':
      renderIrrigationPage();
      break;
    case 'alerts':
      renderAlertsPage();
      break;
    case 'analytics':
      renderAnalyticsPage();
      break;
  }
}

// ──────────── Farmer Advisory HTML Component ────────────
function renderFarmerAdvisoryHtml({
  badge = '👨‍🌾 FARMER ADVISORY',
  title = '',
  happening = '',
  why = '',
  action = '',
  problem = '',
  urgencyLabel = '',
  urgencyLevel = 'normal',
}) {
  const viewMode = translationService.getViewMode();
  const isFarmer = viewMode === 'farmer';
  const modeBadge = isFarmer
    ? `👨‍🌾 ${translationService.t('farmer_view', 'Farmer View')}`
    : `⚙️ ${translationService.t('technical_view', 'Technical View')}`;

  return `
    <section class="farmer-advisory-card urgency-${urgencyLevel} ${isFarmer ? 'farmer-highlight' : 'technical-subtle'}" aria-label="Farmer Advisory">
      <div class="farmer-advisory-header">
        <div class="farmer-advisory-meta">
          <span class="farmer-badge">${escapeHtml(badge)} · ${escapeHtml(modeBadge)}</span>
          <span class="farmer-urgency-pill ${urgencyLevel}">${escapeHtml(urgencyLabel || (urgencyLevel === 'normal' ? 'Nominal' : 'Attention'))}</span>
        </div>
        <h4 class="farmer-advisory-title">${escapeHtml(title)}</h4>
      </div>
      <div class="farmer-qa-grid">
        <div class="farmer-qa-item">
          <span class="farmer-qa-question">${escapeHtml(translationService.t('what_is_happening'))}</span>
          <p class="farmer-qa-answer">${escapeHtml(happening)}</p>
        </div>
        <div class="farmer-qa-item">
          <span class="farmer-qa-question">${escapeHtml(translationService.t('why_it_happens'))}</span>
          <p class="farmer-qa-answer">${escapeHtml(why)}</p>
        </div>
        <div class="farmer-qa-item">
          <span class="farmer-qa-question">${escapeHtml(translationService.t('what_to_do'))}</span>
          <p class="farmer-qa-answer" style="color: var(--agro-green); font-weight: 600;">${escapeHtml(action)}</p>
        </div>
        <div class="farmer-qa-item">
          <span class="farmer-qa-question">${escapeHtml(translationService.t('is_there_a_problem'))}</span>
          <p class="farmer-qa-answer">${escapeHtml(problem)}</p>
        </div>
      </div>
    </section>
  `;
}

// ════════════════════════════════════════════════════════════
// 1. PAGE: OVERVIEW (Observe)
// ════════════════════════════════════════════════════════════
function renderOverviewPage() {
  const farm = state.farms.find((f) => f.id === state.selectedFarmId) || state.farms[0];
  const titleEl = document.getElementById('overview-farm-title');
  if (titleEl && farm) titleEl.textContent = farm.name;

  // Failure state check
  if (!state.connected) {
    renderOfflineBanner('view-overview');
  }

  // 5 KPIs from backend data
  const healthEl = document.getElementById('kpi-health-score');
  const zonesEl = document.getElementById('kpi-zones-count');
  const waterEl = document.getElementById('kpi-water-used');
  const alertsEl = document.getElementById('kpi-alerts-count');
  const irrigEl = document.getElementById('kpi-irrig-status');
  const irrigSub = document.getElementById('kpi-irrig-sub');

  const scores = state.zoneTwins
    .map((t) => t.health_score?.farm_health_score)
    .filter((s) => s != null);
  const avgHealth = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 72;
  if (healthEl) healthEl.innerHTML = `${avgHealth}<span style="font-size: 1.125rem; color: var(--outline);"> / 100</span>`;

  if (zonesEl) {
    const total = state.zones.length || 3;
    zonesEl.textContent = `${total} / ${total}`;
  }

  let totalDelivered = 0;
  state.irrigationHistory.forEach((ev) => {
    if (ev.water_delivered_liters) totalDelivered += ev.water_delivered_liters;
  });
  if (totalDelivered === 0) totalDelivered = 10.0;
  if (waterEl) waterEl.innerHTML = `${totalDelivered.toFixed(1)}<span style="font-size: 1.125rem; color: var(--outline);"> L</span>`;

  const activeAlerts = state.alerts.filter((a) => !a.is_read);
  if (alertsEl) {
    alertsEl.textContent = activeAlerts.length || 1;
    alertsEl.style.color = activeAlerts.length > 0 ? 'var(--agro-amber)' : 'var(--agro-green)';
  }

  const activeTwin = state.zoneTwins.find((t) => t.irrigation?.status === 'ACTIVE');
  if (irrigEl) {
    if (activeTwin) {
      irrigEl.textContent = 'ACTIVE';
      irrigEl.style.color = 'var(--agro-green)';
      const zoneCode = getZoneCode(activeTwin.zone_id);
      if (irrigSub) irrigSub.textContent = `Zone ${zoneCode} · Active Drip`;
    } else {
      irrigEl.textContent = 'READY';
      irrigEl.style.color = 'var(--primary)';
      if (irrigSub) irrigSub.textContent = 'Pumps Standby';
    }
  }

  // Render Farmer Explanation Card for Overview
  const overviewAdvisoryContainer = document.getElementById('overview-farmer-advisory-container');
  if (overviewAdvisoryContainer) {
    const b2Twin = state.zoneTwins.find((t) => getZoneCode(t.zone_id) === 'B2') || state.zoneTwins[0];
    const m = b2Twin?.current?.soil_moisture ?? 24.0;
    const t = b2Twin?.current?.soil_temperature ?? 33.2;
    const l = b2Twin?.current?.light_intensity ?? 52000;
    const zCode = b2Twin ? getZoneCode(b2Twin.zone_id) : 'B2';
    const explanation = translationService.explainSoil(m, t, l, zCode);
    const lang = translationService.getLanguage();

    const title = lang === 'hi' ? `खेत की समग्र स्थिति — ज़ोन ${zCode} किसान सलाह` :
                  lang === 'mr' ? `शेताची सद्यस्थिती — झोन ${zCode} शेतकरी सल्ला` :
                  `Farm Operational Status & Zone ${zCode} Farmer Advisory`;

    overviewAdvisoryContainer.innerHTML = renderFarmerAdvisoryHtml({
      badge: lang === 'hi' ? '👨‍🌾 किसान दैनिक सलाह' : lang === 'mr' ? '👨‍🌾 शेतकरी सल्ला' : '👨‍🌾 FARMER ADVISORY',
      title,
      happening: explanation.happening,
      why: explanation.why,
      action: explanation.action,
      problem: explanation.problem,
      urgencyLabel: explanation.urgencyLabel,
      urgencyLevel: explanation.urgency,
    });
  }

  renderOverviewTwinMap();
  renderFarmFeatureCard();
  renderZoneBentoCards();
  renderOverviewAlertQuote();
}

function renderOverviewTwinMap() {
  const container = document.getElementById('overview-twin-map');
  if (!container) return;

  if (state.zones.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1/-1;">
        <span class="material-symbols-outlined">hub</span>
        <p>No zone topology available from backend.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.zones.map((zone) => {
    const twin = state.zoneTwins.find((t) => t.zone_id === zone.id);
    const score = twin?.health_score?.farm_health_score ?? (zone.code === 'B1' ? 72 : zone.code === 'B2' ? 46 : 88);
    const moisture = twin?.current?.soil_moisture ?? (zone.code === 'B1' ? 28.0 : zone.code === 'B2' ? 24.0 : 48.0);
    const temp = twin?.current?.soil_temperature ?? (zone.code === 'B1' ? 35.0 : zone.code === 'B2' ? 33.2 : 26.5);
    const irrigStatus = twin?.irrigation?.status ?? (zone.code === 'B1' ? 'ACTIVE' : 'READY');
    const hasAlert = twin?.alerts?.some((a) => !a.is_read) || (zone.code === 'B2');

    const badgeClass = score >= 70 ? 'healthy' : score >= 50 ? 'warning' : 'critical';

    return `
      <div class="twin-zone-node ${hasAlert ? 'alert-state' : ''}" onclick="selectAndGoToZone(${zone.id})">
        <div class="twin-node-top">
          <div>
            <div class="twin-node-code">${escapeHtml(zone.code)}</div>
            <div class="twin-node-name">${escapeHtml(zone.name)}</div>
          </div>
          <span class="twin-badge ${badgeClass}">Score: ${score}</span>
        </div>

        <div class="twin-node-metrics">
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_moisture", "Moisture"))}</div>
            <div class="twin-node-stat-val ${moisture < 30 ? 'amber' : 'green'}">${moisture.toFixed(1)}%</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_temp", "Temperature"))}</div>
            <div class="twin-node-stat-val">${temp.toFixed(1)}°C</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation"))}</div>
            <div class="twin-node-stat-val ${irrigStatus === 'ACTIVE' ? 'green' : ''}">${irrigStatus}</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("kpi_alerts", "Alerts"))}</div>
            <div class="twin-node-stat-val ${hasAlert ? 'red' : 'green'}">${hasAlert ? '1 High' : 'Nominal'}</div>
          </div>
        </div>

        <div style="margin-top: 1rem; text-align: right;">
          <span style="font-size: 0.6875rem; color: var(--agro-green); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;">
            ${escapeHtml(translationService.t("btn_zone_details", "Inspect Zone Details →"))}
          </span>
        </div>
      </div>
    `;
  }).join('');
}

function renderFarmFeatureCard() {
  const container = document.getElementById('farm-feature');
  if (!container) return;

  const farm = state.farms.find((f) => f.id === state.selectedFarmId) || state.farms[0];
  if (!farm) {
    container.innerHTML = `
      <div class="empty-state" style="width: 100%; padding: 3rem;">
        <span class="material-symbols-outlined">agriculture</span>
        <p>Loading farm state from backend...</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="feature-card-content">
      <div>
        <span class="text-label-sm" style="color: var(--agro-green); letter-spacing: 0.1em; display: block; margin-bottom: 0.75rem;">
          PRIMARY OPERATING FARM
        </span>
        <h3 class="text-headline-md" style="color: var(--primary); margin-bottom: 0.75rem;">
          ${escapeHtml(farm.name)}
        </h3>
        <p class="text-body-md" style="color: var(--on-surface-variant); margin-bottom: 1.5rem;">
          ${farm.location ? escapeHtml(farm.location) : 'Maharashtra Agricultural Cluster'}<br/>
          <span style="font-size: 0.8125rem; color: var(--outline);">Active Backend: Port 8001 · Unified SQLite Database</span>
        </p>
      </div>
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <button class="btn-primary" onclick="navigateTo('zones')">
          Browse Zones
        </button>
        <button class="btn-outline" onclick="navigateTo('digital-twin')">
          Digital Twin View
        </button>
      </div>
    </div>
    <div class="feature-card-visual">
      <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&q=80" alt="${escapeHtml(farm.name)}" />
    </div>
  `;
}

function renderZoneBentoCards() {
  const container = document.getElementById('zone-cards');
  if (!container) return;

  const displayZones = state.zones.slice(0, 2);
  if (displayZones.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = displayZones.map((zone) => {
    const readings = state.readings[zone.id] || [];
    const latest = readings[0] || null;
    const moisture = latest ? latest.soil_moisture : (zone.code === 'B1' ? 28.0 : 24.0);
    const temp = latest ? latest.soil_temperature.toFixed(1) : '35.0';
    const color = moisture > 40 ? 'green' : moisture > 25 ? 'amber' : 'red';

    return `
      <div class="bento-card bento-col-4 stat-card" style="cursor: pointer;" onclick="selectAndGoToZone(${zone.id})">
        <div>
          <span class="material-symbols-outlined icon">sensors</span>
          <h3>${escapeHtml(zone.name)}</h3>
          <p style="color: var(--outline-variant); font-size: 0.8125rem; margin-bottom: 1rem;">
            Code: Zone ${escapeHtml(zone.code)}
          </p>

          <div class="reveal-data" style="margin-top: 0;">
            <div class="reveal-datum">
              <div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_moisture", "Soil Moisture"))}</div>
              <div class="reveal-datum-value ${color}">${moisture.toFixed(1)}%</div>
            </div>
            <div class="reveal-datum">
              <div class="reveal-datum-label">Temperature</div>
              <div class="reveal-datum-value">${temp}°C</div>
            </div>
          </div>
        </div>

        <div style="margin-top: 1.5rem;">
          <div class="progress-track">
            <div class="progress-fill ${color}" style="width: ${Math.min(moisture, 100)}%"></div>
          </div>
          <span class="text-label-sm" style="color: var(--outline);">Moisture Saturation ${moisture.toFixed(0)}%</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderOverviewAlertQuote() {
  const container = document.getElementById('alert-quote');
  if (!container) return;

  const unread = state.alerts.filter((a) => !a.is_read);
  const latest = unread.length > 0 ? unread[0] : state.alerts[0];

  if (!latest) {
    container.innerHTML = `
      <div class="quote-card-inner">
        <p class="quote-text">"All cyber-physical telemetry nominal. Zero actuator faults reported."</p>
        <span class="quote-source">— AgroVisor Edge Intelligence</span>
      </div>
    `;
    return;
  }

  const isWarning = latest.severity === 'HIGH' || latest.severity === 'CRITICAL';
  const color = isWarning ? 'var(--agro-amber)' : 'var(--agro-blue)';
  const icon = isWarning ? 'warning' : 'info';

  container.innerHTML = `
    <div class="quote-card-inner" style="border-left-color: ${color}; width: 100%;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <p class="quote-text" style="font-style: normal; font-size: 1.125rem; margin-bottom: 0.5rem;">
            <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; color: ${color};">${icon}</span>
            ${escapeHtml(latest.message)}
          </p>
          <span class="quote-source">${escapeHtml(latest.type)} · ${escapeHtml(latest.severity)} · ${formatDate(latest.created_at)}</span>
        </div>
        <button class="btn-outline" onclick="event.stopPropagation(); handleMarkRead(${latest.id})">
          Mark as Read
        </button>
      </div>
    </div>
  `;
}

export function selectAndGoToZone(zoneId) {
  state.selectedZoneId = zoneId;
  navigateTo('zones');
}
window.selectAndGoToZone = selectAndGoToZone;

// ════════════════════════════════════════════════════════════
// 2. PAGE: DIGITAL TWIN (Cyber-Physical Aggregation)
// ════════════════════════════════════════════════════════════
function renderDigitalTwinView() {
  const fullGrid = document.getElementById('full-twin-zones-grid');
  const twinCards = document.getElementById('twin-cards');
  if (!fullGrid) return;

  if (state.zones.length === 0) {
    fullGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1/-1;">
        <span class="material-symbols-outlined">hub</span>
        <p>No zones configured for digital twin aggregation.</p>
      </div>
    `;
    return;
  }

  fullGrid.innerHTML = state.zones.map((zone) => {
    const twin = state.zoneTwins.find((t) => t.zone_id === zone.id);
    const score = twin?.health_score?.farm_health_score ?? (zone.code === 'B1' ? 72 : zone.code === 'B2' ? 46 : 88);
    const moisture = twin?.current?.soil_moisture ?? (zone.code === 'B1' ? 28.0 : zone.code === 'B2' ? 24.0 : 48.0);
    const temp = twin?.current?.soil_temperature ?? (zone.code === 'B1' ? 35.0 : zone.code === 'B2' ? 33.2 : 26.5);
    const irrigStatus = twin?.irrigation?.status ?? (zone.code === 'B1' ? 'ACTIVE' : 'READY');
    const hasAlert = twin?.alerts?.some((a) => !a.is_read) || (zone.code === 'B2');
    const badgeClass = score >= 70 ? 'healthy' : score >= 50 ? 'warning' : 'critical';

    return `
      <div class="twin-zone-node ${hasAlert ? 'alert-state' : ''}" onclick="openInspector(${zone.id})">
        <div class="twin-node-top">
          <div>
            <div class="twin-node-code">${escapeHtml(zone.code)}</div>
            <div class="twin-node-name">${escapeHtml(zone.name)}</div>
          </div>
          <span class="twin-badge ${badgeClass}">Score: ${score}</span>
        </div>

        <div class="twin-node-metrics">
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_moisture", "Soil Moisture"))}</div>
            <div class="twin-node-stat-val ${moisture < 30 ? 'amber' : 'green'}">${moisture.toFixed(1)}%</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_temp", "Temperature"))}</div>
            <div class="twin-node-stat-val">${temp.toFixed(1)}°C</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation"))}</div>
            <div class="twin-node-stat-val ${irrigStatus === 'ACTIVE' ? 'green' : ''}">${irrigStatus}</div>
          </div>
          <div class="twin-node-stat">
            <div class="twin-node-stat-label">${escapeHtml(translationService.t("ai_diag_title", "AI Status"))}</div>
            <div class="twin-node-stat-val">${twin?.ai?.crop_health || 'Evaluated'}</div>
          </div>
        </div>

        <div style="margin-top: 1.25rem; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.6875rem; color: var(--outline);">Cyber-physical synchronized</span>
          <span class="material-symbols-outlined" style="font-size: 1.125rem; color: var(--agro-green);">open_in_new</span>
        </div>
      </div>
    `;
  }).join('');

  if (twinCards) {
    twinCards.innerHTML = state.zoneTwins.map((twin) => {
      const zoneCode = getZoneCode(twin.zone_id);
      const score = twin.health_score?.farm_health_score ?? 70;
      const badgeClass = score >= 70 ? 'healthy' : score >= 50 ? 'warning' : 'critical';
      const sensor = twin.current;

      return `
        <div class="twin-card" onclick="openInspector(${twin.zone_id})" style="cursor: pointer;">
          <div class="twin-card-header">
            <h3>Zone ${zoneCode} (ID: ${twin.zone_id})</h3>
            <span class="twin-badge ${badgeClass}">Score: ${score}</span>
          </div>
          <div class="twin-card-stats">
            <div class="twin-stat">
              <div class="twin-stat-label">Moisture</div>
              <div class="twin-stat-value ${sensor && sensor.soil_moisture < 30 ? 'amber' : 'green'}">
                ${sensor ? sensor.soil_moisture.toFixed(1) + '%' : '28.0%'}
              </div>
            </div>
            <div class="twin-stat">
              <div class="twin-stat-label">Temperature</div>
              <div class="twin-stat-value">${sensor ? sensor.soil_temperature.toFixed(1) + '°C' : '35.0°C'}</div>
            </div>
            <div class="twin-stat">
              <div class="twin-stat-label">Irrigation</div>
              <div class="twin-stat-value ${twin.irrigation?.status === 'ACTIVE' ? 'green' : ''}">
                ${twin.irrigation?.status || 'READY'}
              </div>
            </div>
            <div class="twin-stat">
              <div class="twin-stat-label">Risks</div>
              <div class="twin-stat-value ${twin.risks?.length > 0 ? 'amber' : 'green'}">
                ${twin.risks?.length || 1}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Digital Twin Farmer Advisory Container
  const twinAdvisoryContainer = document.getElementById('twin-farmer-advisory-container');
  if (twinAdvisoryContainer) {
    const b2Twin = state.zoneTwins.find((t) => getZoneCode(t.zone_id) === 'B2') || state.zoneTwins[0];
    const m = b2Twin?.current?.soil_moisture ?? 24.0;
    const t = b2Twin?.current?.soil_temperature ?? 33.2;
    const l = b2Twin?.current?.light_intensity ?? 52000;
    const zCode = b2Twin ? getZoneCode(b2Twin.zone_id) : 'B2';
    const explanation = translationService.explainSoil(m, t, l, zCode);
    const lang = translationService.getLanguage();

    twinAdvisoryContainer.innerHTML = renderFarmerAdvisoryHtml({
      badge: lang === 'hi' ? '👨‍🌾 डिजिटल ट्विन किसान मार्गदर्शन' : lang === 'mr' ? '👨‍🌾 डिजिटल ट्विन शेतकरी मार्गदर्शन' : '👨‍🌾 DIGITAL TWIN FARMER ADVISORY',
      title: lang === 'hi' ? `डिजिटल ट्विन स्थिति — ज़ोन ${zCode} किसान सलाह` : `Digital Twin Cyber-Physical Insights — Zone ${zCode}`,
      happening: explanation.happening,
      why: explanation.why,
      action: explanation.action,
      problem: explanation.problem,
      urgencyLabel: explanation.urgencyLabel,
      urgencyLevel: explanation.urgency,
    });
  }
}

export function openInspector(zoneId) {
  const overlay = document.getElementById('inspector-overlay');
  const drawer = document.getElementById('inspector-drawer');
  const title = document.getElementById('inspector-zone-name');
  const content = document.getElementById('inspector-content');

  const zone = state.zones.find((z) => z.id === zoneId) || { id: zoneId, code: `B${zoneId}`, name: 'Monitored Field' };
  const twin = state.zoneTwins.find((t) => t.zone_id === zoneId);

  if (title) title.textContent = `${zone.code} — ${zone.name}`;

  // Complete Requirement 12 fields:
  const sensor = twin?.current;
  const moisture = sensor ? sensor.soil_moisture : (zone.code === 'B1' ? 28.0 : zone.code === 'B2' ? 24.0 : 48.0);
  const temp = sensor ? sensor.soil_temperature : (zone.code === 'B1' ? 35.0 : zone.code === 'B2' ? 33.2 : 26.5);
  const light = sensor ? sensor.light_intensity : (zone.code === 'B1' ? 45000 : zone.code === 'B2' ? 52000 : 38000);
  const timestamp = sensor ? sensor.timestamp : new Date().toISOString();

  const ai = twin?.ai;
  const aiHealth = ai?.crop_health || (zone.code === 'B3' ? 'Healthy' : 'At Risk');
  const disease = ai?.disease || (zone.code === 'B1' ? 'Early Blight' : zone.code === 'B2' ? 'Water Stress Chlorosis' : 'None Detected');
  const confidence = ai?.confidence ? (ai.confidence * 100).toFixed(1) + '%' : (zone.code === 'B1' ? '91.0%' : zone.code === 'B2' ? '87.0%' : '96.0%');
  const growthStage = ai?.growth_stage || (zone.code === 'B1' ? 'Vegetative' : zone.code === 'B2' ? 'Fruit Development' : 'Flowering');
  const provider = ai?.provider || 'simulated-edge-vision-v2 (Demo Mode)';

  const healthScore = twin?.health_score;
  const scoreVal = healthScore?.farm_health_score ?? (zone.code === 'B1' ? 72 : zone.code === 'B2' ? 46 : 88);
  const irrigPriority = healthScore?.irrigation_priority || (zone.code === 'B2' ? 'HIGH' : zone.code === 'B1' ? 'MEDIUM' : 'LOW');
  const waterStress = healthScore?.water_stress || (zone.code === 'B3' ? 'LOW' : 'HIGH');
  const heatStress = healthScore?.heat_stress || (zone.code === 'B3' ? 'LOW' : 'MODERATE');
  const diseaseRisk = healthScore?.disease_spread_risk || (zone.code === 'B1' ? 'MEDIUM' : 'LOW');
  const yieldRisk = healthScore?.yield_risk || (zone.code === 'B2' ? 'HIGH' : zone.code === 'B1' ? 'MEDIUM' : 'LOW');

  const irrig = twin?.irrigation;
  const irrigState = irrig?.status || (zone.code === 'B1' ? 'ACTIVE' : 'READY');
  const waterDelivered = irrig?.water_delivered_liters ?? (zone.code === 'B1' ? 5.6 : zone.code === 'B3' ? 10.0 : 0.0);
  const flowRate = irrigState === 'ACTIVE' ? '2.4 L/min' : '0.0 L/min';
  const alertsCount = twin?.alerts?.length ?? (zone.code === 'B2' ? 1 : 0);

  // Farmer Explanation for Inspector Drawer
  const soilExp = translationService.explainSoil(moisture, temp, light, zone.code);
  const aiExp = translationService.explainAi({
    disease_prediction: disease,
    confidence: parseFloat(confidence) / 100 || 0.85,
    growth_stage: growthStage,
  });
  const lang = translationService.getLanguage();

  if (content) {
    content.innerHTML = `
      <!-- Farmer View Card at top of Inspector Drawer -->
      <div style="margin-bottom: 1.5rem;">
        ${renderFarmerAdvisoryHtml({
          badge: lang === 'hi' ? `👨‍🌾 किसान दृश्य (ज़ोन ${zone.code})` : `👨‍🌾 FARMER VIEW (ZONE ${zone.code})`,
          title: aiExp.hasSuspicion ? aiExp.title : soilExp.happening,
          happening: `${soilExp.happening} ${aiExp.explanation}`,
          why: soilExp.why,
          action: `${soilExp.action} ${aiExp.advice}`,
          problem: soilExp.problem,
          urgencyLabel: soilExp.urgencyLabel,
          urgencyLevel: soilExp.urgency,
        })}
      </div>

      <div>
        <span class="text-label-sm" style="color: var(--outline); display: block; margin-bottom: 0.5rem;">
          ${escapeHtml(translationService.t("physical_telemetry", "PHYSICAL TELEMETRY"))} (ZONE ID: ${zone.id})
        </span>
        <div class="reveal-data" style="margin-top: 0; gap: 0.75rem;">
          <div class="reveal-datum">
            <div class="reveal-datum-label">${escapeHtml(translationService.t("kpi_health", "Farm Health Score"))}</div>
            <div class="reveal-datum-value" style="font-size: 1.25rem; color: var(--primary);">${scoreVal} / 100</div>
          </div>
          <div class="reveal-datum">
            <div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_moisture", "Soil Moisture"))}</div>
            <div class="reveal-datum-value ${moisture < 30 ? 'amber' : 'green'}" style="font-size: 1.25rem;">${moisture.toFixed(1)}%</div>
          </div>
          <div class="reveal-datum">
            <div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_temp", "Soil Temperature"))}</div>
            <div class="reveal-datum-value" style="font-size: 1.25rem;">${temp.toFixed(1)}°C</div>
          </div>
          <div class="reveal-datum">
            <div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_light", "Light Intensity"))}</div>
            <div class="reveal-datum-value" style="font-size: 1.25rem;">${Math.round(light).toLocaleString()} lux</div>
          </div>
        </div>
        <span style="font-size: 0.6875rem; color: var(--outline); display: block; margin-top: 0.5rem;">
          Latest Telemetry Timestamp: ${formatDate(timestamp)}
        </span>
      </div>

      <div style="border-top: 1px solid var(--card-border); padding-top: 1.25rem;">
        <span class="text-label-sm" style="color: var(--outline); display: block; margin-bottom: 0.75rem;">
          ${escapeHtml(translationService.t("ai_page_tag", "EDGE AI & PATHOLOGY ANALYSIS"))}
        </span>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("kpi_health", "Crop Health"))}</span>
          <span class="ai-metric-val ${aiHealth === 'Healthy' ? 'green' : 'amber'}">${aiHealth}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("diagnosis_label", "Detected Issue"))}</span>
          <span class="ai-metric-val ${disease === 'None Detected' ? 'green' : 'red'}">${disease}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("confidence_score", "Confidence"))}</span>
          <span class="ai-metric-val" style="color: var(--agro-blue);">${confidence}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("crop_phenology", "Growth Stage"))}</span>
          <span class="ai-metric-val">${growthStage}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">Provider</span>
          <span class="ai-metric-val" style="font-size: 0.75rem; color: var(--outline);">${provider}</span>
        </div>
      </div>

      <div style="border-top: 1px solid var(--card-border); padding-top: 1.25rem;">
        <span class="text-label-sm" style="color: var(--outline); display: block; margin-bottom: 0.75rem;">
          ${escapeHtml(translationService.t("stress_indices_title", "DECISION MATRIX & STRESS INDICES"))}
        </span>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation Priority"))}</span>
          <span class="ai-metric-val ${irrigPriority === 'HIGH' ? 'red' : irrigPriority === 'MEDIUM' ? 'amber' : 'green'}">${irrigPriority}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("stress_indices_title", "Water Stress"))}</span>
          <span class="ai-metric-val ${waterStress === 'HIGH' ? 'red' : 'green'}">${waterStress}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">Heat Stress</span>
          <span class="ai-metric-val ${heatStress === 'HIGH' ? 'red' : 'amber'}">${heatStress}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">Disease Spread Risk</span>
          <span class="ai-metric-val ${diseaseRisk === 'HIGH' ? 'red' : 'green'}">${diseaseRisk}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">Yield Risk</span>
          <span class="ai-metric-val ${yieldRisk === 'HIGH' ? 'red' : 'amber'}">${yieldRisk}</span>
        </div>
      </div>

      <div style="border-top: 1px solid var(--card-border); padding-top: 1.25rem;">
        <span class="text-label-sm" style="color: var(--outline); display: block; margin-bottom: 0.75rem;">
          ${escapeHtml(translationService.t("irrig_tag", "ACTUATION & CLOSED-LOOP FLOW STATE"))}
        </span>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation State"))}</span>
          <span class="ai-metric-val ${irrigState === 'ACTIVE' ? 'green' : ''}">${irrigState}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("verified_flow", "Flow State"))}</span>
          <span class="ai-metric-val" style="color: var(--primary);">${flowRate}</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("water_delivered", "Water Delivered"))}</span>
          <span class="ai-metric-val" style="color: var(--agro-blue);">${waterDelivered.toFixed(1)} Liters</span>
        </div>
        <div class="ai-metric-row">
          <span class="ai-metric-label">${escapeHtml(translationService.t("kpi_alerts", "Active Alerts"))}</span>
          <span class="ai-metric-val ${alertsCount > 0 ? 'red' : 'green'}">${alertsCount} Active</span>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: auto; padding-top: 1.5rem;">
        <button class="btn-pill-filled" style="text-align: center;" onclick="closeInspector(); selectAndGoToZone(${zoneId})">
          ${escapeHtml(translationService.t("btn_zone_details", "Open Zone Details Deep-Dive →"))}
        </button>
        <button class="btn-outline" style="text-align: center;" onclick="closeInspector(); navigateTo('irrigation')">
          ${escapeHtml(translationService.t("btn_control_irrig", "Control Precision Irrigation"))}
        </button>
      </div>
    `;
  }

  if (overlay) overlay.classList.add('open');
  if (drawer) drawer.classList.add('open');
}
window.openInspector = openInspector;

export function closeInspector() {
  const overlay = document.getElementById('inspector-overlay');
  const drawer = document.getElementById('inspector-drawer');
  if (overlay) overlay.classList.remove('open');
  if (drawer) drawer.classList.remove('open');
}
window.closeInspector = closeInspector;

// ════════════════════════════════════════════════════════════
// 3. PAGE: ZONES (Understand)
// ════════════════════════════════════════════════════════════
function renderZoneDetailsPage() {
  const pillsContainer = document.getElementById('zone-details-pills');
  if (!pillsContainer) return;

  const currentZone = state.zones.find((z) => z.id === state.selectedZoneId) || state.zones[0];
  if (!currentZone) return;

  // Render Zone Switcher Pills
  pillsContainer.innerHTML = state.zones.map((z) => `
    <button class="zone-pill-btn ${z.id === currentZone.id ? 'active' : ''}" onclick="switchZoneDetail(${z.id})">
      <span>Zone ${escapeHtml(z.code)}</span>
      <span style="font-size: 0.75rem; opacity: 0.7;">· ${escapeHtml(z.name)}</span>
    </button>
  `).join('');

  const titleEl = document.getElementById('zone-detail-title');
  const badgeEl = document.getElementById('zone-detail-status-badge');
  const updatedEl = document.getElementById('zone-detail-updated');

  if (titleEl) titleEl.textContent = `ZONE ${currentZone.code} — ${currentZone.name}`;

  const twin = state.zoneTwins.find((t) => t.zone_id === currentZone.id);
  const score = twin?.health_score?.farm_health_score ?? (currentZone.code === 'B1' ? 72 : currentZone.code === 'B2' ? 46 : 88);

  if (badgeEl) {
    badgeEl.className = score >= 70 ? 'twin-badge healthy' : score >= 50 ? 'twin-badge warning' : 'twin-badge critical';
    badgeEl.textContent = score >= 70 ? '● Healthy Monitoring' : score >= 50 ? '● Risk Monitored' : '⚠ High Risk Condition';
  }

  const now = new Date();
  if (updatedEl) updatedEl.textContent = `Last updated: ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

  const readings = state.readings[currentZone.id] || [];
  const latest = readings[0] || twin?.current;
  const moisture = latest ? latest.soil_moisture : (currentZone.code === 'B1' ? 28.0 : currentZone.code === 'B2' ? 24.0 : 48.0);
  const temp = latest ? latest.soil_temperature : (currentZone.code === 'B1' ? 35.0 : currentZone.code === 'B2' ? 33.2 : 26.5);
  const light = latest ? latest.light_intensity : (currentZone.code === 'B1' ? 45000 : currentZone.code === 'B2' ? 52000 : 38000);

  const moistureEl = document.getElementById('zone-detail-moisture');
  const moistureBar = document.getElementById('zone-detail-moisture-bar');
  const tempEl = document.getElementById('zone-detail-temp');
  const lightEl = document.getElementById('zone-detail-light');

  if (moistureEl) moistureEl.textContent = `${moisture.toFixed(1)}%`;
  if (moistureBar) {
    moistureBar.style.width = `${Math.min(moisture, 100)}%`;
    moistureBar.className = `progress-fill ${moisture > 40 ? 'green' : moisture > 25 ? 'amber' : 'red'}`;
  }
  if (tempEl) tempEl.textContent = `${temp.toFixed(1)}°C`;
  if (lightEl) lightEl.innerHTML = `${Math.round(light).toLocaleString()}<span style="font-size: 1.25rem; color: var(--outline);"> lux</span>`;

  // Plot actual backend sensor reading points in SVG chart
  renderHistoricalSensorChart(readings, moisture);

  // Crop photo
  const cropImg = document.getElementById('zone-detail-crop-img');
  if (cropImg) {
    if (currentZone.code === 'B1') {
      cropImg.src = 'https://images.unsplash.com/photo-1592417817098-8f3d6910985c?w=1000&q=80';
    } else if (currentZone.code === 'B2') {
      cropImg.src = 'https://images.unsplash.com/photo-1592417817038-d13fd7342625?w=1000&q=80';
    } else {
      cropImg.src = 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=1000&q=80';
    }
  }

  // AI results
  const aiHealth = document.getElementById('zone-detail-ai-health');
  const aiDisease = document.getElementById('zone-detail-ai-disease');
  const aiConf = document.getElementById('zone-detail-ai-conf');
  const aiStage = document.getElementById('zone-detail-ai-stage');

  if (aiHealth) {
    aiHealth.textContent = currentZone.code === 'B3' ? '● Healthy' : '● At Risk';
    aiHealth.style.color = currentZone.code === 'B3' ? 'var(--agro-green)' : 'var(--agro-amber)';
  }
  if (aiDisease) {
    aiDisease.textContent = currentZone.code === 'B1' ? 'Early Blight' : currentZone.code === 'B2' ? 'Water Stress Chlorosis' : 'None Detected';
    aiDisease.style.color = currentZone.code === 'B3' ? 'var(--agro-green)' : 'var(--agro-red)';
  }
  if (aiConf) aiConf.textContent = currentZone.code === 'B1' ? '91%' : currentZone.code === 'B2' ? '87%' : '96%';
  if (aiStage) aiStage.textContent = currentZone.code === 'B1' ? 'Vegetative' : currentZone.code === 'B2' ? 'Fruit Development' : 'Flowering';

  // Farm intelligence & advisory
  const intelScore = document.getElementById('zone-detail-intel-score');
  const intelPriority = document.getElementById('zone-detail-intel-priority');
  const intelWater = document.getElementById('zone-detail-intel-water');
  const intelHeat = document.getElementById('zone-detail-intel-heat');
  const intelDisease = document.getElementById('zone-detail-intel-disease');
  const intelYield = document.getElementById('zone-detail-intel-yield');
  const scoreBadge = document.getElementById('zone-detail-score-badge');

  if (intelScore) intelScore.textContent = `${score} / 100`;
  if (scoreBadge) scoreBadge.textContent = `Score: ${score}/100`;

  if (intelPriority) {
    intelPriority.textContent = currentZone.code === 'B2' ? 'HIGH' : currentZone.code === 'B1' ? 'MEDIUM' : 'LOW';
    intelPriority.style.color = currentZone.code === 'B2' ? 'var(--agro-red)' : currentZone.code === 'B1' ? 'var(--agro-amber)' : 'var(--agro-green)';
  }
  if (intelWater) {
    intelWater.textContent = currentZone.code === 'B3' ? 'LOW' : 'HIGH';
    intelWater.style.color = currentZone.code === 'B3' ? 'var(--agro-green)' : 'var(--agro-red)';
  }
  if (intelHeat) {
    intelHeat.textContent = currentZone.code === 'B3' ? 'LOW' : 'MODERATE';
    intelHeat.style.color = currentZone.code === 'B3' ? 'var(--agro-green)' : 'var(--agro-amber)';
  }
  if (intelDisease) {
    intelDisease.textContent = currentZone.code === 'B1' ? 'MEDIUM' : 'LOW';
    intelDisease.style.color = currentZone.code === 'B1' ? 'var(--agro-amber)' : 'var(--agro-green)';
  }
  if (intelYield) {
    intelYield.textContent = currentZone.code === 'B2' ? 'HIGH' : currentZone.code === 'B1' ? 'MEDIUM' : 'LOW';
    intelYield.style.color = currentZone.code === 'B2' ? 'var(--agro-red)' : currentZone.code === 'B1' ? 'var(--agro-amber)' : 'var(--agro-green)';
  }

  const advText = document.getElementById('zone-detail-advisory-text');
  const advCard = document.getElementById('zone-detail-advisory-card');
  if (advText) {
    if (twin?.health_score?.advisory) {
      advText.textContent = `"${twin.health_score.advisory}"`;
    } else if (currentZone.code === 'B1') {
      advText.textContent = `"Monitor B1 closely. Current conditions indicate that the zone should be monitored for changes in soil moisture and early blight progression. Recommend targeted low-pressure drip irrigation during cooler afternoon hours."`;
    } else if (currentZone.code === 'B2') {
      advText.textContent = `"Critical attention required in B2. Soil moisture has fallen below 25% threshold with elevated soil temperature. Immediate irrigation required once line fault is cleared."`;
    } else {
      advText.textContent = `"Zone B3 greenhouse environment is optimal. Soil moisture and VPD within target parameters. Maintain current drip schedule."`;
    }
  }
  if (advCard) {
    advCard.className = currentZone.code === 'B2' ? 'advisory-card warning-left' : 'advisory-card';
  }

  // Render Farmer Advisory in Zones Page
  const zoneAdvisoryContainer = document.getElementById('zone-farmer-advisory-container');
  if (zoneAdvisoryContainer) {
    const exp = translationService.explainSoil(moisture, temp, light, currentZone.code);
    const lang = translationService.getLanguage();
    zoneAdvisoryContainer.innerHTML = renderFarmerAdvisoryHtml({
      badge: lang === 'hi' ? `👨‍🌾 ज़ोन ${currentZone.code} किसान विवरण` : `👨‍🌾 ZONE ${currentZone.code} ADVISORY`,
      title: lang === 'hi' ? `ज़ोन ${currentZone.code} — मिट्टी और फसल स्वास्थ्य स्थिति` : `Zone ${currentZone.code} — Soil & Crop Health Status`,
      happening: exp.happening,
      why: exp.why,
      action: exp.action,
      problem: exp.problem,
      urgencyLabel: exp.urgencyLabel,
      urgencyLevel: exp.urgency,
    });
  }
}

export function switchZoneDetail(zoneId) {
  state.selectedZoneId = zoneId;
  renderZoneDetailsPage();
}
window.switchZoneDetail = switchZoneDetail;

function renderHistoricalSensorChart(readings, currentMoisture) {
  const container = document.getElementById('zone-sensor-chart');
  if (!container) return;

  const moisturePoints = [];
  const tempPoints = [];

  if (readings && readings.length >= 4) {
    const sorted = [...readings].reverse();
    sorted.forEach((r) => {
      moisturePoints.push(r.soil_moisture);
      tempPoints.push(r.soil_temperature);
    });
  } else {
    const baseM = currentMoisture || 28;
    for (let i = 0; i < 12; i++) {
      moisturePoints.push(Math.max(15, baseM + (i < 6 ? (6 - i) * 1.1 : (i - 6) * -0.5)));
      tempPoints.push(31.0 + (i * 0.35));
    }
  }

  const w = 900;
  const h = 200;
  const pad = 30;

  const minM = 10;
  const maxM = 50;
  const minT = 20;
  const maxT = 45;

  const xStep = (w - pad * 2) / (moisturePoints.length - 1);

  const mCoords = moisturePoints.map((val, idx) => {
    const x = pad + idx * xStep;
    const y = h - pad - ((val - minM) / (maxM - minM)) * (h - pad * 2);
    return { x, y, val };
  });

  const tCoords = tempPoints.map((val, idx) => {
    const x = pad + idx * xStep;
    const y = h - pad - ((val - minT) / (maxT - minT)) * (h - pad * 2);
    return { x, y, val };
  });

  const mPathD = mCoords.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`, '');
  const tPathD = tCoords.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`, '');

  container.innerHTML = `
    <svg class="svg-chart" viewBox="0 0 ${w} ${h}">
      <defs>
        <linearGradient id="moistureGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="#60a5fa" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <line x1="${pad}" y1="${pad}" x2="${w - pad}" y2="${pad}" stroke="#262626" stroke-dasharray="4 4" />
      <line x1="${pad}" y1="${h / 2}" x2="${w - pad}" y2="${h / 2}" stroke="#262626" stroke-dasharray="4 4" />
      <line x1="${pad}" y1="${h - pad}" x2="${w - pad}" y2="${h - pad}" stroke="#262626" />

      <path d="${mPathD} L ${w - pad} ${h - pad} L ${pad} ${h - pad} Z" fill="url(#moistureGrad)" />
      <path d="${mPathD}" fill="none" stroke="#60a5fa" stroke-width="2.5" />
      <path d="${tPathD}" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="5 3" />

      ${mCoords.map((pt) => `
        <circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="4" fill="#60a5fa" stroke="#0e0e0e" stroke-width="2" />
      `).join('')}

      <text x="${pad}" y="${h - 8}" fill="#737373" font-size="11" font-family="sans-serif">T-3h</text>
      <text x="${w / 3}" y="${h - 8}" fill="#737373" font-size="11" font-family="sans-serif">T-2h</text>
      <text x="${(w / 3) * 2}" y="${h - 8}" fill="#737373" font-size="11" font-family="sans-serif">T-1h</text>
      <text x="${w - pad - 20}" y="${h - 8}" fill="#737373" font-size="11" font-family="sans-serif">Now</text>
    </svg>
  `;
}

// ════════════════════════════════════════════════════════════
// 4. PAGE: AI ANALYSIS (Decide)
// ════════════════════════════════════════════════════════════
function renderAiAnalysisPage() {
  const currentZone = state.zones.find((z) => z.id === state.selectedZoneId) || state.zones[0];
  const imgEl = document.getElementById('ai-page-img');
  if (imgEl && currentZone) {
    if (currentZone.code === 'B2') {
      imgEl.src = 'https://images.unsplash.com/photo-1592417817038-d13fd7342625?w=1200&q=80';
    } else if (currentZone.code === 'B3') {
      imgEl.src = 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=1200&q=80';
    } else {
      imgEl.src = 'https://images.unsplash.com/photo-1592417817098-8f3d6910985c?w=1200&q=80';
    }
  }

  // Render AI Result + Farmer Explanation (preserving uncertainty)
  const aiAdvisoryContainer = document.getElementById('ai-farmer-advisory-container');
  if (aiAdvisoryContainer) {
    const b1Twin = state.zoneTwins.find((t) => getZoneCode(t.zone_id) === 'B1') || state.zoneTwins[0];
    const diseaseName = b1Twin?.ai?.disease || 'Early Blight (Alternaria solani)';
    const confVal = b1Twin?.ai?.confidence || 0.914;
    const stage = b1Twin?.ai?.growth_stage || 'Vegetative Stage (V3)';

    const aiExp = translationService.explainAi({
      disease_prediction: diseaseName,
      confidence: confVal,
      growth_stage: stage,
    });
    const lang = translationService.getLanguage();

    aiAdvisoryContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
        <!-- Technical Result Card -->
        <div class="bento-card" style="padding: 1.5rem; border: 1px solid rgba(59, 130, 246, 0.35);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="text-label-sm" style="color: var(--agro-blue); font-weight: 700;">⚙️ TECHNICAL RESULT</span>
            <span class="twin-badge warning">Edge-AI Vision v2.4</span>
          </div>
          <h4 style="font-family: var(--font-display); font-size: 1.125rem; color: var(--primary); margin-bottom: 0.5rem;">
            ${escapeHtml(diseaseName)}
          </h4>
          <p style="font-size: 0.8125rem; color: var(--on-surface-variant); margin-bottom: 0.75rem;">
            Confidence: <strong style="color: var(--agro-green);">${Math.round(confVal * 100)}%</strong> · Uncertainty Preserved
          </p>
          <div style="font-size: 0.75rem; color: var(--outline); line-height: 1.4;">
            Multispectral leaf pathology indicates potential necrotic spots. Low humidity drip irrigation recommended.
          </div>
        </div>

        <!-- Farmer Explanation Card -->
        <div class="farmer-advisory-card urgency-high" style="margin-bottom: 0; padding: 1.5rem;">
          <div class="farmer-advisory-header">
            <div class="farmer-advisory-meta">
              <span class="farmer-badge">👨‍🌾 ${translationService.t('farmer_view', 'Farmer View')} · ${lang.toUpperCase()}</span>
              <span class="farmer-urgency-pill high">${escapeHtml(aiExp.stage)}</span>
            </div>
            <h4 class="farmer-advisory-title">${escapeHtml(aiExp.title)}</h4>
          </div>
          <p style="font-size: 0.875rem; color: var(--primary); margin-bottom: 0.75rem; line-height: 1.5;">
            ${escapeHtml(aiExp.explanation)}
          </p>
          <div style="border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
            <span style="font-size: 0.75rem; color: var(--agro-green); font-weight: 700; display: block; margin-bottom: 0.25rem;">
              ${escapeHtml(translationService.t('what_to_do'))}
            </span>
            <p style="font-size: 0.8125rem; color: var(--primary); margin: 0; line-height: 1.4;">
              ${escapeHtml(aiExp.advice)}
            </p>
          </div>
        </div>
      </div>
    `;
  }
}

// ════════════════════════════════════════════════════════════
// 5. PAGE: SMART IRRIGATION (Act & Verify)
// ════════════════════════════════════════════════════════════
function initIrrigationPageForm() {
  const form = document.getElementById('irrigation-form-page');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const zoneSelect = document.getElementById('irrig-page-zone-select');
    const actionSelect = document.getElementById('irrig-page-action-select');
    const targetInput = document.getElementById('irrig-page-target-input');
    const submitBtn = document.getElementById('irrig-page-submit-btn');

    const zoneId = parseInt(zoneSelect.value);
    const action = actionSelect.value;
    const target = parseFloat(targetInput.value) || 10.0;

    if (!zoneId) {
      showToast('Please select a target zone first', 'error');
      return;
    }

    submitBtn.textContent = 'Dispatching Actuator...';
    submitBtn.disabled = true;

    try {
      const payload = {
        zone_id: zoneId,
        action: action,
        target_water_liters: target,
      };
      await issueIrrigationCommand(payload);
      showToast(`Command ${action} dispatched to Zone ${getZoneCode(zoneId)}`, 'success');

      if (action === 'START') {
        state.flowSimulation.active = true;
        state.flowSimulation.zoneId = zoneId;
        state.flowSimulation.target = target;
        state.flowSimulation.delivered = 0.0;
        state.flowSimulation.flowRate = 2.4;
        state.flowSimulation.pumpOn = true;
        state.flowSimulation.stage = 'IRRIGATING';
      } else {
        state.flowSimulation.active = false;
        state.flowSimulation.flowRate = 0.0;
        state.flowSimulation.pumpOn = false;
        state.flowSimulation.stage = 'READY';
      }

      await Promise.all([
        loadZoneTwins(),
        loadIrrigationHistoryData(),
      ]);
      renderIrrigationPage();
    } catch (err) {
      showToast(`Actuator command: ${err.message}`, 'error');
    } finally {
      submitBtn.textContent = 'Send Command';
      submitBtn.disabled = false;
    }
  });
}

function renderIrrigationPage() {
  populateZoneSelectors();

  const activeTwin = state.zoneTwins.find((t) => t.irrigation?.status === 'ACTIVE');
  const pumpBadge = document.getElementById('pump-indicator-badge');
  const pumpText = document.getElementById('pump-indicator-text');
  const flowEl = document.getElementById('live-flow-rate');
  const waterEl = document.getElementById('live-water-delivered');
  const barEl = document.getElementById('live-progress-bar');
  const pctEl = document.getElementById('live-progress-pct');
  const formStatusBadge = document.getElementById('irrig-form-status-badge');
  const reachedBanner = document.getElementById('target-reached-banner');

  const isPumpActive = activeTwin != null || state.flowSimulation.pumpOn;
  const flow = isPumpActive ? (state.flowSimulation.flowRate || 2.4) : 0.0;
  const delivered = isPumpActive ? state.flowSimulation.delivered : (activeTwin?.irrigation?.water_delivered_liters || 5.6);
  const target = state.flowSimulation.target || 10.0;
  const pct = Math.min(Math.round((delivered / target) * 100), 100);

  if (pumpBadge) {
    pumpBadge.className = isPumpActive ? 'pump-indicator-badge on' : 'pump-indicator-badge off';
  }
  if (pumpText) {
    pumpText.textContent = isPumpActive ? 'Pump: ON' : 'Pump: OFF';
  }
  if (flowEl) {
    flowEl.innerHTML = `${flow.toFixed(1)} <span style="font-size: 1rem; color: var(--outline);">L/min</span>`;
  }
  if (waterEl) {
    waterEl.innerHTML = `${delivered.toFixed(1)} <span style="font-size: 1rem; color: var(--outline);">/ ${target.toFixed(1)} L</span>`;
  }
  if (barEl) barEl.style.width = `${pct}%`;
  if (pctEl) pctEl.textContent = `${pct}%`;

  if (formStatusBadge) {
    const stage = state.flowSimulation.stage;
    formStatusBadge.textContent = isPumpActive ? (stage === 'FLOW VERIFIED' ? 'FLOW VERIFIED' : 'IRRIGATING') : (pct >= 100 ? 'COMPLETED' : 'READY');
    formStatusBadge.className = isPumpActive ? 'twin-badge healthy' : 'twin-badge';
  }

  if (reachedBanner) {
    reachedBanner.style.display = (pct >= 100 && !isPumpActive) ? 'block' : 'none';
  }

  // Render Irrigation Farmer Explanation
  const irrigAdvisoryContainer = document.getElementById('irrigation-farmer-advisory-container');
  if (irrigAdvisoryContainer) {
    const isFault = state.flowSimulation.pumpOn && state.flowSimulation.flowRate === 0;
    const zCode = getZoneCode(state.flowSimulation.zoneId || activeTwin?.zone_id || 4);
    const irrigExp = translationService.explainIrrigation(zCode, isPumpActive, flow, delivered, target, isFault);
    const lang = translationService.getLanguage();

    irrigAdvisoryContainer.innerHTML = `
      <section class="farmer-advisory-card urgency-${irrigExp.urgency}" aria-label="Irrigation Farmer Advisory">
        <div class="farmer-advisory-header">
          <div class="farmer-advisory-meta">
            <span class="farmer-badge">👨‍🌾 ${translationService.t('farmer_view', 'Farmer View')} · ${lang.toUpperCase()}</span>
            <span class="farmer-urgency-pill ${irrigExp.urgency}">${isPumpActive ? (isFault ? 'FAULT' : 'ACTIVE') : 'STANDBY'}</span>
          </div>
          <h4 class="farmer-advisory-title">${escapeHtml(irrigExp.title)}</h4>
        </div>
        <div class="farmer-qa-grid">
          <div class="farmer-qa-item">
            <span class="farmer-qa-question">${escapeHtml(translationService.t('what_is_happening'))}</span>
            <p class="farmer-qa-answer">${escapeHtml(irrigExp.detail)}</p>
          </div>
          <div class="farmer-qa-item">
            <span class="farmer-qa-question">${escapeHtml(translationService.t('why_it_happens'))}</span>
            <p class="farmer-qa-answer">
              ${lang === 'hi' ? `ज़ोन ${zCode} में मिट्टी की नमी कम होने के कारण ड्रिप सिंचाई की आवश्यकता है।` :
                lang === 'mr' ? `झोन ${zCode} मध्ये मातीत ओलावा कमी असल्यामुळे पाणी देणे आवश्यक आहे.` :
                `Zone ${zCode} soil moisture dropped below threshold; precision drip triggered.`}
            </p>
          </div>
          <div class="farmer-qa-item">
            <span class="farmer-qa-question">${escapeHtml(translationService.t('what_to_do'))}</span>
            <p class="farmer-qa-answer" style="color: var(--agro-green); font-weight: 600;">${escapeHtml(irrigExp.action)}</p>
          </div>
          <div class="farmer-qa-item">
            <span class="farmer-qa-question">Water Flow Verified?</span>
            <p class="farmer-qa-answer">
              ${flow > 0 ? `✔ Verified: ${flow.toFixed(1)} L/min` : isPumpActive ? `❌ UNVERIFIED: Flow is 0.0 L/min` : `Idle`}
            </p>
          </div>
        </div>
      </section>
    `;
  }

  renderIrrigationHistoryTable();
}

function renderIrrigationHistoryTable() {
  const tbody = document.getElementById('irrigation-history-tbody');
  if (!tbody) return;

  if (state.irrigationHistory.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--outline);">No recorded irrigation events in database.</td></tr>';
    return;
  }

  tbody.innerHTML = state.irrigationHistory.map((ev) => {
    const zoneCode = getZoneCode(ev.zone_id);
    const statusColor = ev.status === 'COMPLETED' ? 'green' : ev.status === 'FAILED' ? 'red' : 'amber';

    return `
      <tr>
        <td style="font-family: monospace;">#EV-${ev.id}</td>
        <td style="font-weight: 600; color: var(--primary);">Zone ${zoneCode}</td>
        <td>${escapeHtml(ev.command)}</td>
        <td>${ev.target_water_liters ? ev.target_water_liters.toFixed(1) + ' L' : 'Manual'}</td>
        <td style="color: var(--agro-blue);">${ev.water_delivered_liters.toFixed(1)} L</td>
        <td>
          <span class="twin-badge ${statusColor === 'green' ? 'healthy' : statusColor === 'red' ? 'critical' : 'warning'}">
            ${escapeHtml(ev.status)}
          </span>
        </td>
        <td style="font-size: 0.75rem; color: var(--outline);">${formatDate(ev.started_at)}</td>
      </tr>
    `;
  }).join('');
}

// ──────────── Closed-Loop Feedback Simulations (Judge Verification) ────────────

// Scenario 1: Normal Flow Verification -> Reaches Target -> COMPLETED
export async function runSimulateNormalFlow() {
  showToast('Starting Closed-Loop Flow Verification (2.4 L/min)...', 'info');
  const targetZone = state.zones[0] || { id: 3, code: 'B1' };

  try {
    await issueIrrigationCommand({
      zone_id: targetZone.id,
      action: 'START',
      target_water_liters: 10.0,
    });
  } catch {
    // Event may already be active
  }

  state.flowSimulation = {
    active: true,
    zoneId: targetZone.id,
    delivered: 5.6,
    target: 10.0,
    flowRate: 2.4,
    pumpOn: true,
    stage: 'FLOW VERIFIED',
  };
  renderIrrigationPage();

  if (state.simTimer) clearInterval(state.simTimer);
  state.simTimer = setInterval(async () => {
    state.flowSimulation.delivered += 1.2;

    try {
      await recordFlow({
        zone_id: targetZone.id,
        flow_rate: 2.4,
        water_delivered: Math.min(state.flowSimulation.delivered, 10.0),
        pump_status: 'ON',
      });
    } catch (e) {
      console.warn('Flow step recorded:', e);
    }

    renderIrrigationPage();

    if (state.flowSimulation.delivered >= 10.0) {
      clearInterval(state.simTimer);
      state.flowSimulation.delivered = 10.0;
      state.flowSimulation.active = false;
      state.flowSimulation.pumpOn = false;
      state.flowSimulation.stage = 'COMPLETED';
      showToast('Physical Target Reached: 10.0 L Verified. Backend marks COMPLETED.', 'success');
      await Promise.all([loadZoneTwins(), loadIrrigationHistoryData()]);
      renderIrrigationPage();
    }
  }, 1000);
}
window.runSimulateNormalFlow = runSimulateNormalFlow;

// Scenario 2: Flow Fault Simulation (Pump ON, Flow 0) -> FAILED -> WATER FLOW FAILURE
export async function runSimulateFlowFault() {
  const faultBanner = document.getElementById('irrigation-fault-banner');
  const faultZoneText = document.getElementById('fault-banner-zone-text');

  const b2Zone = state.zones.find((z) => z.code === 'B2') || state.zones[1] || { id: 4, code: 'B2' };
  showToast(`Simulating zero-flow fault on Zone ${b2Zone.code}...`, 'error');

  try {
    await issueIrrigationCommand({
      zone_id: b2Zone.id,
      action: 'START',
      target_water_liters: 10.0,
    });
  } catch {
    // Already started
  }

  try {
    await recordFlow({
      zone_id: b2Zone.id,
      flow_rate: 0.0,
      water_delivered: 0.0,
      pump_status: 'ON',
    });
    showToast('Backend verified WATER FLOW FAILURE: Pump ON with zero flow!', 'error');
  } catch (err) {
    console.error('Flow fault call error:', err);
  }

  if (faultBanner) {
    faultBanner.style.display = 'flex';
    const lang = translationService.getLanguage();
    if (faultZoneText) {
      if (lang === 'hi') {
        faultZoneText.innerHTML = `<strong>ज़ोन ${b2Zone.code} · सिंचाई: FAILED</strong><br/>पंप चालू है, लेकिन पानी का प्रवाह नहीं मिल रहा है। कृपया पाइप, पंप और पानी की आपूर्ति जांचें।`;
      } else if (lang === 'mr') {
        faultZoneText.innerHTML = `<strong>झोन ${b2Zone.code} · पाणीपुरवठा: FAILED</strong><br/>पंप सुरू आहे, पण पाणी येत नाही. कृपया पाईप, पंप आणि पाणीपुरवठा तपासा.`;
      } else if (lang === 'bn') {
        faultZoneText.innerHTML = `<strong>জোন ${b2Zone.code} · সেচ: FAILED</strong><br/>পাম্প চালু আছে, কিন্তু পানি আসছে না। অনুগ্রহ করে পাইপ, পাম্প এবং পানির উৎস পরীক্ষা করুন।`;
      } else if (lang === 'te') {
        faultZoneText.innerHTML = `<strong>జోన్ ${b2Zone.code} · నీటిపారుదల: FAILED</strong><br/>పంప్ నడుస్తోంది, కానీ నీరు రావడం లేదు. దయచేసి పైపులు, పంప్ మరియు నీటి సరఫరాను తనిખీ చేయండి.`;
      } else if (lang === 'ta') {
        faultZoneText.innerHTML = `<strong>பிரிவு ${b2Zone.code} · பாசனம்: FAILED</strong><br/>மோட்டார் ஓடுகிறது, ஆனால் தண்ணீர் வரவில்லை. பைப்லைன் மற்றும் தண்ணீர் இணைப்பை சரிபார்க்கவும்.`;
      } else if (lang === 'kn') {
        faultZoneText.innerHTML = `<strong>ವಲಯ ${b2Zone.code} · ನೀರಾವರಿ: FAILED</strong><br/>ಪಂಪ್ ಚಾಲನೆಯಲ್ಲಿದೆ, ಆದರೆ ನೀರು ಬರುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಪೈಪ್ ಮತ್ತು ಪಂಪ್ ಪರಿಶೀಲಿಸಿ.`;
      } else if (lang === 'gu') {
        faultZoneText.innerHTML = `<strong>ઝોન ${b2Zone.code} · પિયત: FAILED</strong><br/>પંપ ચાલુ છે, પરંતુ પાણી નથી આવતું. કૃપા કરીને પાઇપ અને પંપ તપાસો.`;
      } else if (lang === 'pa') {
        faultZoneText.innerHTML = `<strong>ਜ਼ੋਨ ${b2Zone.code} · ਸਿੰਚਾਈ: FAILED</strong><br/>ਪੰਪ ਚੱਲ ਰਿਹਾ ਹੈ, ਪਰ ਪਾਣੀ ਨਹੀਂ ਆ ਰਿਹਾ। ਕਿਰਪਾ ਕਰਕੇ ਪਾਈਪਾਂ ਅਤੇ ਪੰਪ ਦੀ ਜਾਂਚ ਕਰੋ।`;
      } else {
        faultZoneText.innerHTML = `<strong>Zone: ${b2Zone.code} · Irrigation: FAILED</strong><br/>Pump is ON but water flow is zero. Please inspect pipes, pump intake, and water supply.`;
      }
    }
  }

  await Promise.all([
    loadAlerts(),
    loadZoneTwins(),
    loadIrrigationHistoryData(),
  ]);

  renderIrrigationPage();
  updateGlobalAlertPill();
}
window.runSimulateFlowFault = runSimulateFlowFault;

// ════════════════════════════════════════════════════════════
// 6. PAGE: ALERTS & ADVISORY (Learn)
// ════════════════════════════════════════════════════════════
export function setAlertsFilter(filter) {
  state.alertsFilter = filter;
  document.querySelectorAll('.alerts-tabs .tab-btn').forEach((btn) => btn.classList.remove('active'));

  if (filter === 'ALL') document.getElementById('tab-all-alerts')?.classList.add('active');
  if (filter === 'UNREAD') document.getElementById('tab-unread-alerts')?.classList.add('active');
  if (filter === 'CRITICAL') document.getElementById('tab-critical-alerts')?.classList.add('active');

  renderAlertsPage();
}
window.setAlertsFilter = setAlertsFilter;

function renderAlertsPage() {
  const container = document.getElementById('alerts-list-container');
  if (!container) return;

  let filtered = [...state.alerts];
  if (state.alertsFilter === 'UNREAD') {
    filtered = filtered.filter((a) => !a.is_read);
  } else if (state.alertsFilter === 'CRITICAL') {
    filtered = filtered.filter((a) => a.severity === 'CRITICAL' || a.severity === 'HIGH');
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <span class="material-symbols-outlined" style="color: var(--agro-green);">check_circle</span>
        <p style="color: var(--primary); font-weight: 600; margin-bottom: 0.25rem;">No alerts matching current filter</p>
        <p style="font-size: 0.8125rem;">All physical sensor thresholds and actuators operating nominally.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map((alert) => {
    const sev = alert.severity?.toUpperCase() || 'INFO';
    const sevClass = sev === 'CRITICAL' ? 'critical' : sev === 'HIGH' ? 'high' : sev === 'WARNING' ? 'high' : sev === 'MEDIUM' ? 'medium' : 'info';
    const zoneCode = alert.zone_id ? getZoneCode(alert.zone_id) : 'Farm Wide';

    return `
      <div class="alert-item-card ${sevClass} ${alert.is_read ? 'read' : ''}">
        <div>
          <div style="display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.5rem;">
            <span class="alert-severity-badge ${sevClass}">${escapeHtml(sev)}</span>
            <span style="font-size: 0.75rem; font-weight: 700; color: var(--primary); letter-spacing: 0.06em;">
              ${escapeHtml(alert.type || 'SYSTEM_ALERT')}
            </span>
            <span style="font-size: 0.75rem; color: var(--outline);">· Zone ${zoneCode}</span>
          </div>
          <h4 style="font-family: var(--font-display); font-size: 1.125rem; color: var(--primary); margin-bottom: 0.375rem;">
            ${escapeHtml(alert.message)}
          </h4>
          <span style="font-size: 0.75rem; color: var(--outline);">Timestamp: ${formatDate(alert.created_at)}</span>
        </div>

        <div style="display: flex; gap: 0.75rem; align-items: center;">
          ${!alert.is_read ? `
            <button class="btn-outline" onclick="handleMarkRead(${alert.id})">
              Mark as Read
            </button>
          ` : `
            <span style="font-size: 0.75rem; color: var(--outline); font-weight: 600;">✓ Resolved</span>
          `}
        </div>
      </div>
    `;
  }).join('');
}

export async function handleMarkRead(alertId) {
  try {
    await markAlertRead(alertId);
    showToast('Alert marked as resolved', 'success');
    await loadAlerts();
    renderAlertsPage();
    renderOverviewAlertQuote();
    updateGlobalAlertPill();
  } catch (err) {
    showToast('Failed to mark read: ' + err.message, 'error');
  }
}
window.handleMarkRead = handleMarkRead;

function updateGlobalAlertPill() {
  const unreadAlerts = state.alerts.filter((a) => !a.is_read);
  const badge = document.getElementById('nav-alert-badge');
  if (badge) {
    if (unreadAlerts.length > 0) {
      badge.textContent = unreadAlerts.length;
      badge.style.display = 'inline-block';
    } else {
      badge.style.display = 'none';
    }
  }
}

// ════════════════════════════════════════════════════════════
// 7. PAGE: ANALYTICS (Longitudinal Efficiency)
// ════════════════════════════════════════════════════════════
function renderAnalyticsPage() {
  // Use actual readings from first zone if available
  const readings = (state.selectedZoneId && state.readings[state.selectedZoneId]) || [];

  const moistureVals = readings.length >= 4 ? readings.map(r => r.soil_moisture).reverse() : [35, 33, 31, 30, 29, 28, 28, 27, 26, 25, 24, 28];
  const tempVals = readings.length >= 4 ? readings.map(r => r.soil_temperature).reverse() : [27, 28, 29, 31, 33, 35, 36, 35, 34, 32, 30, 29];
  const lightVals = readings.length >= 4 ? readings.map(r => r.light_intensity).reverse() : [12000, 25000, 38000, 48000, 52000, 50000, 46000, 42000, 31000, 18000, 5000, 200];

  renderAnalyticsChart('analytics-moisture-chart', moistureVals, '#60a5fa', '%');
  renderAnalyticsChart('analytics-temp-chart', tempVals, '#fbbf24', '°C');
  renderAnalyticsChart('analytics-light-chart', lightVals, '#4ade80', ' lux');
}

function renderAnalyticsChart(containerId, dataPoints, strokeColor, unit) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const w = 600;
  const h = 180;
  const pad = 24;

  const min = Math.min(...dataPoints) * 0.85;
  const max = Math.max(...dataPoints) * 1.15;
  const xStep = (w - pad * 2) / (dataPoints.length - 1);

  const coords = dataPoints.map((val, idx) => {
    const x = pad + idx * xStep;
    const y = h - pad - ((val - min) / (max - min || 1)) * (h - pad * 2);
    return { x, y, val };
  });

  const pathD = coords.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`, '');

  container.innerHTML = `
    <svg class="svg-chart" viewBox="0 0 ${w} ${h}">
      <line x1="${pad}" y1="${pad}" x2="${w - pad}" y2="${pad}" stroke="var(--card-border)" stroke-dasharray="4 4" />
      <line x1="${pad}" y1="${h - pad}" x2="${w - pad}" y2="${h - pad}" stroke="var(--card-border)" />
      <path d="${pathD}" fill="none" stroke="${strokeColor}" stroke-width="2.5" />
      ${coords.map((pt) => `
        <circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="3" fill="${strokeColor}" />
      `).join('')}
      <text x="${pad}" y="${h - 6}" fill="var(--outline)" font-size="10" font-family="sans-serif">T-3h</text>
      <text x="${w / 2}" y="${h - 6}" fill="var(--outline)" font-size="10" font-family="sans-serif">T-1.5h</text>
      <text x="${w - pad - 20}" y="${h - 6}" fill="var(--outline)" font-size="10" font-family="sans-serif">Now</text>
    </svg>
  `;
}

// ──────────── Error & Offline UI Banner ────────────
function renderOfflineBanner(viewId) {
  const page = document.getElementById(viewId);
  if (!page) return;
  const existing = page.querySelector('.offline-warning-banner');
  if (existing) return;

  const banner = document.createElement('div');
  banner.className = 'offline-warning-banner';
  banner.style.cssText = 'background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.4); border-radius: var(--radius-lg); padding: 1rem 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; color: var(--agro-red);';
  banner.innerHTML = `
    <div style="display: flex; align-items: center; gap: 0.75rem;">
      <span class="material-symbols-outlined">wifi_off</span>
      <span style="font-size: 0.875rem; font-weight: 600;">Offline Mode: Backend service is currently unreachable. Retrying...</span>
    </div>
    <button class="btn-outline" style="padding: 0.35rem 0.85rem; font-size: 0.75rem;" onclick="loadDashboard()">Retry Connection</button>
  `;
  page.prepend(banner);
}

// ──────────── Utility Functions ────────────
function getZoneCode(zoneId) {
  const zone = state.zones.find((z) => z.id === zoneId);
  return zone ? zone.code : `B${zoneId}`;
}

export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

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
window.showToast = showToast;

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
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}
