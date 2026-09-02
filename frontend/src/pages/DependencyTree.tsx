import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
} from 'lucide-react';
import { useDependencyTree } from '../hooks/useApi';
import type { DependencyTreeNode } from '../types';
import { ScanSelectorHeader } from '../components/ScanSelectorHeader';
import { motion } from 'framer-motion';

export function DependencyTreePage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const { data: treeData, refetch, loading } = useDependencyTree(scanId ? parseInt(scanId, 10) : null);

  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const selectedNode = selectedNodeId && treeData ? treeData.find((n: any) => n.id === selectedNodeId) : null;

  useEffect(() => {
    if (scanId) {
      refetch();
    }
  }, [scanId]);

  const nodes = treeData || [];
  const relationships = nodes.filter(n => n.parent_id).map(n => ({ dependency_id: n.id, parent_dependency_id: n.parent_id, risk: n.risk_score }));

  const getNodeColor = (node: DependencyTreeNode) => {
    if (!node) return '#1e2736';
    const risk = node.risk_score;
    if (risk >= 70) return '#ff4d4d';
    if (risk >= 40) return '#ff8c42';
    if (risk >= 20) return '#ffd700';
    return '#00ffc8';
  };

  const handleNodeClick = (nodeId: number) => {
    setSelectedNodeId(nodeId);
  };

  const getRiskBadgeStyle = (score: number) => {
    if (score >= 70) return { color: '#ff4d4d', background: 'rgba(255,77,77,0.1)', border: '1px solid rgba(255,77,77,0.3)' };
    if (score >= 40) return { color: '#ff8c42', background: 'rgba(255,140,66,0.1)', border: '1px solid rgba(255,140,66,0.3)' };
    if (score >= 20) return { color: '#ffd700', background: 'rgba(255,215,0,0.1)', border: '1px solid rgba(255,215,0,0.25)' };
    return { color: '#00ffc8', background: 'rgba(0,255,200,0.08)', border: '1px solid rgba(0,255,200,0.2)' };
  };

  return (
    <div className="max-w-7xl mx-auto">
      <ScanSelectorHeader
        currentScanId={scanId ? parseInt(scanId, 10) : null}
        onScanChange={(id) => navigate(`/dependency-tree/${id}`)}
        title="Dependency Tree"
      />

      {!scanId ? (
        <motion.div
          className="card py-16 text-center"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <LayoutDashboard className="h-14 w-14 mx-auto mb-4 opacity-20" style={{ color: '#00ffc8' }} />
          <h2
            className="text-base font-bold uppercase tracking-widest mb-2"
            style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
          >
            NO SCAN SELECTED
          </h2>
          <p className="text-xs" style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}>
            Please select a project and scan from the dropdowns above to view the dependency tree.
          </p>
        </motion.div>
      ) : loading ? (
        <div
          className="h-96 flex items-center justify-center card"
        >
          <div className="text-center">
            <div
              className="w-8 h-8 border-2 rounded-full mx-auto mb-3 animate-spin"
              style={{ borderColor: '#1e2736', borderTopColor: '#00ffc8' }}
            />
            <span className="text-xs uppercase tracking-widest" style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}>
              LOADING DEPENDENCY TREE...
            </span>
          </div>
        </div>
      ) : nodes.length === 0 ? (
        <motion.div
          className="h-96 flex flex-col items-center justify-center card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <Package className="h-14 w-14 mb-4 opacity-20" style={{ color: '#00ffc8' }} />
          <p
            className="text-base font-bold uppercase tracking-widest"
            style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
          >
            NO DEPENDENCIES FOUND
          </p>
        </motion.div>
      ) : (
        <motion.div
          className="card mb-6"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="card-header flex items-center justify-between">
            <h3
              className="text-xs font-bold uppercase tracking-widest"
              style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
            >
              DEPENDENCY TREE VISUALIZATION
            </h3>
            <div
              className="text-xxs uppercase tracking-widest"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              {nodes.length} DEPENDENCIES
            </div>
          </div>
          <div className="card-body p-0">
            <svg
              id="dependency-svg"
              width="100%"
              height="600"
              viewBox="0 0 1200 800"
              style={{
                overflow: 'auto',
                background: 'rgba(10,10,10,0.4)',
              }}
            >
              {/* Background grid lines */}
              <defs>
                <pattern id="dep-grid" width="48" height="48" patternUnits="userSpaceOnUse">
                  <path d="M 48 0 L 0 0 0 48" fill="none" stroke="rgba(0,255,200,0.03)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="1200" height="800" fill="url(#dep-grid)" />

              <g fill="none" strokeWidth="2">
                {renderConnections(nodes, relationships)}

                {nodes.map((node: DependencyTreeNode, i: number) => {
                  const cx = 200 + i * 150;
                  const cy = 100 + (i % 3) * 200;
                  const nodeColor = getNodeColor(node);
                  const isSelected = node.id === selectedNodeId;

                  return (
                    <g
                      key={i}
                      onClick={() => handleNodeClick(node.id)}
                      cursor="pointer"
                    >
                      {/* Glow ring for selected */}
                      {isSelected && (
                        <circle
                          cx={cx}
                          cy={cy}
                          r={34}
                          fill="none"
                          stroke={nodeColor}
                          strokeWidth="1"
                          opacity="0.4"
                        />
                      )}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={28}
                        fill={`${nodeColor}18`}
                        stroke={nodeColor}
                        strokeWidth={isSelected ? 2 : 1}
                        style={{
                          filter: isSelected ? `drop-shadow(0 0 8px ${nodeColor})` : `drop-shadow(0 0 4px ${nodeColor}40)`,
                        }}
                      />
                      <text
                        x={cx}
                        y={cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill={nodeColor}
                        fontFamily="JetBrains Mono, monospace"
                        fontSize={9}
                        fontWeight="600"
                      >
                        {node.name?.substring(0, 8)}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>

            {selectedNode && (
              <div
                className="m-6"
                style={{
                  background: '#161b27',
                  border: '1px solid #1e2736',
                  borderRadius: '2px',
                  padding: '1.5rem',
                }}
              >
                <h3
                  className="text-xs font-bold uppercase tracking-widest mb-4"
                  style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
                >
                  SELECTED PACKAGE DETAILS
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'PACKAGE',  value: selectedNode.name },
                    { label: 'VERSION',  value: selectedNode.version || 'unknown' },
                    { label: 'TYPE',     value: selectedNode.dependency_type || '—' },
                    { label: 'STATUS',   value: selectedNode.status || '—' },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-xxs uppercase tracking-widest mb-1" style={{ color: '#6b7a90' }}>{label}</p>
                      <p className="text-xs font-mono font-semibold capitalize" style={{ color: '#eaf5ee' }}>{value}</p>
                    </div>
                  ))}
                </div>
                {selectedNode.risk_score != null && (
                  <div className="mt-4 flex items-center gap-3">
                    <span
                      className="text-xxs font-bold uppercase tracking-wider px-2.5 py-1"
                      style={{
                        ...getRiskBadgeStyle(selectedNode.risk_score),
                        borderRadius: '1px',
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                    >
                      RISK: {selectedNode.risk_score.toFixed(1)}/100
                    </span>
                    {selectedNode.vulnerabilities_count > 0 && (
                      <span className="badge-critical">
                        {selectedNode.vulnerabilities_count} VULN{selectedNode.vulnerabilities_count > 1 ? 'S' : ''}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}

function renderConnections(nodes: any[], relationships: any[]) {
  const lines: React.ReactNode[] = [];
  const nodeMap = new Map(nodes.map((n: any, i: number) => [n.id, { x: 200 + i * 150, y: 100 + (i % 3) * 200 }]));

  relationships.forEach((rel: any, idx: number) => {
    const parent = nodeMap.get(rel.parent_dependency_id);
    const child = nodeMap.get(rel.dependency_id);
    if (parent && child) {
      const strokeColor =
        rel.risk >= 70 ? 'rgba(255,77,77,0.5)' :
        rel.risk >= 40 ? 'rgba(255,140,66,0.4)' :
        'rgba(0,255,200,0.15)';
      const strokeWidth = rel.risk >= 70 ? 2 : rel.risk >= 40 ? 1.5 : 1;
      lines.push(
        <line
          key={idx}
          x1={parent.x} y1={parent.y}
          x2={child.x} y2={child.y}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={rel.risk < 40 ? '4 4' : undefined}
        />
      );
    }
  });

  return lines;
}