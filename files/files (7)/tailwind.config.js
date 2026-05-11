/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['Syne', 'sans-serif'],
      },
      colors: {
        ink:   { DEFAULT: '#0D0D0F', 50: '#f5f5f6', 100: '#e8e8ea', 200: '#d0d0d4', 300: '#a8a8b0', 400: '#78788a', 500: '#55556a', 600: '#3c3c4f', 700: '#282834', 800: '#18181f', 900: '#0D0D0F' },
        lime:  { DEFAULT: '#C8F135', 50: '#f5fde0', 100: '#eafab8', 200: '#d8f575', 300: '#C8F135', 400: '#aad418', 500: '#84a810', 600: '#627d0b', 700: '#475c09', 800: '#304009', 900: '#1e2806' },
        slate: { DEFAULT: '#6B7A9F', 50: '#f4f5f9', 100: '#e6e8f2', 200: '#cdd2e6', 300: '#a8b0d0', 400: '#7e8bbb', 500: '#6B7A9F', 600: '#4e5b82', 700: '#3b4568', 800: '#272e47', 900: '#141826' },
      },
      animation: {
        'fade-up':   'fadeUp 0.5s ease forwards',
        'fade-in':   'fadeIn 0.3s ease forwards',
        'pulse-dot': 'pulseDot 1.4s ease-in-out infinite',
        'slide-in':  'slideIn 0.35s cubic-bezier(0.16,1,0.3,1) forwards',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeUp:   { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeIn:   { from: { opacity: 0 }, to: { opacity: 1 } },
        pulseDot: { '0%,80%,100%': { transform: 'scale(0)' }, '40%': { transform: 'scale(1)' } },
        slideIn:  { from: { opacity: 0, transform: 'translateX(20px)' }, to: { opacity: 1, transform: 'translateX(0)' } },
      },
    },
  },
  plugins: [],
}
