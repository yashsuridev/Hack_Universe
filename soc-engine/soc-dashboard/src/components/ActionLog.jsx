// Design reasoning:
// The ActionLog is a compact chronological log of automated playbook actions.
// Each entry shows: icon, action name, target, status badge, elapsed time.
// Uses monospace for IPs and action names. Limited to last 20 entries.

import { ShieldOff, Cpu, Server } from 'lucide-react'
import { StatusBadge } from './Badges'
import { formatDistanceToNow } from '../utils/time'

const ACTION_ICONS = {
  block_ip:              { icon: ShieldOff, color: '#FB923C' },
  isolate_device:        { icon: Server,    color: '#F87171' },
  quarantine_transfer:   { icon: Cpu,       color: '#A78BFA' },
  flag_for_review:       { icon: Cpu,       color: '#06B6D4' },
}

export default function ActionLog({ alerts }) {
  const actions = [...alerts]
    .filter(a => a.action_taken?.action)
    .slice(0, 20)

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '14px 16px 12px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
          Automated Response Log
        </span>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          Last {actions.length} actions
        </span>
      </div>

      <div style={{ overflowY: 'auto', maxHeight: 260 }}>
        {actions.length === 0 ? (
          <div style={{ padding: '32px 0', textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
            No automated actions yet
          </div>
        ) : actions.map((alert, i) => {
          const meta = ACTION_ICONS[alert.action_taken?.action] || ACTION_ICONS.flag_for_review
          const Icon = meta.icon
          return (
            <div key={alert.alert_id + i} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 16px',
              borderBottom: i < actions.length - 1 ? '1px solid var(--border-muted)' : 'none',
              transition: 'background 0.1s',
            }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-surface-2)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{
                width: 28, height: 28, borderRadius: 6, flexShrink: 0,
                background: `${meta.color}18`,
                border: `1px solid ${meta.color}30`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={13} color={meta.color} />
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                  <code style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>
                    {alert.action_taken?.action}
                  </code>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>→</span>
                  <code style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>
                    {alert.source_ip}
                  </code>
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                  {formatDistanceToNow(alert.action_taken?.timestamp || alert.timestamp)}
                </div>
              </div>

              <StatusBadge status={alert.action_taken?.status} />
            </div>
          )
        })}
      </div>
    </div>
  )
}
