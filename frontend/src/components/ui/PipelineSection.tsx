import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const STAGES = [
  {
    id: 1,
    code: '01',
    name: 'INGEST',
    icon: '⬇',
    tagline: 'Raw Signal Acquisition',
    description: 'Intake of SBOM manifests, package.json/requirements.txt, and lockfiles. Multi-format CycloneDX parsing with deduplication and normalization across all ecosystems.',
    color: '#00ffc8',
  },
  {
    id: 2,
    code: '02',
    name: 'DETECT',
    icon: '◎',
    tagline: 'Threat Pattern Recognition',
    description: 'Cross-referenced against OSV, NVD, and GitHub Advisory databases. ML-assisted anomaly scoring for typosquatting, abandoned packages, and supply-chain injection vectors.',
    color: '#ff8c42',
  },
  {
    id: 3,
    code: '03',
    name: 'CONTAIN',
    icon: '⬡',
    tagline: 'Automated Risk Isolation',
    description: 'Auto-prioritization of critical CVEs and zero-days. Blast-radius analysis traces transitive dependency chains. Generates containment recommendations in real time.',
    color: '#ff4d4d',
  },
  {
    id: 4,
    code: '04',
    name: 'SUMMARIZE',
    icon: '⬢',
    tagline: 'Intelligence Synthesis',
    description: 'Gemini-powered natural language summaries of each threat vector. Risk scoring with CVSS breakdown, remediation priority queue, and executive-ready briefings.',
    color: '#ffd700',
  },
  {
    id: 5,
    code: '05',
    name: 'STREAM',
    icon: '↑',
    tagline: 'Continuous Delivery',
    description: 'Webhook-triggered alerts, SIEM integrations, and CI/CD gate enforcement. Real-time dashboard updates with full audit trail and compliance report generation.',
    color: '#00ffc8',
  },
];

