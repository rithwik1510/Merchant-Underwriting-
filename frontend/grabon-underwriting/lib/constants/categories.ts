export const CATEGORY_CONFIG = {
  food: {
    label: "Food & Grocery",
    glyph: "food",
    color: "#2563EB",
    bg: "rgba(37,99,235,0.10)",
    border: "rgba(37,99,235,0.18)",
  },
  fashion: {
    label: "Fashion",
    glyph: "fashion",
    color: "#4F46E5",
    bg: "rgba(79,70,229,0.10)",
    border: "rgba(79,70,229,0.18)",
  },
  electronics: {
    label: "Electronics",
    glyph: "electronics",
    color: "#0F766E",
    bg: "rgba(15,118,110,0.10)",
    border: "rgba(15,118,110,0.18)",
  },
  travel: {
    label: "Travel",
    glyph: "travel",
    color: "#0369A1",
    bg: "rgba(3,105,161,0.10)",
    border: "rgba(3,105,161,0.18)",
  },
  health_beauty: {
    label: "Health & Beauty",
    glyph: "health_beauty",
    color: "#BE123C",
    bg: "rgba(190,18,60,0.08)",
    border: "rgba(190,18,60,0.16)",
  },
  home_lifestyle: {
    label: "Home & Lifestyle",
    glyph: "home_lifestyle",
    color: "#334155",
    bg: "rgba(51,65,85,0.08)",
    border: "rgba(51,65,85,0.16)",
  },
} as const;

export type CategoryKey = keyof typeof CATEGORY_CONFIG;
export type CategoryGlyphKey = (typeof CATEGORY_CONFIG)[CategoryKey]["glyph"];

export function getCategoryConfig(category: string) {
  return (
    CATEGORY_CONFIG[category as CategoryKey] ?? {
      label: category,
      glyph: "home_lifestyle" as const,
      color: "#334155",
      bg: "rgba(51,65,85,0.08)",
      border: "rgba(51,65,85,0.16)",
    }
  );
}
