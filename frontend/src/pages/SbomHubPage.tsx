import { Link } from 'react-router-dom';
import { Package, Shield, FileText, Share2, AlertTriangle } from 'lucide-react';
import { HeroSection } from '../components/ui/HeroSection';
import { AnimatedCard } from '../components/ui/AnimatedCard';

export function SbomHubPage() {
  return (
    <div style={{ background: '#0a0a0a' }}>
      <HeroSection 
        title1={['SBOM', 'AUDITOR']} 
        title2={['COMMAND', 'CENTER']} 
        subtitle={'Manage projects, explore dependencies, and generate compliance reports.\nComplete visibility into your software supply chain.'}
        ctaText={'EXPLORE SBOM MODULES'}
      />

      <div id="dashboard-content" style={{ scrollMarginTop: '80px', paddingBottom: '100px' }}>
        <section className="py-24 relative" style={{ background: '#0a0a0a' }}>
          <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />
          <div className="max-w-7xl mx-auto px-6 relative z-10">
            
            <div className="mb-12">
              <h2 className="cyber-heading text-3xl">SBOM MODULES</h2>
              <p className="mt-3 text-sm" style={{ color: '#6b7a90', fontFamily: "'JetBrains Mono', monospace" }}>
                Select a module to view your software bill of materials data.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <Link to="/projects">
                <AnimatedCard intensity={5}>
                  <div className="card-body text-center py-12">
                    <Package className="h-12 w-12 mx-auto mb-4" style={{ color: '#00ffc8' }} />
                    <h3 className="text-xl font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>Projects</h3>
                    <p className="text-xs" style={{ color: '#6b7a90' }}>Manage your scanned repositories and upload new ZIP archives.</p>
                  </div>
                </AnimatedCard>
              </Link>

              <Link to="/vulnerabilities">
                <AnimatedCard intensity={5}>
                  <div className="card-body text-center py-12">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-4" style={{ color: '#ff4d4d' }} />
                    <h3 className="text-xl font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>Vulnerabilities</h3>
                    <p className="text-xs" style={{ color: '#6b7a90' }}>Review critical CVEs and risk findings across all dependencies.</p>
                  </div>
                </AnimatedCard>
              </Link>

              <Link to="/sbom">
                <AnimatedCard intensity={5}>
                  <div className="card-body text-center py-12">
                    <Shield className="h-12 w-12 mx-auto mb-4" style={{ color: '#00c89a' }} />
                    <h3 className="text-xl font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>SBOM Explorer</h3>
                    <p className="text-xs" style={{ color: '#6b7a90' }}>Deep dive into your component manifest and licenses.</p>
                  </div>
                </AnimatedCard>
              </Link>

              <Link to="/dependency-tree">
                <AnimatedCard intensity={5}>
                  <div className="card-body text-center py-12">
                    <Share2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#ffd700' }} />
                    <h3 className="text-xl font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>Dependency Tree</h3>
                    <p className="text-xs" style={{ color: '#6b7a90' }}>Visualize transitive dependencies and pinpoint risks.</p>
                  </div>
                </AnimatedCard>
              </Link>

              <Link to="/reports">
                <AnimatedCard intensity={5}>
                  <div className="card-body text-center py-12">
                    <FileText className="h-12 w-12 mx-auto mb-4" style={{ color: '#06B6D4' }} />
                    <h3 className="text-xl font-bold uppercase tracking-wide mb-2" style={{ color: '#eaf5ee' }}>Reports</h3>
                    <p className="text-xs" style={{ color: '#6b7a90' }}>Export executive summaries and compliance documents.</p>
                  </div>
                </AnimatedCard>
              </Link>
            </div>
            
          </div>
        </section>
      </div>
    </div>
  );
}
