/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bubble: {
          pink: '#F6E5EB',
          'pink-light': '#FDF8FA',
          'pink-border': '#EDD4DC',
          cream: '#FCF9F3',
          'cream-dark': '#F4EFE6',
          'cream-border': '#E8E1D3',
          sage: '#BDCEB8',
          'sage-light': '#EBF2EA',
          'sage-border': '#A7BCA2',
          'sage-dark': '#6D8A6B',
          'sage-deep': '#486047',
          ink: '#1B251D',
          muted: '#637265',
          heart: '#EF4444',
          'heart-bg': '#FEE2E2',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(109, 138, 107, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04)',
        'card': '0 8px 30px rgba(72, 96, 71, 0.08)',
        'swipe': '0 12px 35px -4px rgba(27, 37, 29, 0.15)',
      }
    },
  },
  plugins: [],
}
