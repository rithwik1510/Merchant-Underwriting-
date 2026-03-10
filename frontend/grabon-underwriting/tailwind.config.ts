import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        go: {
          950: "rgb(var(--go-950) / <alpha-value>)",
          900: "rgb(var(--go-900) / <alpha-value>)",
          800: "rgb(var(--go-800) / <alpha-value>)",
          700: "rgb(var(--go-700) / <alpha-value>)",
          600: "rgb(var(--go-600) / <alpha-value>)",
          500: "rgb(var(--go-500) / <alpha-value>)",
          400: "rgb(var(--go-400) / <alpha-value>)",
          300: "rgb(var(--go-300) / <alpha-value>)",
          200: "rgb(var(--go-200) / <alpha-value>)",
          100: "rgb(var(--go-100) / <alpha-value>)",
          50: "rgb(var(--go-50) / <alpha-value>)",
        },
        ink: {
          900: "rgb(var(--ink-900) / <alpha-value>)",
          800: "rgb(var(--ink-800) / <alpha-value>)",
          700: "rgb(var(--ink-700) / <alpha-value>)",
          600: "rgb(var(--ink-600) / <alpha-value>)",
          500: "rgb(var(--ink-500) / <alpha-value>)",
          400: "rgb(var(--ink-400) / <alpha-value>)",
          300: "rgb(var(--ink-300) / <alpha-value>)",
          200: "rgb(var(--ink-200) / <alpha-value>)",
          100: "rgb(var(--ink-100) / <alpha-value>)",
          50: "rgb(var(--ink-50) / <alpha-value>)",
        },
        risk: {
          950: "rgb(var(--risk-950) / <alpha-value>)",
          900: "rgb(var(--risk-900) / <alpha-value>)",
          800: "rgb(var(--risk-800) / <alpha-value>)",
          700: "rgb(var(--risk-700) / <alpha-value>)",
          600: "rgb(var(--risk-600) / <alpha-value>)",
          500: "rgb(var(--risk-500) / <alpha-value>)",
          400: "rgb(var(--risk-400) / <alpha-value>)",
          300: "rgb(var(--risk-300) / <alpha-value>)",
          200: "rgb(var(--risk-200) / <alpha-value>)",
          100: "rgb(var(--risk-100) / <alpha-value>)",
          50: "rgb(var(--risk-50) / <alpha-value>)",
        },
        success: {
          600: "rgb(var(--success-600) / <alpha-value>)",
          500: "rgb(var(--success-500) / <alpha-value>)",
          100: "rgb(var(--success-100) / <alpha-value>)",
          50: "rgb(var(--success-50) / <alpha-value>)",
        },
        surface: {
          base: "rgb(var(--surface-base) / <alpha-value>)",
          muted: "rgb(var(--surface-muted) / <alpha-value>)",
          card: "rgb(var(--surface-card) / <alpha-value>)",
          deep: "rgb(var(--surface-deep) / <alpha-value>)",
          100: "rgb(var(--surface-100) / <alpha-value>)",
          50: "rgb(var(--surface-50) / <alpha-value>)",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      fontFamily: {
        sans: ["var(--font-jakarta)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
        display: ["var(--font-outfit)", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,23,42,0.04), 0 12px 30px rgba(37,99,235,0.06)",
        "card-hover": "0 8px 20px rgba(15,23,42,0.08), 0 18px 40px rgba(37,99,235,0.10)",
        "card-active": "0 0 0 2px rgba(37,99,235,0.18), 0 10px 30px rgba(37,99,235,0.12)",
        brand: "0 8px 24px rgba(37,99,235,0.24)",
        "brand-lg": "0 18px 48px rgba(37,99,235,0.18)",
        danger: "0 8px 28px rgba(220,38,38,0.14)",
        soft: "0 10px 22px rgba(15,23,42,0.06)",
      },
      backgroundImage: {
        "control-grid":
          "linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(18px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-400% 0" },
          "100%": { backgroundPosition: "400% 0" },
        },
        "slide-right": {
          "0%": { opacity: "0", transform: "translateX(-12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-4px)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.45s ease-out forwards",
        "fade-in": "fade-in 0.3s ease-out forwards",
        "scale-in": "scale-in 0.3s ease-out forwards",
        shimmer: "shimmer 1.8s linear infinite",
        "slide-right": "slide-right 0.35s ease-out forwards",
        float: "float 3s ease-in-out infinite",
      },
      borderRadius: {
        "2xl": "1.125rem",
        "3xl": "1.5rem",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
