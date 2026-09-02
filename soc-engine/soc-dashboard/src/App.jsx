import { useState } from 'react'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import StatCard from './components/StatCard'
import AlertTable from './components/AlertTable'
import AlertDetailPanel from './components/AlertDetailPanel'
import ActionLog from './components/ActionLog'
import ThreatChart from './components/ThreatChart'
import { useSOC } from './hooks/useSOC'
import {
  Activity, ShieldAlert, CheckCircle, Clock,
  Lock, Cpu, Radar, TrendingUp
} from 'lucide-react'

export default function App() {
  const {
    alerts, wsConnected, simRunning, loading, kpis,
    toggleSimulator, approveAlert, overrideAlert,
  } = useSOC()

  const [activeNav, setActiveNav] = useState('dashboard')
  const [selectedAlert, setSelectedAlert] = useState(null)

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-base)' }}>

      {/* ── Sidebar ── */}
      <Sidebar activeNav={activeNav} onNavChange={setActiveNav} />

      {/* ── Main column ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

        {/* ── TopBar ── */}
        <TopBar
          wsConnected={wsConnected}
          alertCount={kpis.activeIncidents}
          onSimulate={toggleSimulator}
          simRunning={simRunning}
        />

        {/* ── Scrollable content area ── */}
        <main style={{
          flex: 1, overflowY: 'auto',
          padding: '20px 24px',
          display: 'flex', flexDirection: 'column', gap: 20,
        }}>

          {/* ── Page header ── */}
          <div>
            <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Security Operations Dashboard
            </h1>
            <p style={{ margin: '3px 0 0', fontSize: 12, color: 'var(--text-muted)' }}>
              Real-time threat detection, automated response, and analyst oversight
            </p>
          </div>

          {/* ── KPI cards ── */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 14,
          }}>
            <StatCard
              icon={ShieldAlert}
              label="Total Threats Today"
              value={kpis.total}
              sub="Detected by AI pipeline"
              accent="#06B6D4"
              loading={loading}
              trend={kpis.total > 5 ? { up: true, value: '+' + kpis.total } : undefined}
            />
            <StatCard
              icon={Activity}
              label="Active Incidents"
              value={kpis.activeIncidents}
              sub="Awaiting analyst review"
              accent="#F87171"
              loading={loading}
            />
            <StatCard
              icon={CheckCircle}
              label="Auto-Resolved"
              value={`${kpis.autoResolvedPct}%`}
              sub={`${kpis.resolved} of ${kpis.total} alerts`}
              accent="#4ADE80"
              loading={loading}
              trend={kpis.autoResolvedPct > 0 ? { up: false, value: kpis.autoResolvedPct + '%' } : undefined}
            />
            <StatCard
              icon={Lock}
              label="Brute Force Blocked"
              value={kpis.bruteForce}
              sub="IPs auto-blocked"
              accent="#FB923C"
              loading={loading}
            />
          </div>

          {/* ── Chart + Action Log row ── */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: 14,
          }}>
            <ThreatChart alerts={alerts} />
            <ActionLog alerts={alerts} />
          </div>

          {/* ── Alert Table ── */}
          <AlertTable
            alerts={alerts}
            selectedId={selectedAlert?.alert_id}
            onSelect={setSelectedAlert}
            loading={loading}
          />

          {/* Bottom breathing room */}
          <div style={{ height: 16 }} />
        </main>
      </div>

      {/* ── Alert Detail Panel (slide-in) ── */}
      {selectedAlert && (
        <AlertDetailPanel
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onApprove={approveAlert}
          onOverride={overrideAlert}
        />
      )}
    </div>
  )
}
