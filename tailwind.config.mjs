/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        falun: {
          50: "#fef2f2",
          100: "#fde3e1",
          200: "#fcc9c4",
          300: "#e88072",
          400: "#d4564a",
          500: "#c33a2e",
          600: "#9a2520",
          700: "#7f1d19",
          800: "#6a1a16",
          900: "#521614",
          950: "#2d0c0a",
        },
        ink: {
          50: "#f5f5f4",
          100: "#e5e5e3",
          200: "#c8c7c3",
          300: "#a3a29d",
          400: "#7a7972",
          500: "#5c5b55",
          600: "#403f3b",
          700: "#2d2d29",
          800: "#1a1a1a",
          900: "#0f0f0f",
          950: "#080808",
        },
        parchment: {
          50: "#fdfcfa",
          100: "#faf8f4",
          200: "#f5f0e8",
          300: "#f0e9dd",
          400: "#e5d9c5",
          500: "#d4c5a9",
          600: "#bda87e",
          700: "#a08c62",
          800: "#7d6c4a",
          900: "#5c4f38",
          950: "#3d3425",
        },
      },
      fontFamily: {
        serif: ["Newsreader", "Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        base: ["17px", { lineHeight: "1.6" }],
      },
      boxShadow: {
        card: "0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)",
        "card-hover": "0 10px 25px rgba(0, 0, 0, 0.08), 0 4px 10px rgba(0, 0, 0, 0.04)",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        fadeUp: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "fade-up": "fadeUp 0.4s ease-out",
      },
    },
  },
  plugins: [],
};
