import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  XCircle,
  RefreshCw,
  ArrowLeft,
  Activity,
  Database,
  Shield,
  Terminal,
  CheckCircle2,
} from 'lucide-react';
import { motion, type Variants } from 'framer-motion';
import { api } from '../services/api';
import { getRiskLevelColor, cn } from '../utils/helpers';

/* ─── animation variants ─────────────────────────────────────────── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.4, 0, 0.2, 1] as const },
  },
};

/* glowPulse: not a Variants object — used directly as animate/transition props */
const glowPulseAnimate = {
  boxShadow: [
    '0 0 0px rgba(0,255,200,0)',
    '0 0 18px rgba(0,255,200,0.3)',
    '0 0 0px rgba(0,255,200,0)',
  ],
};
const glowPulseTransition = {
  duration: 2.5,
  repeat: Infinity,
  ease: 'easeInOut' as const,
};

/* ─── tiny label helper ──────────────────────────────────────────── */
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xxs uppercase tracking-widest font-mono mb-1" style={{ color: 'var(--color-muted)' }}>
      {children}
    </p>
  );
}

/* ─── info row inside a card ─────────────────────────────────────── */
function InfoRow({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="flex items-start gap-3 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
      <Icon
        className="h-4 w-4 mt-0.5 flex-shrink-0"
        style={{ color: 'var(--color-accent)' }}
      />
      <div className="flex-1 min-w-0">
        <SectionLabel>{label}</SectionLabel>
        <p className="text-sm font-mono" style={{ color: 'var(--color-text)' }}>
          {value}
        </p>
        {sub && (
          <p className="text-xxs font-mono mt-0.5" style={{ color: 'var(--color-muted)' }}>
            {sub}
          </p>
        )}
      </div>
    </div>
  );
}

