/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        shield: {
          1: '#9f4a4a',
          2: '#c67a2e',
          3: '#3b6e91',
          4: '#2e8a7a',
          5: '#1d5c3f',
        },
      },
    },
  },
  plugins: [],
}
