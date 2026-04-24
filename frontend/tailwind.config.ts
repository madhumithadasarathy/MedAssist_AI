import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          50: '#f9f9f9',
          100: '#ececec',
          200: '#e3e3e3',
          300: '#cdcdcd',
          400: '#b4b4b4',
          500: '#9b9b9b',
          600: '#676767',
          700: '#424242',
          800: '#2f2f2f',
          900: '#212121',
          950: '#171717',
        },
        primary: '#10a37f',
        primaryHover: '#0b8265',
        ink: {
          DEFAULT: '#ececec',
          muted: '#b4b4b4',
        }
      },
      boxShadow: {
        panel: "0 0 15px rgba(0, 0, 0, 0.5)",
      },
      backgroundImage: {
        "medical-grid":
          "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
