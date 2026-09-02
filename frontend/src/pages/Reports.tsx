import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Download,
  RefreshCw,
  XCircle,
  LayoutDashboard,
  ChevronRight,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useScans, useScan } from '../hooks/useApi';
import { api } from '../services/api';
import { getRiskLevelLabel, getSeverityBadgeClass, cn, downloadBlob } from '../utils/helpers';
import type { ReportSummary, Scan } from '../types';
import { ScanSelectorHeader } from '../components/ScanSelectorHeader';

/* ─── Animation variants ─────────────────────────────────────── */
const cardVariants = {
  hidden:  { opacity: 0, y: 18 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' as any } },
};

const modalVariants = {
  hidden:  { opacity: 0, scale: 0.96 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.2, ease: 'easeOut' as any } },
  exit:    { opacity: 0, scale: 0.95, transition: { duration: 0.15 } },
};

/* ─── Risk-level → badge class mapping ─────────────────────────── */
function getRiskBadgeClass(level: string): string {
  switch ((level ?? '').toLowerCase()) {
    case 'critical': return 'badge-critical';
    case 'high':     return 'badge-high';
    case 'medium':   return 'badge-medium';
    case 'low':      return 'badge-low';
    default:         return 'badge-safe';
  }
}

/* ─── Severity accent colour for the count number ───────────────── */
function getSeverityCountClass(sev: string): string {
  switch (sev.toLowerCase()) {
    case 'critical': return 'text-[#ff4d4d]';
    case 'high':     return 'text-[#ff8c42]';
    case 'medium':   return 'text-[#ffd700]';
    case 'low':      return 'text-[#00ffc8]';
    default:         return 'text-[#eaf5ee]';
  }
}

