/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        lavender: "#8B5CF6",
        purple: "#6D28D9",
        pink: "#EC4899",
        ink: "#27223A",
        soft: "#FAF7FF"
      }
    }
  },
  plugins: []
}
