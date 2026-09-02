/// <reference types="vite/client" />
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Project,
  Scan,
  DependencySummary,
  DependencyStatusRow,
  DependencyTreeNode,
  Vulnerability,
  VulnerabilitySummary,
  VulnerabilityStats,
  RiskScore,
  SBOMResponse,
  SBOMExplorerResponse,
  SBOMExplorerFilters,
  ScanComparison,
  ReportSummary,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<any>) => {
        const message = error.response?.data?.detail || error.message || 'An error occurred';
        return Promise.reject(new Error(message));
      }
    );
  }

  async getProjects(): Promise<Project[]> {
    const response = await this.client.get<Project[]>('/projects');
    return response.data;
  }

  async getProject(id: number): Promise<Project> {
    const response = await this.client.get<Project>(`/projects/${id}`);
    return response.data;
  }

  async createProject(data: { name: string; description?: string }): Promise<Project> {
    const response = await this.client.post<Project>('/projects', data);
    return response.data;
  }

  async updateProject(id: number, data: Partial<Project>): Promise<Project> {
    const response = await this.client.patch<Project>(`/projects/${id}`, data);
    return response.data;
  }

  async deleteProject(id: number): Promise<void> {
    await this.client.delete(`/projects/${id}`);
  }

  async uploadAndScan(projectId: number, file: File): Promise<Scan> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.client.post<Scan>(`/projects/${projectId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getScans(projectId: number): Promise<Scan[]> {
    const response = await this.client.get<Scan[]>(`/projects/${projectId}/scans`);
    return response.data;
  }

  async getLatestScan(projectId: number): Promise<Scan> {
    const response = await this.client.get<Scan>(`/projects/${projectId}/scans/latest`);
    return response.data;
  }

  async getScan(scanId: number): Promise<Scan> {
    const response = await this.client.get<Scan>(`/scans/${scanId}`);
    return response.data;
  }

  async getScanDependencies(scanId: number, filters?: {
    ecosystem?: string;
    dependency_type?: string;
    status?: string;
  }): Promise<DependencySummary[]> {
    const params = new URLSearchParams();
    if (filters?.ecosystem) params.append('ecosystem', filters.ecosystem);
    if (filters?.dependency_type) params.append('dependency_type', filters.dependency_type);
    if (filters?.status) params.append('status', filters.status);
    
    const response = await this.client.get<DependencySummary[]>(`/scans/${scanId}/dependencies?${params}`);
    return response.data;
  }

  async getDependencyStatus(scanId: number): Promise<DependencyStatusRow[]> {
    const response = await this.client.get<DependencyStatusRow[]>(`/scans/${scanId}/dependency-status`);
    return response.data;
  }

  async getDependencyTree(scanId: number): Promise<DependencyTreeNode[]> {
    const response = await this.client.get<DependencyTreeNode[]>(`/scans/${scanId}/dependency-tree`);
    return response.data;
  }

  async getScanVulnerabilities(scanId: number, severity?: string): Promise<VulnerabilitySummary[]> {
    const params = severity ? `?severity=${severity}` : '';
    const response = await this.client.get<VulnerabilitySummary[]>(`/scans/${scanId}/vulnerabilities${params}`);
    return response.data;
  }

  async getVulnerabilityStats(scanId: number): Promise<VulnerabilityStats> {
    const response = await this.client.get<VulnerabilityStats>(`/vulnerabilities/scan/${scanId}/stats`);
    return response.data;
  }

  async getVulnerability(vulnerabilityId: number): Promise<Vulnerability> {
    const response = await this.client.get<Vulnerability>(`/vulnerabilities/${vulnerabilityId}`);
    return response.data;
  }

  async getScanRisk(scanId: number): Promise<RiskScore> {
    const response = await this.client.get<RiskScore>(`/scans/${scanId}/risk`);
    return response.data;
  }

  async compareScans(scan1Id: number, scan2Id: number): Promise<ScanComparison> {
    const response = await this.client.post<ScanComparison>('/scans/compare', null, {
      params: { scan_1_id: scan1Id, scan_2_id: scan2Id },
    });
    return response.data;
  }

  async getSBOM(scanId: number): Promise<SBOMResponse> {
    const response = await this.client.get<SBOMResponse>(`/sbom/scan/${scanId}`);
    return response.data;
  }

  async downloadSBOM(scanId: number): Promise<Blob> {
    const response = await this.client.get(`/sbom/scan/${scanId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async exploreSBOM(scanId: number, filters: SBOMExplorerFilters, page = 1, pageSize = 50): Promise<SBOMExplorerResponse> {
    const params = new URLSearchParams();
    if (filters.ecosystem) params.append('ecosystem', filters.ecosystem);
    if (filters.dependency_type) params.append('dependency_type', filters.dependency_type);
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    if (filters.has_vulnerabilities !== undefined && filters.has_vulnerabilities !== null) {
      params.append('has_vulnerabilities', filters.has_vulnerabilities.toString());
    }
    if (filters.license) params.append('license', filters.license);
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    
    const response = await this.client.get<SBOMExplorerResponse>(`/sbom/scan/${scanId}/explorer?${params}`);
    return response.data;
  }

  async downloadJsonReport(scanId: number): Promise<Blob> {
    const response = await this.client.get(`/reports/scan/${scanId}/json`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async getReportSummary(scanId: number): Promise<ReportSummary> {
    const response = await this.client.get<ReportSummary>(`/reports/scan/${scanId}/summary`);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiService();