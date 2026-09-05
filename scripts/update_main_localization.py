# -*- coding: utf-8 -*-
"""
AgroVisor Edge — Update main.js with dynamic localization
"""

def update_main():
    path = r'frontend/src/main.js'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update handleLanguageChange & updateLanguageUI
    old_handle = '''export function handleLanguageChange(langCode) {
  translationService.setLanguage(langCode);
  updateLanguageUI();
  renderCurrentView();
  const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === langCode);
  showToast(`Language switched to ${langObj?.nativeName || langCode}`, 'info');
}'''

    new_handle = '''export function handleLanguageChange(langCode) {
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
}'''

    if old_handle in content:
        content = content.replace(old_handle, new_handle, 1)

    old_init = '''function initLanguageAndViews() {
  updateLanguageUI();
  updateViewModeUI();

  translationService.subscribe(() => {
    updateLanguageUI();
    updateViewModeUI();
  });
}'''

    new_init = '''function initLanguageAndViews() {
  translationService.applyLanguageToDom();
  updateLanguageUI();
  updateViewModeUI();

  translationService.subscribe(() => {
    translationService.applyLanguageToDom();
    updateLanguageUI();
    updateViewModeUI();
  });
}'''

    if old_init in content:
        content = content.replace(old_init, new_init, 1)

    old_update_ui = '''function updateLanguageUI() {
  const lang = translationService.getLanguage();
  const select = document.getElementById('language-selector');
  if (select && select.value !== lang) {
    select.value = lang;
  }'''

    new_update_ui = '''function updateLanguageUI() {
  const lang = translationService.getLanguage();
  translationService.applyLanguageToDom();
  const select = document.getElementById('language-selector');
  if (select && select.value !== lang) {
    select.value = lang;
  }'''

    if old_update_ui in content:
        content = content.replace(old_update_ui, new_update_ui, 1)

    # 2. Localize Overview twin map node labels
    content = content.replace(
        '<div class="twin-node-stat-label">Moisture</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_moisture", "Moisture"))}</div>'
    )
    content = content.replace(
        '<div class="twin-node-stat-label">Temperature</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_temp", "Temperature"))}</div>'
    )
    content = content.replace(
        '<div class="twin-node-stat-label">Irrigation</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation"))}</div>'
    )
    content = content.replace(
        '<div class="twin-node-stat-label">Alerts</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("kpi_alerts", "Alerts"))}</div>'
    )
    content = content.replace(
        'Inspect Zone Details →',
        '${escapeHtml(translationService.t("btn_zone_details", "Inspect Zone Details →"))}'
    )

    # 3. Localize Digital Twin node stats
    content = content.replace(
        '<div class="twin-node-stat-label">Soil Moisture</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("sensor_moisture", "Soil Moisture"))}</div>'
    )
    content = content.replace(
        '<div class="twin-node-stat-label">AI Status</div>',
        '<div class="twin-node-stat-label">${escapeHtml(translationService.t("ai_diag_title", "AI Status"))}</div>'
    )

    # 4. Localize Inspector drawer headers & metrics
    content = content.replace(
        'PHYSICAL TELEMETRY (ZONE ID: ${zone.id})',
        '${escapeHtml(translationService.t("physical_telemetry", "PHYSICAL TELEMETRY"))} (ZONE ID: ${zone.id})'
    )
    content = content.replace(
        '<div class="reveal-datum-label">Farm Health Score</div>',
        '<div class="reveal-datum-label">${escapeHtml(translationService.t("kpi_health", "Farm Health Score"))}</div>'
    )
    content = content.replace(
        '<div class="reveal-datum-label">Soil Moisture</div>',
        '<div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_moisture", "Soil Moisture"))}</div>'
    )
    content = content.replace(
        '<div class="reveal-datum-label">Soil Temperature</div>',
        '<div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_temp", "Soil Temperature"))}</div>'
    )
    content = content.replace(
        '<div class="reveal-datum-label">Light Intensity</div>',
        '<div class="reveal-datum-label">${escapeHtml(translationService.t("sensor_light", "Light Intensity"))}</div>'
    )
    content = content.replace(
        'EDGE AI & PATHOLOGY ANALYSIS',
        '${escapeHtml(translationService.t("ai_page_tag", "EDGE AI & PATHOLOGY ANALYSIS"))}'
    )
    content = content.replace(
        'DECISION MATRIX & STRESS INDICES',
        '${escapeHtml(translationService.t("stress_indices_title", "DECISION MATRIX & STRESS INDICES"))}'
    )
    content = content.replace(
        'ACTUATION & CLOSED-LOOP FLOW STATE',
        '${escapeHtml(translationService.t("irrig_tag", "ACTUATION & CLOSED-LOOP FLOW STATE"))}'
    )
    content = content.replace(
        '<span class="ai-metric-label">Crop Health</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("kpi_health", "Crop Health"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Detected Issue</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("diagnosis_label", "Detected Issue"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Confidence</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("confidence_score", "Confidence"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Growth Stage</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("crop_phenology", "Growth Stage"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Irrigation Priority</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation Priority"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Water Stress</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("stress_indices_title", "Water Stress"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Irrigation State</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("kpi_irrig", "Irrigation State"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Flow State</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("verified_flow", "Flow State"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Water Delivered</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("water_delivered", "Water Delivered"))}</span>'
    )
    content = content.replace(
        '<span class="ai-metric-label">Active Alerts</span>',
        '<span class="ai-metric-label">${escapeHtml(translationService.t("kpi_alerts", "Active Alerts"))}</span>'
    )
    content = content.replace(
        'Open Zone Details Deep-Dive →',
        '${escapeHtml(translationService.t("btn_zone_details", "Open Zone Details Deep-Dive →"))}'
    )
    content = content.replace(
        'Control Precision Irrigation',
        '${escapeHtml(translationService.t("btn_control_irrig", "Control Precision Irrigation"))}'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated main.js with comprehensive localization calls")

if __name__ == '__main__':
    update_main()
