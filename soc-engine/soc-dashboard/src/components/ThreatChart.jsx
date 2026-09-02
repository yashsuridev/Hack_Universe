// Design reasoning:
// ThreatChart uses a Recharts AreaChart to show threat volume over time.
// We use a compact sparkline style with an accent-colored area fill and
// no distracting gridlines. The chart is a "glance metric" — not for deep
// analysis — so it's small (200px tall) and labeled minimally.

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useMemo } from 'react'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-surface-2)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 6, padding: '6px 10px',
      fontSize: 11, color: 'var(--text-primary)',
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 2 }}>{label}</div>
      <strong>{payload[0].value} alert{payload[0].value !== 1 ? 's' : ''}</strong>
    </div>
  )
}

export default function ThreatChart({ alerts }) {
  // Bin alerts by minute
  const data = useMemo(() => {
    if (!alerts.length) return []
    const bins = {}
    alerts.forEach(a => {
      const d = new Date(a.timestamp)
      const key = `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
      bins[key] = (bins[key] || 0) + 1
    })
    return Object.entries(bins).slice(-12).map(([time, count]) => ({ time, count }))
  }, [alerts])

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '14px 16px 8px',
      overflow: 'hidden',
    }}>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
          Threat Volume
        </span>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>
          Last 12 min
        </span>
      </div>

      {data.length < 2 ? (
        <div style={{
          height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-muted)', fontSize: 12,
        }}>
          Collecting data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
            <defs>
              <linearGradient id="accentGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              tick={{ fontSize: 9, fill: '#484F58', fontFamily: 'var(--font-mono)' }}
              axisLine={false} tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 9, fill: '#484F58' }}
              axisLine={false} tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#06B6D4"
              strokeWidth={1.5}
              fill="url(#accentGrad)"
              dot={false}
              activeDot={{ r: 3, fill: '#06B6D4', strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
