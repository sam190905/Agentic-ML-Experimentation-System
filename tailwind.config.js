/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1d2628",
        paper: "#f5f7f5",
        mint: "#d8eee4",
        signal: "#d95f3f",
        "signal-soft": "#f8e3dc",
      },
      boxShadow: {
        soft: "0 12px 40px rgba(29, 38, 40, 0.07)",
        lift: "0 18px 50px rgba(29, 38, 40, 0.11)",
      },
    },
  },
  plugins: [],
};
