import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Package,
  Shield,
  AlertTriangle,
  FileText,
  RefreshCw,
  ChevronRight,
  X,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useProject, useLatestScan, useScan, useScans } from '../hooks/useApi';
import { api } from '../services/api';
import { formatRelativeTime, formatDate, getRiskLevelColor, getRiskLevelLabel, cn } from '../utils/helpers';
import { AnimatedCard } from '../components/ui/AnimatedCard';
import type { Scan } from '../types';

// ── Shared tokens ────────────────────────────────────────────────────────────
const BG_PAGE   = '#0a0a0a';
const BG_CARD   = '#161b27';
const BG_CARD2  = '#0d1117';
const BORDER    = '#1e2736';
const ACCENT    = '#00ffc8';
const TEXT      = '#eaf5ee';
const MUTED     = '#6b7a90';
const DANGER    = '#ff4d4d';
const WARNING   = '#f59e0b';
const RADIUS    = '2px';

// ── Fade-in stagger helpers ──────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.07, duration: 0.45, ease: 'easeOut' as any },
  }),
};

// ── Status colour map ────────────────────────────────────────────────────────
function statusStyle(status: string): React.CSSProperties {
  switch (status) {
    case 'completed': return { color: ACCENT,   background: 'rgba(0,255,200,0.08)',  border: `1px solid rgba(0,255,200,0.3)` };
    case 'running':   return { color: WARNING,  background: 'rgba(245,158,11,0.08)', border: `1px solid rgba(245,158,11,0.3)` };
    case 'failed':    return { color: DANGER,   background: 'rgba(255,77,77,0.08)',  border: `1px solid rgba(255,77,77,0.3)` };
    default:          return { color: MUTED,    background: 'rgba(107,122,144,0.08)',border: `1px solid rgba(107,122,144,0.25)` };
  }
}

