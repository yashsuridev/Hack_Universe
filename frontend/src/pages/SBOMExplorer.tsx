import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Package,
  Download,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useSBOMExplorer } from '../hooks/useApi';
import { api } from '../services/api';
import { cn, downloadBlob } from '../utils/helpers';
import type { SBOMExplorerFilters, SBOMExplorerComponent } from '../types';
import { ScanSelectorHeader } from '../components/ScanSelectorHeader';
import { AnimatedCard } from '../components/ui/AnimatedCard';

// ─── helpers ────────────────────────────────────────────────────────────────

function getStatusStyle(status: string): React.CSSProperties {
  const s = status?.toLowerCase() ?? '';
  if (s === 'safe' || s === 'low') {
    return {
      color: '#00ffc8',
      background: 'rgba(0,255,200,0.08)',
      border: '1px solid rgba(0,255,200,0.2)',
    };
  }
  if (s === 'vulnerable' || s === 'critical') {
    return {
      color: '#ff4d4d',
      background: 'rgba(255,77,77,0.08)',
      border: '1px solid rgba(255,77,77,0.2)',
    };
  }
  if (s === 'high') {
    return {
      color: '#ff8c42',
      background: 'rgba(255,140,66,0.08)',
      border: '1px solid rgba(255,140,66,0.2)',
    };
  }
  if (s === 'medium') {
    return {
      color: '#ffd700',
      background: 'rgba(255,215,0,0.08)',
      border: '1px solid rgba(255,215,0,0.2)',
    };
  }
  // fallback – muted
  return {
    color: '#6b7a90',
    background: 'rgba(107,122,144,0.08)',
    border: '1px solid rgba(107,122,144,0.2)',
  };
}

// ─── page ────────────────────────────────────────────────────────────────────

