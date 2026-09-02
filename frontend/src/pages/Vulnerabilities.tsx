import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Shield,
  Info,
  Download,
  RefreshCw,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useScanVulnerabilities } from '../hooks/useApi';
import { api } from '../services/api';
import { formatDate, getSeverityBadgeClass, cn, downloadBlob } from '../utils/helpers';
import type { VulnerabilitySummary } from '../types';
import { ScanSelectorHeader } from '../components/ScanSelectorHeader';
import { VulnerabilityDetailModal } from '../components/VulnerabilityDetailModal';

/* ── severity glow helpers ────────────────────────────────────── */
function getSeverityGlowStyle(severity: string): React.CSSProperties {
  switch (severity.toLowerCase()) {
    case 'critical':
      return {
        border: '1px solid rgba(255,77,77,0.55)',
        boxShadow: '0 0 10px rgba(255,77,77,0.35), 0 0 3px rgba(255,77,77,0.6) inset',
        color: '#ff4d4d',
        background: 'rgba(255,77,77,0.12)',
      };
    case 'high':
      return {
        border: '1px solid rgba(255,140,66,0.45)',
        boxShadow: '0 0 8px rgba(255,140,66,0.25)',
        color: '#ff8c42',
        background: 'rgba(255,140,66,0.10)',
      };
    case 'medium':
      return {
        border: '1px solid rgba(255,215,0,0.4)',
        boxShadow: '0 0 8px rgba(255,215,0,0.2)',
        color: '#ffd700',
        background: 'rgba(255,215,0,0.08)',
      };
    case 'low':
      return {
        border: '1px solid rgba(0,255,200,0.3)',
        boxShadow: '0 0 8px rgba(0,255,200,0.18)',
        color: '#00ffc8',
        background: 'rgba(0,255,200,0.08)',
      };
    default:
      return {
        border: '1px solid rgba(107,122,144,0.35)',
        color: '#6b7a90',
        background: 'rgba(107,122,144,0.08)',
      };
  }
}

function getCardHoverGlow(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical': return 'hover:shadow-[0_0_24px_rgba(255,77,77,0.18),0_0_60px_rgba(0,0,0,0.6)]  hover:border-[rgba(255,77,77,0.35)]';
    case 'high':     return 'hover:shadow-[0_0_20px_rgba(255,140,66,0.15),0_0_60px_rgba(0,0,0,0.5)] hover:border-[rgba(255,140,66,0.3)]';
    case 'medium':   return 'hover:shadow-[0_0_20px_rgba(255,215,0,0.12),0_0_60px_rgba(0,0,0,0.5)]  hover:border-[rgba(255,215,0,0.25)]';
    case 'low':      return 'hover:shadow-[0_0_20px_rgba(0,255,200,0.14),0_0_60px_rgba(0,0,0,0.5)]  hover:border-[rgba(0,255,200,0.25)]';
    default:         return 'hover:shadow-cyber hover:border-cyber-border';
  }
}

/* ── framer-motion variants ───────────────────────────────────── */
const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.055 },
  },
};

const cardVariants = {
  hidden:  { opacity: 0, y: 18 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.38, ease: [0.16, 1, 0.3, 1] as const } },
};

/* ================================================================
   VulnerabilitiesPage
   ================================================================ */
