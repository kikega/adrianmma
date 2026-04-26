/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        'butcher-red': '#c41e3a',
        'butcher-dark': '#0d0d0d',
        'butcher-gray': '#1a1a1a',
        'butcher-gold': '#d4af37',
      },
      fontFamily: {
        'display': ['Oswald', 'sans-serif'],
        'body': ['Roboto', 'sans-serif'],
      }
    }
  },
  plugins: [],
}
