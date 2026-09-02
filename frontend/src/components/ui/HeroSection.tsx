'use client';

import { Suspense, lazy } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

/* ─────────────────────────────────────────────
   Types
───────────────────────────────────────────── */


/* ─────────────────────────────────────────────
   Lazy-loaded 3-D canvas (code-split chunk)
───────────────────────────────────────────── */
const NetworkCanvas = lazy(() =>
  import('./HeroNetworkCanvas').then((m) => ({ default: m.HeroNetworkCanvas }))
);

/* ─────────────────────────────────────────────
   Animation variants
───────────────────────────────────────────── */
const STAGGER_CONTAINER = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.12, delayChildren: 0.3 },
  },
};

const WORD_VARIANT = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
  },
};

const FADE_UP = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] as const },
  },
};

/* ─────────────────────────────────────────────
   HeroSection
───────────────────────────────────────────── */
export function HeroSection({
  title1 = 'THE NEW STANDARD'.split(' '),
  title2 = 'IN THREAT DEFENSE'.split(' '),
  subtitle = 'Autonomous SBOM auditing. Real-time vulnerability detection.\nZero-trust software supply chain intelligence.',
  ctaText = 'VIEW LIVE DASHBOARD'
}: {
  title1?: string[];
  title2?: string[];
  subtitle?: React.ReactNode;
  ctaText?: string;
}) {
  const shouldReduceMotion = useReducedMotion();

  const handleCTAClick = () => {
    const next = document.getElementById('dashboard-content');
    if (next) {
      next.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      className="hero-section"
      style={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* ── Background gradient ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 80% 60% at 50% -10%, #001a2e 0%, #00050f 60%, #000000 100%)',
          zIndex: 0,
        }}
      />

      {/* ── Cyber grid ── */}
      <div
        aria-hidden="true"
        className="cyber-grid"
        style={{ position: 'absolute', inset: 0, zIndex: 1 }}
      />

      {/* ── Scanline overlay ── */}
      <div
        aria-hidden="true"
        className="scanline-overlay"
        style={{ position: 'absolute', inset: 0, zIndex: 2 }}
      />

      {/* ── Three.js Network Canvas (lazy, skipped for reduced-motion) ── */}
      {!shouldReduceMotion && (
        <Suspense fallback={null}>
          <NetworkCanvas />
        </Suspense>
      )}

      {/* ── Foreground Content ── */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          paddingTop: '10rem',
          paddingLeft: '1.5rem',
          paddingRight: '1.5rem',
          flex: 1,
        }}
      >
        {/* Label */}
        <motion.p
          custom={0}
          variants={FADE_UP}
          initial="hidden"
          animate="visible"
          style={{
            fontFamily: 'monospace',
            fontSize: '0.7rem',
            letterSpacing: '0.25em',
            color: '#00ffc8',
            marginBottom: '2rem',
            opacity: 0.85,
          }}
        >
          [ AUTONOMOUS SOC PLATFORM v2.6 ]
        </motion.p>

        {/* Headline */}
        <motion.h1
          variants={STAGGER_CONTAINER}
          initial="hidden"
          animate="visible"
          style={{
            fontFamily: 'monospace',
            fontWeight: 900,
            textTransform: 'uppercase',
            fontSize: 'clamp(3rem, 8vw, 6rem)',
            lineHeight: 1.05,
            color: '#ffffff',
            marginBottom: '1.75rem',
            maxWidth: '900px',
          }}
        >
          {/* Line 1 */}
          <span style={{ display: 'block' }}>
            {title1.map((word, i) => (
              <motion.span
                key={`h1-${i}`}
                variants={WORD_VARIANT}
                style={{ display: 'inline-block', marginRight: '0.35em' }}
              >
                {word}
              </motion.span>
            ))}
          </span>
          {/* Line 2 — accent color */}
          <span style={{ display: 'block', color: '#00ffc8' }}>
            {title2.map((word, i) => (
              <motion.span
                key={`h2-${i}`}
                variants={WORD_VARIANT}
                style={{ display: 'inline-block', marginRight: '0.35em' }}
              >
                {word}
              </motion.span>
            ))}
          </span>
        </motion.h1>

        {/* Subtext */}
        <motion.p
          custom={0.9}
          variants={FADE_UP}
          initial="hidden"
          animate="visible"
          style={{
            fontFamily: 'monospace',
            fontSize: 'clamp(0.8rem, 1.6vw, 1rem)',
            color: 'rgba(255,255,255,0.45)',
            lineHeight: 1.9,
            maxWidth: '580px',
            marginBottom: '3rem',
            whiteSpace: 'pre-line',
          }}
        >
          {subtitle}
        </motion.p>

        {/* CTA */}
        <motion.div
          custom={1.3}
          variants={FADE_UP}
          initial="hidden"
          animate="visible"
        >
          <button
            className="btn-primary"
            onClick={handleCTAClick}
            style={{
              fontFamily: 'monospace',
              letterSpacing: '0.12em',
              fontSize: '0.85rem',
              display: 'inline-block',
            }}
          >
            [ {ctaText} ]
          </button>
        </motion.div>
      </div>

      {/* ── Bottom accent line + glow dot ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '1px',
          background:
            'linear-gradient(90deg, transparent, rgba(0,255,200,0.15) 30%, rgba(0,255,200,0.35) 50%, rgba(0,255,200,0.15) 70%, transparent)',
          zIndex: 10,
        }}
      >
        {/* glow dot */}
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: '#00ffc8',
            boxShadow:
              '0 0 12px 4px rgba(0,255,200,0.6), 0 0 32px 12px rgba(0,255,200,0.2)',
          }}
        />
      </div>
    </section>
  );
}
