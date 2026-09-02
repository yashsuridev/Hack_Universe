import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Navbar } from '../components/ui/Navbar';
import { Footer } from '../components/ui/Footer';

export function MainLayout() {
  const location = useLocation();

  // Scroll-driven background gradient via CSS custom properties
  useEffect(() => {
    const onScroll = () => {
      const scrollY = window.scrollY;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const progress = maxScroll > 0 ? scrollY / maxScroll : 0;

      // Create a wave: 0 → 1 → 0 as user scrolls
      const wave = Math.sin(progress * Math.PI);
      document.documentElement.style.setProperty('--scroll-progress', String(progress));
      document.documentElement.style.setProperty('--bg-gradient-alpha', String(wave));
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Scroll to top on route change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [location.pathname]);

  const fullBleedRoutes = ['/dashboard', '/sbom-hub', '/network-scanner', '/autonomous-response'];
  const isFullBleed = fullBleedRoutes.includes(location.pathname);

  return (
    <div
      className="min-h-screen"
      style={{ background: '#0a0a0a', color: '#eaf5ee', fontFamily: "'JetBrains Mono', monospace" }}
    >
      {/* Fixed Navbar */}
      <Navbar />

      {/* Main content — push below fixed navbar */}
      <main
        id="main-content"
        style={{ paddingTop: isFullBleed ? '0' : '64px' }}
        aria-label="Main content"
      >
        {isFullBleed ? (
          // Full-bleed treatment (hero handles its own top spacing)
          <Outlet />
        ) : (
          // Other pages get padded content area
          <div
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
            id="dashboard-content"
          >
            <Outlet />
          </div>
        )}
      </main>

      {/* Global Footer */}
      <Footer />
    </div>
  );
}