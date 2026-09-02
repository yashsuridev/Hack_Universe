// Design reasoning:
// The detail panel slides in from the right as a fixed overlay — this avoids
// layout reflow compared to inline expansion. It has three sections:
//   1. Header bar — alert identity, severity, close button
//   2. AI Summary — highlighted block with the Gemini analysis
//   3. Event Timeline — a vertical connector timeline, showing the
//      sequence of events (detection → playbook → analyst action)
//   4. Action buttons — Approve / Override, with loading state

import { useEffect, useState } from 'react'
import { X, Clock, Cpu, ShieldAlert, User, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { SeverityBadge, TypeBadge, StatusBadge } from './Badges'
import { formatDistanceToNow } from '../utils/time'

const TIMELINE_EVENTS = (alert) => [
  {
    icon: AlertTriangle,
    color: '#FB923C',
    label: 'Threat Detected',
    detail: `Rule-based / ML engine flagged ${alert.type} from ${alert.source_ip}`,
    time: alert.timestamp,
  },
  {
    icon: Cpu,
    color: '#06B6D4',
    label: 'Playbook Executed',
    detail: `Action: ${alert.action_taken?.action || '—'} → ${alert.action_taken?.target || 'target'}`,
    time: alert.action_taken?.timestamp,
  },
  {
    icon: User,
    color: '#A78BFA',
    label: 'Analyst Review Pending',
    detail: 'Awaiting human-in-the-loop approval or override',
    time: null,
  },
]

export default function AlertDetailPanel({ alert, onClose, onApprove, onOverride }) {
  const [approving, setApproving] = useState(false)
  const [overriding, setOverriding] = useState(false)
  const [done, setDone] = useState(null)

  // Reset done state when alert changes
  useEffect(() => { setDone(null) }, [alert?.alert_id])

  if (!alert) return null

  const handleApprove = async () => {
    setApproving(true)
    await onApprove(alert.alert_id)
    setApproving(false)
    setDone('approved')
  }

  const handleOverride = async () => {
    setOverriding(true)
    await onOverride(alert.alert_id)
    setOverriding(false)
    setDone('overridden')
  }

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.45)',
          zIndex: 40,
        }}
        className="fade-in"
      />

      {/* Panel */}
      <div
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0,
          width: '100%', maxWidth: 520,
          background: 'var(--bg-surface)',
          borderLeft: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-modal)',
          zIndex: 50,
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
          animation: 'slideInFromRight 0.25s cubic-bezier(0.16,1,0.3,1) both',
        }}
      >
        {/* Panel header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <SeverityBadge severity={alert.severity} />
              <TypeBadge type={alert.type} />
            </div>
            <code style={{
              fontSize: 10, color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
            }}>
              ID: {alert.alert_id}
            </code>
          </div>
          <button
            onClick={onClose}
            style={{
              width: 30, height: 30, borderRadius: 6,
              border: '1px solid var(--border-subtle)',
              background: 'var(--bg-surface-2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: 'var(--text-secondary)',
              transition: 'all 0.15s',
            }}
          >
            <X size={14} />
          </button>
        </div>

        {/* Scrollable body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>

          {/* Meta row */}
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: 12, marginBottom: 20,
          }}>
            {[
              { label: 'Source IP', val: alert.source_ip, mono: true },
              { label: 'Detected', val: formatDistanceToNow(alert.timestamp), mono: false },
              { label: 'Action Taken', val: alert.action_taken?.action || '—', mono: true },
              { label: 'Exec Status', val: <StatusBadge status={alert.action_taken?.status} />, mono: false },
            ].map(({ label, val, mono }, i) => (
              <div key={i} style={{
                background: 'var(--bg-surface-2)',
                border: '1px solid var(--border-muted)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 12px',
              }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>
                  {label}
                </div>
                {mono
                  ? <code style={{ fontSize: 12, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{val}</code>
                  : <div style={{ fontSize: 12 }}>{val}</div>
                }
              </div>
            ))}
          </div>

          {/* AI Summary */}
          <div style={{
            background: 'rgba(6,182,212,0.05)',
            border: '1px solid rgba(6,182,212,0.18)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 16px',
            marginBottom: 20,
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              marginBottom: 10,
              fontSize: 11, fontWeight: 700,
              color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.07em',
            }}>
              <Cpu size={12} /> AI Incident Analysis
            </div>
            <p style={{
              fontSize: 13, lineHeight: 1.7,
              color: 'var(--text-primary)',
              margin: 0,
              whiteSpace: 'pre-wrap',
            }}>
              {alert.incident_summary || 'No AI summary available.'}
            </p>
          </div>

          {/* Timeline */}
          <div style={{ marginBottom: 20 }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: 'var(--text-muted)',
              textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 12,
            }}>
              Event Timeline
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {TIMELINE_EVENTS(alert).map(({ icon: Icon, color, label, detail, time }, i, arr) => (
                <div key={i} style={{ display: 'flex', gap: 12 }}>
                  {/* Connector */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 24, flexShrink: 0 }}>
                    <div style={{
                      width: 24, height: 24, borderRadius: '50%',
                      background: `${color}20`, border: `1.5px solid ${color}60`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      <Icon size={11} color={color} />
                    </div>
                    {i < arr.length - 1 && (
                      <div style={{ width: 1, flex: 1, minHeight: 24, background: 'var(--border-subtle)', margin: '2px 0' }} />
                    )}
                  </div>
                  {/* Content */}
                  <div style={{ paddingBottom: 16, flex: 1, paddingTop: 2 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{label}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{detail}</div>
                    {time && (
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
                        {new Date(time).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Analyst controls — pinned bottom */}
        <div style={{
          padding: '14px 20px',
          borderTop: '1px solid var(--border-subtle)',
          background: 'var(--bg-surface)',
          flexShrink: 0,
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 10 }}>
            Human-in-the-Loop Analyst Decision
          </div>

          {done ? (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center',
              padding: '12px 16px', borderRadius: 'var(--radius-md)',
              background: done === 'approved' ? 'rgba(34,197,94,0.08)' : 'rgba(249,115,22,0.08)',
              border: `1px solid ${done === 'approved' ? 'rgba(34,197,94,0.25)' : 'rgba(249,115,22,0.25)'}`,
              color: done === 'approved' ? '#4ADE80' : '#FB923C',
              fontSize: 13, fontWeight: 600,
              className: 'fade-in',
            }}>
              {done === 'approved' ? <CheckCircle size={15} /> : <XCircle size={15} />}
              {done === 'approved' ? 'Action Approved — decision recorded' : 'Action Overridden — playbook reverted'}
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={handleApprove}
                disabled={approving || overriding}
                style={{
                  flex: 1, height: 36, borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(34,197,94,0.3)',
                  background: approving ? 'rgba(34,197,94,0.12)' : 'rgba(34,197,94,0.08)',
                  color: '#4ADE80',
                  cursor: approving ? 'wait' : 'pointer',
                  fontSize: 12, fontWeight: 600,
                  fontFamily: 'var(--font-sans)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                  transition: 'all 0.15s',
                }}
              >
                <CheckCircle size={13} />
                {approving ? 'Approving…' : 'Approve Action'}
              </button>
              <button
                onClick={handleOverride}
                disabled={approving || overriding}
                style={{
                  flex: 1, height: 36, borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(249,115,22,0.3)',
                  background: overriding ? 'rgba(249,115,22,0.12)' : 'rgba(249,115,22,0.08)',
                  color: '#FB923C',
                  cursor: overriding ? 'wait' : 'pointer',
                  fontSize: 12, fontWeight: 600,
                  fontFamily: 'var(--font-sans)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                  transition: 'all 0.15s',
                }}
              >
                <XCircle size={13} />
                {overriding ? 'Reverting…' : 'Override & Revert'}
              </button>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideInFromRight {
          from { transform: translateX(100%); opacity: 0; }
          to   { transform: translateX(0);   opacity: 1; }
        }
      `}</style>
    </>
  )
}