/* ─── main component ─────────────────────────────────────────────── */
export function SettingsPage() {
  const [systemStatus, setSystemStatus] = useState<'initial' | 'checking' | 'healthy' | 'error'>('initial');
  const [systemInfo, setSystemInfo] = useState<any>(null);

  const checkHealth = async () => {
    setSystemStatus('checking');
    try {
      const data = await api.healthCheck();
      setSystemStatus(data.status === 'healthy' ? 'healthy' : 'error');
      setSystemInfo(data);
    } catch (error) {
      setSystemStatus('error');
      console.error('Health check failed:', error);
    }
  };

  if (systemStatus === 'initial') {
    setSystemStatus('checking');
    checkHealth();
  }

  /* ─── status pill colour ───────────────────────────────────────── */
  const statusColor =
    systemStatus === 'healthy'
      ? { color: 'var(--color-accent)', border: 'rgba(0,255,200,0.35)', bg: 'rgba(0,255,200,0.08)' }
      : systemStatus === 'checking'
      ? { color: '#ffd700',            border: 'rgba(255,215,0,0.35)',  bg: 'rgba(255,215,0,0.08)'  }
      : { color: '#ff4d4d',            border: 'rgba(255,77,77,0.35)',  bg: 'rgba(255,77,77,0.08)'  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-4 font-mono">

      {/* ── page masthead ──────────────────────────────────────────── */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.45, delay: 0 * 0.1, ease: [0.4, 0, 0.2, 1] as const }}
        className="mb-10"
      >
        <p className="text-xxs uppercase tracking-widest mb-1" style={{ color: 'var(--color-accent)' }}>
          [ CONFIGURATION CONSOLE ]
        </p>
        <div className="flex items-end justify-between gap-4">
          <h1
            className="text-2xl font-bold uppercase tracking-widest"
            style={{ color: 'var(--color-text)', letterSpacing: '0.18em' }}
          >
            SYSTEM SETTINGS
          </h1>
          <Link
            to="/"
            className="btn-ghost text-xs flex items-center gap-1"
            aria-label="Go to dashboard"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
        </div>
        {/* accent rule */}
        <div
          className="mt-3 h-px w-full"
          style={{
            background: 'linear-gradient(90deg, var(--color-accent), transparent)',
          }}
        />
      </motion.div>

      {/* ── system config card ─────────────────────────────────────── */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.45, delay: 1 * 0.1, ease: [0.4, 0, 0.2, 1] as const }}
        className="card mb-6"
      >
        {/* card top accent stripe */}
        <div
          className="h-px w-full"
          style={{
            background:
              'linear-gradient(90deg, var(--color-accent), rgba(0,255,200,0.3), transparent)',
          }}
        />

        {/* card header */}
        <div className="card-header flex items-center gap-3">
          <Terminal className="h-4 w-4 flex-shrink-0" style={{ color: 'var(--color-accent)' }} />
          <div>
            <SectionLabel>panel_id :: cfg-001</SectionLabel>
            <h2
              className="text-xs font-bold uppercase tracking-widest"
              style={{ color: 'var(--color-text)' }}
            >
              Application Config
            </h2>
          </div>

          {/* live status badge — glowPulse animate props used directly (not as Variants) */}
          <motion.span
            animate={systemStatus === 'healthy' ? glowPulseAnimate : undefined}
            transition={systemStatus === 'healthy' ? glowPulseTransition : undefined}
            className="ml-auto text-xxs uppercase tracking-widest px-2.5 py-1 font-mono border"
            style={{
              color:       statusColor.color,
              borderColor: statusColor.border,
              background:  statusColor.bg,
            }}
          >
            {systemStatus === 'checking' ? '● PROBING…' : systemStatus === 'healthy' ? '● ONLINE' : '● ERROR'}
          </motion.span>
        </div>

        {/* card body */}
        <div className="card-body p-0">
          <div className="px-6 py-2">
            <InfoRow
              icon={Activity}
              label="Application Version"
              value={systemInfo?.app_version || '1.0.0'}
            />
            <InfoRow
              icon={Shield}
              label="Environment"
              value={systemInfo?.status || 'development'}
            />
            <InfoRow
              icon={Database}
              label="Database Type"
              value="SQLite (development)"
              sub="PostgreSQL (production)"
            />
            <InfoRow
              icon={Shield}
              label="Vulnerability Source"
              value="OSV.dev API"
              sub="Free, no API key required"
            />

            {/* version / copyright footer row */}
            <div className="py-5">
              <SectionLabel>Version</SectionLabel>
              <p className="text-xs font-mono" style={{ color: 'var(--color-muted)' }}>
                SBOM Auditor v1.0.0
              </p>
              <p className="mt-1.5 text-xxs font-mono" style={{ color: 'var(--color-muted)' }}>
                Copyright &copy; 2026 Security Engineering Team
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ── healthy status notice (optional inline callout) ─────────── */}
      {systemStatus === 'healthy' && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="card mb-6"
        >
          <div
            className="h-px w-full"
            style={{
              background:
                'linear-gradient(90deg, var(--color-accent), rgba(0,255,200,0.3), transparent)',
            }}
          />
          <div className="card-body flex items-center gap-3 py-4">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0" style={{ color: 'var(--color-accent)' }} />
            <div>
              <SectionLabel>system health check</SectionLabel>
              <p className="text-xs font-mono" style={{ color: 'var(--color-text)' }}>
                All systems operational
              </p>
            </div>
            <button
              onClick={checkHealth}
              className="btn-ghost ml-auto text-xs flex items-center gap-1"
              aria-label="Retry health check"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Re-check
            </button>
          </div>
        </motion.div>
      )}

      {/* ── error / warning system status card ─────────────────────── */}
      {systemStatus !== 'initial' && systemStatus !== 'healthy' && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="card mb-6"
        >
          {/* red accent top stripe on error */}
          <div
            className="h-px w-full"
            style={{
              background:
                systemStatus === 'error'
                  ? 'linear-gradient(90deg, #ff4d4d, rgba(255,77,77,0.3), transparent)'
                  : 'linear-gradient(90deg, #ffd700, rgba(255,215,0,0.3), transparent)',
            }}
          />

          <div className="card-header flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal
                className="h-4 w-4 flex-shrink-0"
                style={{
                  color: systemStatus === 'error' ? '#ff4d4d' : '#ffd700',
                }}
              />
              <div>
                <SectionLabel>panel_id :: sys-health</SectionLabel>
                <h2
                  className="text-xs font-bold uppercase tracking-widest"
                  style={{ color: 'var(--color-text)' }}
                >
                  System Status
                </h2>
              </div>
            </div>
            <span
              className={cn(
                'text-xxs uppercase tracking-widest px-2.5 py-1 font-mono border',
                getRiskLevelColor(systemStatus === 'error' ? 'critical' : 'high')
              )}
            >
              {systemStatus === 'error' ? 'ERROR' : 'WARNING'}
            </span>
          </div>

          <div className="card-body text-center py-10">
            <XCircle
              className="h-12 w-12 mx-auto mb-4"
              style={{ color: '#ff4d4d' }}
            />
            <p
              className="text-sm font-mono uppercase tracking-widest mb-6"
              style={{ color: 'var(--color-muted)' }}
            >
              System health check failed
            </p>
            <button
              onClick={checkHealth}
              className="btn-primary inline-flex items-center gap-2"
              aria-label="Retry health check"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
          </div>
        </motion.div>
      )}

      {/* ── terminal-style footer tag ───────────────────────────────── */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        className="text-xxs font-mono text-center tracking-widest"
        style={{ color: 'var(--color-muted)' }}
      >
        &gt;_ SBOM_AUDITOR :: CONFIG_CONSOLE :: {new Date().getFullYear()}
      </motion.p>
    </div>
  );
}