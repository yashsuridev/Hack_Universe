import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Plus,
  Search,
  Package,
  Shield,
  Clock,
  X,
} from 'lucide-react';
import { motion, Variants } from 'framer-motion';
import { useProjects } from '../hooks/useApi';
import { api } from '../services/api';
import { formatRelativeTime } from '../utils/helpers';
import type { Project } from '../types';
import { AnimatedCard } from '../components/ui/AnimatedCard';

/* ─── animation variants ─────────────────────────────────────── */
const containerVariants: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.07,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 24, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring' as const, stiffness: 260, damping: 22 },
  },
};

/* ─── risk badge helper ───────────────────────────────────────── */
function RiskBadge({ level }: { level: string }) {
  const cls =
    level === 'CRITICAL'
      ? 'badge-critical'
      : level === 'HIGH'
      ? 'badge-high'
      : level === 'MEDIUM'
      ? 'badge-medium'
      : 'badge-low';
  return <span className={cls}>{level}</span>;
}

/* ─── main page ───────────────────────────────────────────────── */
export function Projects() {
  const navigate = useNavigate();
  const { data: projects, loading, refetch } = useProjects();
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  const filteredProjects =
    projects?.filter(
      (p) =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.description?.toLowerCase().includes(search.toLowerCase())
    ) || [];

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    setCreating(true);
    try {
      await api.createProject({
        name: newProjectName.trim(),
        description: newProjectDesc.trim() || undefined,
      });
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectDesc('');
      refetch();
    } catch (error) {
      alert('Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (project: Project) => {
    if (
      !confirm(
        `Are you sure you want to delete "${project.name}"? This will also delete all its scans.`
      )
    ) {
      return;
    }
    try {
      await api.deleteProject(project.id);
      refetch();
    } catch (error) {
      alert('Failed to delete project');
    }
  };

  return (
    <div
      className="max-w-7xl mx-auto"
      style={{ fontFamily: "'JetBrains Mono', monospace" }}
    >
      {/* ── Page header ── */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p
            className="text-xs tracking-widest mb-1"
            style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
          >
            [ ACTIVE SCAN TARGETS ]
          </p>
          <h1
            className="cyber-heading text-3xl font-bold uppercase tracking-widest"
            style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
          >
            PROJECTS
          </h1>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
          aria-label="Create new project"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </button>
      </div>

      {/* ── Search bar ── */}
      <div className="card mb-6">
        <div className="card-body">
          <div className="relative max-w-md">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5"
              style={{ color: '#6b7a90' }}
              aria-hidden="true"
            />
            <input
              type="search"
              placeholder="Search projects..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-10"
              aria-label="Search projects"
            />
          </div>
        </div>
      </div>

      {/* ── States ── */}
      {loading ? (
        <div className="card">
          <div className="card-body text-center py-12 flex flex-col items-center gap-4">
            {/* Cyber accent spinner */}
            <div
              className="h-10 w-10 rounded-sm border-2 animate-spin"
              style={{
                borderColor: 'transparent',
                borderTopColor: '#00ffc8',
                borderRightColor: '#00ffc8',
              }}
              role="status"
              aria-label="Loading projects"
            />
            <p
              className="text-sm tracking-widest uppercase"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              Fetching projects...
            </p>
          </div>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-16 flex flex-col items-center gap-4">
            <Package
              className="h-16 w-16"
              style={{ color: '#00ffc8', opacity: 0.35 }}
              aria-hidden="true"
            />
            <h3
              className="text-lg font-medium uppercase tracking-widest"
              style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
            >
              {search ? 'No matching projects' : 'No projects yet'}
            </h3>
            <p
              className="text-sm"
              style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
            >
              {search
                ? 'Try adjusting your search terms'
                : 'Create your first project to start scanning for vulnerabilities.'}
            </p>
            {!search && (
              <button
                className="mt-2 btn-primary"
                onClick={() => setShowCreateModal(true)}
                aria-label="Create first project"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </button>
            )}
          </div>
        </div>
      ) : (
        <motion.div
          className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {filteredProjects.map((project) => (
            <motion.div key={project.id} variants={itemVariants}>
              <ProjectCard
                project={project}
                onView={() => navigate(`/projects/${project.id}`)}
                onDelete={() => handleDelete(project)}
              />
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* ── Create modal ── */}
      {showCreateModal && (
        <CreateProjectModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreate}
          creating={creating}
          name={newProjectName}
          setName={setNewProjectName}
          description={newProjectDesc}
          setDescription={setNewProjectDesc}
        />
      )}
    </div>
  );
}

/* ─── ProjectCard ─────────────────────────────────────────────── */
function ProjectCard({
  project,
  onView,
  onDelete,
}: {
  project: Project;
  onView: () => void;
  onDelete: () => void;
}) {
  return (
    <AnimatedCard intensity={6} className="h-full">
      <Link
        to={`/projects/${project.id}`}
        className="block h-full"
        tabIndex={0}
        aria-label={`Open project ${project.name}`}
      >
        <div className="card-body h-full flex flex-col">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3
                className="text-base font-bold uppercase tracking-widest truncate"
                style={{ color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
              >
                {project.name}
              </h3>
              {project.description && (
                <p
                  className="mt-1 text-sm line-clamp-2"
                  style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
                >
                  {project.description}
                </p>
              )}
            </div>
            <Shield
              className="h-9 w-9 flex-shrink-0 ml-2"
              style={{ color: '#00ffc8', opacity: 0.7 }}
              aria-hidden="true"
            />
          </div>

          {/* Meta row */}
          <div
            className="mt-4 flex items-center gap-4 text-sm"
            style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
          >
            <span className="flex items-center gap-1">
              <Package className="h-4 w-4" aria-hidden="true" />
              {project.scan_count || 0} scans
            </span>
            {project.latest_scan && (
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" aria-hidden="true" />
                {formatRelativeTime(project.latest_scan.created_at)}
              </span>
            )}
          </div>

          {/* Risk badge */}
          {project.latest_scan && (
            <div className="mt-4 flex items-center gap-3">
              <RiskBadge level={project.latest_scan.risk_level} />
              <span
                className="text-sm"
                style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}
              >
                Score: {project.latest_scan.risk_score.toFixed(1)}/100
              </span>
            </div>
          )}

          {/* Spacer */}
          <div className="flex-1" />

          {/* Actions */}
          <div
            className="mt-4 pt-4 flex items-center justify-end gap-2"
            style={{ borderTop: '1px solid #1e2736' }}
          >
            <button
              onClick={(e) => {
                e.preventDefault();
                onDelete();
              }}
              className="btn-ghost text-sm transition-colors"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
              aria-label={`Delete project ${project.name}`}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLButtonElement).style.color = '#ff4d4d')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLButtonElement).style.color = '')
              }
            >
              Delete
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                onView();
              }}
              className="btn-ghost text-sm"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
              aria-label={`View details for ${project.name}`}
            >
              View Details
            </button>
          </div>
        </div>
      </Link>
    </AnimatedCard>
  );
}

