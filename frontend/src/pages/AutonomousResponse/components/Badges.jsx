// Design reasoning:
// The severity badge is a compact pill — font-size 10px, all-caps, consistent
// horizontal padding. It uses CSS class names tied to the design token
// variables from index.css for all four severity levels.

export function SeverityBadge({ severity }) {
  const s = severity?.toLowerCase() || 'low'
  const label = { critical: 'CRITICAL', high: 'HIGH', medium: 'MEDIUM', low: 'LOW' }[s] || s.toUpperCase()

  return (
    <span
      className={`badge-${s}`}
      style={{
        display: 'inline-block',
        fontSize: 10, fontWeight: 700,
        padding: '2px 8px',
        borderRadius: 99,
        letterSpacing: '0.06em',
        fontFamily: 'var(--font-sans)',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  )
}

// ─── Alert Type Label ──────────────────────────────────────────────────────
const TYPE_META = {
  brute_force:  { label: 'Brute Force',         color: '#FB923C' },
  c2_beacon:    { label: 'C2 Beacon',            color: '#A78BFA' },
  data_exfil:   { label: 'Data Exfiltration',    color: '#F87171' },
  anomaly:      { label: 'ML Anomaly',           color: '#06B6D4' },
}

export function TypeBadge({ type }) {
  const meta = TYPE_META[type] || { label: type, color: '#8B949E' }
  return (
    <span style={{
      fontSize: 11, fontWeight: 500,
      color: meta.color,
      whiteSpace: 'nowrap',
    }}>
      {meta.label}
    </span>
  )
}

// ─── Status Badge ──────────────────────────────────────────────────────────
const STATUS_META = {
  completed:              { label: 'Resolved',          bg: 'rgba(34,197,94,0.1)',   color: '#4ADE80',  border: 'rgba(34,197,94,0.25)'  },
  skipped:                { label: 'Skipped',            bg: 'rgba(234,179,8,0.1)',   color: '#FACC15',  border: 'rgba(234,179,8,0.25)'  },
  validated_by_analyst:   { label: 'Analyst Approved',  bg: 'rgba(34,197,94,0.1)',   color: '#4ADE80',  border: 'rgba(34,197,94,0.25)'  },
  overridden_by_analyst:  { label: 'Analyst Override',  bg: 'rgba(249,115,22,0.1)',  color: '#FB923C',  border: 'rgba(249,115,22,0.25)' },
}

export function StatusBadge({ status }) {
  const raw = status?.split(' ')[0]?.toLowerCase() || 'completed'
  const key = Object.keys(STATUS_META).find(k => raw.includes(k.split('_')[0])) || 'completed'
  const meta = STATUS_META[key] || STATUS_META.completed
  return (
    <span style={{
      fontSize: 10, fontWeight: 600,
      padding: '2px 8px', borderRadius: 99,
      background: meta.bg, color: meta.color,
      border: `1px solid ${meta.border}`,
      whiteSpace: 'nowrap',
    }}>
      {meta.label}
    </span>
  )
}
