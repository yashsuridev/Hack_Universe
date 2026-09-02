// Design-level reasoning:
// The Sidebar is fixed-width (56px collapsed / 220px expanded on desktop).
// Uses a two-level nav structure: icon + label. Active state uses the accent
// color with a left-border indicator — same pattern as Datadog / Linear.
// Logo area carries the product brand at the top.

import { useState } from 'react'
import {
  LayoutDashboard, Bell, FolderOpen, BookOpen,
  Settings, Shield, ChevronRight, ChevronLeft,
  Activity, LogOut, Zap
} from 'lucide-react'

const NAV_ITEMS = [
  { id: 'dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { id: 'alerts',     label: 'Alerts',     icon: Bell },
  { id: 'incidents',  label: 'Incidents',  icon: FolderOpen },
  { id: 'playbooks',  label: 'Playbooks',  icon: BookOpen },
  { id: 'settings',   label: 'Settings',   icon: Settings },
]

export default function Sidebar({ activeNav, onNavChange }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      style={{
        width: collapsed ? 56 : 220,
        minWidth: collapsed ? 56 : 220,
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s cubic-bezier(0.4,0,0.2,1)',
        overflow: 'hidden',
        position: 'relative',
        zIndex: 20,
      }}
    >
      {/* Logo */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '20px 14px 16px',
        borderBottom: '1px solid var(--border-muted)',
        minHeight: 64,
      }}>
        <div style={{
          width: 28, height: 28, borderRadius: 6, flexShrink: 0,
          background: 'linear-gradient(135deg, #06B6D4 0%, #0284C7 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 12px rgba(6,182,212,0.35)',
        }}>
          <Shield size={15} color="#fff" strokeWidth={2.5} />
        </div>
        {!collapsed && (
          <div style={{ overflow: 'hidden' }}>
            <div style={{
              fontWeight: 700, fontSize: 13, color: 'var(--text-primary)',
              letterSpacing: '-0.01em', whiteSpace: 'nowrap',
            }}>
              SentinelAI
            </div>
            <div style={{
              fontSize: 10, color: 'var(--text-muted)',
              textTransform: 'uppercase', letterSpacing: '0.08em',
              whiteSpace: 'nowrap',
            }}>
              Cyber SOC
            </div>
          </div>
        )}
      </div>

      {/* Nav links */}
      <nav style={{ flex: 1, padding: '10px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const active = activeNav === id
          return (
            <button
              key={id}
              onClick={() => onNavChange(id)}
              title={collapsed ? label : undefined}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '8px 10px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: active ? 'var(--accent-glow)' : 'transparent',
                color: active ? 'var(--accent)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
                fontSize: 13, fontWeight: active ? 600 : 400,
                width: '100%', textAlign: 'left',
                transition: 'all 0.15s ease',
                position: 'relative',
                borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'var(--bg-surface-2)' }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
            >
              <Icon size={16} strokeWidth={active ? 2.5 : 1.8} style={{ flexShrink: 0 }} />
              {!collapsed && <span style={{ whiteSpace: 'nowrap' }}>{label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Bottom: status indicator + collapse toggle */}
      <div style={{
        padding: '10px 8px',
        borderTop: '1px solid var(--border-muted)',
        display: 'flex', flexDirection: 'column', gap: 4,
      }}>
        {/* System status */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '6px 10px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(34,197,94,0.07)',
          border: '1px solid rgba(34,197,94,0.2)',
        }}>
          <Activity size={13} color="#4ADE80" />
          {!collapsed && (
            <span style={{ fontSize: 11, color: '#4ADE80', fontWeight: 500, whiteSpace: 'nowrap' }}>
              All Systems Operational
            </span>
          )}
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(c => !c)}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 6, padding: '6px 10px',
            borderRadius: 'var(--radius-md)', border: 'none',
            background: 'transparent', color: 'var(--text-muted)',
            cursor: 'pointer', width: '100%',
            fontSize: 11, fontFamily: 'var(--font-sans)',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-surface-2)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          {collapsed
            ? <ChevronRight size={14} />
            : <><ChevronLeft size={14} /><span style={{ whiteSpace: 'nowrap' }}>Collapse</span></>
          }
        </button>
      </div>
    </aside>
  )
}
