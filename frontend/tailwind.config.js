/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        apple: {
          pink: '#FC3C44',
          dark: '#1C1C1E',
          card: '#2C2C2E',
          border: '#3A3A3C',
          text: '#EBEBF5',
          muted: '#8E8E93',
        },
      },
    },
  },
  plugins: [],
}
