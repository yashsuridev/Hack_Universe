// Design reasoning:
// KPI cards use a subtle top-border accent-color rule to signal the metric
// category (a pattern from Grafana and Datadog). The value is large (28px)
// to be instantly readable from a projector distance. The delta pill shows
// trend context. Skeleton state matches the card dimensions precisely.

export default function StatCard({ icon: Icon, label, value, sub, accent, loading, trend }) {
  if (loading) {
    return (
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: '18px 20px',
        borderTop: `2px solid ${accent || 'var(--accent)'}`,
      }}>
        <div className="skeleton" style={{ height: 12, width: 80, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 28, width: 60, marginBottom: 8 }} />
        <div className="skeleton" style={{ height: 10, width: 120 }} />
      </div>
    )
  }

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '18px 20px',
      borderTop: `2px solid ${accent || 'var(--accent)'}`,
      transition: 'background 0.15s, box-shadow 0.15s',
      cursor: 'default',
    }}
      onMouseEnter={e => {
        e.currentTarget.style.background = 'var(--bg-surface-2)'
        e.currentTarget.style.boxShadow = 'var(--shadow-card)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = 'var(--bg-surface)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          {label}
        </span>
        <div style={{
          width: 28, height: 28, borderRadius: 6,
          background: `${accent}18` || 'var(--accent-glow)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {Icon && <Icon size={14} color={accent || 'var(--accent)'} />}
        </div>
      </div>

      {/* Value */}
      <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1, marginBottom: 8 }}>
        {value}
      </div>

      {/* Sub / trend */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{sub}</span>
        {trend && (
          <span style={{
            fontSize: 10, fontWeight: 600, padding: '1px 6px',
            borderRadius: 99,
            background: trend.up ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)',
            color: trend.up ? '#F87171' : '#4ADE80',
            border: `1px solid ${trend.up ? 'rgba(239,68,68,0.2)' : 'rgba(34,197,94,0.2)'}`,
          }}>
            {trend.up ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
    </div>
  )
}
