export interface Project {
  id: number;
  name: string;
  description: string | null;
  status: 'active' | 'archived' | 'deleted';
  created_at: string;
  updated_at: string;
  ecosystems?: ProjectEcosystem[];
  scan_count?: number;
  latest_scan?: ScanSummary;
}

export interface ProjectEcosystem {
  id: number;
  ecosystem: 'npm' | 'pypi' | 'maven' | 'unknown';
  manifest_path: string;
  lockfile_path: string | null;
  detected_at: string;
}

export interface ScanSummary {
  id: number;
  status: string;
  risk_score: number;
  risk_level: string;
  total_dependencies: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  created_at: string;
}

export interface Scan {
  id: number;
  project_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  scan_type: string;
  total_dependencies: number;
  direct_dependencies: number;
  transitive_dependencies: number;
  dev_dependencies: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  risk_score: number;
  risk_level: string;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  scan_metadata: Record<string, any> | null;
  dependencies?: Dependency[];
  vulnerabilities?: Vulnerability[];
  risk_findings?: RiskFinding[];
}

export interface Dependency {
  id: number;
  scan_id: number;
  name: string;
  ecosystem: string;
  declared_version: string | null;
  resolved_version: string | null;
  latest_version: string | null;
  recommended_version: string | null;
  dependency_type: 'direct' | 'transitive' | 'development' | 'optional' | 'peer';
  purl: string | null;
  license: string | null;
  license_url: string | null;
  status: 'safe' | 'vulnerable' | 'review' | 'unknown';
  risk_score: number;
  has_lifecycle_scripts: boolean;
  lifecycle_scripts: Record<string, any> | null;
  typosquatting_flag: boolean;
  typosquatting_details: Record<string, any> | null;
  package_metadata: Record<string, any> | null;
  dependency_path: string[] | null;
  created_at: string;
  updated_at: string;
  vulnerabilities?: Vulnerability[];
  license_info?: LicenseInfo;
  relationships?: DependencyRelationship[];
}

export interface DependencySummary {
  id: number;
  name: string;
  ecosystem: string;
  declared_version: string | null;
  resolved_version: string | null;
  latest_version: string | null;
  recommended_version: string | null;
  dependency_type: string;
  purl: string | null;
  license: string | null;
  status: string;
  risk_score: number;
  has_lifecycle_scripts: boolean;
  typosquatting_flag: boolean;
}

export interface DependencyStatusRow {
  package: string;
  type: string;
  declared: string | null;
  installed: string | null;
  latest: string | null;
  security: string;
  severity: string | null;
  fixed_version: string | null;
  risk: number;
  purl: string | null;
  license: string | null;
  has_lifecycle_scripts: boolean;
  typosquatting_flag: boolean;
  dependency_path: string[] | null;
}

export interface DependencyTreeNode {
  id: number;
  name: string;
  version: string;
  ecosystem: string;
  dependency_type: string;
  status: string;
  risk_score: number;
  vulnerabilities_count: number;
  children: DependencyTreeNode[];
  parent_id: number | null;
}

export interface Vulnerability {
  id: number;
  scan_id: number;
  dependency_id: number;
  osv_id: string;
  cve_id: string | null;
  ghsa_id: string | null;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'none' | 'unknown';
  cvss_score: number | null;
  cvss_vector: string | null;
  summary: string | null;
  details: string | null;
  affected_versions: string | null;
  fixed_version: string | null;
  references: any[] | null;
  published_at: string | null;
  modified_at: string | null;
  created_at: string;
  dependency?: Dependency;
}

export interface VulnerabilitySummary {
  id: number;
  dependency_id: number;
  dependency_name: string;
  osv_id: string;
  cve_id: string | null;
  ghsa_id: string | null;
  severity: string;
  cvss_score: number | null;
  affected_versions: string | null;
  fixed_version: string | null;
  published_at: string | null;
}

export interface VulnerabilityStats {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  unknown: number;
  by_ecosystem: Record<string, Record<string, number>>;
  by_severity: Record<string, number>;
}

