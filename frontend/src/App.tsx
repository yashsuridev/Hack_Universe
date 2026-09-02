import { Routes, Route, Navigate, useParams } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { SbomHubPage } from './pages/SbomHubPage';
import { Projects } from './pages/Projects';
import { ProjectDetail } from './pages/ProjectDetail';
import { VulnerabilitiesPage as Vulnerabilities } from './pages/Vulnerabilities';
import { SBOMExplorerPage as SBOMExplorer } from './pages/SBOMExplorer';
import { DependencyTreePage as DependencyTree } from './pages/DependencyTree';
import { ReportsPage as Reports } from './pages/Reports';
import { SettingsPage as Settings } from './pages/Settings';
// @ts-ignore
import AutonomousResponsePage from './pages/AutonomousResponse/AutonomousResponsePage';
import { NetworkScannerPage } from './pages/NetworkScannerPage';

function ScanRedirect() {
  const { scanId } = useParams<{ scanId: string }>();
  return <Navigate to={`/vulnerabilities/${scanId}`} replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route element={<MainLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="sbom-hub" element={<SbomHubPage />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/:projectId" element={<ProjectDetail />} />
        <Route path="vulnerabilities" element={<Vulnerabilities />} />
        <Route path="vulnerabilities/:scanId" element={<Vulnerabilities />} />
        <Route path="sbom" element={<SBOMExplorer />} />
        <Route path="sbom/:scanId" element={<SBOMExplorer />} />
        <Route path="dependency-tree" element={<DependencyTree />} />
        <Route path="dependency-tree/:scanId" element={<DependencyTree />} />
        <Route path="reports" element={<Reports />} />
        <Route path="reports/:scanId" element={<Reports />} />
        <Route path="scans/:scanId" element={<ScanRedirect />} />
        <Route path="network-scanner" element={<NetworkScannerPage />} />
        <Route path="autonomous-response" element={<AutonomousResponsePage />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;