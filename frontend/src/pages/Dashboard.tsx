import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Package,
  AlertTriangle,
  Shield,
  FileText,
  Plus,
  Clock,
  XCircle,
  Info,
  ChevronRight,
  Download,
  RefreshCw,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useProjects, useLatestScan, useScanRisk, useDependencyStatus } from '../hooks/useApi';
import { api } from '../services/api';
import {
  formatRelativeTime,
  getSeverityBadgeClass,
  getRiskLevelLabel,
  cn,
} from '../utils/helpers';
import type { Scan } from '../types';
import { HeroSection } from '../components/ui/HeroSection';
import { PipelineSection } from '../components/ui/PipelineSection';
import { StatCounters } from '../components/ui/StatCounters';
import { StatementSection } from '../components/ui/StatementSection';
import { PartnersStrip } from '../components/ui/PartnersStrip';
import { AnimatedCard } from '../components/ui/AnimatedCard';

// Helper for severity risk color (using cyber design system)
function getCyberRiskColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'critical': return '#ff4d4d';
    case 'high':     return '#ff8c42';
    case 'medium':   return '#ffd700';
    case 'low':      return '#00ffc8';
    default:         return '#6b7a90';
  }
}

function getRiskBgClass(level: string): string {
  switch (level.toLowerCase()) {
    case 'critical': return 'badge-critical';
    case 'high':     return 'badge-high';
    case 'medium':   return 'badge-medium';
    case 'low':      return 'badge-low';
    default:         return 'badge';
  }
}

