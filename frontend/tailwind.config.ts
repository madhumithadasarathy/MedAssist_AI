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
        mist: "#eff8fb",
        aqua: "#bdeff2",
        teal: "#0f7c82",
        slateblue: "#214b63",
        ink: "#123145",
      },
      boxShadow: {
        panel: "0 20px 50px rgba(18, 49, 69, 0.10)",
      },
      backgroundImage: {
        "medical-grid":
          "radial-gradient(circle at 1px 1px, rgba(15,124,130,0.08) 1px, transparent 0)",
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
