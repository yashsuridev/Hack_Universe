import { ShieldAlert, Activity, Search } from 'lucide-react';
import { useState, useEffect } from 'react';
import { HeroSection } from '../components/ui/HeroSection';

const NETWORK_SCANNER_API = import.meta.env.VITE_NETWORK_SCANNER_API_URL || 'http://localhost:8002';

export function NetworkScannerPage() {
  const [target, setTarget] = useState('127.0.0.1');
  const [status, setStatus] = useState({ running: false, results: null as any, error: null as any });

  const checkStatus = async () => {
    try {
      const res = await fetch(`${NETWORK_SCANNER_API}/api/scan/status`);
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Scanner API offline");
    }
  };

  useEffect(() => {
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const startScan = async () => {
    try {
      await fetch(`${NETWORK_SCANNER_API}/api/scan/start?target=${target}`, { method: 'POST' });
      checkStatus();
    } catch (e) {
      alert("Failed to connect to scanner API.");
    }
  };

  const results = status.results;
  const hostsFound = results ? results.hosts_discovered : '--';
  const openPorts = results ? results.total_open_ports : '--';

  return (
    <div style={{ background: '#0a0a0a' }}>
      <HeroSection 
        title1={['NETWORK', 'SCANNER']} 
        title2={['VULNERABILITY', 'DISCOVERY']} 
        subtitle={'Scan local networks and remote targets for open ports and vulnerable services.\nHigh-speed asynchronous probing engine.'}
        ctaText={'INITIALIZE SCANNER'}
      />

      <div id="dashboard-content" style={{ scrollMarginTop: '80px', paddingBottom: '100px' }}>
        <section className="py-24 relative" style={{ background: '#0a0a0a' }}>
          <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />
          <div className="max-w-7xl mx-auto px-6 relative z-10">
            
            <div className="flex flex-col bg-[#161b27] text-[#eaf5ee] p-8 rounded-2xl border border-[#1e2736] relative z-20 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <Search className="w-8 h-8 text-[#00ffc8]" />
                <h2 className="text-2xl font-bold uppercase tracking-widest">Network Scanner</h2>
              </div>
              
              <p className="text-[#8B949E] mb-8 max-w-2xl">
                Enter a target IP, CIDR range (e.g. 192.168.1.0/24), or your default gateway. Ensure the backend scanner API is running on port 8002.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-[#0a0a0a] p-6 rounded-xl border border-[#30363D] flex flex-col items-center justify-center text-center">
                  <Activity className="w-8 h-8 text-[#06B6D4] mb-3" />
                  <h3 className="text-sm uppercase tracking-wider text-[#8B949E] mb-1">Status</h3>
                  <span className="text-xl font-bold">{status.running ? "Scanning..." : "Idle"}</span>
                </div>
                <div className="bg-[#0a0a0a] p-6 rounded-xl border border-[#30363D] flex flex-col items-center justify-center text-center">
                  <ShieldAlert className="w-8 h-8 text-[#F87171] mb-3" />
                  <h3 className="text-sm uppercase tracking-wider text-[#8B949E] mb-1">Open Ports</h3>
                  <span className="text-3xl font-bold text-[#F87171]">{openPorts}</span>
                </div>
                <div className="bg-[#0a0a0a] p-6 rounded-xl border border-[#30363D] flex flex-col items-center justify-center text-center">
                  <Search className="w-8 h-8 text-[#4ADE80] mb-3" />
                  <h3 className="text-sm uppercase tracking-wider text-[#8B949E] mb-1">Endpoints Discovered</h3>
                  <span className="text-3xl font-bold">{hostsFound}</span>
                </div>
              </div>

              <div className="flex justify-center mt-12 gap-4">
                <input 
                  type="text" 
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="px-4 py-3 bg-[#0a0a0a] border border-[#30363D] rounded-lg text-white w-64 focus:border-[#00ffc8] focus:outline-none"
                  placeholder="e.g. 192.168.1.1"
                />
                <button 
                  onClick={startScan}
                  disabled={status.running}
                  className="px-8 py-3 bg-transparent border-2 border-[#00ffc8] text-[#00ffc8] font-bold uppercase tracking-widest rounded-lg hover:bg-[#00ffc8] hover:text-[#0a0a0a] transition-colors disabled:opacity-50">
                  {status.running ? "Scanning..." : "Initialize Scan"}
                </button>
              </div>

              {status.error && (
                <div className="mt-8 p-4 bg-red-900/20 border border-red-500 rounded-lg text-red-400">
                  Error: {status.error}
                </div>
              )}
              
              {results && results.hosts && (
                <div className="mt-8">
                  <h3 className="text-xl mb-4 font-bold text-[#00ffc8] border-b border-[#30363D] pb-2">Scan Results</h3>
                  <pre className="bg-[#0a0a0a] p-6 rounded-xl border border-[#30363D] overflow-auto max-h-96 text-xs text-[#a3b1c6]">
                    {JSON.stringify(results.hosts, null, 2)}
                  </pre>
                </div>
              )}
            </div>

          </div>
        </section>
      </div>
    </div>
  );
}
