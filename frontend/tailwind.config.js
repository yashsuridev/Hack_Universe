/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // === CYBER DESIGN SYSTEM ===
        cyber: {
          black:   '#0a0a0a',
          base:    '#0d1117',
          navy:    '#0a0f1e',
          slate:   '#111827',
          panel:   '#161b27',
          border:  '#1e2736',
          accent:  '#00ffc8',
          'accent-dim': '#00c89a',
          'accent-glow': 'rgba(0, 255, 200, 0.12)',
          red:     '#ff4d4d',
          'red-glow': 'rgba(255, 77, 77, 0.15)',
          orange:  '#ff8c42',
          yellow:  '#ffd700',
          text:    '#eaf5ee',
          muted:   '#6b7a90',
          subtle:  '#2d3748',
        },
        // === SEVERITY SYSTEM ===
        danger: {
          50:  '#1a0505',
          100: '#2d0a0a',
          200: '#5c1a1a',
          300: '#8b2a2a',
          400: '#cc3333',
          500: '#ff4d4d',
          600: '#ff6666',
          700: '#ff8080',
          800: '#ffb3b3',
          900: '#ffe6e6',
        },
        warning: {
          50:  '#1a1400',
          100: '#2d2400',
          200: '#5c4800',
          300: '#8b6c00',
          400: '#cc9f00',
          500: '#ffd700',
          600: '#ffde33',
          700: '#ffe566',
          800: '#fff099',
          900: '#fffacc',
        },
        success: {
          50:  '#001a13',
          100: '#002d22',
          200: '#005c44',
          300: '#008b66',
          400: '#00c899',
          500: '#00ffc8',
          600: '#33ffd3',
          700: '#66ffde',
          800: '#99ffe9',
          900: '#ccfff4',
        },
        primary: {
          50:  '#001a13',
          100: '#002d22',
          200: '#005c44',
          300: '#008b66',
          400: '#00c899',
          500: '#00ffc8',
          600: '#00c89a',
          700: '#009870',
          800: '#006848',
          900: '#003824',
        },
      },
      fontFamily: {
        sans:  ['"JetBrains Mono"', '"Space Mono"', 'monospace'],
        mono:  ['"JetBrains Mono"', '"Space Mono"', 'monospace'],
      },
      fontSize: {
        'xxs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      letterSpacing: {
        'widest':   '0.25em',
        'ultrawide': '0.4em',
      },
      boxShadow: {
        'cyber':       '0 0 20px rgba(0, 255, 200, 0.08), 0 0 40px rgba(0, 255, 200, 0.04)',
        'cyber-hover': '0 0 30px rgba(0, 255, 200, 0.2), 0 0 60px rgba(0, 255, 200, 0.08)',
        'cyber-btn':   '0 0 20px rgba(0, 255, 200, 0.3)',
        'red-glow':    '0 0 20px rgba(255, 77, 77, 0.3)',
        'panel':       '0 4px 32px rgba(0, 0, 0, 0.6)',
        'inner-glow':  'inset 0 1px 0 rgba(255, 255, 255, 0.04)',
      },
      backdropBlur: {
        'xs': '4px',
      },
      animation: {
        'glow-pulse':    'glow-pulse 3s ease-in-out infinite',
        'scan-line':     'scan-line 4s linear infinite',
        'fade-up':       'fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'counter-roll':  'counter-roll 0.1s linear',
        'border-flow':   'border-flow 4s linear infinite',
        'float':         'float 6s ease-in-out infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: '0.6', filter: 'blur(0px)' },
          '50%':      { opacity: '1',   filter: 'blur(1px)' },
        },
        'scan-line': {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(200vh)' },
        },
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'border-flow': {
          '0%':   { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '200% 50%' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
      },
      transitionTimingFunction: {
        'cyber': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'stiff': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}