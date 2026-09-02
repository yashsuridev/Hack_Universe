import { motion } from 'framer-motion';

const partners = [
  { name: 'Gemini AI',       abbr: 'GEMINI AI' },
  { name: 'OSV Database',    abbr: 'OSV DB' },
  { name: 'GitHub Advisory', abbr: 'GHSA' },
  { name: 'NVD / NIST',      abbr: 'NVD/NIST' },
  { name: 'CycloneDX',       abbr: 'CYCLONEDX' },
  { name: 'SIEM Integration',abbr: 'SIEM' },
  { name: 'Splunk',          abbr: 'SPLUNK' },
  { name: 'Elastic',         abbr: 'ELASTIC' },
];

export function PartnersStrip() {
  return (
    <section
      className="py-20 relative overflow-hidden"
      style={{ background: '#070a0e' }}
    >
      {/* Top border glow */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,255,200,0.08) 30%, rgba(0,255,200,0.08) 70%, transparent 100%)',
        }}
      />

      <div className="max-w-5xl mx-auto px-6">
        {/* Label */}
        <motion.p
          className="text-center text-xs font-mono uppercase tracking-widest mb-12"
          style={{ color: '#3d4a58' }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          INTEGRATED WITH
        </motion.p>

        {/* Partners row */}
        <motion.div
          className="flex flex-wrap items-center justify-center gap-6 md:gap-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{
            hidden: {},
            visible: {
              transition: { staggerChildren: 0.07, delayChildren: 0.1 },
            },
          }}
        >
          {partners.map((partner) => (
            <motion.div
              key={partner.name}
              variants={{
                hidden:  { opacity: 0, y: 12 },
                visible: { opacity: 1, y: 0 },
              }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            >
              <div
                className="px-5 py-2.5 text-xs font-mono font-semibold uppercase tracking-widest cursor-default transition-all duration-300"
                style={{
                  color: '#3d4a58',
                  border: '1px solid #1a2230',
                  borderRadius: '1px',
                  letterSpacing: '0.16em',
                  background: 'rgba(22,27,39,0.3)',
                  userSelect: 'none',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.color = '#00ffc8';
                  (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,255,200,0.25)';
                  (e.currentTarget as HTMLElement).style.background = 'rgba(0,255,200,0.04)';
                  (e.currentTarget as HTMLElement).style.boxShadow = '0 0 16px rgba(0,255,200,0.08)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.color = '#3d4a58';
                  (e.currentTarget as HTMLElement).style.borderColor = '#1a2230';
                  (e.currentTarget as HTMLElement).style.background = 'rgba(22,27,39,0.3)';
                  (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                }}
              >
                {partner.abbr}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Bottom border glow */}
      <div
        className="absolute bottom-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,255,200,0.04) 50%, transparent 100%)',
        }}
      />
    </section>
  );
}
