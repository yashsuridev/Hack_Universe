import { Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const NAV_LINKS = ['Pipeline', 'Models', 'Docs', 'Privacy'] as const;

const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: 'easeOut' as any, delay },
  }),
};

export function Footer() {
  return (
    <footer className="site-footer bg-black border-t border-[#00ffc8]/20 w-full">
      {/* ── Main grid ─────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 py-16 grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">

        {/* ── LEFT COLUMN ───────────────────────────────────────── */}
        <motion.div
          className="flex flex-col gap-8"
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          custom={0}
        >
          {/* Wordmark */}
          <div className="flex items-center gap-2">
            <Shield
              className="text-[#00ffc8] shrink-0"
              size={22}
              strokeWidth={1.75}
            />
            <span className="font-mono font-bold text-white tracking-[0.18em] text-base uppercase">
              HACK//UNIVERSE
            </span>
          </div>

          {/* Nav links */}
          <nav className="flex flex-col gap-3">
            {NAV_LINKS.map((label) => (
              <a
                key={label}
                href="#"
                className="font-mono text-sm text-[#a0a0b0] tracking-widest uppercase
                           hover:text-[#00ffc8] transition-colors duration-200 w-fit"
              >
                {label}
              </a>
            ))}
          </nav>

          {/* CTA button */}
          <div>
            <a
              href="#"
              className="btn-primary inline-block font-mono text-xs tracking-[0.2em] uppercase
                         px-6 py-3 bg-[#00ffc8] text-black font-bold
                         hover:bg-[#00e6b4] transition-colors duration-200 cursor-pointer"
            >
              [ REQUEST ACCESS ]
            </a>
          </div>
        </motion.div>

        {/* ── RIGHT COLUMN — SOC Alerts card ────────────────────── */}
        <motion.div
          className="bg-[#0a0a0a] border border-[#00ffc8]/15 p-8 flex flex-col gap-5"
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          custom={0.15}
        >
          {/* Heading */}
          <h3 className="font-mono font-bold text-[#00ffc8] tracking-[0.22em] text-sm uppercase">
            GET SOC ALERTS
          </h3>

          {/* Subtext */}
          <p className="font-mono text-xs text-[#6b6b80] leading-relaxed tracking-wide">
            Real-time threat intelligence delivered to your inbox.
          </p>

          {/* Email input */}
          <input
            type="email"
            placeholder="your@email.com"
            className="input w-full bg-black border border-[#00ffc8]/25 text-white
                       font-mono text-sm px-4 py-3
                       placeholder:text-[#3a3a4a]
                       focus:outline-none focus:border-[#00ffc8]/70
                       transition-colors duration-200"
          />

          {/* Checkbox */}
          <label className="flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              className="mt-0.5 shrink-0 w-4 h-4 appearance-none border border-[#00ffc8]/40
                         bg-black checked:bg-[#00ffc8] checked:border-[#00ffc8]
                         focus:outline-none cursor-pointer transition-colors duration-200"
            />
            <span className="font-mono text-xs text-[#6b6b80] leading-relaxed
                             group-hover:text-[#a0a0b0] transition-colors duration-200">
              I agree to receive security bulletins
            </span>
          </label>

          {/* Submit button */}
          <button
            type="button"
            className="btn-primary w-full font-mono text-xs tracking-[0.2em] uppercase
                       px-6 py-3 bg-[#00ffc8] text-black font-bold
                       hover:bg-[#00e6b4] transition-colors duration-200"
          >
            [ SUBSCRIBE ]
          </button>
        </motion.div>
      </div>

      {/* ── BOTTOM BAR ────────────────────────────────────────── */}
      <motion.div
        className="border-t border-[#00ffc8]/10 px-6 py-5"
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        custom={0.3}
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span className="font-mono text-[10px] text-[#3a3a4a] tracking-widest uppercase">
            © 2026 HACK//UNIVERSE. ALL RIGHTS RESERVED.
          </span>
          <a
            href="mailto:security@hackuniverse.io"
            className="font-mono text-[10px] text-[#3a3a4a] tracking-widest uppercase
                       hover:text-[#00ffc8] transition-colors duration-200"
          >
            security@hackuniverse.io
          </a>
        </div>
      </motion.div>
    </footer>
  );
}
