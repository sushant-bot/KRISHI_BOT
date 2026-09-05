# -*- coding: utf-8 -*-
"""
AgroVisor Edge — Injects data-i18n tags into index.html
"""

import sys

def inject_tags():
    path = r'frontend/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    replacements = [
        # Brand
        ('<span class="brand-title">AGROVISOR EDGE</span>', '<span class="brand-title" data-i18n="brand_title">AGROVISOR EDGE</span>'),
        ('<span class="brand-subtitle">FARM INTELLIGENCE SYSTEM</span>', '<span class="brand-subtitle" data-i18n="brand_subtitle">FARM INTELLIGENCE SYSTEM</span>'),
        ('<span>Rover: Demo</span>', '<span data-i18n="rover_status">Rover: Demo</span>'),
        ('<span style="color: var(--agro-green); font-weight: 600;">System Online</span>', '<span data-i18n="system_online" style="color: var(--agro-green); font-weight: 600;">System Online</span>'),
        ('<span style="color: var(--outline);">· Nashik Agro Valley, Maharashtra</span>', '<span data-i18n="location_tag" style="color: var(--outline);">· Nashik Agro Valley, Maharashtra</span>'),

        # Hero
        ('MOBILE EDGE-AI FARM INTELLIGENCE & PRECISION IRRIGATION\n          </span>', 'MOBILE EDGE-AI FARM INTELLIGENCE & PRECISION IRRIGATION\n          </span>\n<!-- i18n tag will be on parent -->'),
        ('<span class="text-label-sm" style="color: var(--agro-green); letter-spacing: 0.12em; display: block; margin-bottom: 0.75rem;">\n            MOBILE EDGE-AI FARM INTELLIGENCE & PRECISION IRRIGATION\n          </span>',
         '<span class="text-label-sm" data-i18n="hero_tag" style="color: var(--agro-green); letter-spacing: 0.12em; display: block; margin-bottom: 0.75rem;">MOBILE EDGE-AI FARM INTELLIGENCE & PRECISION IRRIGATION</span>'),
        ('<h1 class="text-display-xl animate-in" style="font-size: 3.5rem; margin-bottom: 1rem;">\n            AgroVisor Edge\n          </h1>',
         '<h1 class="text-display-xl animate-in" data-i18n="hero_title" style="font-size: 3.5rem; margin-bottom: 1rem;">AgroVisor Edge</h1>'),
        ('<p class="text-body-lg animate-in animate-delay-1" style="max-width: 38rem; margin-bottom: 2rem;">\n            Autonomous crop monitoring, edge vision diagnosis, closed-loop irrigation verification, and cyber-physical Digital Twin aggregation.\n          </p>',
         '<p class="text-body-lg animate-in animate-delay-1" data-i18n="hero_desc" style="max-width: 38rem; margin-bottom: 2rem;">Autonomous crop monitoring, edge vision diagnosis, closed-loop irrigation verification, and cyber-physical Digital Twin aggregation.</p>'),
        ('<button class="btn-pill-filled" onclick="document.getElementById(\'operational-overview\').scrollIntoView({behavior:\'smooth\'})">\n              Enter Dashboard\n            </button>',
         '<button class="btn-pill-filled" data-i18n="hero_enter" onclick="document.getElementById(\'operational-overview\').scrollIntoView({behavior:\'smooth\'})">Enter Dashboard</button>'),
        ('<button class="btn-outline" onclick="navigateTo(\'digital-twin\')">\n              Open Digital Twin\n            </button>',
         '<button class="btn-outline" data-i18n="hero_open_twin" onclick="navigateTo(\'digital-twin\')">Open Digital Twin</button>'),

        # Overview Header
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              AGROVISOR EDGE · FARM INTELLIGENCE PLATFORM\n            </span>',
         '<span class="text-label-sm" data-i18n="platform_subtitle" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">AGROVISOR EDGE · FARM INTELLIGENCE PLATFORM</span>'),
        ('<button class="btn-outline" onclick="loadDashboard()">\n              <span class="material-symbols-outlined" style="font-size: 0.875rem; vertical-align: middle; margin-right: 0.25rem;">refresh</span>\n              Sync Farm Data\n            </button>',
         '<button class="btn-outline" data-i18n-html="btn_sync_data" onclick="loadDashboard()"><span class="material-symbols-outlined" style="font-size: 0.875rem; vertical-align: middle; margin-right: 0.25rem;">refresh</span>Sync Farm Data</button>'),
        ('<button class="btn-pill-filled" onclick="navigateTo(\'irrigation\')">\n              Control Irrigation\n            </button>',
         '<button class="btn-pill-filled" data-i18n="btn_control_irrig" onclick="navigateTo(\'irrigation\')">Control Irrigation</button>'),

        # KPIs
        ('<span>Farm Health</span>', '<span data-i18n="kpi_health">Farm Health</span>'),
        ('<span class="twin-badge healthy" style="padding: 0.1rem 0.5rem;">Optimal Target</span>', '<span class="twin-badge healthy" data-i18n="kpi_health_opt" style="padding: 0.1rem 0.5rem;">Optimal Target</span>'),
        ('<span>Zones</span>', '<span data-i18n="kpi_zones">Zones</span>'),
        ('<span style="color: var(--agro-green);">● All Monitored</span>', '<span data-i18n="kpi_zones_all" style="color: var(--agro-green);">● All Monitored</span>'),
        ('<span>Water Used</span>', '<span data-i18n="kpi_water">Water Used</span>'),
        ('<span>Delivered Today</span>', '<span data-i18n="kpi_water_today">Delivered Today</span>'),
        ('<span>Alerts</span>\n              <span class="material-symbols-outlined" style="font-size: 1rem; color: var(--agro-amber);">warning</span>',
         '<span data-i18n="kpi_alerts">Alerts</span>\n              <span class="material-symbols-outlined" style="font-size: 1rem; color: var(--agro-amber);">warning</span>'),
        ('<span style="color: var(--agro-amber);">⚠ High Severity</span>', '<span data-i18n="kpi_alerts_high" style="color: var(--agro-amber);">⚠ High Severity</span>'),
        ('<span>Irrigation</span>\n              <span class="material-symbols-outlined" style="font-size: 1rem; color: var(--agro-green);">valve</span>',
         '<span data-i18n="kpi_irrig">Irrigation</span>\n              <span class="material-symbols-outlined" style="font-size: 1rem; color: var(--agro-green);">valve</span>'),

        # Overview sections
        ('<h3>Digital Twin Topology</h3>', '<h3 data-i18n="sec_twin_topology">Digital Twin Topology</h3>'),
        ('<p>Real-time physical spatial state across monitored zones.</p>', '<p data-i18n="sec_twin_desc">Real-time physical spatial state across monitored zones.</p>'),
        ('<h3>Farm Overview & Micro-Climate Summary</h3>', '<h3 data-i18n="sec_farm_summary">Farm Overview & Micro-Climate Summary</h3>'),
        ('<p>High-density agronomic sensor telemetry aggregated across edge gateways.</p>', '<p data-i18n="sec_farm_desc">High-density agronomic sensor telemetry aggregated across edge gateways.</p>'),
        ('<h3>Recent Critical Incidents</h3>', '<h3 data-i18n="sec_recent_alerts">Recent Critical Incidents</h3>'),
        ('<button class="btn-outline" onclick="navigateTo(\'alerts\')">\n              View All Alerts →\n            </button>',
         '<button class="btn-outline" data-i18n="view_all_alerts" onclick="navigateTo(\'alerts\')">View All Alerts →</button>'),

        # Digital Twin View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              CYBER-PHYSICAL MODEL\n            </span>',
         '<span class="text-label-sm" data-i18n="twin_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">CYBER-PHYSICAL MODEL</span>'),
        ('<h2>Autonomous Zone Topology</h2>', '<h2 data-i18n="twin_title">Autonomous Zone Topology</h2>'),
        ('<p>Real-time sensor telemetry and Edge-AI predictions aggregated into digital twins.</p>', '<p data-i18n="twin_desc">Real-time sensor telemetry and Edge-AI predictions aggregated into digital twins.</p>'),
        ('<span class="text-label-sm" style="color: var(--outline);">Click zone card to open Inspector Drawer</span>', '<span class="text-label-sm" data-i18n="twin_click_hint" style="color: var(--outline);">Click zone card to open Inspector Drawer</span>'),

        # Zones View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              MICRO-CLIMATE TELEMETRY\n            </span>',
         '<span class="text-label-sm" data-i18n="zones_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">MICRO-CLIMATE TELEMETRY</span>'),
        ('<h2>Zone Diagnostics & Telemetry</h2>', '<h2 data-i18n="zones_title">Zone Diagnostics & Telemetry</h2>'),
        ('<p>Comprehensive sensor history, crop visual inspection, and automated agronomic recommendations.</p>', '<p data-i18n="zones_desc">Comprehensive sensor history, crop visual inspection, and automated agronomic recommendations.</p>'),
        ('<h4>Soil Moisture</h4>', '<h4 data-i18n="sensor_moisture">Soil Moisture</h4>'),
        ('<h4>Soil Temperature</h4>', '<h4 data-i18n="sensor_temp">Soil Temperature</h4>'),
        ('<h4>Light Intensity</h4>', '<h4 data-i18n="sensor_light">Light Intensity</h4>'),
        ('<h3>Historic Sensor Readings (Last 4 Hours)</h3>', '<h3 data-i18n="chart_title">Historic Sensor Readings (Last 4 Hours)</h3>'),
        ('<p>Dynamic soil moisture (%) and temperature (°C) trends captured by edge gateway.</p>', '<p data-i18n="chart_desc">Dynamic soil moisture (%) and temperature (°C) trends captured by edge gateway.</p>'),
        ('<h3>High-Resolution Foliar Capture</h3>', '<h3 data-i18n="crop_photo_title">High-Resolution Foliar Capture</h3>'),
        ('<p>Edge camera frame synchronized with telemetry.</p>', '<p data-i18n="crop_photo_desc">Edge camera frame synchronized with telemetry.</p>'),
        ('<h4>AI Pathology Assessment</h4>', '<h4 data-i18n="ai_diag_title">AI Pathology Assessment</h4>'),
        ('<h4>Agronomic Stress Indices</h4>', '<h4 data-i18n="stress_indices_title">Agronomic Stress Indices</h4>'),
        ('<h4>Autonomous Decision & Expert Advisory</h4>', '<h4 data-i18n="decision_advisory_title">Autonomous Decision & Expert Advisory</h4>'),

        # AI Analysis View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              COMPUTER VISION & LEAF PATHOLOGY\n            </span>',
         '<span class="text-label-sm" data-i18n="ai_page_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">COMPUTER VISION & LEAF PATHOLOGY</span>'),
        ('<h2>AI Crop Vision Diagnosis</h2>', '<h2 data-i18n="ai_page_title">AI Crop Vision Diagnosis</h2>'),
        ('<p>High-resolution optical scans processed by on-farm Edge-AI models for early disease detection, foliar stress, and phenological stage tracking.</p>',
         '<p data-i18n="ai_page_desc">High-resolution optical scans processed by on-farm Edge-AI models for early disease detection, foliar stress, and phenological stage tracking.</p>'),
        ('<span class="ai-pill-tag simulated">Demo Simulation Provider Active</span>', '<span class="ai-pill-tag simulated" data-i18n="demo_provider_tag">Demo Simulation Provider Active</span>'),
        ('<h3 style="font-family: var(--font-display); font-size: 1.5rem; color: var(--primary); margin-bottom: 0.75rem;">\n                Pathological Assessment\n              </h3>',
         '<h3 data-i18n="pathology_assessment" style="font-family: var(--font-display); font-size: 1.5rem; color: var(--primary); margin-bottom: 0.75rem;">Pathological Assessment</h3>'),
        ('<span class="ai-metric-label">Diagnosis</span>', '<span class="ai-metric-label" data-i18n="diagnosis_label">Diagnosis</span>'),
        ('<span class="ai-metric-label">Confidence Score</span>', '<span class="ai-metric-label" data-i18n="confidence_score">Confidence Score</span>'),
        ('<span class="ai-metric-label">Crop Phenology</span>', '<span class="ai-metric-label" data-i18n="crop_phenology">Crop Phenology</span>'),
        ('<span class="ai-metric-label">Canopy Coverage</span>', '<span class="ai-metric-label" data-i18n="canopy_coverage">Canopy Coverage</span>'),
        ('<span class="ai-metric-label">Recommended Action</span>', '<span class="ai-metric-label" data-i18n="recommended_action">Recommended Action</span>'),
        ('<button class="btn-pill-filled" style="width: 100%; text-align: center;" onclick="navigateTo(\'irrigation\')">\n                Proceed to Precision Irrigation →\n              </button>',
         '<button class="btn-pill-filled" data-i18n="btn_proceed_irrig" style="width: 100%; text-align: center;" onclick="navigateTo(\'irrigation\')">Proceed to Precision Irrigation →</button>'),

        # Smart Irrigation View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              ACTUATION & PHYSICAL FEEDBACK\n            </span>',
         '<span class="text-label-sm" data-i18n="irrig_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">ACTUATION & PHYSICAL FEEDBACK</span>'),
        ('<h2>Irrigation Control Center</h2>', '<h2 data-i18n="irrig_title">Irrigation Control Center</h2>'),
        ('<p>Target volume dispatch, real-time solenoid valve actuation, and closed-loop flow meter verification.</p>',
         '<p data-i18n="irrig_desc">Target volume dispatch, real-time solenoid valve actuation, and closed-loop flow meter verification.</p>'),
        ('<span style="font-weight: 700; color: var(--primary); font-size: 0.9375rem; display: block;">\n                JUDGE DEMONSTRATION: Physical Flow Feedback Loop\n              </span>',
         '<span data-i18n="judge_demo_title" style="font-weight: 700; color: var(--primary); font-size: 0.9375rem; display: block;">JUDGE DEMONSTRATION: Physical Flow Feedback Loop</span>'),
        ('<span style="font-size: 0.75rem; color: var(--on-surface-variant);">\n                Simulate real physical responses from the edge flow meter to test target completion vs fault alert generation.\n              </span>',
         '<span data-i18n="judge_demo_desc" style="font-size: 0.75rem; color: var(--on-surface-variant);">Simulate real physical responses from the edge flow meter to test target completion vs fault alert generation.</span>'),
        ('<button id="btn-sim-normal" class="btn-sim-success" onclick="runSimulateNormalFlow()">\n              <span class="material-symbols-outlined" style="font-size: 1rem;">water_drop</span>\n              ▶ Simulate Normal Flow (2.4 L/min)\n            </button>',
         '<button id="btn-sim-normal" class="btn-sim-success" data-i18n="btn_sim_normal" onclick="runSimulateNormalFlow()">▶ Simulate Normal Flow (2.4 L/min)</button>'),
        ('<button id="btn-sim-fault" class="btn-sim-fault" onclick="runSimulateFlowFault()">\n              <span class="material-symbols-outlined" style="font-size: 1rem;">error</span>\n              ⚠ Simulate Flow Fault (Pump ON, Flow 0)\n            </button>',
         '<button id="btn-sim-fault" class="btn-sim-fault" data-i18n="btn_sim_fault" onclick="runSimulateFlowFault()">⚠ Simulate Flow Fault (Pump ON, Flow 0)</button>'),
        ('<h3 style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Dispatch Command</h3>',
         '<h3 data-i18n="dispatch_command" style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Dispatch Command</h3>'),
        ('<label class="form-label" for="irrig-page-zone-select">Target Zone</label>',
         '<label class="form-label" data-i18n="target_zone" for="irrig-page-zone-select">Target Zone</label>'),
        ('<label class="form-label" for="irrig-page-action-select">Command Action</label>',
         '<label class="form-label" data-i18n="command_action" for="irrig-page-action-select">Command Action</label>'),
        ('<label class="form-label" for="irrig-page-target-input">Target Volume (Liters)</label>',
         '<label class="form-label" data-i18n="target_volume" for="irrig-page-target-input">Target Volume (Liters)</label>'),
        ('<button type="submit" id="irrig-page-submit-btn" class="btn-pill-filled" style="width: 100%;">\n                Send Command\n              </button>',
         '<button type="submit" id="irrig-page-submit-btn" class="btn-pill-filled" data-i18n="btn_send_command" style="width: 100%;">Send Command</button>'),
        ('<h3 style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Live Actuator Feedback</h3>',
         '<h3 data-i18n="live_feedback" style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Live Actuator Feedback</h3>'),
        ('<span class="text-label-sm" style="color: var(--outline);">Pump Status</span>',
         '<span class="text-label-sm" data-i18n="pump_status" style="color: var(--outline);">Pump Status</span>'),
        ('<span class="text-label-sm" style="color: var(--outline);">Verified Flow Rate</span>',
         '<span class="text-label-sm" data-i18n="verified_flow" style="color: var(--outline);">Verified Flow Rate</span>'),
        ('<span class="text-label-sm" style="color: var(--outline);">Water Delivered</span>',
         '<span class="text-label-sm" data-i18n="water_delivered" style="color: var(--outline);">Water Delivered</span>'),
        ('<span class="text-label-sm" style="color: var(--outline);">Target Progress</span>',
         '<span class="text-label-sm" data-i18n="target_progress" style="color: var(--outline);">Target Progress</span>'),
        ('<h3 style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Closed-Loop Actuation History</h3>',
         '<h3 data-i18n="actuation_history" style="font-family: var(--font-display); font-size: 1.25rem; color: var(--primary);">Closed-Loop Actuation History</h3>'),
        ('<th>Event ID</th>', '<th data-i18n="th_event_id">Event ID</th>'),
        ('<th>Zone</th>', '<th data-i18n="th_zone">Zone</th>'),
        ('<th>Command</th>', '<th data-i18n="th_command">Command</th>'),
        ('<th>Target Volume</th>', '<th data-i18n="th_target">Target Volume</th>'),
        ('<th>Water Delivered</th>', '<th data-i18n="th_delivered">Water Delivered</th>'),
        ('<th>Status</th>', '<th data-i18n="th_status">Status</th>'),
        ('<th>Timestamp</th>', '<th data-i18n="th_timestamp">Timestamp</th>'),

        # Alerts View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              SYSTEM ALERTS & NOTIFICATIONS\n            </span>',
         '<span class="text-label-sm" data-i18n="alerts_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">SYSTEM ALERTS & NOTIFICATIONS</span>'),
        ('<h2>Alerts & Incident Hub</h2>', '<h2 data-i18n="alerts_title">Alerts & Incident Hub</h2>'),
        ('<p>Audit trail of critical thresholds, zero-flow anomalies, and agronomic risks.</p>',
         '<p data-i18n="alerts_desc">Audit trail of critical thresholds, zero-flow anomalies, and agronomic risks.</p>'),
        ('<button class="tab-btn active" id="tab-all-alerts" onclick="setAlertsFilter(\'ALL\')">\n              All Alerts\n            </button>',
         '<button class="tab-btn active" id="tab-all-alerts" data-i18n="tab_all" onclick="setAlertsFilter(\'ALL\')">All Alerts</button>'),
        ('<button class="tab-btn" id="tab-unread-alerts" onclick="setAlertsFilter(\'UNREAD\')">\n              Unread\n            </button>',
         '<button class="tab-btn" id="tab-unread-alerts" data-i18n="tab_unread" onclick="setAlertsFilter(\'UNREAD\')">Unread</button>'),
        ('<button class="tab-btn" id="tab-critical-alerts" onclick="setAlertsFilter(\'CRITICAL\')">\n              Critical Only\n            </button>',
         '<button class="tab-btn" id="tab-critical-alerts" data-i18n="tab_critical" onclick="setAlertsFilter(\'CRITICAL\')">Critical Only</button>'),

        # Analytics View
        ('<span class="text-label-sm" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">\n              PERFORMANCE & HISTORICAL METRICS\n            </span>',
         '<span class="text-label-sm" data-i18n="analytics_tag" style="color: var(--outline); letter-spacing: 0.1em; display: block; margin-bottom: 0.25rem;">PERFORMANCE & HISTORICAL METRICS</span>'),
        ('<h2>Farm Analytics & Historical Trends</h2>', '<h2 data-i18n="analytics_title">Farm Analytics & Historical Trends</h2>'),
        ('<p>Cross-zone comparative analytics, model precision rates, and water efficiency metrics.</p>',
         '<p data-i18n="analytics_desc">Cross-zone comparative analytics, model precision rates, and water efficiency metrics.</p>'),

        # Inspector Drawer
        ('<span class="text-label-sm" style="color: var(--agro-green); letter-spacing: 0.08em; display: block;">DIGITAL TWIN INSPECTOR</span>',
         '<span class="text-label-sm" data-i18n="inspector_title" style="color: var(--agro-green); letter-spacing: 0.08em; display: block;">DIGITAL TWIN INSPECTOR</span>'),
    ]

    count = 0
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new, 1)
            count += 1

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Injected {count} data-i18n replacements into index.html")

if __name__ == '__main__':
    inject_tags()
