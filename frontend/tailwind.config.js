/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        ivory: "#FBF3E7",
        maroon: { DEFAULT: "#7A1730", deep: "#5A1126", ink: "#3A1220" },
        gold: { DEFAULT: "#C8A248", soft: "#E8D49A" },
        marigold: "#E08A1E",
        sage: "#5E7B5A",
        muted: "#9A7C6A",
        line: "#EADBC4",
        card: { DEFAULT: "#FFFFFF", warm: "#FDF6EC" },
      },
      fontFamily: {
        display: ["Marcellus", "Georgia", "serif"],
        serifItalic: ["'Cormorant Garamond'", "Georgia", "serif"],
        sans: ["Mukta", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px -22px rgba(90,17,38,.4)",
        cardHover: "0 18px 40px -24px rgba(90,17,38,.45)",
        modal: "0 40px 80px -30px rgba(0,0,0,.6)",
      },
      borderRadius: { card: "2px 2px 8px 8px" },
    },
  },
  plugins: [],
};
