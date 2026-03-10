"use client";

import { CategoryGlyphKey } from "@/lib/constants/categories";

interface CategoryGlyphProps {
  glyph: CategoryGlyphKey;
  className?: string;
  stroke?: string;
}

function SvgWrapper({
  children,
  className,
  stroke = "currentColor",
}: {
  children: React.ReactNode;
  className?: string;
  stroke?: string;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke={stroke}
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export function CategoryGlyph({
  glyph,
  className = "h-5 w-5",
  stroke = "currentColor",
}: CategoryGlyphProps) {
  switch (glyph) {
    case "food":
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <path d="M6 8h12l-1.2 7.2a2 2 0 0 1-2 1.8H9.2a2 2 0 0 1-2-1.8L6 8Z" />
          <path d="M9 8V6.8A2.8 2.8 0 0 1 11.8 4h.4A2.8 2.8 0 0 1 15 6.8V8" />
          <path d="M9.5 12h5" />
        </SvgWrapper>
      );
    case "fashion":
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <path d="M9 5.5 7.8 8 5 9.2l1.6 9.3h10.8L19 9.2 16.2 8 15 5.5h-6Z" />
          <path d="M10 8.5c.5.7 1.1 1 2 1s1.5-.3 2-1" />
          <path d="M12 9.5v9" />
        </SvgWrapper>
      );
    case "electronics":
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <rect x="5" y="6" width="14" height="10" rx="2.2" />
          <path d="M9 18h6" />
          <path d="M10.5 10 9 12.4h2l-1 2.1 3-3.7h-2l1.5-2.8Z" />
        </SvgWrapper>
      );
    case "travel":
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <path d="M4 15.5h16" />
          <path d="m7 13 5-8 1.5 3.8L18 10l-6 3-2.5-.8L7 13Z" />
          <path d="M5.5 19h13" />
        </SvgWrapper>
      );
    case "health_beauty":
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <path d="M12 4c2 2.5 4.5 3.7 4.5 7.1A4.5 4.5 0 0 1 12 15.6a4.5 4.5 0 0 1-4.5-4.5C7.5 7.7 10 6.5 12 4Z" />
          <path d="M12 15.6V20" />
          <path d="M9.5 18h5" />
        </SvgWrapper>
      );
    case "home_lifestyle":
    default:
      return (
        <SvgWrapper className={className} stroke={stroke}>
          <path d="M5 10.5 12 5l7 5.5V19a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-8.5Z" />
          <path d="M9.5 20v-4.8a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1V20" />
        </SvgWrapper>
      );
  }
}
