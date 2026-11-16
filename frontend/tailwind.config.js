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
          pink: '#F6E2E9',
          'pink-light': '#FDEBF1',
          'pink-border': '#EBDDE2',
          cream: '#FEFAF3',
          'cream-dark': '#F4EEE4',
          'cream-border': '#EBDDE2',
          sage: '#B8CFB3',
          'sage-light': '#E3EDDF',
          'sage-border': '#84A282',
          'sage-dark': '#84A282',
          'sage-deep': '#4F6B52',
          ink: '#2B3A2E',
          muted: '#5E6B60',
          heart: '#EF4444',
          'heart-bg': '#FEE2E2',
        }
      },
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
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