export function PipelineSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [activeStage, setActiveStage] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mq.matches);
    if (mq.matches) return;

    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      const totalScrollLength = (STAGES.length - 1) * window.innerHeight * 0.6;

      ScrollTrigger.create({
        trigger: section,
        start: 'top top',
        end: `+=${totalScrollLength}`,
        pin: true,
        pinSpacing: true,
        onUpdate: (self) => {
          const stageIndex = Math.min(
            Math.floor(self.progress * STAGES.length),
            STAGES.length - 1
          );
          setActiveStage(stageIndex);
        },
      });
    }, section);

    return () => ctx.revert();
  }, []);

  if (reducedMotion) {
    return (
      <section className="py-24" style={{ background: '#0a0a0a' }}>
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-xs font-mono uppercase tracking-widest text-cyber-muted mb-12 text-center">
            AUTONOMOUS PIPELINE
          </p>
          <div className="grid md:grid-cols-5 gap-4">
            {STAGES.map((stage) => (
              <div key={stage.id} className="card p-5">
                <div className="text-2xl mb-3">{stage.icon}</div>
                <div className="text-xs font-mono text-cyber-muted mb-1">{stage.code}</div>
                <div className="text-sm font-bold uppercase tracking-wider mb-2" style={{ color: stage.color }}>
                  {stage.name}
                </div>
                <p className="text-xxs text-cyber-muted leading-relaxed">{stage.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section
      ref={sectionRef}
      className="pipeline-section relative overflow-hidden"
      style={{ background: '#0a0a0a', minHeight: '100vh' }}
      aria-label="Autonomous pipeline stages"
    >
      {/* Background grid */}
      <div className="absolute inset-0 cyber-grid opacity-40" />

      <div ref={contentRef} className="relative z-10 flex flex-col h-screen justify-center px-6 md:px-12 lg:px-24">
        {/* Header */}
        <div className="mb-12">
          <motion.p
            className="text-xs font-mono uppercase tracking-widest mb-3"
            style={{ color: '#6b7a90' }}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            AUTONOMOUS PIPELINE
          </motion.p>
          <motion.h2
            className="cyber-heading text-3xl md:text-5xl"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            FIVE STAGES.
            <br />
            <span style={{ color: '#00ffc8' }}>ZERO BLIND SPOTS.</span>
          </motion.h2>
        </div>

        {/* Stages display */}
        <div className="grid lg:grid-cols-2 gap-8 items-center max-w-6xl">
          {/* Left: Stage list / progress */}
          <div className="flex flex-col gap-3">
            {STAGES.map((stage, i) => {
              const isActive = i === activeStage;
              const isPast = i < activeStage;
              return (
                <motion.div
                  key={stage.id}
                  className="flex items-center gap-4 cursor-pointer"
                  onClick={() => setActiveStage(i)}
                  animate={{
                    opacity: isActive ? 1 : isPast ? 0.5 : 0.3,
                    x: isActive ? 8 : 0,
                  }}
                  transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                >
                  {/* Connector line */}
                  <div className="flex flex-col items-center">
                    <div
                      className="w-8 h-8 flex items-center justify-center text-sm font-bold transition-all duration-300"
                      style={{
                        border: `1px solid ${isActive ? stage.color : '#1e2736'}`,
                        color: isActive ? stage.color : '#6b7a90',
                        background: isActive ? `${stage.color}15` : 'transparent',
                        borderRadius: '2px',
                        boxShadow: isActive ? `0 0 16px ${stage.color}30` : 'none',
                      }}
                    >
                      {stage.code}
                    </div>
                    {i < STAGES.length - 1 && (
                      <div
                        className="w-px mt-1"
                        style={{
                          height: '24px',
                          background: isPast
                            ? `linear-gradient(to bottom, ${stage.color}, ${STAGES[i+1].color})`
                            : '#1e2736',
                          transition: 'background 0.5s ease',
                        }}
                      />
                    )}
                  </div>
                  <div>
                    <div
                      className="text-xs font-bold uppercase tracking-widest transition-all duration-300"
                      style={{ color: isActive ? stage.color : '#eaf5ee' }}
                    >
                      {stage.name}
                    </div>
                    <div className="text-xxs text-cyber-muted">{stage.tagline}</div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Right: Active stage card */}
          <motion.div
            key={activeStage}
            className="pipeline-card active"
            initial={{ opacity: 0, x: 40, rotateY: -8 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            exit={{ opacity: 0, x: -40 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            style={{ perspective: '800px', transformStyle: 'preserve-3d' }}
          >
            {/* Stage number */}
            <div
              className="text-7xl font-bold leading-none mb-4 opacity-10 select-none"
              style={{ color: STAGES[activeStage].color, letterSpacing: '-0.04em' }}
            >
              {STAGES[activeStage].code}
            </div>

            {/* Icon + name */}
            <div className="flex items-center gap-4 mb-6">
              <div
                className="w-14 h-14 flex items-center justify-center text-2xl"
                style={{
                  border: `1px solid ${STAGES[activeStage].color}`,
                  color: STAGES[activeStage].color,
                  boxShadow: `0 0 24px ${STAGES[activeStage].color}20`,
                  borderRadius: '2px',
                }}
              >
                {STAGES[activeStage].icon}
              </div>
              <div>
                <h3
                  className="text-2xl font-bold uppercase tracking-widest"
                  style={{ color: STAGES[activeStage].color }}
                >
                  {STAGES[activeStage].name}
                </h3>
                <p className="text-xs text-cyber-muted">{STAGES[activeStage].tagline}</p>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm leading-relaxed" style={{ color: '#c8d8cc' }}>
              {STAGES[activeStage].description}
            </p>

            {/* Progress dots */}
            <div className="flex gap-2 mt-6">
              {STAGES.map((_, i) => (
                <div
                  key={i}
                  className="h-0.5 flex-1 transition-all duration-500 cursor-pointer"
                  style={{
                    background: i <= activeStage ? STAGES[activeStage].color : '#1e2736',
                    boxShadow: i === activeStage ? `0 0 8px ${STAGES[activeStage].color}` : 'none',
                  }}
                  onClick={() => setActiveStage(i)}
                />
              ))}
            </div>

            {/* Scroll hint */}
            <p className="text-xxs text-cyber-muted mt-3 text-right">
              SCROLL TO ADVANCE →
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
