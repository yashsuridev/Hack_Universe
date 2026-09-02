// Utility: human-readable relative timestamps

export function formatDistanceToNow(isoString) {
  if (!isoString) return '—'
  try {
    const d = new Date(isoString)
    const diff = Math.floor((Date.now() - d.getTime()) / 1000)
    if (diff < 5)  return 'just now'
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '—'
  }
}
