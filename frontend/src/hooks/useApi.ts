import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../services/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseApiOptions {
  immediate?: boolean;
}

export function useApi<T>(
  apiCall: () => Promise<T>, 
  options: UseApiOptions = {}, 
  deps: any[] = []
) {
  const { immediate = true } = options;
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const apiCallRef = useRef(apiCall);
  useEffect(() => {
    apiCallRef.current = apiCall;
  }, [apiCall]);

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await apiCallRef.current();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error');
      setState({ data: null, loading: false, error: err });
      throw err;
    }
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, immediate]);

  return { ...state, execute, refetch: execute };
}

export function useProjects() {
  return useApi(() => api.getProjects(), {}, []);
}

export function useProject(id: number | null) {
  return useApi(() => api.getProject(id!), { immediate: !!id }, [id]);
}

export function useScans(projectId: number | null) {
  return useApi(() => api.getScans(projectId!), { immediate: !!projectId }, [projectId]);
}

export function useLatestScan(projectId: number | null) {
  return useApi(() => api.getLatestScan(projectId!), { immediate: !!projectId }, [projectId]);
}

export function useScan(scanId: number | null) {
  return useApi(() => api.getScan(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useScanDependencies(
  scanId: number | null, 
  filters?: {
    ecosystem?: string;
    dependency_type?: string;
    status?: string;
  }
) {
  return useApi(
    () => api.getScanDependencies(scanId!, filters),
    { immediate: !!scanId },
    [scanId, filters?.ecosystem, filters?.dependency_type, filters?.status]
  );
}

export function useDependencyStatus(scanId: number | null) {
  return useApi(() => api.getDependencyStatus(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useDependencyTree(scanId: number | null) {
  return useApi(() => api.getDependencyTree(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useScanVulnerabilities(scanId: number | null, severity?: string) {
  return useApi(
    () => api.getScanVulnerabilities(scanId!, severity),
    { immediate: !!scanId },
    [scanId, severity]
  );
}

export function useVulnerabilityStats(scanId: number | null) {
  return useApi(() => api.getVulnerabilityStats(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useVulnerability(vulnerabilityId: number | null) {
  return useApi(() => api.getVulnerability(vulnerabilityId!), { immediate: !!vulnerabilityId }, [vulnerabilityId]);
}

export function useScanRisk(scanId: number | null) {
  return useApi(() => api.getScanRisk(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useSBOM(scanId: number | null) {
  return useApi(() => api.getSBOM(scanId!), { immediate: !!scanId }, [scanId]);
}

export function useSBOMExplorer(scanId: number | null, filters: any, page = 1, pageSize = 50) {
  return useApi(
    () => api.exploreSBOM(scanId!, filters, page, pageSize),
    { immediate: !!scanId },
    [
      scanId,
      filters?.ecosystem,
      filters?.dependency_type,
      filters?.status,
      filters?.search,
      filters?.has_vulnerabilities,
      filters?.license,
      page,
      pageSize
    ]
  );
}

export function useReportSummary(scanId: number | null) {
  return useApi(() => api.getReportSummary(scanId!), { immediate: !!scanId }, [scanId]);
}