export interface RiskFinding {
  id: number;
  scan_id: number;
  dependency_id: number | null;
  finding_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  recommendation: string | null;
  evidence: Record<string, any> | null;
  affected_versions: string | null;
  fixed_version: string | null;
  cve_ids: string[] | null;
  osv_ids: string[] | null;
  score_contribution: number;
  created_at: string;
}

export interface RiskFindingSummary {
  id: number;
  finding_type: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string | null;
  score_contribution: number;
}

export interface RiskScore {
  score: number;
  level: string;
  max_score: number;
  breakdown: Record<string, number>;
  findings: RiskFindingSummary[];
  summary: string;
}

export interface SBOMComponent {
  type: string;
  name: string;
  version: string;
  purl: string | null;
  description: string | null;
  licenses: any[] | null;
  hashes: any[] | null;
  external_references: any[] | null;
  properties: Record<string, any> | null;
}

export interface SBOMDependency {
  ref: string;
  depends_on: string[];
}

export interface SBOMVulnerability {
  id: string;
  source: any | null;
  ratings: any[] | null;
  cwes: number[] | null;
  description: string | null;
  recommendations: any[] | null;
  advisories: any[] | null;
  affects: any[] | null;
  properties: Record<string, any> | null;
}

export interface SBOMMetadata {
  timestamp: string;
  tools: any[] | null;
  authors: any[] | null;
  component: SBOMComponent | null;
  manufacture: any | null;
  supplier: any | null;
  licenses: any[] | null;
  properties: Record<string, any> | null;
}

export interface SBOMResponse {
  bomFormat: string;
  specVersion: string;
  serialNumber: string | null;
  version: number;
  metadata: SBOMMetadata | null;
  components: SBOMComponent[];
  services: any[];
  dependencies: SBOMDependency[];
  compositions: any[];
  vulnerabilities: SBOMVulnerability[];
}

export interface SBOMExplorerFilters {
  ecosystem?: string;
  dependency_type?: string;
  status?: string;
  search?: string;
  has_vulnerabilities?: boolean;
  license?: string;
}

export interface SBOMExplorerResponse {
  components: SBOMExplorerComponent[];
  total: number;
  page: number;
  page_size: number;
  filters: SBOMExplorerFilters;
}

export interface SBOMExplorerComponent {
  id: number;
  name: string;
  version: string;
  ecosystem: string;
  dependency_type: string;
  purl: string | null;
  license: string | null;
  status: string;
  vulnerabilities_count: number;
  vulnerabilities: string[];
  latest_version: string | null;
  recommended_version: string | null;
  has_lifecycle_scripts: boolean;
  typosquatting_flag: boolean;
}

export interface LicenseInfo {
  id: number;
  spdx_id: string | null;
  name: string | null;
  url: string | null;
  risk_level: string;
  is_osi_approved: boolean;
  is_fsf_libre: boolean;
}

export interface DependencyRelationship {
  id: number;
  dependency_id: number;
  parent_dependency_id: number;
  relationship_type: string;
}

export interface ScanComparison {
  scan_1: Scan;
  scan_2: Scan;
  new_dependencies: DependencySummary[];
  removed_dependencies: DependencySummary[];
  new_vulnerabilities: VulnerabilitySummary[];
  resolved_vulnerabilities: VulnerabilitySummary[];
  version_changes: Array<{ package: string; old_version: string; new_version: string }>;
  risk_score_change: number;
}

export interface ReportSummary {
  project: { id: number; name: string };
  scan: { id: number; risk_score: number; risk_level: string; total_dependencies: number };
  dependency_stats: {
    by_ecosystem: Record<string, { total: number; direct: number; transitive: number; dev: number }>;
    by_type: { direct: number; transitive: number; development: number };
  };
  vulnerability_stats: Record<string, number>;
  risk_findings_summary: Record<string, { count: number; total_score: number }>;
  top_recommendations: Recommendation[];
}

export interface Recommendation {
  priority: 'critical' | 'high' | 'medium' | 'low';
  action: string;
  reason: string;
  package: string;
  current_version: string | null;
  fixed_version: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}