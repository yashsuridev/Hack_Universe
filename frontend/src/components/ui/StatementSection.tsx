import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

export function StatementSection() {
  return (
    <section
      className="relative py-24 overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #0a0f1e 50%, #0a0a0a 100%)' }}
    >
      {/* Subtle noise overlay */}
      <div className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(ellipse 60% 40% at 80% 50%, rgba(0,255,200,0.04) 0%, transparent 70%)`,
        }}
      />

      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24">
        <div className="grid lg:grid-cols-2 gap-16 items-center">

          {/* LEFT: Bold heading */}
          <motion.div
            initial={{ opacity: 0, x: -32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-6" style={{ color: '#6b7a90' }}>
              WHY HACK//UNIVERSE
            </p>
            <h2 className="cyber-heading" style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)', lineHeight: 1.05 }}>
              SECURITY ISN'T A
              <br />
              <span style={{ color: '#00ffc8' }}>CHECKBOX.</span>
              <br />
              IT'S A POSTURE.
            </h2>
          </motion.div>

          {/* RIGHT: paragraph + CTA */}
          <motion.div
            className="flex gap-6"
            initial={{ opacity: 0, x: 32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Accent vertical bar */}
            <div
              className="w-0.5 flex-shrink-0 self-stretch"
              style={{
                background: 'linear-gradient(to bottom, #00ffc8, rgba(0,255,200,0.1))',
              }}
            />

            <div className="flex flex-col gap-6">
              <p className="text-sm leading-relaxed" style={{ color: '#c8d8cc', fontFamily: "'JetBrains Mono', monospace" }}>
                Legacy SCA tools tell you what's wrong after it's already wrong.
                Hack Universe operates at the velocity of your pipeline — scanning,
                scoring, and surfacing threats before they reach production.
                From deep SBOM introspection to autonomous containment, this is
                what zero-trust supply chain looks like in practice.
              </p>

              <div className="flex flex-wrap gap-4">
                <Link to="/dashboard">
                  <button id="statement-cta-dashboard" className="btn-primary text-xs px-6 py-3">
                    [ VIEW LIVE DASHBOARD ]
                  </button>
                </Link>
                <Link to="/reports">
                  <button id="statement-cta-reports" className="btn-secondary text-xs px-6 py-3">
                    READ THE REPORTS
                  </button>
                </Link>
              </div>

              {/* Micro stats */}
              <div className="flex gap-8 pt-4 border-t" style={{ borderColor: '#1e2736' }}>
                {[
                  { val: '< 0.8s', label: 'Detection Latency' },
                  { val: '100%', label: 'OSV Coverage' },
                  { val: 'SOC 2', label: 'Compliant' },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="text-sm font-bold" style={{ color: '#00ffc8' }}>{item.val}</div>
                    <div className="text-xxs uppercase tracking-wider" style={{ color: '#6b7a90' }}>{item.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
