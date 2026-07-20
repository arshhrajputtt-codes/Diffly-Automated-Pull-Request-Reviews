/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0D1117',        // GitHub dark bg
        card: '#161B22',      // GitHub dark card/panel
        'card-hover': '#1C2129',
        border: '#30363D',    // GitHub dark border
        text: '#E6EDF3',
        'text-dim': '#8B949E',
        'text-faint': '#6E7681',
        accent: '#238636',    // GitHub's merged/success green
        'accent-hover': '#2EA043',
        warn: '#D29922',
        danger: '#F85149',
        diffAdd: '#3FB950',
        diffAddBg: 'rgba(63,185,80,0.15)',
        diffDel: '#F85149',
        diffDelBg: 'rgba(248,81,73,0.15)',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
