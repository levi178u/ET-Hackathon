/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#12141c", 
        surface: "#1f222e",   
        surfaceHover: "#2a2e3d",
        primary: "#e15e37", // Matches the coral/orange in screenshots
        primaryHover: "#c5441e",
        textDefault: "#e2e8f0",
        textMuted: "#94a3b8"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif'],
      }
    },
  },
  plugins: [],
}