export function SBOMExplorerPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<SBOMExplorerFilters>({
    ecosystem: undefined,
    dependency_type: undefined,
    status: undefined,
    search: undefined,
    has_vulnerabilities: undefined,
    license: undefined,
  });
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);

  const { data: explorerData, loading } = useSBOMExplorer(
    scanId ? parseInt(scanId, 10) : null,
    filters,
    page,
    pageSize
  );

  useEffect(() => {
    // Reset page to 1 when filters or scan changes
    setPage(1);
  }, [filters, scanId]);

  const handleDownload = async () => {
    if (!scanId) return;
    const blob = await api.downloadSBOM(parseInt(scanId, 10));
    downloadBlob(blob, `project-sbom.json`);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const components = explorerData?.components || [];
  const total = explorerData?.total ?? 0;

  return (
    <div className="max-w-7xl mx-auto space-y-6 px-2 py-2">

      {/* ── Mini Hero ─────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-2"
      >
        <p
          className="text-xxs tracking-widest uppercase mb-1"
          style={{ color: '#00ffc8' }}
        >
          // Software Bill of Materials
        </p>
        <h1
          className="cyber-heading text-2xl md:text-3xl tracking-widest"
          style={{ color: '#eaf5ee' }}
        >
          SBOM&nbsp;<span style={{ color: '#00ffc8' }}>EXPLORER</span>
        </h1>
      </motion.div>

      <ScanSelectorHeader
        currentScanId={scanId ? parseInt(scanId, 10) : null}
        onScanChange={(id) => navigate(`/sbom/${id}`)}
        title="SBOM Explorer"
      />

      {!scanId ? (
        /* ── No scan selected ──────────────────────────────────────────── */
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.35 }}
          className="card py-20 flex flex-col items-center justify-center text-center gap-4"
        >
          <Package
            className="h-16 w-16"
            style={{ color: '#1e2736' }}
          />
          <h2
            className="cyber-heading text-lg tracking-widest"
            style={{ color: '#eaf5ee' }}
          >
            NO SCAN SELECTED
          </h2>
          <p className="text-xs" style={{ color: '#6b7a90' }}>
            Select a project and scan from the dropdowns above to explore the SBOM.
          </p>
        </motion.div>
      ) : (
        <>
          {/* ── Filter Panel ─────────────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="card"
          >
            {/* Header */}
            <div className="card-header flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h3
                  className="cyber-heading text-sm tracking-widest"
                  style={{ color: '#eaf5ee' }}
                >
                  SBOM COMPONENTS
                </h3>
                <p className="text-xxs mt-1" style={{ color: '#6b7a90' }}>
                  Exploring{' '}
                  <span style={{ color: '#00ffc8' }}>{total}</span>{' '}
                  CycloneDX components
                </p>
              </div>
              <button onClick={handleDownload} className="btn-secondary text-xs py-1.5 px-4">
                <Download className="h-3.5 w-3.5 mr-1.5" />
                Download JSON
              </button>
            </div>

            {/* Filter rows */}
            <div
              className="card-body p-4 space-y-4 border-t"
              style={{ borderColor: '#1e2736' }}
            >
              {/* Ecosystem */}
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className="text-xxs uppercase tracking-widest mr-1"
                  style={{ color: '#6b7a90' }}
                >
                  Ecosystem:
                </span>
                <SelectableTag
                  label="All"
                  selected={!filters.ecosystem}
                  onSelect={() => setFilters({ ...filters, ecosystem: undefined })}
                />
                <SelectableTag
                  label="npm"
                  selected={filters.ecosystem === 'npm'}
                  onSelect={() => setFilters({ ...filters, ecosystem: 'npm' })}
                />
                <SelectableTag
                  label="pypi"
                  selected={filters.ecosystem === 'pypi'}
                  onSelect={() => setFilters({ ...filters, ecosystem: 'pypi' })}
                />
                <SelectableTag
                  label="Maven"
                  selected={filters.ecosystem === 'maven'}
                  onSelect={() => setFilters({ ...filters, ecosystem: 'maven' })}
                />
              </div>

              {/* Dependency type */}
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className="text-xxs uppercase tracking-widest mr-1"
                  style={{ color: '#6b7a90' }}
                >
                  Type:
                </span>
                <SelectableTag
                  label="All"
                  selected={!filters.dependency_type}
                  onSelect={() => setFilters({ ...filters, dependency_type: undefined })}
                />
                <SelectableTag
                  label="Direct"
                  selected={filters.dependency_type === 'direct'}
                  onSelect={() => setFilters({ ...filters, dependency_type: 'direct' })}
                />
                <SelectableTag
                  label="Transitive"
                  selected={filters.dependency_type === 'transitive'}
                  onSelect={() => setFilters({ ...filters, dependency_type: 'transitive' })}
                />
                <SelectableTag
                  label="Development"
                  selected={filters.dependency_type === 'development'}
                  onSelect={() => setFilters({ ...filters, dependency_type: 'development' })}
                />
              </div>

              {/* Security Status */}
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className="text-xxs uppercase tracking-widest mr-1"
                  style={{ color: '#6b7a90' }}
                >
                  Security Status:
                </span>
                <SelectableTag
                  label="All"
                  selected={!filters.status}
                  onSelect={() => setFilters({ ...filters, status: undefined })}
                />
                <SelectableTag
                  label="Safe"
                  selected={filters.status === 'safe'}
                  onSelect={() => setFilters({ ...filters, status: 'safe' })}
                />
                <SelectableTag
                  label="Vulnerable"
                  selected={filters.status === 'vulnerable'}
                  onSelect={() => setFilters({ ...filters, status: 'vulnerable' })}
                />
              </div>

              {/* Search + dropdowns */}
              <div
                className="flex flex-col sm:flex-row gap-3 pt-3 border-t"
                style={{ borderColor: '#1e2736' }}
              >
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search component name..."
                    value={filters.search || ''}
                    onChange={(e) =>
                      setFilters({ ...filters, search: e.target.value || undefined })
                    }
                    className="input py-1.5 text-xs"
                  />
                </div>
                <div className="flex gap-2">
                  <select
                    value={filters.has_vulnerabilities?.toString() ?? 'all'}
                    onChange={(e) =>
                      setFilters({
                        ...filters,
                        has_vulnerabilities:
                          e.target.value === 'true'
                            ? true
                            : e.target.value === 'false'
                            ? false
                            : undefined,
                      })
                    }
                    className="input w-44 text-xs py-1.5"
                  >
                    <option value="all">Security: All</option>
                    <option value="true">With Vulnerabilities</option>
                    <option value="false">Without Vulnerabilities</option>
                  </select>
                  <select
                    value={filters.license || ''}
                    onChange={(e) =>
                      setFilters({ ...filters, license: e.target.value || undefined })
                    }
                    className="input w-40 text-xs py-1.5"
                  >
                    <option value="">All Licenses</option>
                    <option value="MIT">MIT</option>
                    <option value="Apache-2.0">Apache-2.0</option>
                    <option value="BSD-3-Clause">BSD-3-Clause</option>
                    <option value="GPL-3.0">GPL-3.0</option>
                    <option value="LGPL-3.0">LGPL-3.0</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>
              </div>
            </div>
          </motion.div>

          {/* ── Content area ─────────────────────────────────────────────── */}
          {loading ? (
            /* Loading */
            <div
              className="h-96 flex flex-col items-center justify-center gap-4"
              style={{ color: '#6b7a90' }}
            >
              {/* Accent ring spinner */}
              <span
                className="inline-block h-10 w-10 rounded-full border-2 border-t-transparent animate-spin"
                style={{ borderColor: 'rgba(0,255,200,0.3)', borderTopColor: '#00ffc8' }}
              />
              <p className="text-xxs uppercase tracking-widest" style={{ color: '#6b7a90' }}>
                Loading components…
              </p>
            </div>
          ) : components.length > 0 ? (
            <>
              {/* ── Component grid ─────────────────────────────────────── */}
              <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {components.map((comp: SBOMExplorerComponent, idx: number) => (
                  <motion.div
                    key={comp.id}
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: Math.min(idx * 0.04, 0.6) }}
                  >
                    <AnimatedCard
                      intensity={5}
                      className="h-full"
                    >
                      <div className="p-4 space-y-2.5">

                        {/* Name + Status badge */}
                        <div className="flex items-start justify-between gap-2">
                          <div className="truncate min-w-0">
                            <h4
                              className="text-sm font-bold truncate"
                              style={{ color: '#eaf5ee' }}
                              title={comp.name}
                            >
                              {comp.name}
                            </h4>
                            <p
                              className="text-xxs font-mono mt-0.5"
                              style={{ color: '#6b7a90' }}
                            >
                              v{comp.version}
                            </p>
                          </div>
                          <span
                            className="flex-shrink-0 px-2 py-0.5 text-xxs font-semibold uppercase tracking-wider"
                            style={{
                              ...getStatusStyle(comp.status),
                              borderRadius: '2px',
                              fontFamily: 'var(--font-mono)',
                            }}
                          >
                            {comp.status}
                          </span>
                        </div>

                        {/* Ecosystem + dependency type */}
                        <div className="flex items-center justify-between">
                          <span className="text-xxs uppercase" style={{ color: '#6b7a90' }}>
                            {comp.ecosystem}
                          </span>
                          <span className="text-xxs capitalize" style={{ color: '#6b7a90' }}>
                            {comp.dependency_type}
                          </span>
                        </div>

                        {/* Badge row */}
                        <div className="flex flex-wrap gap-1 pt-1">
                          {comp.vulnerabilities_count > 0 && (
                            <span
                              className="px-1.5 py-0.5 text-xxs font-medium"
                              style={{
                                background: 'rgba(255,77,77,0.1)',
                                color: '#ff4d4d',
                                borderRadius: '2px',
                              }}
                            >
                              {comp.vulnerabilities_count}{' '}
                              Vuln{comp.vulnerabilities_count > 1 ? 's' : ''}
                            </span>
                          )}
                          {comp.license && (
                            <span
                              className="px-1.5 py-0.5 text-xxs font-mono truncate max-w-[110px]"
                              style={{
                                background: 'rgba(107,122,144,0.12)',
                                color: '#6b7a90',
                                borderRadius: '2px',
                              }}
                              title={comp.license}
                            >
                              {comp.license}
                            </span>
                          )}
                          {comp.has_lifecycle_scripts && (
                            <span
                              className="px-1.5 py-0.5 text-xxs"
                              style={{
                                background: 'rgba(255,215,0,0.1)',
                                color: '#ffd700',
                                borderRadius: '2px',
                              }}
                            >
                              Lifecycle
                            </span>
                          )}
                          {comp.typosquatting_flag && (
                            <span
                              className="px-1.5 py-0.5 text-xxs"
                              style={{
                                background: 'rgba(255,140,66,0.1)',
                                color: '#ff8c42',
                                borderRadius: '2px',
                              }}
                            >
                              Typosquatting
                            </span>
                          )}
                        </div>

                        {/* Recommended version */}
                        {comp.recommended_version &&
                          comp.recommended_version !== comp.version && (
                            <p
                              className="text-xxs pt-1.5 border-t"
                              style={{
                                color: '#00ffc8',
                                borderColor: '#1e2736',
                              }}
                            >
                              Upgrade:{' '}
                              <span className="font-bold">
                                v{comp.recommended_version}
                              </span>
                            </p>
                          )}
                      </div>
                    </AnimatedCard>
                  </motion.div>
                ))}
              </div>

              {/* ── Pagination ─────────────────────────────────────────── */}
              {total > pageSize && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                  className="flex justify-center items-center gap-4 pt-4"
                >
                  <button
                    onClick={() => handlePageChange(page - 1)}
                    className="btn-secondary text-xs py-1.5 px-4"
                    disabled={page <= 1}
                  >
                    ← Previous
                  </button>
                  <span
                    className="text-xxs uppercase tracking-widest"
                    style={{ color: '#6b7a90' }}
                  >
                    Page{' '}
                    <span style={{ color: '#eaf5ee' }}>{page}</span>
                    {' '}of{' '}
                    <span style={{ color: '#eaf5ee' }}>
                      {Math.ceil(total / pageSize)}
                    </span>
                  </span>
                  <button
                    onClick={() => handlePageChange(page + 1)}
                    className="btn-secondary text-xs py-1.5 px-4"
                    disabled={page * pageSize >= total}
                  >
                    Next →
                  </button>
                </motion.div>
              )}
            </>
          ) : (
            /* ── Empty state ─────────────────────────────────────────────── */
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.35 }}
              className="card h-80 flex flex-col items-center justify-center gap-4"
            >
              <Package
                className="h-14 w-14"
                style={{ color: '#1e2736' }}
              />
              <p
                className="cyber-heading text-sm tracking-widest"
                style={{ color: '#eaf5ee' }}
              >
                NO COMPONENTS FOUND
              </p>
              <p className="text-xs" style={{ color: '#6b7a90' }}>
                Try adjusting your filters or search query.
              </p>
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}

// ─── SelectableTag ───────────────────────────────────────────────────────────

function SelectableTag({
  label,
  selected,
  onSelect,
}: {
  label: string;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        'inline-flex items-center gap-1 text-xxs font-semibold px-3 py-1 uppercase tracking-widest transition-all duration-150',
      )}
      style={{
        borderRadius: '2px',
        fontFamily: 'var(--font-mono)',
        border: selected
          ? '1px solid rgba(0,255,200,0.5)'
          : '1px solid rgba(30,39,54,0.8)',
        background: selected
          ? 'rgba(0,255,200,0.08)'
          : 'rgba(22,27,39,0.5)',
        color: selected ? '#00ffc8' : '#6b7a90',
      }}
    >
      {label}
    </button>
  );
}