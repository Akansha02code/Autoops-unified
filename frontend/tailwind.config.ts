import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: { colors: { autoops: { purple: "#4B2E83", teal: "#0F6E56", request: "#6B3FA0", amber: "#B8860B", danger: "#C0392B" } } } },
  plugins: [],
};

export default config;