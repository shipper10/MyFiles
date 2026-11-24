/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans Arabic"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        paper: {
          bg: '#F7F6F2',
          surface: '#FFFFFF',
          subtle: '#EFECE6',
          border: '#E2DFD7',
          ink: '#18181B',
          muted: '#686762',
        },
        charcoal: {
          bg: '#161616',
          surface: '#1E1E1D',
          subtle: '#262624',
          border: '#30302D',
          ink: '#ECEBE6',
          muted: '#9A9891',
        },
        accent: {
          DEFAULT: '#C84B31',
          hover: '#A63A23',
        },
      },
    },
  },
  plugins: [],
};
