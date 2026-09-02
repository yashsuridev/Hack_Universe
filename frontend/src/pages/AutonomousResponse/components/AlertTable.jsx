// Design reasoning:
// The AlertTable renders as a semantic <table> (correct for tabular data —
// important for accessibility). Columns: severity dot, type, source IP,
// destination action, timestamp, status. New rows use the 'alert-enter'
// CSS animation so they slide in without being jarring. Active row has a
// subtle left-border glow using the accent color. Monospace font for IPs.

import { SeverityBadge, TypeBadge, StatusBadge } from './Badges'
import { formatDistanceToNow } from '../utils/time'

function SkeletonRow() {
  return (
    <tr>
      {[80, 100, 110, 120, 90, 80].map((w, i) => (
        <td key={i} style={{ padding: '12px 14px' }}>
          <div className="skeleton" style={{ height: 12, width: w }} />
        </td>
      ))}
    </tr>
  )
}

export default function AlertTable({ alerts, selectedId, onSelect, loading }) {
  const COLS = ['Severity', 'Type', 'Source IP', 'Action Taken', 'Detected', 'Status']

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
    }}>
      {/* Table header bar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 16px 12px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div>
          <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
            Live Alert Feed
          </span>
          <span style={{
            marginLeft: 8, fontSize: 11,
            color: 'var(--text-muted)',
          }}>
            {alerts.length} event{alerts.length !== 1 ? 's' : ''}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="live-dot" style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#4ADE80', display: 'inline-block',
          }} />
          <span style={{ fontSize: 11, color: '#4ADE80', fontWeight: 500 }}>Streaming</span>
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: 420 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ position: 'sticky', top: 0, background: 'var(--bg-surface-2)', zIndex: 1 }}>
              {COLS.map(col => (
                <th key={col} style={{
                  padding: '8px 14px',
                  textAlign: 'left',
                  fontSize: 10, fontWeight: 700,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase', letterSpacing: '0.07em',
                  borderBottom: '1px solid var(--border-muted)',
                  whiteSpace: 'nowrap',
                }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && alerts.length === 0
              ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
              : alerts.length === 0
                ? (
                  <tr>
                    <td colSpan={6} style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                      No alerts yet — run the simulation to generate live threats
                    </td>
                  </tr>
                )
                : alerts.map((alert, idx) => {
                  const active = alert.alert_id === selectedId
                  return (
                    <tr
                      key={alert.alert_id}
                      className={idx === 0 && !loading ? 'alert-enter' : undefined}
                      onClick={() => onSelect(alert)}
                      style={{
                        cursor: 'pointer',
                        background: active ? 'var(--accent-glow)' : 'transparent',
                        borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
                        transition: 'background 0.1s, border-color 0.1s',
                      }}
                      onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'var(--bg-surface-2)' }}
                      onMouseLeave={e => { if (!active) e.currentTarget.style.background = active ? 'var(--accent-glow)' : 'transparent' }}
                    >
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)' }}>
                        <SeverityBadge severity={alert.severity} />
                      </td>
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)' }}>
                        <TypeBadge type={alert.type} />
                      </td>
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)' }}>
                        <code style={{ fontSize: 12, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', background: 'var(--bg-surface-3)', padding: '2px 6px', borderRadius: 4 }}>
                          {alert.source_ip}
                        </code>
                      </td>
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)', fontSize: 12, color: 'var(--text-secondary)', maxWidth: 160 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                          {alert.action_taken?.action || '—'}
                        </span>
                      </td>
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)', fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {formatDistanceToNow(alert.timestamp)}
                      </td>
                      <td style={{ padding: '11px 14px', borderBottom: '1px solid var(--border-muted)' }}>
                        <StatusBadge status={alert.action_taken?.status} />
                      </td>
                    </tr>
                  )
                })
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