export function Dashboard() {
  const navigate = useNavigate();
  const { data: projects, refetch: refetchProjects } = useProjects();
  const [selectedProjectId] = useState<number | null>(null);
  const [scanHistory, setScanHistory] = useState<Scan[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showNewScanModal, setShowNewScanModal] = useState(false);
  const [uploading, setUploading] = useState(false);

  const { data: latestScan } = useLatestScan(selectedProjectId);
  const { data: riskData } = useScanRisk(latestScan?.id ?? null);
  const { data: dependencyStatus, loading: depsLoading } = useDependencyStatus(latestScan?.id ?? null);

  useEffect(() => {
    if (selectedProjectId) {
      loadScanHistory(selectedProjectId);
    } else {
      setScanHistory([]);
    }
  }, [selectedProjectId]);

  const loadScanHistory = async (projectId: number) => {
    setLoadingHistory(true);
    try {
      const scans = await api.getScans(projectId);
      setScanHistory(scans.slice(0, 10));
    } catch (error) {
      console.error('Failed to load scan history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedProjectId) return;

    setUploading(true);
    try {
      const scan = await api.uploadAndScan(selectedProjectId, file);
      navigate(`/scans/${scan.id}`);
      setShowNewScanModal(false);
      refetchProjects();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload and scan project. Please try again.');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  // === LANDING STATE (no project selected) ===
  if (!selectedProjectId) {
    return (
      <div style={{ background: '#0a0a0a' }}>
        {/* Hero with 3D scene */}
        <HeroSection />

        {/* Scroll-anchored content */}
        <div id="dashboard-content" style={{ scrollMarginTop: '80px' }}>
          {/* Projects grid */}
          <section className="py-24 relative" style={{ background: '#0a0a0a' }}>
            <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />
            <div className="max-w-7xl mx-auto px-6 relative z-10">
              <motion.div
                className="mb-12 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                <div>
                  <p className="text-xs font-mono uppercase tracking-widest mb-2" style={{ color: '#6b7a90' }}>
                    ACTIVE PROJECTS
                  </p>
                  <h1 className="cyber-heading text-3xl md:text-4xl">
                    SBOM AUDITOR
                    <br />
                    <span style={{ color: '#00ffc8' }}>DASHBOARD</span>
                  </h1>
                  <p className="mt-3 text-sm" style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}>
                    Select a project to view its security overview, or create a new project to get started.
                  </p>
                </div>
                <Link to="/projects">
                  <button id="dashboard-new-project-btn" className="btn-primary text-xs px-6 py-3">
                    <Plus className="h-4 w-4 mr-2" />
                    [ NEW PROJECT ]
                  </button>
                </Link>
              </motion.div>

              {/* Project cards */}
              {projects && projects.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {projects.map((project, i) => (
                    <motion.div
                      key={project.id}
                      initial={{ opacity: 0, y: 24 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.08, duration: 0.45 }}
                    >
                      <AnimatedCard intensity={5} onClick={() => navigate(`/projects/${project.id}`)}>
                        <div className="card-body">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3
                                className="text-base font-bold uppercase tracking-wide"
                                style={{ color: '#eaf5ee' }}
                              >
                                {project.name}
                              </h3>
                              {project.description && (
                                <p className="mt-1 text-xs line-clamp-2" style={{ color: '#6b7a90' }}>
                                  {project.description}
                                </p>
                              )}
                            </div>
                            <Shield className="h-8 w-8 flex-shrink-0" style={{ color: '#00ffc8', opacity: 0.6 }} />
                          </div>
                          <div className="mt-4 flex items-center gap-4 text-xs" style={{ color: '#6b7a90' }}>
                            <span className="flex items-center gap-1">
                              <Package className="h-3 w-3" />
                              {project.scan_count || 0} scans
                            </span>
                            {project.latest_scan && (
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatRelativeTime(project.latest_scan.created_at)}
                              </span>
                            )}
                          </div>
                          {project.latest_scan && (
                            <div className="mt-4 flex items-center gap-3">
                              <span className={getRiskBgClass(project.latest_scan.risk_level)}>
                                {getRiskLevelLabel(project.latest_scan.risk_level)}
                              </span>
                              <span className="text-xs font-mono" style={{ color: '#6b7a90' }}>
                                Score: {project.latest_scan.risk_score.toFixed(1)}/100
                              </span>
                            </div>
                          )}
                        </div>
                      </AnimatedCard>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <AnimatedCard>
                  <div className="card-body text-center py-16">
                    <Package className="h-14 w-14 mx-auto mb-4 opacity-20" style={{ color: '#00ffc8' }} />
                    <h3 className="text-base font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>
                      NO PROJECTS YET
                    </h3>
                    <p className="text-sm mb-6" style={{ color: '#6b7a90' }}>
                      Create your first project to start scanning for vulnerabilities.
                    </p>
                    <button
                      id="dashboard-empty-create-btn"
                      className="btn-primary text-xs"
                      onClick={() => navigate('/projects')}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      [ CREATE PROJECT ]
                    </button>
                  </div>
                </AnimatedCard>
              )}
            </div>
          </section>

          {/* Pipeline */}
          <PipelineSection />

          {/* Stat counters */}
          <StatCounters />

          {/* Statement */}
          <StatementSection />

          {/* Partners */}
          <PartnersStrip />
        </div>
      </div>
    );
  }

  // === PROJECT SELECTED STATE ===
  const project = projects?.find(p => p.id === selectedProjectId);

  return (
    <div className="max-w-7xl mx-auto pt-6">
      {/* Breadcrumb + header */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <Link
            to="/projects"
            className="inline-flex items-center gap-2 text-xs mb-2 transition-colors hover:text-cyber-accent"
            style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
          >
            <ChevronRight className="h-3 w-3 rotate-180" />
            BACK TO PROJECTS
          </Link>
          <div className="flex items-center gap-4">
            <h1 className="cyber-heading text-2xl md:text-3xl">{project?.name}</h1>
            {project?.latest_scan && (
              <span className={getRiskBgClass(project.latest_scan.risk_level)}>
                {getRiskLevelLabel(project.latest_scan.risk_level)} RISK
              </span>
            )}
          </div>
          <p className="mt-1 text-xs" style={{ color: '#6b7a90' }}>
            {project?.description || 'No description provided'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            id="dashboard-new-scan-btn"
            className="btn-secondary text-xs"
            onClick={() => setShowNewScanModal(true)}
            disabled={uploading}
          >
            <RefreshCw className="h-3 w-3 mr-2" />
            NEW SCAN
          </button>
          <Link to={`/projects/${selectedProjectId}`}>
            <button id="dashboard-view-details-btn" className="btn-primary text-xs">
              <FileText className="h-3 w-3 mr-2" />
              VIEW DETAILS
            </button>
          </Link>
        </div>
      </div>

      {/* Stat cards */}
      {latestScan && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6 mb-8">
          <StatCard title="DEPENDENCIES" value={latestScan.total_dependencies} icon={Package} accentColor="#00ffc8" trend={{ value: latestScan.direct_dependencies, label: 'direct' }} />
          <StatCard title="CRITICAL"     value={latestScan.critical_count}      icon={AlertTriangle} accentColor="#ff4d4d" />
          <StatCard title="HIGH"         value={latestScan.high_count}          icon={AlertTriangle} accentColor="#ff8c42" />
          <StatCard title="MEDIUM"       value={latestScan.medium_count}        icon={AlertTriangle} accentColor="#ffd700" />
          <StatCard title="LOW"          value={latestScan.low_count}           icon={Info}          accentColor="#00ffc8" />
          <StatCard title="RISK SCORE"   value={`${riskData?.score ?? latestScan.risk_score}/100`} icon={Shield} accentColor={getCyberRiskColor(riskData?.level ?? latestScan.risk_level)} trend={{ value: riskData?.level ?? latestScan.risk_level, label: 'level' }} />
        </div>
      )}

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        <AnimatedCard intensity={4}>
          <div className="card-header flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
              RISK BREAKDOWN
            </h2>
            {riskData && (
              <span className="text-xxs" style={{ color: '#6b7a90' }}>
                {riskData.summary}
              </span>
            )}
          </div>
          <div className="card-body">
            {riskData ? (
              <RiskBreakdownChart breakdown={riskData.breakdown} />
            ) : (
              <div className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>
                Loading risk data...
              </div>
            )}
          </div>
        </AnimatedCard>

        <AnimatedCard intensity={4}>
          <div className="card-header flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
              SCAN HISTORY
            </h2>
            <button
              className="btn-ghost text-xxs"
              onClick={() => { if (selectedProjectId) loadScanHistory(selectedProjectId); }}
              disabled={loadingHistory}
            >
              <RefreshCw className="h-3 w-3 mr-1" /> REFRESH
            </button>
          </div>
          <div className="card-body p-0">
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>DATE</th>
                    <th>DEPS</th>
                    <th>CRITICAL</th>
                    <th>HIGH</th>
                    <th>RISK</th>
                    <th>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {loadingHistory ? (
                    <tr><td colSpan={6} className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>Loading...</td></tr>
                  ) : scanHistory.length === 0 ? (
                    <tr><td colSpan={6} className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>No scan history</td></tr>
                  ) : (
                    scanHistory.map((scan) => (
                      <tr
                        key={scan.id}
                        className="cursor-pointer"
                        onClick={() => navigate(`/scans/${scan.id}`)}
                      >
                        <td className="text-xs">{formatRelativeTime(scan.created_at)}</td>
                        <td className="text-xs">{scan.total_dependencies}</td>
                        <td><span className="badge-critical">{scan.critical_count}</span></td>
                        <td><span className="badge-high">{scan.high_count}</span></td>
                        <td>
                          <span
                            className="badge"
                            style={{
                              color: getCyberRiskColor(scan.risk_level),
                              borderColor: `${getCyberRiskColor(scan.risk_level)}40`,
                              background: `${getCyberRiskColor(scan.risk_level)}10`,
                            }}
                          >
                            {scan.risk_score.toFixed(1)}
                          </span>
                        </td>
                        <td>
                          <span className={cn('badge',
                            scan.status === 'completed' && 'badge-safe',
                            scan.status === 'running'   && 'badge-review',
                            scan.status === 'failed'    && 'badge-critical',
                          )}>
                            {scan.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </AnimatedCard>
      </div>

      {/* Dependency status */}
      <AnimatedCard intensity={2}>
        <div className="card-header flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
            DEPENDENCY STATUS
          </h2>
          <div className="flex items-center gap-2">
            {latestScan && (
              <a
                href={`/api/reports/scan/${latestScan.id}/json`}
                download={`${project?.name}-scan-${latestScan.id}-report.json`}
                className="btn-ghost text-xxs"
              >
                <Download className="h-3 w-3 mr-1" />
                EXPORT JSON
              </a>
            )}
          </div>
        </div>
        <div className="card-body p-0">
          {depsLoading ? (
            <div className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>
              Loading dependencies...
            </div>
          ) : dependencyStatus && dependencyStatus.length > 0 ? (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th className="w-48">PACKAGE</th>
                    <th className="w-24">TYPE</th>
                    <th className="w-28">DECLARED</th>
                    <th className="w-28">INSTALLED</th>
                    <th className="w-28">LATEST</th>
                    <th className="w-32">SECURITY</th>
                    <th className="w-24">SEVERITY</th>
                    <th className="w-28">FIXED</th>
                    <th>RISK</th>
                  </tr>
                </thead>
                <tbody>
                  {dependencyStatus.slice(0, 50).map((dep) => (
                    <tr
                      key={dep.package}
                      className="cursor-pointer"
                      onClick={() => navigate(`/scans/${latestScan?.id}/dependencies/${dep.package}`)}
                    >
                      <td className="font-mono font-medium text-xs">{dep.package}</td>
                      <td><span className="badge" style={{ color: '#6b7a90', borderColor: '#1e2736', background: 'rgba(30,39,54,0.4)' }}>{dep.type}</span></td>
                      <td className="font-mono text-xs" style={{ color: '#6b7a90' }}>{dep.declared || '-'}</td>
                      <td className="font-mono text-xs">{dep.installed || '-'}</td>
                      <td className="font-mono text-xs" style={{ color: '#6b7a90' }}>{dep.latest || '-'}</td>
                      <td><span className={getSeverityBadgeClass(dep.security)}>{dep.security}</span></td>
                      <td>{dep.severity && dep.severity !== 'none' && dep.severity !== 'unknown' ? (
                        <span className={getSeverityBadgeClass(dep.severity)}>{dep.severity.toUpperCase()}</span>
                      ) : '-'}</td>
                      <td className="font-mono text-xs" style={{ color: '#00ffc8' }}>{dep.fixed_version || '-'}</td>
                      <td>
                        <div className="w-20 h-1.5 overflow-hidden" style={{ background: '#1e2736', borderRadius: '0' }}>
                          <div
                            className="h-full"
                            style={{
                              width: `${Math.min(dep.risk, 100)}%`,
                              background: getCyberRiskColor(dep.risk > 70 ? 'critical' : dep.risk > 40 ? 'high' : dep.risk > 20 ? 'medium' : 'low'),
                              transition: 'width 0.5s ease',
                            }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>No dependencies found</div>
          )}
        </div>
      </AnimatedCard>

      {showNewScanModal && (
        <NewScanModal
          projectId={selectedProjectId}
          onClose={() => setShowNewScanModal(false)}
          onUpload={handleFileUpload}
          uploading={uploading}
        />
      )}
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

function StatCard({
  title, value, icon: Icon, accentColor, trend,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  accentColor: string;
  trend?: { value: string | number; label: string };
}) {
  return (
    <AnimatedCard intensity={6}>
      <div className="card-body">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>{title}</p>
            <p className="mt-2 text-2xl font-bold" style={{ color: accentColor, fontFamily: "'JetBrains Mono', monospace", textShadow: `0 0 20px ${accentColor}40` }}>
              {value}
            </p>
            {trend && (
              <p className="mt-1 text-xxs uppercase" style={{ color: '#6b7a90' }}>
                {trend.value} {trend.label}
              </p>
            )}
          </div>
          <div
            className="p-2.5"
            style={{
              border: `1px solid ${accentColor}30`,
              background: `${accentColor}08`,
              borderRadius: '2px',
            }}
          >
            <Icon className="h-5 w-5" style={{ color: accentColor }} />
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
}

function RiskBreakdownChart({ breakdown }: { breakdown: Record<string, number> }) {
  const entries = Object.entries(breakdown).filter(([, v]) => v > 0);

  if (entries.length === 0) {
    return <div className="text-center py-8 text-xs" style={{ color: '#6b7a90' }}>No risk factors detected</div>;
  }

  const maxValue = Math.max(...entries.map(([, v]) => v));

  return (
    <div className="space-y-3">
      {entries.map(([key, value]) => (
        <div key={key} className="flex items-center gap-3">
          <span className="w-32 text-xxs uppercase tracking-wider" style={{ color: '#6b7a90' }}>
            {key.replace(/_/g, ' ')}
          </span>
          <div className="flex-1 h-1.5 overflow-hidden" style={{ background: '#1e2736' }}>
            <div
              className="h-full"
              style={{
                width: `${(value / maxValue) * 100}%`,
                background: 'linear-gradient(90deg, #00ffc8, #00c89a)',
                boxShadow: '0 0 8px rgba(0,255,200,0.3)',
                transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
            />
          </div>
          <span className="w-14 text-xxs font-mono text-right" style={{ color: '#6b7a90' }}>
            {value.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
}

function NewScanModal({
  onClose, onUpload, uploading,
}: {
  projectId: number | null;
  onClose: () => void;
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  uploading: boolean;
}) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="max-w-md w-full"
        style={{
          background: '#161b27',
          border: '1px solid #1e2736',
          borderRadius: '2px',
        }}
        onClick={(e) => e.stopPropagation()}
        initial={{ scale: 0.95, y: 16 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      >
        <div
          className="p-5 flex items-center justify-between"
          style={{ borderBottom: '1px solid #1e2736' }}
        >
          <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: '#eaf5ee' }}>
            NEW SCAN
          </h2>
          <button
            onClick={onClose}
            className="p-1 transition-colors"
            style={{ color: '#6b7a90' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#ff4d4d'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#6b7a90'; }}
            aria-label="Close"
          >
            <XCircle className="h-4 w-4" />
          </button>
        </div>
        <div className="p-6">
          <p className="text-xs mb-5" style={{ color: '#6b7a90' }}>
            Upload a ZIP file containing your project to scan for vulnerabilities.
          </p>
          <div
            className="p-8 text-center"
            style={{
              border: '2px dashed #1e2736',
              borderRadius: '2px',
              transition: 'border-color 0.2s ease',
            }}
            onDragEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = '#00ffc8'; }}
            onDragLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = '#1e2736'; }}
          >
            <input
              type="file"
              accept=".zip"
              onChange={onUpload}
              disabled={uploading}
              className="hidden"
              id="zip-upload"
            />
            <label htmlFor="zip-upload" className="cursor-pointer">
              <FileText className="h-10 w-10 mx-auto mb-3 opacity-30" style={{ color: '#00ffc8' }} />
              <p className="text-xs" style={{ color: '#6b7a90' }}>Click to select or drag and drop a ZIP file</p>
              <p className="text-xxs mt-1" style={{ color: '#3d4a58' }}>Max size: 50MB</p>
            </label>
          </div>
          {uploading && (
            <div className="mt-4 text-center text-xs" style={{ color: '#6b7a90' }}>
              <div className="inline-flex items-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" style={{ color: '#00ffc8' }} />
                SCANNING PROJECT...
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}