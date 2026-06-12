/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          deep: "#0A0A0A",
          card: "#111111",
          dark: "#0A0A0A"
        },
        primary: {
          light: "#86efac",
          DEFAULT: "#39FF14",
          dark: "#2DB810"
        },
        accent: {
          DEFAULT: "#39FF14",
          hover: "#2DB810",
          muted: "rgba(57, 255, 20, 0.08)",
          border: "rgba(57, 255, 20, 0.27)",
        },
        surface: {
          DEFAULT: "#111111",
          secondary: "#1A1A1A",
          border: "#1E1E1E",
        },
        text: {
          primary: "#ffffff",
          secondary: "#9CA3AF",
          muted: "#6b7280"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular"]
      }
    },
  },
  plugins: [],
}
