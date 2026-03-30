import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "lo-black": "#000000",
        "lo-violet": "#7B2FFF",
        "lo-cyan":   "#00E5FF",
        "lo-pink":   "#FF2D9B",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        glow:  "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        float: { "0%,100%":{ transform:"translateY(0)" }, "50%":{ transform:"translateY(-10px)" } },
        glow:  { from:{ boxShadow:"0 0 20px rgba(123,47,255,0.3)" }, to:{ boxShadow:"0 0 40px rgba(123,47,255,0.7)" } },
      },
    },
  },
  plugins: [],
};
export default config;