export function VulnerabilitiesPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();

  const { data: vulnerabilities, loading, refetch } = useScanVulnerabilities(
    scanId ? parseInt(scanId, 10) : 0,
    undefined
  );

  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'medium' | 'low'>('all');
  const [search, setSearch] = useState('');
  const [selectedVulnerabilityId, setSelectedVulnerabilityId] = useState<number | null>(null);

  const filteredVulns = vulnerabilities?.filter((v: VulnerabilitySummary) => {
    if (filter !== 'all' && v.severity !== filter) return false;
    if (search && !v.osv_id.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  }) || [];

  useEffect(() => {
    if (scanId) {
      refetch();
    }
  }, [scanId]);

  const handleExport = async () => {
    if (!scanId) return;
    const blob = await api.downloadJsonReport(parseInt(scanId, 10));
    downloadBlob(blob, `scan-${scanId}-report.json`);
  };

  return (
    <div className="max-w-7xl mx-auto font-mono" style={{ fontFamily: 'var(--font-mono)' }}>
      {/* ── Scan selector ──────────────────────────────────────── */}
      <ScanSelectorHeader
        currentScanId={scanId ? parseInt(scanId, 10) : null}
        onScanChange={(id) => navigate(`/vulnerabilities/${id}`)}
        title="Vulnerabilities"
      />

      {!scanId ? (
        /* ── No scan selected ──────────────────────────────────── */
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] as const }}
          className="card py-20 text-center"
        >
          <Shield
            className="h-16 w-16 mx-auto mb-5"
            style={{ color: 'var(--color-muted)' }}
          />
          <h2
            className="cyber-heading text-xl mb-2"
            style={{ color: 'var(--color-text)' }}
          >
            No Scan Selected
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-muted)' }}>
            Please select a project and scan from the dropdowns above to view vulnerabilities.
          </p>
        </motion.div>
      ) : (
        <>
          {/* ── Filter / control bar ─────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] as const }}
            className="card mb-6"
          >
            <div className="card-header flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              {/* title */}
              <div>
                <h3
                  className="cyber-heading text-base tracking-widest"
                  style={{ color: 'var(--color-text)' }}
                >
                  Vulnerabilities List
                </h3>
                <p className="text-xs mt-0.5" style={{ color: 'var(--color-muted)' }}>
                  <span style={{ color: 'var(--color-accent)' }}>{filteredVulns.length}</span>
                  &nbsp;vulnerabilities
                </p>
              </div>

              {/* controls */}
              <div className="flex flex-wrap items-center gap-2">
                {/* severity filter */}
                <span className="text-xxs uppercase tracking-widest" style={{ color: 'var(--color-muted)' }}>
                  Severity:
                </span>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  className="input w-28 text-xs py-1.5"
                >
                  <option value="all">All</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>

                {/* search */}
                <span className="text-xxs uppercase tracking-widest" style={{ color: 'var(--color-muted)' }}>
                  Search:
                </span>
                <input
                  type="text"
                  placeholder="OSV / CVE / GHSA…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="input w-52 text-xs py-1.5"
                />

                {/* export */}
                <button
                  onClick={handleExport}
                  className="btn-ghost text-xs py-1.5 px-3 flex items-center gap-1.5"
                  title="Export JSON report"
                >
                  <Download className="h-3.5 w-3.5" style={{ color: 'var(--color-accent)' }} />
                  Export JSON
                </button>

                {/* summary */}
                <button
                  onClick={() => navigate(`/reports/${scanId}`)}
                  className="btn-ghost text-xs py-1.5 px-3 flex items-center gap-1.5"
                  title="View Summary"
                >
                  <Info className="h-3.5 w-3.5" style={{ color: 'var(--color-accent)' }} />
                  Summary
                </button>
              </div>
            </div>
          </motion.div>

          {/* ── Content area ─────────────────────────────────────── */}
          {loading ? (
            /* loading spinner */
            <div className="h-96 flex flex-col items-center justify-center gap-4">
              <RefreshCw
                className="h-9 w-9 animate-spin"
                style={{ color: 'var(--color-accent)' }}
              />
              <span
                className="text-xs uppercase tracking-widest animate-pulse"
                style={{ color: 'var(--color-muted)' }}
              >
                Loading vulnerabilities…
              </span>
            </div>
          ) : filteredVulns.length === 0 ? (
            /* empty state */
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
              className="card h-80 flex flex-col items-center justify-center gap-4"
            >
              <Info
                className="h-14 w-14"
                style={{ color: 'var(--color-muted)', opacity: 0.4 }}
              />
              <p
                className="cyber-heading text-base"
                style={{ color: 'var(--color-muted)' }}
              >
                No vulnerabilities found
              </p>
              <p className="text-xxs uppercase tracking-widest" style={{ color: 'var(--color-muted)', opacity: 0.5 }}>
                Try adjusting the severity filter or search query
              </p>
            </motion.div>
          ) : (
            /* vulnerability grid with staggered fade-in */
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.05 }}
            >
              {filteredVulns.map((vuln: VulnerabilitySummary) => (
                <motion.div
                  key={vuln.id}
                  variants={cardVariants}
                  className={cn(
                    'card cursor-pointer border transition-all duration-300',
                    getCardHoverGlow(vuln.severity)
                  )}
                  onClick={() => setSelectedVulnerabilityId(vuln.id)}
                  aria-label={`View vulnerability ${vuln.osv_id}`}
                >
                  {/* scan-line shimmer overlay */}
                  <div className="scanline-overlay" />

                  <div className="card-body space-y-3 relative z-10">
                    {/* ── Top row: letter box + name + badge ─── */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {/* severity letter indicator */}
                        <span
                          className="w-8 h-8 flex items-center justify-center font-bold text-sm flex-shrink-0"
                          style={{
                            fontFamily: 'var(--font-mono)',
                            borderRadius: '2px',
                            ...getSeverityGlowStyle(vuln.severity),
                          }}
                        >
                          {vuln.severity.charAt(0).toUpperCase()}
                        </span>

                        <div>
                          <h3
                            className="font-semibold text-sm tracking-wide"
                            style={{ color: 'var(--color-text)' }}
                          >
                            {vuln.dependency_name}
                          </h3>
                          <p className="text-xxs mt-0.5 font-mono" style={{ color: 'var(--color-muted)' }}>
                            {vuln.osv_id}
                            {vuln.cve_id && (
                              <span className="ml-1" style={{ color: 'var(--color-accent)' }}>
                                ({vuln.cve_id})
                              </span>
                            )}
                            {vuln.ghsa_id && (
                              <span className="ml-1" style={{ color: '#ffd700' }}>
                                ({vuln.ghsa_id})
                              </span>
                            )}
                          </p>
                        </div>
                      </div>

                      {/* severity badge */}
                      <span className={cn(getSeverityBadgeClass(vuln.severity))}>
                        {vuln.severity}
                      </span>
                    </div>

                    {/* ── Version details ───────────────────── */}
                    <div
                      className="grid grid-cols-2 gap-2 text-xxs pt-2"
                      style={{ borderTop: '1px solid var(--color-border)' }}
                    >
                      <div>
                        <p
                          className="uppercase tracking-wider mb-0.5"
                          style={{ color: 'var(--color-muted)', fontSize: '0.6rem' }}
                        >
                          Affected Versions
                        </p>
                        <p
                          className="font-mono line-clamp-1"
                          style={{ color: 'var(--color-text)' }}
                        >
                          {vuln.affected_versions || '—'}
                        </p>
                      </div>
                      <div>
                        <p
                          className="uppercase tracking-wider mb-0.5"
                          style={{ color: 'var(--color-muted)', fontSize: '0.6rem' }}
                        >
                          Fixed Version
                        </p>
                        <p
                          className="font-mono font-semibold line-clamp-1"
                          style={{ color: 'var(--color-accent)' }}
                        >
                          {vuln.fixed_version || '—'}
                        </p>
                      </div>
                    </div>

                    {/* ── Footer row: published + CVSS ──────── */}
                    <div
                      className="flex items-center justify-between pt-1"
                      style={{
                        borderTop: '1px solid var(--color-border)',
                        color: 'var(--color-muted)',
                        fontSize: '0.6rem',
                      }}
                    >
                      <span className="uppercase tracking-wider">
                        Published: {vuln.published_at ? formatDate(vuln.published_at) : 'N/A'}
                      </span>
                      {vuln.cvss_score !== null && (
                        <span
                          className="font-semibold tracking-wide"
                          style={{ color: 'var(--color-text)' }}
                        >
                          CVSS&nbsp;
                          <span style={{ color: 'var(--color-accent)' }}>
                            {vuln.cvss_score.toFixed(1)}
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </>
      )}

      {/* ── Detail modal ─────────────────────────────────────────── */}
      {selectedVulnerabilityId && (
        <VulnerabilityDetailModal
          vulnerabilityId={selectedVulnerabilityId}
          onClose={() => setSelectedVulnerabilityId(null)}
        />
      )}
    </div>
  );
}