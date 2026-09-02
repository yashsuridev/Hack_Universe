"""Part 6 — Frontend Dashboard

Plain HTML/JS + Tailwind CSS dashboard (no build step required).
Features:
- Live alert feed via WebSocket
- Color-coded severity indicators
- AI-generated incident summary panel
- Automated action log
- Approve/Override buttons
- Stats/threat map panel
- Attack Simulator controls (Start/Stop)
- Dark theme SOC dashboard style
"""

# ---------------------------------------------------------------------------
# HTML (single file, inline CSS/JS for simplicity)
# ---------------------------------------------------------------------------

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Cyber SOC — AI Cyberdefense Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    fontFamily: {
                        sans: ["Inter", "sans-serif"]
                    }
                }
            }
        }
    </script>
    <style>
        .pulse-red {
            animation: pulse-red 2s infinite;
        }
        @keyframes pulse-red {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen font-sans">
    
    <!-- Topbar -->
    <header class="bg-gray-800/90 backdrop-blur border-b border-gray-700/80 sticky top-0 z-50 py-3.5 shadow-lg">
        <div class="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 to-red-500 flex items-center justify-center shadow-md shadow-red-900/30">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                </div>
                <div>
                    <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-100 to-gray-400">Autonomous Cyber SOC</h1>
                    <p class="text-xs text-gray-400 font-medium">AI-Powered Cyberattack Detection & Autonomous Response</p>
                </div>
            </div>

            <div class="flex items-center gap-3">
                <!-- Simulator Control Buttons -->
                <button id="sim-start-btn" onclick="startSimulator()" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-900/30 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
                    Simulate Attack
                </button>
                <button id="sim-stop-btn" onclick="stopSimulator()" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-red-600/80 hover:bg-red-600 text-white transition-all hidden flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 8a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1H9a1 1 0 01-1-1V8z" clip-rule="evenodd"/></svg>
                    Stop Simulation
                </button>

                <div class="h-4 w-px bg-gray-700 mx-1"></div>

                <!-- Status Badges -->
                <span id="ws-status" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                    <span class="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></span> Connecting...
                </span>

                <button id="refresh-btn" class="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-gray-700/50 transition-colors" title="Refresh Feed">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>
            </div>
        </div>
    </header>

    <!-- Main content -->
    <div class="max-w-7xl mx-auto p-6 space-y-6">

        <!-- Stats row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-gray-800/60 backdrop-blur rounded-2xl p-5 border border-gray-700/60 shadow-lg">
                <div class="flex items-center justify-between text-gray-400 mb-2">
                    <span class="text-xs uppercase tracking-wider font-semibold">Total Threat Alerts</span>
                    <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                </div>
                <div class="text-3xl font-extrabold text-white" id="total-alerts">0</div>
                <div class="text-xs text-gray-500 mt-1">Processed by AI pipeline</div>
            </div>

            <div class="bg-gray-800/60 backdrop-blur rounded-2xl p-5 border border-gray-700/60 shadow-lg">
                <div class="flex items-center justify-between text-orange-400 mb-2">
                    <span class="text-xs uppercase tracking-wider font-semibold">High Severity</span>
                    <svg class="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                </div>
                <div class="text-3xl font-extrabold text-orange-400" id="high-alerts">0</div>
                <div class="text-xs text-gray-500 mt-1">Automated response executed</div>
            </div>

            <div class="bg-gray-800/60 backdrop-blur rounded-2xl p-5 border border-gray-700/60 shadow-lg">
                <div class="flex items-center justify-between text-red-400 mb-2">
                    <span class="text-xs uppercase tracking-wider font-semibold">Critical Threats</span>
                    <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                </div>
                <div class="text-3xl font-extrabold text-red-400" id="critical-alerts">0</div>
                <div class="text-xs text-gray-500 mt-1">Immediate containment</div>
            </div>

            <div class="bg-gray-800/60 backdrop-blur rounded-2xl p-5 border border-gray-700/60 shadow-lg">
                <div class="flex items-center justify-between text-blue-400 mb-2">
                    <span class="text-xs uppercase tracking-wider font-semibold">Brute-Force Attacks</span>
                    <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                </div>
                <div class="text-3xl font-extrabold text-blue-400" id="by-type-brute">0</div>
                <div class="text-xs text-gray-500 mt-1">IP auto-blocked</div>
            </div>
        </div>

        <!-- Main Dashboard Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- Live Alert Feed (Left Column, 5 cols) -->
            <div class="lg:col-span-5 bg-gray-800/60 backdrop-blur rounded-2xl border border-gray-700/60 overflow-hidden flex flex-col h-[560px] shadow-xl">
                <div class="p-4 border-b border-gray-700/60 flex items-center justify-between bg-gray-800/40">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        <h2 class="font-bold text-sm uppercase tracking-wider text-gray-200">Live Alert Stream</h2>
                    </div>
                    <button id="clear-btn" class="text-xs text-gray-400 hover:text-white px-2 py-1 rounded hover:bg-gray-700/50 transition-colors">
                        Clear Feed
                    </button>
                </div>

                <div class="p-3 overflow-y-auto flex-1 space-y-2" id="alert-feed">
                    <div class="text-gray-500 text-center py-16 text-sm">
                        <svg class="w-8 h-8 mx-auto mb-2 text-gray-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m0 14v1m8-8h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/></svg>
                        Connecting to real-time alert stream...
                    </div>
                </div>
            </div>

            <!-- Selected Alert Detail (Right Column, 7 cols) -->
            <div class="lg:col-span-7">
                <!-- Empty Placeholder -->
                <div id="no-selection-placeholder" class="bg-gray-800/60 backdrop-blur rounded-2xl border border-gray-700/60 p-12 text-center h-[560px] flex flex-col items-center justify-center text-gray-400">
                    <div class="w-16 h-16 rounded-2xl bg-gray-700/40 flex items-center justify-center mb-4 text-gray-500">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"/></svg>
                    </div>
                    <h3 class="text-base font-semibold text-gray-200">No Incident Selected</h3>
                    <p class="text-xs text-gray-500 mt-1 max-w-sm">Click on any threat alert in the stream on the left, or click <span class="text-emerald-400 font-medium">"Simulate Attack"</span> to start generating live threat telemetry.</p>
                </div>

                <!-- Alert Detail Card -->
                <div id="selected-alert" class="bg-gray-800/60 backdrop-blur rounded-2xl border border-gray-700/60 p-6 h-[560px] overflow-y-auto hidden flex flex-col justify-between shadow-xl">
                    <div>
                        <!-- Header -->
                        <div class="flex items-start justify-between gap-4 pb-4 border-b border-gray-700/60">
                            <div class="flex items-start gap-3.5">
                                <div class="w-12 h-12 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center shrink-0" id="alert-severity-icon">
                                    <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="font-bold text-lg text-white" id="alert-title">Select an alert</h3>
                                    <p class="text-xs text-gray-400 mt-0.5" id="alert-desc">No alert selected</p>
                                    <p class="text-[11px] font-mono text-gray-500 mt-1" id="alert-meta"></p>
                                </div>
                            </div>
                            <span id="alert-severity-badge" class="px-2.5 py-1 text-xs font-bold rounded-lg bg-red-500/20 text-red-400 border border-red-500/30">
                                HIGH
                            </span>
                        </div>

                        <!-- AI Incident Summary -->
                        <div class="mt-5 p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20">
                            <div class="flex items-center gap-2 mb-2">
                                <svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                <h4 class="font-bold text-xs uppercase tracking-wider text-indigo-300">AI Incident Analysis (Gemini)</h4>
                            </div>
                            <p class="text-sm text-gray-300 leading-relaxed font-normal" id="incident-summary">Loading AI summary...</p>
                        </div>

                        <!-- Automated Action Executed -->
                        <div class="mt-5">
                            <h4 class="font-bold text-xs uppercase tracking-wider text-gray-400 mb-3">Autonomous Playbook Response</h4>
                            <div class="grid grid-cols-2 gap-3 text-xs bg-gray-900/40 p-4 rounded-xl border border-gray-700/40" id="action-details">
                                <div class="space-y-1">
                                    <span class="text-gray-500">Action:</span>
                                    <p class="font-semibold text-white" id="action-action">—</p>
                                </div>
                                <div class="space-y-1">
                                    <span class="text-gray-500">Target IP / Resource:</span>
                                    <p class="font-mono text-emerald-400 font-medium" id="action-target">—</p>
                                </div>
                                <div class="space-y-1">
                                    <span class="text-gray-500">Execution Status:</span>
                                    <p class="font-semibold text-blue-400" id="action-status">—</p>
                                </div>
                                <div class="space-y-1">
                                    <span class="text-gray-500">Timestamp:</span>
                                    <p class="font-mono text-gray-400" id="action-timestamp">—</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Human Analyst Controls -->
                    <div class="mt-6 pt-4 border-t border-gray-700/60">
                        <div class="flex items-center justify-between mb-2">
                            <h4 class="font-bold text-xs uppercase tracking-wider text-gray-400">Human-in-the-Loop Analyst Override</h4>
                            <span class="text-[11px] text-gray-500">Validate or revert AI decisions</span>
                        </div>
                        <div class="flex gap-3">
                            <button id="approve-btn" onclick="approveAlert()" class="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold text-xs transition-all shadow-md shadow-emerald-900/20 flex items-center justify-center gap-1.5">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Approve Action
                            </button>
                            <button id="override-btn" onclick="overrideAlert()" class="flex-1 py-2.5 bg-red-600/80 hover:bg-red-600 text-white rounded-xl font-semibold text-xs transition-all shadow-md shadow-red-900/20 flex items-center justify-center gap-1.5">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                                Override & Revert
                            </button>
                        </div>
                    </div>
                </div>

            </div>

        </div>

    </div>

    <!-- JavaScript Application Logic -->
    <script>
        // Automatic API & WebSocket URL resolution
        const isFileProtocol = window.location.protocol === 'file:';
        const host = (!isFileProtocol && window.location.host) ? window.location.host : 'localhost:8000';
        const WS_URL = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + host + '/ws/alerts';
        const API_BASE = (window.location.protocol === 'https:' ? 'https://' : 'http://') + host + '/api';

        window.alertsMap = {};
        let pendingOverrideAlertId = null;

        const severityColors = {
            critical: 'bg-red-600/20 text-red-400 border-red-500/30',
            high: 'bg-orange-600/20 text-orange-400 border-orange-500/30',
            medium: 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30',
            low: 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30'
        };

        const typeIcons = {
            'brute_force': '🔐',
            'c2_beacon': '📡',
            'data_exfil': '📤',
            'anomaly': '⚡'
        };

        // Create alert entry HTML string
        function createAlertElement(alert) {
            window.alertsMap[alert.alert_id] = alert;
            const severity = alert.severity || 'low';
            const type = alert.type || 'unknown';
            const srcIP = alert.source_ip || 'unknown';
            const timestamp = alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'just now';
            const action = alert.action_taken ? (alert.action_taken.action || '—') : '—';
            
            const colorClass = severityColors[severity] || severityColors.low;
            const icon = typeIcons[type] || '🚨';
            const typeName = type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

            return `
                <div class="alert-entry p-3.5 rounded-xl bg-gray-800/40 border border-gray-700/50 cursor-pointer hover:bg-gray-700/50 hover:border-gray-600/60 transition-all" 
                     onclick="selectAlertById('${alert.alert_id}')">
                    <div class="flex items-center justify-between gap-3">
                        <div class="flex items-center gap-3 min-w-0">
                            <div class="w-9 h-9 rounded-lg bg-gray-700/60 flex items-center justify-center shrink-0 text-base">
                                ${icon}
                            </div>
                            <div class="min-w-0">
                                <p class="font-semibold text-sm text-white truncate">${typeName}</p>
                                <p class="text-xs text-gray-400 truncate">${srcIP} &bull; ${timestamp}</p>
                            </div>
                        </div>
                        <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded-md border ${colorClass} shrink-0">
                            ${severity}
                        </span>
                    </div>
                </div>
            `;
        }

        // Select an alert for detail panel
        function selectAlertById(alertId) {
            const alert = window.alertsMap[alertId];
            if (!alert) return;

            pendingOverrideAlertId = alert.alert_id;
            const severity = alert.severity || 'low';
            const type = alert.type || 'unknown';
            const srcIP = alert.source_ip || 'unknown';
            const timestamp = alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'just now';
            const at = alert.action_taken || {};
            const summary = alert.incident_summary || 'No summary available for this alert.';

            const typeDisplay = type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            document.getElementById('alert-title').textContent = `${typeDisplay} Detected`;
            document.getElementById('alert-desc').textContent = `Source IP: ${srcIP} • ${timestamp}`;
            document.getElementById('alert-meta').textContent = `Alert ID: ${alert.alert_id || 'N/A'}`;

            document.getElementById('incident-summary').textContent = summary;
            document.getElementById('action-action').textContent = at.action || '—';
            document.getElementById('action-target').textContent = at.target || '—';
            document.getElementById('action-status').textContent = at.status || '—';
            document.getElementById('action-timestamp').textContent = at.timestamp || '—';

            // Badge
            const badge = document.getElementById('alert-severity-badge');
            badge.textContent = severity.toUpperCase();
            badge.className = `px-2.5 py-1 text-xs font-bold rounded-lg border ${severityColors[severity] || severityColors.low}`;

            document.getElementById('no-selection-placeholder').classList.add('hidden');
            document.getElementById('selected-alert').classList.remove('hidden');
        }

        // Stats tracking
        function updateStats() {
            const alerts = Object.values(window.alertsMap);
            const total = alerts.length;
            const high = alerts.filter(a => a.severity === 'high').length;
            const critical = alerts.filter(a => a.severity === 'critical').length;
            const brute = alerts.filter(a => a.type === 'brute_force').length;

            document.getElementById('total-alerts').textContent = total;
            document.getElementById('high-alerts').textContent = high;
            document.getElementById('critical-alerts').textContent = critical;
            document.getElementById('by-type-brute').textContent = brute;
        }

        // Start Simulator
        async function startSimulator() {
            try {
                const res = await fetch(`${API_BASE}/simulator/start`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({duration_sec: 60})
                });
                const data = await res.json();
                showToast(data.message || 'Simulator started', 'success');
                checkSimStatus();
            } catch (err) {
                showToast('Failed to start simulator: ' + err.message, 'warning');
            }
        }

        // Stop Simulator
        async function stopSimulator() {
            try {
                const res = await fetch(`${API_BASE}/simulator/stop`, {
                    method: 'POST'
                });
                const data = await res.json();
                showToast(data.message || 'Simulator stopped', 'info');
                checkSimStatus();
            } catch (err) {
                showToast('Failed to stop simulator', 'warning');
            }
        }

        // Check simulator running status
        async function checkSimStatus() {
            try {
                const res = await fetch(`${API_BASE}/simulator/status`);
                const data = await res.json();
                const startBtn = document.getElementById('sim-start-btn');
                const stopBtn = document.getElementById('sim-stop-btn');
                if (data.running) {
                    startBtn.classList.add('hidden');
                    stopBtn.classList.remove('hidden');
                } else {
                    startBtn.classList.remove('hidden');
                    stopBtn.classList.add('hidden');
                }
            } catch (e) {}
        }

        // Approve action
        async function approveAlert() {
            if (!pendingOverrideAlertId) return;
            try {
                const response = await fetch(`${API_BASE}/alerts/${pendingOverrideAlertId}/approve`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({approved: true, comment: 'Analyst validated automated action'})
                });
                const data = await response.json();
                showToast('Action approved by analyst', 'success');
                if (window.alertsMap[pendingOverrideAlertId]) {
                    window.alertsMap[pendingOverrideAlertId].action_taken.status = 'validated_by_analyst';
                    selectAlertById(pendingOverrideAlertId);
                }
            } catch (e) {
                showToast('Approval failed', 'warning');
            }
        }

        // Override action
        async function overrideAlert() {
            if (!pendingOverrideAlertId) return;
            try {
                const response = await fetch(`${API_BASE}/alerts/${pendingOverrideAlertId}/approve`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({approved: false, comment: 'Manual override by analyst'})
                });
                const data = await response.json();
                showToast('Action overridden by analyst', 'warning');
                if (window.alertsMap[pendingOverrideAlertId]) {
                    window.alertsMap[pendingOverrideAlertId].action_taken.status = 'overridden_by_analyst';
                    selectAlertById(pendingOverrideAlertId);
                }
            } catch (e) {
                showToast('Override failed', 'warning');
            }
        }

        // Show toast notification
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            const bg = type === 'success' ? 'bg-emerald-600' : type === 'warning' ? 'bg-amber-600' : 'bg-blue-600';
            toast.className = `fixed top-16 left-1/2 transform -translate-x-1/2 px-5 py-2.5 rounded-xl text-white font-medium text-xs shadow-2xl z-50 transition-all ${bg}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        // WebSocket setup
        function initWS() {
            const statusBadge = document.getElementById('ws-status');
            try {
                let socket = new WebSocket(WS_URL);

                socket.onopen = () => {
                    statusBadge.className = "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                    statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400"></span> SOC Live';
                };

                socket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const feed = document.getElementById('alert-feed');

                        // Clear empty state message if present
                        if (feed.children.length === 1 && feed.children[0].tagName === 'DIV') {
                            feed.innerHTML = '';
                        }

                        if (data.type === 'history') {
                            data.alerts.forEach(alert => {
                                window.alertsMap[alert.alert_id] = alert;
                                feed.insertAdjacentHTML('afterbegin', createAlertElement(alert));
                            });
                            updateStats();
                            if (data.alerts.length > 0) {
                                selectAlertById(data.alerts[data.alerts.length - 1].alert_id);
                            }
                        } else if (data.type === 'new_alert') {
                            const alert = data.alert;
                            window.alertsMap[alert.alert_id] = alert;
                            feed.insertAdjacentHTML('afterbegin', createAlertElement(alert));
                            updateStats();
                            selectAlertById(alert.alert_id);
                        }
                    } catch (e) {
                        console.error('WS message error:', e);
                    }
                };

                socket.onclose = () => {
                    statusBadge.className = "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20";
                    statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-400"></span> Disconnected';
                    setTimeout(initWS, 3000);
                };

                socket.onerror = () => {
                    socket.close();
                };
            } catch (e) {
                console.error("WebSocket init error:", e);
            }
        }

        document.getElementById('refresh-btn').addEventListener('click', () => location.reload());
        document.getElementById('clear-btn').addEventListener('click', () => {
            window.alertsMap = {};
            document.getElementById('alert-feed').innerHTML = '<div class="text-gray-500 text-center py-16 text-sm">Feed cleared. Click "Simulate Attack" to start.</div>';
            document.getElementById('selected-alert').classList.add('hidden');
            document.getElementById('no-selection-placeholder').classList.remove('hidden');
            updateStats();
        });

        // Init
        initWS();
        checkSimStatus();
        setInterval(checkSimStatus, 5000);
    </script>
</body>
</html>"""

if __name__ == "__main__":
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML)
    with open("part6_dashboard.html", "w", encoding="utf-8") as f:
        f.write(HTML)
    print("Exported dashboard HTML to index.html and part6_dashboard.html")