// ────────────────────────────────────────────────────────────────────────────
export function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const id = parseInt(projectId || '0', 10);
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);
  const [showNewScanModal, setShowNewScanModal] = useState(false);
  const [uploading, setUploading] = useState(false);

  const { data: project, loading: projectLoading, refetch: refetchProject } = useProject(id);
  const { data: latestScan } = useLatestScan(id);
  const { data: scans, loading: scansLoading } = useScans(id);
  const { data: scan } = useScan(selectedScanId);

  useEffect(() => {
    if (scans && scans.length > 0 && !selectedScanId) {
      setSelectedScanId(scans[0].id);
    }
  }, [scans, selectedScanId]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const newScan = await api.uploadAndScan(id, file);
      navigate(`/scans/${newScan.id}`);
      setShowNewScanModal(false);
      refetchProject();
    } catch (error) {
      alert('Failed to upload and scan project');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  // ── Loading ────────────────────────────────────────────────────────────────
  if (projectLoading) {
    return (
      <div
        style={{ background: BG_PAGE, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: 40, height: 40,
              border: `2px solid ${BORDER}`,
              borderTop: `2px solid ${ACCENT}`,
              borderRadius: '50%',
              animation: 'spin 0.9s linear infinite',
              margin: '0 auto 12px',
            }}
          />
          <p style={{ color: MUTED, fontFamily: 'JetBrains Mono, monospace', fontSize: 12, letterSpacing: '0.1em' }}>
            LOADING PROJECT…
          </p>
        </div>
      </div>
    );
  }

  // ── Not found ──────────────────────────────────────────────────────────────
  if (!project) {
    return (
      <div style={{ background: BG_PAGE, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: MUTED, fontFamily: 'JetBrains Mono, monospace', fontSize: 14 }}>// Project not found</p>
      </div>
    );
  }

  // ── Main render ────────────────────────────────────────────────────────────
  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 16px', fontFamily: 'JetBrains Mono, monospace' }}>

      {/* ── Page header ─────────────────────────────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{ marginBottom: 32, display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <button
            onClick={() => navigate('/projects')}
            className="btn-ghost"
            aria-label="Back to projects"
            style={{ padding: '6px 8px', borderRadius: RADIUS }}
          >
            <ArrowLeft className="h-5 w-5" style={{ color: MUTED }} />
          </button>
          <div>
            <h1
              style={{
                fontSize: 26,
                fontWeight: 700,
                color: TEXT,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                margin: 0,
              }}
            >
              {project.name}
            </h1>
            <p style={{ marginTop: 4, color: MUTED, fontSize: 13 }}>
              {project.description || '// no description provided'}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            className="btn-secondary"
            onClick={() => setShowNewScanModal(true)}
            disabled={uploading}
            style={{ borderRadius: RADIUS, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em' }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            NEW SCAN
          </button>
        </div>
      </motion.div>

      {/* ── Body grid ───────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gap: 24, gridTemplateColumns: 'repeat(3, 1fr)' }}>

        {/* ── Left column (span 2) ─────────────────────────────────────────── */}
        <div style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'column', gap: 24 }}>

          {/* Scans table card */}
          <motion.div custom={1} variants={fadeUp} initial="hidden" animate="visible">
            <AnimatedCard intensity={4} style={{ borderRadius: RADIUS }}>
              {/* card-header */}
              <div
                className="card-header"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  borderBottom: `1px solid ${BORDER}`,
                  padding: '16px 20px',
                }}
              >
                <h2
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: ACCENT,
                    letterSpacing: '0.14em',
                    textTransform: 'uppercase',
                    margin: 0,
                  }}
                >
                  SCANS
                </h2>
                {latestScan && (
                  <span
                    style={{
                      ...statusStyle('completed'),
                      padding: '3px 10px',
                      borderRadius: RADIUS,
                      fontSize: 11,
                      letterSpacing: '0.08em',
                    }}
                  >
                    LATEST: {getRiskLevelLabel(latestScan.risk_level)} ({latestScan.risk_score.toFixed(1)}/100)
                  </span>
                )}
              </div>

              {/* card-body */}
              <div className="card-body" style={{ padding: 0 }}>
                {scansLoading ? (
                  <div style={{ padding: '32px', textAlign: 'center', color: MUTED, fontSize: 13 }}>
                    // loading scans…
                  </div>
                ) : scans && scans.length > 0 ? (
                  <div className="table-container" style={{ overflowX: 'auto' }}>
                    <table
                      className="table"
                      style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}
                    >
                      <thead>
                        <tr style={{ borderBottom: `1px solid ${BORDER}` }}>
                          {['Date', 'Type', 'Deps', 'Crit', 'High', 'Med', 'Low', 'Risk', 'Status', ''].map((h) => (
                            <th
                              key={h}
                              style={{
                                padding: '10px 14px',
                                textAlign: 'left',
                                color: MUTED,
                                letterSpacing: '0.1em',
                                fontSize: 10,
                                textTransform: 'uppercase',
                                fontWeight: 600,
                                whiteSpace: 'nowrap',
                                background: BG_CARD2,
                              }}
                            >
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {scans.map((scanItem, idx) => (
                          <motion.tr
                            key={scanItem.id}
                            custom={idx}
                            variants={fadeUp}
                            initial="hidden"
                            animate="visible"
                            style={{
                              borderBottom: `1px solid ${BORDER}`,
                              background: selectedScanId === scanItem.id
                                ? 'rgba(0,255,200,0.04)'
                                : 'transparent',
                              cursor: 'pointer',
                              transition: 'background 0.2s',
                            }}
                            onMouseEnter={(e) => {
                              (e.currentTarget as HTMLTableRowElement).style.background = 'rgba(0,255,200,0.04)';
                            }}
                            onMouseLeave={(e) => {
                              (e.currentTarget as HTMLTableRowElement).style.background =
                                selectedScanId === scanItem.id ? 'rgba(0,255,200,0.04)' : 'transparent';
                            }}
                          >
                            <td style={{ padding: '10px 14px', color: TEXT, whiteSpace: 'nowrap' }}>
                              {formatRelativeTime(scanItem.created_at)}
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span
                                style={{
                                  background: 'rgba(107,122,144,0.12)',
                                  color: MUTED,
                                  border: `1px solid ${BORDER}`,
                                  borderRadius: RADIUS,
                                  padding: '2px 8px',
                                  fontSize: 11,
                                  letterSpacing: '0.06em',
                                }}
                              >
                                {scanItem.scan_type}
                              </span>
                            </td>
                            <td style={{ padding: '10px 14px', color: TEXT }}>{scanItem.total_dependencies}</td>
                            <td style={{ padding: '10px 14px' }}>
                              <span className="badge-critical">{scanItem.critical_count}</span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span className="badge-high">{scanItem.high_count}</span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span className="badge-medium">{scanItem.medium_count}</span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span className="badge-low">{scanItem.low_count}</span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span
                                className={cn('px-2 py-1 text-xs font-medium', getRiskLevelColor(scanItem.risk_level))}
                                style={{ borderRadius: RADIUS }}
                              >
                                {scanItem.risk_score.toFixed(1)}
                              </span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <span
                                style={{
                                  ...statusStyle(scanItem.status),
                                  padding: '2px 8px',
                                  borderRadius: RADIUS,
                                  fontSize: 11,
                                  letterSpacing: '0.06em',
                                  textTransform: 'uppercase',
                                  display: 'inline-block',
                                }}
                              >
                                {scanItem.status}
                              </span>
                            </td>
                            <td style={{ padding: '10px 14px' }}>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedScanId(scanItem.id);
                                }}
                                className="btn-ghost"
                                aria-label="View scan details"
                                style={{ padding: 4, borderRadius: RADIUS }}
                              >
                                <ChevronRight className="h-4 w-4" style={{ color: ACCENT }} />
                              </button>
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ padding: '40px 24px', textAlign: 'center', color: MUTED }}>
                    <Package
                      className="h-12 w-12 mx-auto mb-3"
                      style={{ color: BORDER, marginBottom: 12 }}
                    />
                    <p style={{ fontSize: 13, color: MUTED }}>// No scans yet. Click "NEW SCAN" to upload a project ZIP.</p>
                  </div>
                )}
              </div>
            </AnimatedCard>
          </motion.div>

          {/* Scan detail card */}
          <AnimatePresence>
            {selectedScanId && scan && (
              <motion.div
                key={selectedScanId}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: 'easeOut' as any }}
              >
                <ScanDetailCard scan={scan} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ── Right column ──────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

          {/* Project Info */}
          <motion.div custom={2} variants={fadeUp} initial="hidden" animate="visible">
            <AnimatedCard intensity={5} style={{ borderRadius: RADIUS }}>
              <div
                className="card-header"
                style={{ borderBottom: `1px solid ${BORDER}`, padding: '16px 20px' }}
              >
                <h2
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: ACCENT,
                    letterSpacing: '0.16em',
                    textTransform: 'uppercase',
                    margin: 0,
                  }}
                >
                  PROJECT INFO
                </h2>
              </div>
              <div className="card-body" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
                <InfoRow label="Status">
                  <span style={{ color: TEXT, fontWeight: 600, textTransform: 'capitalize' }}>
                    {project.status}
                  </span>
                </InfoRow>
                <InfoRow label="Created">
                  <span style={{ color: TEXT }}>{formatDate(project.created_at)}</span>
                </InfoRow>
                <InfoRow label="Updated">
                  <span style={{ color: TEXT }}>{formatDate(project.updated_at)}</span>
                </InfoRow>
                <InfoRow label="Total Scans">
                  <span style={{ color: ACCENT, fontWeight: 700 }}>{project.scan_count || 0}</span>
                </InfoRow>
                {project.ecosystems && project.ecosystems.length > 0 && (
                  <div>
                    <p style={{ fontSize: 10, color: MUTED, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>
                      Ecosystems
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {project.ecosystems.map((eco) => (
                        <span
                          key={eco.id}
                          style={{
                            background: 'rgba(0,255,200,0.07)',
                            color: ACCENT,
                            border: `1px solid rgba(0,255,200,0.25)`,
                            borderRadius: RADIUS,
                            padding: '3px 10px',
                            fontSize: 10,
                            letterSpacing: '0.1em',
                            textTransform: 'uppercase',
                          }}
                        >
                          {eco.ecosystem.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </AnimatedCard>
          </motion.div>

          {/* Latest Scan Summary */}
          {latestScan && (
            <motion.div custom={3} variants={fadeUp} initial="hidden" animate="visible">
              <AnimatedCard intensity={5} style={{ borderRadius: RADIUS }}>
                <div
                  className="card-header"
                  style={{ borderBottom: `1px solid ${BORDER}`, padding: '16px 20px' }}
                >
                  <h2
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: ACCENT,
                      letterSpacing: '0.16em',
                      textTransform: 'uppercase',
                      margin: 0,
                    }}
                  >
                    LATEST SCAN SUMMARY
                  </h2>
                </div>
                <div className="card-body" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <StatRow label="Total Dependencies" value={latestScan.total_dependencies} />
                  <StatRow label="Direct" value={latestScan.direct_dependencies} />
                  <StatRow label="Transitive" value={latestScan.transitive_dependencies} />
                  <StatRow label="Development" value={latestScan.dev_dependencies} />

                  <div style={{ borderTop: `1px solid ${BORDER}`, paddingTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <StatRow label="Critical" value={latestScan.critical_count} color={DANGER} />
                    <StatRow label="High"     value={latestScan.high_count}     color={DANGER} />
                    <StatRow label="Medium"   value={latestScan.medium_count}   color={WARNING} />
                    <StatRow label="Low"      value={latestScan.low_count}      color={MUTED} />
                  </div>

                  <div style={{ borderTop: `1px solid ${BORDER}`, paddingTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <StatRow label="Risk Score" value={`${latestScan.risk_score.toFixed(1)}/100`} color={ACCENT} />
                    <StatRow label="Risk Level" value={getRiskLevelLabel(latestScan.risk_level)} />
                  </div>
                </div>
              </AnimatedCard>
            </motion.div>
          )}
        </div>
      </div>

      {/* ── New Scan Modal ───────────────────────────────────────────────────── */}
      <AnimatePresence>
        {showNewScanModal && (
          <NewScanModal
            onClose={() => setShowNewScanModal(false)}
            onUpload={handleFileUpload}
            uploading={uploading}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

// ── ScanDetailCard ────────────────────────────────────────────────────────────
function ScanDetailCard({ scan }: { scan: Scan }) {
  return (
    <AnimatedCard intensity={4} style={{ borderRadius: RADIUS }}>
      <div
        className="card-header"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${BORDER}`,
          padding: '16px 20px',
        }}
      >
        <h2
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: ACCENT,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            margin: 0,
          }}
        >
          SCAN DETAILS
        </h2>
        <Link
          to={`/scans/${scan.id}`}
          className="btn-secondary"
          style={{ borderRadius: RADIUS, fontSize: 11, letterSpacing: '0.06em', fontFamily: 'JetBrains Mono, monospace' }}
        >
          VIEW FULL DETAILS
        </Link>
      </div>

      <div className="card-body" style={{ padding: 20 }}>
        {/* Mini stat cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
          <MiniStatCard title="DEPS"       value={scan.total_dependencies}        icon={Package}       accent={ACCENT} />
          <MiniStatCard title="CRITICAL"   value={scan.critical_count}            icon={AlertTriangle} accent={DANGER} />
          <MiniStatCard title="HIGH"       value={scan.high_count}               icon={AlertTriangle} accent={WARNING} />
          <MiniStatCard title="RISK"       value={`${scan.risk_score}/100`}      icon={Shield}        accent={ACCENT} />
        </div>

        {/* Time rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: MUTED }}>Started</span>
            <span style={{ color: TEXT, fontWeight: 600 }}>{scan.started_at ? formatDate(scan.started_at) : 'N/A'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: MUTED }}>Completed</span>
            <span style={{ color: TEXT, fontWeight: 600 }}>{scan.completed_at ? formatDate(scan.completed_at) : 'N/A'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: MUTED }}>Status</span>
            <span
              style={{
                ...statusStyle(scan.status),
                padding: '2px 10px',
                borderRadius: RADIUS,
                fontSize: 11,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {scan.status}
            </span>
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
}

// ── MiniStatCard ──────────────────────────────────────────────────────────────
function MiniStatCard({
  title,
  value,
  icon: Icon,
  accent,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  accent: string;
}) {
  return (
    <div
      style={{
        background: BG_CARD2,
        border: `1px solid ${BORDER}`,
        borderRadius: RADIUS,
        padding: '14px 12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div>
        <p style={{ fontSize: 9, color: MUTED, letterSpacing: '0.12em', textTransform: 'uppercase', margin: '0 0 4px' }}>
          {title}
        </p>
        <p style={{ fontSize: 20, fontWeight: 700, color: TEXT, margin: 0 }}>{value}</p>
      </div>
      <div
        style={{
          background: `${accent}15`,
          border: `1px solid ${accent}30`,
          borderRadius: RADIUS,
          padding: 8,
        }}
      >
        <Icon className="h-5 w-5" style={{ color: accent }} />
      </div>
    </div>
  );
}

// ── StatRow ───────────────────────────────────────────────────────────────────
function StatRow({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
      <span style={{ color: MUTED }}>{label}</span>
      <span style={{ fontWeight: 600, color: color || TEXT }}>{value}</span>
    </div>
  );
}

// ── InfoRow ───────────────────────────────────────────────────────────────────
function InfoRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p style={{ fontSize: 10, color: MUTED, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 3 }}>
        {label}
      </p>
      <div style={{ fontSize: 13 }}>{children}</div>
    </div>
  );
}

// ── NewScanModal ──────────────────────────────────────────────────────────────
function NewScanModal({
  onClose,
  onUpload,
  uploading,
}: {
  onClose: () => void;
  onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  uploading: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(0,0,0,0.72)',
        padding: 16,
        backdropFilter: 'blur(4px)',
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
        style={{
          background: BG_CARD,
          border: `1px solid ${BORDER}`,
          borderRadius: RADIUS,
          maxWidth: 480,
          width: '100%',
          fontFamily: 'JetBrains Mono, monospace',
          boxShadow: `0 0 40px rgba(0,255,200,0.06), 0 20px 60px rgba(0,0,0,0.8)`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal header */}
        <div
          style={{
            padding: '18px 24px',
            borderBottom: `1px solid ${BORDER}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: ACCENT,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              margin: 0,
            }}
          >
            NEW SCAN
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: MUTED,
              padding: 4,
              borderRadius: RADIUS,
              display: 'flex',
              transition: 'color 0.15s',
            }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = TEXT)}
            onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = MUTED)}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal body */}
        <div style={{ padding: 24 }}>
          <p style={{ color: MUTED, fontSize: 13, marginBottom: 20, lineHeight: 1.6 }}>
            Upload a ZIP file containing your project to scan for vulnerabilities.
          </p>

          {/* Drop zone */}
          <div
            style={{
              border: `2px dashed ${BORDER}`,
              borderRadius: RADIUS,
              padding: '36px 24px',
              textAlign: 'center',
              background: BG_CARD2,
              transition: 'border-color 0.2s, background 0.2s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLDivElement).style.borderColor = `${ACCENT}60`;
              (e.currentTarget as HTMLDivElement).style.background = 'rgba(0,255,200,0.03)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLDivElement).style.borderColor = BORDER;
              (e.currentTarget as HTMLDivElement).style.background = BG_CARD2;
            }}
          >
            <input
              type="file"
              accept=".zip"
              onChange={onUpload}
              disabled={uploading}
              className="hidden"
              id="zip-upload"
            />
            <label htmlFor="zip-upload" style={{ cursor: 'pointer', display: 'block' }}>
              <FileText
                className="h-12 w-12 mx-auto"
                style={{ color: MUTED, marginBottom: 12 }}
              />
              <p style={{ color: TEXT, fontSize: 13, marginBottom: 4 }}>
                Click to select or drag &amp; drop a ZIP file
              </p>
              <p style={{ color: MUTED, fontSize: 11, letterSpacing: '0.06em' }}>MAX SIZE: 50 MB</p>
            </label>
          </div>

          {/* Uploading indicator */}
          {uploading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ marginTop: 20, textAlign: 'center', color: ACCENT, fontSize: 13 }}
            >
              <RefreshCw
                className="h-5 w-5 animate-spin inline-block"
                style={{ marginRight: 8, color: ACCENT }}
              />
              Scanning…
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}