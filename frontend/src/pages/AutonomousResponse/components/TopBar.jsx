// Design reasoning:
// TopBar is a 56px fixed bar. Search sits center-left. Right side has
// the live connection status chip (WebSocket health), a notification bell,
// and a compact user avatar/profile area. The live status chip uses a
// pulsing dot — a subtle real-time indicator pattern from Datadog.

import { Search, Bell, User, Wifi, WifiOff } from 'lucide-react'

export default function TopBar({ wsConnected, alertCount, onSimulate, simRunning }) {
  return (
    <header style={{
      height: 56,
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex', alignItems: 'center',
      padding: '0 20px',
      gap: 12,
      flexShrink: 0,
      position: 'sticky', top: 0, zIndex: 10,
    }}>
      {/* Search */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        background: 'var(--bg-surface-3)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0 12px', height: 34,
        flex: 1, maxWidth: 360,
        transition: 'border-color 0.15s',
      }}
        onFocus={e => e.currentTarget.style.borderColor = 'var(--accent)'}
        onBlur={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
      >
        <Search size={13} color="var(--text-muted)" />
        <input
          placeholder="Search alerts, IPs, alert IDs…"
          style={{
            background: 'transparent', border: 'none', outline: 'none',
            color: 'var(--text-primary)', fontSize: 13,
            fontFamily: 'var(--font-sans)', width: '100%',
          }}
        />
        <kbd style={{
          fontSize: 10, color: 'var(--text-muted)',
          background: 'var(--bg-surface-2)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 3, padding: '1px 5px',
          fontFamily: 'var(--font-mono)',
          whiteSpace: 'nowrap',
        }}>⌘K</kbd>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Simulate button */}
      <button
        onClick={onSimulate}
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '0 14px', height: 32,
          borderRadius: 'var(--radius-md)',
          border: simRunning
            ? '1px solid rgba(239,68,68,0.4)'
            : '1px solid rgba(6,182,212,0.35)',
          background: simRunning
            ? 'rgba(239,68,68,0.1)'
            : 'rgba(6,182,212,0.08)',
          color: simRunning ? '#F87171' : 'var(--accent)',
          cursor: 'pointer',
          fontSize: 12, fontWeight: 600,
          fontFamily: 'var(--font-sans)',
          transition: 'all 0.15s',
          whiteSpace: 'nowrap',
        }}
      >
        {simRunning ? (
          <>
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: '#F87171',
              animation: 'pulse-dot 1.2s ease-in-out infinite',
              display: 'inline-block',
            }} />
            Stop Simulation
          </>
        ) : (
          <>▶ Run Simulation</>
        )}
      </button>

      {/* WebSocket status */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '0 10px', height: 28,
        borderRadius: 'var(--radius-md)',
        background: wsConnected ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
        border: `1px solid ${wsConnected ? 'rgba(34,197,94,0.25)' : 'rgba(239,68,68,0.25)'}`,
        fontSize: 11, fontWeight: 500,
        color: wsConnected ? '#4ADE80' : '#F87171',
      }}>
        {wsConnected ? (
          <>
            <span className="live-dot" style={{
              width: 6, height: 6, borderRadius: '50%',
              background: '#4ADE80', display: 'inline-block',
            }} />
            SOC Live
          </>
        ) : (
          <>
            <WifiOff size={11} />
            Disconnected
          </>
        )}
      </div>

      {/* Notification bell */}
      <button style={{
        position: 'relative',
        width: 34, height: 34,
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        background: 'var(--bg-surface-2)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer', flexShrink: 0,
        transition: 'background 0.15s',
      }}
        onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-surface-3)'}
        onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-surface-2)'}
      >
        <Bell size={15} color="var(--text-secondary)" />
        {alertCount > 0 && (
          <span style={{
            position: 'absolute', top: 5, right: 5,
            width: 7, height: 7, borderRadius: '50%',
            background: '#F87171',
            border: '1.5px solid var(--bg-surface)',
          }} />
        )}
      </button>

      {/* User avatar */}
      <div style={{
        width: 34, height: 34,
        borderRadius: 'var(--radius-md)',
        background: 'linear-gradient(135deg, #1e40af, #0284c7)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer', flexShrink: 0,
        fontSize: 12, fontWeight: 700, color: '#fff',
        border: '1px solid rgba(6,182,212,0.25)',
      }}>
        YK
      </div>
    </header>
  )
}
