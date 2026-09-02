// Custom hook: manages WebSocket connection, alert state, and API calls.
// Separating data logic from UI means components stay pure and testable.

import { useEffect, useRef, useState, useCallback } from 'react'

const API = 'http://localhost:8001/api'
const WS_URL = `ws://localhost:8001/ws/alerts`

export function useSOC() {
  const [alerts, setAlerts] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [simRunning, setSimRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  // ── WebSocket ────────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setWsConnected(true)
        setLoading(false)
      }

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data)
          if (data.type === 'history') {
            setAlerts(data.alerts.reverse())
            setLoading(false)
          } else if (data.type === 'new_alert') {
            setAlerts(prev => [data.alert, ...prev].slice(0, 200))
          }
        } catch { /* ignore malformed frames */ }
      }

      ws.onclose = () => {
        setWsConnected(false)
        reconnectTimer.current = setTimeout(connect, 3000)
      }

      ws.onerror = () => ws.close()
    } catch {
      reconnectTimer.current = setTimeout(connect, 3000)
    }
  }, [])

  useEffect(() => {
    connect()
    // Poll sim status
    const statusInterval = setInterval(async () => {
      try {
        const r = await fetch(`${API}/simulator/status`)
        const d = await r.json()
        setSimRunning(d.running)
      } catch { /* offline */ }
    }, 4000)

    return () => {
      clearTimeout(reconnectTimer.current)
      clearInterval(statusInterval)
      wsRef.current?.close()
    }
  }, [connect])

  // ── Simulation control ───────────────────────────────────────────────────
  const toggleSimulator = useCallback(async () => {
    if (simRunning) {
      await fetch(`${API}/simulator/stop`, { method: 'POST' })
      setSimRunning(false)
    } else {
      await fetch(`${API}/simulator/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_sec: 120 }),
      })
      setSimRunning(true)
    }
  }, [simRunning])

  // ── Analyst actions ──────────────────────────────────────────────────────
  const approveAlert = useCallback(async (alertId) => {
    await fetch(`${API}/alerts/${alertId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: true, comment: 'Approved via SentinelAI SOC dashboard' }),
    })
    setAlerts(prev => prev.map(a =>
      a.alert_id === alertId
        ? { ...a, action_taken: { ...a.action_taken, status: 'validated_by_analyst' } }
        : a
    ))
  }, [])

  const overrideAlert = useCallback(async (alertId) => {
    await fetch(`${API}/alerts/${alertId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: false, comment: 'Overridden via SentinelAI SOC dashboard' }),
    })
    setAlerts(prev => prev.map(a =>
      a.alert_id === alertId
        ? { ...a, action_taken: { ...a.action_taken, status: 'overridden_by_analyst' } }
        : a
    ))
  }, [])

  // ── Derived KPIs ─────────────────────────────────────────────────────────
  const kpis = {
    total: alerts.length,
    activeIncidents: alerts.filter(a => !a.action_taken?.status?.includes('validated') && !a.action_taken?.status?.includes('overridden')).length,
    resolved: alerts.filter(a => a.action_taken?.status === 'completed').length,
    autoResolvedPct: alerts.length > 0
      ? Math.round((alerts.filter(a => a.action_taken?.status === 'completed').length / alerts.length) * 100)
      : 0,
    highCritical: alerts.filter(a => ['high', 'critical'].includes(a.severity)).length,
    bruteForce: alerts.filter(a => a.type === 'brute_force').length,
  }

  return {
    alerts, wsConnected, simRunning, loading, kpis,
    toggleSimulator, approveAlert, overrideAlert,
  }
}
