/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        coinsy: {
          gold: "#FFD700",
          amber: "#F59E0B",
          dark: "#0F172A",
          card: "#1E293B",
          border: "#334155",
          accent: "#EAB308"
        }
      }
    },
  },
  plugins: [],
}