/* ─── CreateProjectModal ──────────────────────────────────────── */
function CreateProjectModal({
  onClose,
  onSubmit,
  creating,
  name,
  setName,
  description,
  setDescription,
}: {
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  creating: boolean;
  name: string;
  setName: (v: string) => void;
  description: string;
  setDescription: (v: string) => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.72)' }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Create project modal"
    >
      <motion.div
        className="max-w-md w-full"
        style={{
          background: '#161b27',
          border: '1px solid #1e2736',
          borderRadius: '2px',
          fontFamily: "'JetBrains Mono', monospace",
        }}
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ type: 'spring' as const, stiffness: 300, damping: 28 }}
      >
        <form onSubmit={onSubmit}>
          {/* Modal header */}
          <div
            className="p-6 flex items-center justify-between"
            style={{ borderBottom: '1px solid #1e2736' }}
          >
            <div>
              <p
                className="text-xs tracking-widest mb-0.5"
                style={{ color: '#6b7a90' }}
              >
                [ NEW TARGET ]
              </p>
              <h2
                className="text-base font-bold uppercase tracking-widest"
                style={{ color: '#eaf5ee' }}
              >
                Create Project
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-1 transition-colors"
              style={{ color: '#6b7a90' }}
              aria-label="Close modal"
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLButtonElement).style.color = '#ff4d4d')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLButtonElement).style.color = '#6b7a90')
              }
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>

          {/* Modal body */}
          <div className="p-6 space-y-4">
            <div>
              <label
                htmlFor="name"
                className="block text-xs font-medium uppercase tracking-widest mb-1"
                style={{ color: '#6b7a90' }}
              >
                Project Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="e.g., my-web-app"
                required
                disabled={creating}
                autoFocus
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              />
            </div>
            <div>
              <label
                htmlFor="description"
                className="block text-xs font-medium uppercase tracking-widest mb-1"
                style={{ color: '#6b7a90' }}
              >
                Description{' '}
                <span style={{ color: '#6b7a90', textTransform: 'none' }}>
                  (optional)
                </span>
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input min-h-[100px] resize-none"
                placeholder="Brief description of the project..."
                disabled={creating}
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              />
            </div>
          </div>

          {/* Modal footer */}
          <div
            className="p-6 flex justify-end gap-3"
            style={{ borderTop: '1px solid #1e2736' }}
          >
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={creating}
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={creating || !name.trim()}
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}