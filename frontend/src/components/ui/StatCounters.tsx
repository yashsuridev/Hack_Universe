import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';

// ─── Stat definitions ────────────────────────────────────────────────────────

type StatConfig =
  | { kind: 'integer';  target: number; label: string }
  | { kind: 'decimal';  target: number; decimals: number; suffix: string; label: string }
  | { kind: 'suffix-int'; target: number; suffix: string; label: string }
  | { kind: 'clamp';    from: number; target: number; decimals: number; suffix: string; label: string };

const STATS: StatConfig[] = [
  { kind: 'integer',    target: 24891,  label: 'THREATS DETECTED' },
  { kind: 'integer',    target: 18440,  label: 'ALERTS AUTO-CONTAINED' },
  { kind: 'decimal',    target: 0.8,    decimals: 1, suffix: 's', label: 'AVG RESPONSE TIME' },
  { kind: 'suffix-int', target: 4,      suffix: '.2M', label: 'PACKAGES SCANNED' },
  { kind: 'clamp',      from: 99.90,    target: 99.97, decimals: 2, suffix: '%', label: 'UPTIME' },
];

// ─── Formatting helpers ───────────────────────────────────────────────────────

function formatInteger(n: number): string {
  return Math.floor(n).toLocaleString('en-US');
}

// ─── Individual counter hook ─────────────────────────────────────────────────

function useCountUp(stat: StatConfig, active: boolean): string {
  const [display, setDisplay] = useState<string>(() => getInitial(stat));

  useEffect(() => {
    if (!active) return;

    const DURATION = 1500; // ms
    const INTERVAL = 16;   // ~60 fps
    const steps = Math.floor(DURATION / INTERVAL);
    let step = 0;

    const id = setInterval(() => {
      step++;
      const progress = Math.min(step / steps, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);

      setDisplay(interpolate(stat, eased));

      if (step >= steps) {
        clearInterval(id);
        setDisplay(getTarget(stat));
      }
    }, INTERVAL);

    return () => clearInterval(id);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  return display;
}

function getInitial(stat: StatConfig): string {
  switch (stat.kind) {
    case 'integer':    return '0';
    case 'decimal':    return `0.${'0'.repeat(stat.decimals)}${stat.suffix}`;
    case 'suffix-int': return `0${stat.suffix}`;
    case 'clamp':      return `${stat.from.toFixed(stat.decimals)}${stat.suffix}`;
  }
}

function getTarget(stat: StatConfig): string {
  switch (stat.kind) {
    case 'integer':    return formatInteger(stat.target);
    case 'decimal':    return `${stat.target.toFixed(stat.decimals)}${stat.suffix}`;
    case 'suffix-int': return `${stat.target}${stat.suffix}`;
    case 'clamp':      return `${stat.target.toFixed(stat.decimals)}${stat.suffix}`;
  }
}

function interpolate(stat: StatConfig, t: number): string {
  switch (stat.kind) {
    case 'integer': {
      const val = stat.target * t;
      return formatInteger(val);
    }
    case 'decimal': {
      const val = stat.target * t;
      return `${val.toFixed(stat.decimals)}${stat.suffix}`;
    }
    case 'suffix-int': {
      const val = stat.target * t;
      return `${Math.floor(val)}${stat.suffix}`;
    }
    case 'clamp': {
      const val = stat.from + (stat.target - stat.from) * t;
      return `${val.toFixed(stat.decimals)}${stat.suffix}`;
    }
  }
}

// ─── Single stat card ─────────────────────────────────────────────────────────

interface StatCardProps {
  stat: StatConfig;
  active: boolean;
  index: number;
}

function StatCard({ stat, active, index }: StatCardProps) {
  const value = useCountUp(stat, active);

  return (
    <motion.div
      className="flex flex-col items-center gap-3 flex-1 min-w-0"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.5, delay: index * 0.1, ease: 'easeOut' }}
    >
      {/* Value */}
      <div className="relative flex flex-col items-center gap-1">
        <span
          className="stat-counter font-mono text-4xl sm:text-5xl font-bold tabular-nums"
          style={{ color: '#00ffc8', textShadow: '0 0 18px rgba(0,255,200,0.35)' }}
        >
          {value}
        </span>
        {/* Thin accent underline */}
        <span
          className="block h-px w-full"
          style={{ background: 'linear-gradient(90deg, transparent, #00ffc8, transparent)' }}
        />
      </div>

      {/* Label */}
      <span
        className="font-mono text-xs uppercase tracking-widest"
        style={{ color: '#6b7280', letterSpacing: '0.18em' }}
      >
        {stat.label}
      </span>
    </motion.div>
  );
}

// ─── Main export ─────────────────────────────────────────────────────────────

export function StatCounters() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !active) {
          setActive(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [active]);

  return (
    <section
      ref={sectionRef}
      className="relative w-full py-20 overflow-hidden"
      style={{ background: '#050a0e' }}
    >
      {/* Cyber-grid background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0,255,200,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,255,200,0.04) 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px',
        }}
      />

      {/* Ambient glow */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% 50%, rgba(0,255,200,0.05) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 max-w-6xl mx-auto px-6 flex flex-col items-center gap-14">
        {/* Section heading */}
        <motion.p
          className="font-mono text-xs uppercase tracking-[0.3em]"
          style={{ color: '#4b5563' }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          PLATFORM INTELLIGENCE
        </motion.p>

        {/* Counters row */}
        <div className="w-full flex flex-wrap justify-center gap-10 sm:gap-0 sm:divide-x sm:divide-[#1a2a22]">
          {STATS.map((stat, i) => (
            <div key={stat.label} className="sm:px-8 first:pl-0 last:pr-0">
              <StatCard stat={stat} active={active} index={i} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