/* ═══════════════════════════════════════════════════════════════ */
export function ReportsPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const currentScanId = scanId ? parseInt(scanId, 10) : null;

  const [selectedScanId,       setSelectedScanId]       = useState<number | null>(null);
  const [reportsData,          setReportsData]           = useState<ReportSummary | null>(null);
  const [loadingReport,        setLoadingReport]         = useState(false);
  const [showExportModal,      setShowExportModal]       = useState(false);
  const [exportFormat,         setExportFormat]          = useState<'json' | 'pdf'>('json');
  const [showComparisonModal,  setShowComparisonModal]   = useState(false);
  const [scanId1,              setScanId1]               = useState<number | null>(null);
  const [scanId2,              setScanId2]               = useState<number | null>(null);

  /* Sync selectedScanId with URL parameter */
  useEffect(() => {
    setSelectedScanId(currentScanId);
  }, [currentScanId]);

  /* Fetch scan details to get parent project_id context */
  const { data: currentScan } = useScan(selectedScanId);
  const projectId = currentScan?.project_id || null;

  /* Retrieve project scans for compare selection lists */
  const { data: scans } = useScans(projectId);

  /* Fetch report summary */
  useEffect(() => {
    if (selectedScanId) {
      const fetchReport = async () => {
        setLoadingReport(true);
        try {
          const summary = await api.getReportSummary(selectedScanId);
          setReportsData(summary);
        } catch (error) {
          console.error('Failed to load report summary:', error);
          setReportsData(null);
        } finally {
          setLoadingReport(false);
        }
      };
      fetchReport();
    } else {
      setReportsData(null);
    }
  }, [selectedScanId]);

  const handleExport = async () => {
    if (!selectedScanId) return;
    let bgBlob: Blob;
    if (exportFormat === 'json') {
      bgBlob = await api.downloadJsonReport(selectedScanId);
    } else {
      alert('PDF export not yet available');
      return;
    }
    downloadBlob(bgBlob, `scan-${selectedScanId}-report.${exportFormat}`);
    setShowExportModal(false);
  };

  const handleCompare = () => {
    if (!scanId1 || !scanId2) {
      alert('Please select two scans to compare');
      return;
    }
    setShowComparisonModal(true);
  };

  /* ─── Shared label style ──────────────────────────────────────── */
  const sectionLabel = 'text-xxs uppercase tracking-widest text-[#6b7a90] font-mono';

  return (
    <div className="max-w-7xl mx-auto" style={{ fontFamily: "'JetBrains Mono', monospace" }}>

      {/* Scan selector header — untouched */}
      <ScanSelectorHeader
        currentScanId={currentScanId}
        onScanChange={(id) => navigate(`/reports/${id}`)}
        title="Reports"
      />

      {/* ── No scan selected ─────────────────────────────────────── */}
      {!currentScanId ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="card py-20 text-center"
        >
          <LayoutDashboard className="h-14 w-14 mx-auto mb-5" style={{ color: '#1e2736' }} />
          <h2
            className="text-sm font-bold uppercase tracking-widest mb-2"
            style={{ color: '#eaf5ee' }}
          >
            No Scan Selected
          </h2>
          <p className={sectionLabel + ' normal-case'} style={{ fontSize: '0.78rem' }}>
            Select a project and scan from the dropdowns above to view reports.
          </p>
        </motion.div>

      /* ── Loading ─────────────────────────────────────────────── */
      ) : loadingReport ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card h-96 flex items-center justify-center gap-3"
        >
          <RefreshCw
            className="h-6 w-6 animate-spin"
            style={{ color: '#00ffc8' }}
          />
          <span className={sectionLabel} style={{ fontSize: '0.78rem' }}>
            Loading report summary…
          </span>
        </motion.div>

      /* ── Error ───────────────────────────────────────────────── */
      ) : !reportsData ? (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="card h-96 flex flex-col items-center justify-center gap-3"
          style={{
            background: 'rgba(255,77,77,0.04)',
            borderColor: 'rgba(255,77,77,0.25)',
          }}
        >
          <XCircle className="h-14 w-14" style={{ color: '#ff4d4d' }} />
          <p
            className="text-sm font-bold uppercase tracking-widest"
            style={{ color: '#eaf5ee' }}
          >
            Failed to load report data
          </p>
          <p className={sectionLabel} style={{ fontSize: '0.75rem' }}>
            Please ensure the scan completed successfully.
          </p>
        </motion.div>

      /* ── Main content ─────────────────────────────────────────── */
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

            {/* Left column — Report Summary + Actions */}
            <div className="lg:col-span-2 space-y-6">

              {/* ── Report Summary card ──────────────────────────── */}
              <motion.div
                className="card"
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: 0 * 0.08, duration: 0.35, ease: 'easeOut' as any }}
              >
                <div className="card-header flex items-center justify-between">
                  <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                    Report Summary
                  </h2>
                  {reportsData?.scan && selectedScanId && (
                    <span className={getRiskBadgeClass(reportsData.scan.risk_level ?? 'LOW')}>
                      {getRiskLevelLabel(reportsData.scan.risk_level ?? 'LOW')}
                    </span>
                  )}
                </div>

                <div className="card-body space-y-6">
                  {/* Stats grid */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <p className={sectionLabel}>Dependencies</p>
                      <div>
                        <p className="text-2xl font-bold" style={{ color: '#00ffc8' }}>
                          {reportsData.dependency_stats.by_type.direct}
                        </p>
                        <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                          Direct
                        </p>
                      </div>
                      <div>
                        <p className="text-xl font-bold" style={{ color: '#00c89a' }}>
                          {reportsData.dependency_stats.by_type.transitive}
                        </p>
                        <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                          Transitive
                        </p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className={sectionLabel}>Vulnerabilities</p>
                      <div>
                        <p className="text-2xl font-bold" style={{ color: '#ff4d4d' }}>
                          {reportsData.vulnerability_stats.critical}
                        </p>
                        <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                          Critical
                        </p>
                      </div>
                      <div>
                        <p className="text-xl font-bold" style={{ color: '#ff8c42' }}>
                          {reportsData.vulnerability_stats.high}
                        </p>
                        <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                          High
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Top Recommendations */}
                  <div
                    className="p-4 space-y-3"
                    style={{
                      background: '#0d1117',
                      border: '1px solid #1e2736',
                      borderRadius: '2px',
                    }}
                  >
                    <p className={sectionLabel}>Top Recommendations</p>
                    <ul className="space-y-3">
                      {reportsData.top_recommendations?.slice(0, 5).map((rec: any, i: number) => (
                        <li key={i} className="flex items-start gap-3 font-mono text-xs">
                          <span
                            className="mt-0.5 text-xxs font-bold uppercase tracking-widest shrink-0"
                            style={{
                              color: (rec.priority === 'HIGH' || rec.priority === 'CRITICAL')
                                ? '#ff4d4d'
                                : '#00ffc8',
                            }}
                          >
                            [{rec.priority}]
                          </span>
                          <div>
                            <p style={{ color: '#eaf5ee' }}>{rec.package}</p>
                            <p style={{ color: '#6b7a90', fontSize: '0.7rem' }}>{rec.reason}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </motion.div>

              {/* ── Actions card ─────────────────────────────────── */}
              <motion.div
                className="card"
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: 1 * 0.08, duration: 0.35, ease: 'easeOut' as any }}
              >
                <div className="card-header">
                  <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                    Actions
                  </h2>
                </div>
                <div className="card-body flex flex-wrap gap-3">
                  <button
                    onClick={() => { setExportFormat('json'); setShowExportModal(true); }}
                    className="btn-secondary"
                    aria-label="Export as JSON"
                  >
                    <Download className="h-3.5 w-3.5 mr-2" />
                    Export JSON
                  </button>
                  <button
                    onClick={() => { setExportFormat('pdf'); setShowExportModal(true); }}
                    className="btn-secondary"
                    aria-label="Export as PDF"
                  >
                    <Download className="h-3.5 w-3.5 mr-2" />
                    Export PDF
                  </button>
                  <button
                    onClick={handleCompare}
                    className="btn-secondary"
                    aria-label="Compare scans"
                  >
                    <ChevronRight className="h-3.5 w-3.5 mr-2" />
                    Compare Scans
                  </button>
                </div>
              </motion.div>
            </div>

            {/* Right column — Scan Comparison + Vulnerability Stats */}
            <div className="space-y-6">

              {/* ── Scan Comparison card ─────────────────────────── */}
              <motion.div
                className="card"
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: 2 * 0.08, duration: 0.35, ease: 'easeOut' as any }}
              >
                <div className="card-header">
                  <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                    Scan Comparison
                  </h2>
                </div>
                <div className="card-body p-4">
                  {selectedScanId && (
                    <div className="space-y-3">
                      <div>
                        <p className={cn(sectionLabel, 'mb-1')}>First Scan</p>
                        <select
                          onChange={(e) => setScanId1(parseInt(e.target.value, 10))}
                          className="input w-full"
                        >
                          <option value="">Select first scan</option>
                          {scans?.map((s: Scan) => (
                            <option key={s.id} value={s.id}>
                              {s.status}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <p className={cn(sectionLabel, 'mb-1')}>Second Scan</p>
                        <select
                          onChange={(e) => setScanId2(parseInt(e.target.value, 10))}
                          className="input w-full"
                        >
                          <option value="">Select second scan</option>
                          {scans?.map((s: Scan) => (
                            <option key={s.id} value={s.id}>
                              {s.status}
                            </option>
                          ))}
                        </select>
                      </div>
                      <button
                        onClick={handleCompare}
                        className="btn-primary w-full"
                      >
                        Compare
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* ── Vulnerability Statistics card ─────────────────── */}
              <motion.div
                className="card"
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: 3 * 0.08, duration: 0.35, ease: 'easeOut' as any }}
              >
                <div className="card-header">
                  <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                    Vulnerability Statistics
                  </h2>
                </div>
                <div className="card-body p-4">
                  {reportsData && reportsData.vulnerability_stats ? (
                    <div className="space-y-3">
                      {['critical', 'high', 'medium', 'low'].map((sev) => {
                        const count = reportsData.vulnerability_stats[sev as keyof typeof reportsData.vulnerability_stats];
                        if (count > 0) {
                          return (
                            <div key={sev} className="flex items-center justify-between gap-3">
                              <span className={cn(getSeverityBadgeClass(sev))}>
                                {sev.toUpperCase()}
                              </span>
                              <span
                                className={cn('text-xl font-bold tabular-nums', getSeverityCountClass(sev))}
                              >
                                {count}
                              </span>
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 py-4">
                      <RefreshCw className="h-4 w-4 animate-spin" style={{ color: '#00ffc8' }} />
                      <p className={sectionLabel}>Loading…</p>
                    </div>
                  )}
                </div>
              </motion.div>
            </div>
          </div>

          {/* ════════════════════════════════════════════════════════
              EXPORT MODAL
          ════════════════════════════════════════════════════════ */}
          <AnimatePresence>
            {showExportModal && (
              <div
                className="fixed inset-0 z-50 flex items-center justify-center p-4"
                style={{ background: 'rgba(0,0,0,0.75)' }}
                onClick={() => setShowExportModal(false)}
              >
                <motion.div
                  className="w-full max-w-md"
                  style={{
                    background: '#161b27',
                    border: '1px solid #1e2736',
                    borderRadius: '2px',
                  }}
                  variants={modalVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal header */}
                  <div
                    className="flex items-center justify-between px-6 py-4"
                    style={{ borderBottom: '1px solid #1e2736' }}
                  >
                    <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                      Export Report
                    </h2>
                    <button
                      onClick={() => setShowExportModal(false)}
                      className="btn-ghost p-1"
                      aria-label="Close export modal"
                    >
                      <XCircle className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Modal body */}
                  <div className="px-6 py-5 space-y-4">
                    <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                      Choose export format:
                    </p>
                    <div className="space-y-3">
                      <button
                        onClick={() => {
                          setExportFormat('json');
                          handleExport();
                        }}
                        className="btn-primary w-full"
                        aria-label="Export as JSON"
                      >
                        <Download className="h-3.5 w-3.5 mr-2" />
                        JSON
                      </button>
                      <button
                        onClick={() => {
                          setExportFormat('pdf');
                          alert('PDF export not yet available');
                          setShowExportModal(false);
                        }}
                        className="btn-secondary w-full"
                        aria-label="Export as PDF"
                      >
                        <Download className="h-3.5 w-3.5 mr-2" />
                        PDF
                      </button>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* ════════════════════════════════════════════════════════
              COMPARISON MODAL
          ════════════════════════════════════════════════════════ */}
          <AnimatePresence>
            {showComparisonModal && (
              <div
                className="fixed inset-0 z-50 flex items-center justify-center p-4"
                style={{ background: 'rgba(0,0,0,0.75)' }}
                onClick={() => setShowComparisonModal(false)}
              >
                <motion.div
                  className="w-full max-w-2xl"
                  style={{
                    background: '#161b27',
                    border: '1px solid #1e2736',
                    borderRadius: '2px',
                  }}
                  variants={modalVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal header */}
                  <div
                    className="flex items-center justify-between px-6 py-4"
                    style={{ borderBottom: '1px solid #1e2736' }}
                  >
                    <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
                      Compare Scans
                    </h2>
                    <button
                      onClick={() => setShowComparisonModal(false)}
                      className="btn-ghost p-1"
                      aria-label="Close comparison modal"
                    >
                      <XCircle className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Modal body */}
                  <div className="px-6 py-5 space-y-4">
                    <p className="text-xxs uppercase tracking-widest mb-2" style={{ color: '#6b7a90' }}>
                      Select two scans to compare:
                    </p>

                    <div>
                      <p className={cn(sectionLabel, 'mb-1')}>First Scan</p>
                      <select
                        onChange={(e) => setScanId1(parseInt(e.target.value, 10))}
                        className="input w-full"
                      >
                        <option value="">First scan</option>
                        {scans?.map((s: Scan) => (
                          <option key={s.id} value={s.id}>
                            {s.status}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <p className={cn(sectionLabel, 'mb-1')}>Second Scan</p>
                      <select
                        onChange={(e) => setScanId2(parseInt(e.target.value, 10))}
                        className="input w-full"
                      >
                        <option value="">Second scan</option>
                        {scans?.map((s: Scan) => (
                          <option key={s.id} value={s.id}>
                            {s.status}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex gap-3 pt-1">
                      <button
                        onClick={() => setShowComparisonModal(false)}
                        className="btn-secondary flex-1"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => setShowComparisonModal(false)}
                        className="btn-primary flex-1"
                      >
                        Compare
                      </button>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  );
}