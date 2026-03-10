"use client";

import { motion } from "framer-motion";
import { useAnimatedScore } from "@/hooks/useAnimatedScore";

interface ScoreGaugeProps {
  score: number | null;
  size?: number;
}

const ARC_DEG = 250;
const START_DEG = 145;

function polar(cx: number, cy: number, r: number, deg: number) {
  const rad = ((deg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arc(cx: number, cy: number, r: number, start: number, end: number) {
  const a = polar(cx, cy, r, start);
  const b = polar(cx, cy, r, end);
  const large = end - start > 180 ? 1 : 0;
  return `M ${a.x} ${a.y} A ${r} ${r} 0 ${large} 1 ${b.x} ${b.y}`;
}

function getScoreTone(score: number | null) {
  if (score == null) return { color: "#94a3b8", glow: "rgba(148,163,184,0.18)" };
  if (score >= 75) return { color: "#145af2", glow: "rgba(20,90,242,0.22)" };
  if (score >= 55) return { color: "#2563eb", glow: "rgba(37,99,235,0.18)" };
  if (score >= 40) return { color: "#7c3aed", glow: "rgba(124,58,237,0.18)" };
  return { color: "#dc2626", glow: "rgba(220,38,38,0.18)" };
}

export function ScoreGauge({ score, size = 200 }: ScoreGaugeProps) {
  const { displayScore, gaugeProgress } = useAnimatedScore(score);
  const tone = getScoreTone(score);

  const cx = size / 2;
  const cy = size / 2;
  const r = size * 0.36;
  const strokeWidth = size * 0.06;
  const trackEnd = START_DEG + ARC_DEG;
  const ringPath = arc(cx, cy, r, START_DEG, trackEnd);
  const gradientId = `score-track-${size}`;
  const valueText = score !== null ? displayScore.toFixed(2) : "-";
  const valueSize = valueText.length >= 5 ? size * 0.27 : size * 0.3;
  const labelText = score !== null ? "POLICY SCORE" : "PENDING";
  const labelTop = cy + size * 0.24;

  return (
    <div className="relative flex items-center justify-center overflow-hidden" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#e2e8f0" />
            <stop offset="100%" stopColor="#cbd5e1" />
          </linearGradient>
        </defs>

        <path
          d={ringPath}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {score !== null && gaugeProgress > 0.01 ? (
          <>
            <motion.path
              d={ringPath}
              fill="none"
              stroke={tone.glow}
              strokeWidth={strokeWidth + 8}
              strokeLinecap="round"
              initial={{ opacity: 0, pathLength: 0 }}
              animate={{ opacity: 1, pathLength: gaugeProgress }}
              transition={{ duration: 0.85, ease: [0.22, 1, 0.36, 1] }}
            />
            <motion.path
              d={ringPath}
              fill="none"
              stroke={tone.color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              initial={{ opacity: 0, pathLength: 0 }}
              animate={{ opacity: 1, pathLength: gaugeProgress }}
              transition={{ duration: 0.85, ease: [0.22, 1, 0.36, 1] }}
            />
          </>
        ) : null}

      </svg>

      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-mono font-extrabold leading-none text-ink-900"
          style={{
            fontSize: valueSize,
            letterSpacing: "-0.06em",
          }}
        >
          {valueText}
        </div>
        <div
          className="absolute left-1/2 -translate-x-1/2 text-center font-sans font-medium tracking-[0.18em] text-ink-500"
          style={{
            top: labelTop,
            fontSize: size * 0.08,
            whiteSpace: "nowrap",
          }}
        >
          {labelText}
        </div>
      </div>
    </div>
  );
}
