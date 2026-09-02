import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useProjects } from '../hooks/useApi';
import type { Project, Scan } from '../types';
import { Layers, RefreshCw } from 'lucide-react';

interface ScanSelectorHeaderProps {
  currentScanId: number | null;
  onScanChange: (scanId: number) => void;
  title: string;
}

export function ScanSelectorHeader({ currentScanId, onScanChange, title }: ScanSelectorHeaderProps) {
  const { data: projects, loading: loadingProjects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [scans, setScans] = useState<Scan[]>([]);
  const [loadingScans, setLoadingScans] = useState(false);

  // Set selected project based on current scan
  useEffect(() => {
    if (currentScanId) {
      const fetchScanProject = async () => {
        try {
          const scan = await api.getScan(currentScanId);
          setSelectedProjectId(scan.project_id);
        } catch (err) {
          console.error('Failed to fetch project for scan:', err);
        }
      };
      fetchScanProject();
    }
  }, [currentScanId]);

  // Fetch scans when selected project changes
  useEffect(() => {
    if (selectedProjectId) {
      const fetchScans = async () => {
        setLoadingScans(true);
        try {
          const projectScans = await api.getScans(selectedProjectId);
          setScans(projectScans);

          if (!currentScanId || !projectScans.some(s => s.id === currentScanId)) {
            const completedScan = projectScans.find(s => s.status === 'completed');
            const scanToSelect = completedScan || projectScans[0];
            if (scanToSelect) {
              onScanChange(scanToSelect.id);
            }
          }
        } catch (err) {
          console.error('Failed to fetch scans for project:', err);
        } finally {
          setLoadingScans(false);
        }
      };
      fetchScans();
    } else {
      setScans([]);
    }
  }, [selectedProjectId]);

  return (
    <div
      className="mb-6"
      style={{
        background: '#161b27',
        border: '1px solid #1e2736',
        borderRadius: '2px',
        padding: '0',
      }}
    >
      <div
        style={{ padding: '1rem 1.5rem' }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        {/* Title */}
        <div className="flex items-center gap-3">
          <Layers
            className="h-5 w-5 flex-shrink-0"
            style={{ color: '#00ffc8', opacity: 0.8 }}
          />
          <div>
            <h2
              className="text-sm font-bold uppercase tracking-widest"
              style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
            >
              {title}
            </h2>
            <p
              className="text-xxs uppercase tracking-wider"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              SELECT PROJECT &amp; SCAN TO VIEW DETAILS
            </p>
          </div>
        </div>

        {/* Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Project selector */}
          <div className="flex items-center gap-2">
            <span
              className="text-xxs uppercase tracking-widest flex-shrink-0"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              PROJECT:
            </span>
            {loadingProjects ? (
              <div className="flex items-center gap-1" style={{ color: '#6b7a90' }}>
                <RefreshCw className="h-3 w-3 animate-spin" style={{ color: '#00ffc8' }} />
                <span className="text-xxs" style={{ fontFamily: "'JetBrains Mono', monospace" }}>Loading...</span>
              </div>
            ) : (
              <select
                value={selectedProjectId || ''}
                onChange={(e) => setSelectedProjectId(e.target.value ? parseInt(e.target.value, 10) : null)}
                className="input py-1.5 px-3 w-44 text-xs"
              >
                <option value="">-- Select Project --</option>
                {projects?.map((proj: Project) => (
                  <option key={proj.id} value={proj.id}>
                    {proj.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Scan selector */}
          <div className="flex items-center gap-2">
            <span
              className="text-xxs uppercase tracking-widest flex-shrink-0"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              SCAN:
            </span>
            {loadingScans ? (
              <div className="flex items-center gap-1" style={{ color: '#6b7a90' }}>
                <RefreshCw className="h-3 w-3 animate-spin" style={{ color: '#00ffc8' }} />
                <span className="text-xxs" style={{ fontFamily: "'JetBrains Mono', monospace" }}>Loading...</span>
              </div>
            ) : (
              <select
                value={currentScanId || ''}
                onChange={(e) => onScanChange(parseInt(e.target.value, 10))}
                disabled={!selectedProjectId || scans.length === 0}
                className="input py-1.5 px-3 w-60 text-xs"
              >
                {scans.length === 0 ? (
                  <option value="">{selectedProjectId ? 'No scans found' : '-- Select Project First --'}</option>
                ) : (
                  scans.map((scan: Scan) => (
                    <option key={scan.id} value={scan.id}>
                      {new Date(scan.created_at).toLocaleString()} ({scan.status})
                    </option>
                  ))
                )}
              </select>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
