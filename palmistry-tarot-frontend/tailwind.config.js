/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Our palette: a deep midnight backdrop with warm gold for emphasis.
        // Chosen deliberately over the generic "cream + terracotta" AI look.
        midnight: '#160F27',
        plum: '#2B1B45',
        parchment: '#F1E9DA',
        gold: '#C9A24B',
        lavender: '#9B87B5',
      },
      fontFamily: {
        display: ['"Cormorant Garamond"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
