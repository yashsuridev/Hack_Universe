import { NavLink, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Shield, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const navLinks = [
  { name: 'Dashboard',    href: '/dashboard' },
  { name: 'SBOM',         href: '/sbom-hub' },
  { name: 'Scanner',      href: '/network-scanner' },
  { name: 'Auto-Response',href: '/autonomous-response' },
];

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMobileOpen(false);
  }, [location]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <header
        className="navbar"
        style={{
          boxShadow: scrolled
            ? '0 1px 0 rgba(0,255,200,0.06), 0 4px 24px rgba(0,0,0,0.4)'
            : 'none',
          transition: 'box-shadow 0.3s ease',
        }}
        role="banner"
      >
        {/* Logo */}
        <NavLink
          to="/dashboard"
          className="flex items-center gap-2.5 mr-6 flex-shrink-0 group"
          aria-label="Hack Universe Home"
        >
          <div className="relative">
            <Shield
              className="h-7 w-7 transition-all duration-300 group-hover:drop-shadow-[0_0_8px_rgba(0,255,200,0.8)]"
              style={{ color: '#00ffc8' }}
            />
            <div
              className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              style={{ background: 'radial-gradient(circle, rgba(0,255,200,0.15) 0%, transparent 70%)' }}
            />
          </div>
          <span
            className="text-sm font-bold uppercase tracking-widest"
            style={{ color: '#eaf5ee', letterSpacing: '0.2em' }}
          >
            HACK<span style={{ color: '#00ffc8' }}>//</span>UNIVERSE
          </span>
        </NavLink>

        {/* Nav links — pill container */}
        <nav
          className="hidden lg:flex items-center gap-1 px-3 py-1.5 ml-auto"
          style={{
            background: 'rgba(22,27,39,0.8)',
            border: '1px solid rgba(30,39,54,0.9)',
            borderRadius: '2px',
          }}
          aria-label="Primary navigation"
        >
          {navLinks.map((link) => (
            <NavLink
              key={link.href}
              to={link.href}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'active' : ''}`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </nav>

        {/* CTA + Settings */}
        <div className="flex items-center gap-3 ml-4 flex-shrink-0">
          <NavLink
            to="/settings"
            className="hidden lg:flex items-center"
          >
            <button
              id="launch-console-btn"
              className="btn-primary text-xs px-5 py-2"
              style={{ letterSpacing: '0.15em' }}
            >
              [ LAUNCH CONSOLE ]
            </button>
          </NavLink>

          {/* Mobile hamburger */}
          <button
            className="lg:hidden p-2 text-cyber-muted hover:text-cyber-accent transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/70"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              aria-hidden="true"
            />
            <motion.nav
              className="fixed top-16 left-0 right-0 z-50 border-b"
              style={{
                background: 'rgba(13,17,23,0.98)',
                backdropFilter: 'blur(20px)',
                borderColor: 'rgba(30,39,54,0.9)',
              }}
              initial={{ y: -16, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -16, opacity: 0 }}
              transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              aria-label="Mobile navigation"
            >
              <div className="flex flex-col py-2">
                {navLinks.map((link, i) => (
                  <motion.div
                    key={link.href}
                    initial={{ x: -16, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: i * 0.05, duration: 0.2 }}
                  >
                    <NavLink
                      to={link.href}
                      className={({ isActive }) =>
                        `block px-6 py-3 text-xs font-mono uppercase tracking-widest transition-colors ${
                          isActive
                            ? 'text-cyber-accent bg-cyber-panel border-l-2'
                            : 'text-cyber-muted hover:text-cyber-text hover:bg-cyber-panel'
                        }`
                      }
                      style={({ isActive }) => ({
                        borderColor: isActive ? '#00ffc8' : 'transparent',
                      })}
                    >
                      {link.name}
                    </NavLink>
                  </motion.div>
                ))}
                <div className="px-6 py-3">
                  <NavLink to="/settings">
                    <button className="btn-primary w-full text-xs py-2.5">
                      [ LAUNCH CONSOLE ]
                    </button>
                  </NavLink>
                </div>
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
