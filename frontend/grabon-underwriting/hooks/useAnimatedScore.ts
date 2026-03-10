"use client";

import { useEffect, useState } from "react";

export function useAnimatedScore(
  targetScore: number | null,
  duration = 1400
) {
  const [displayScore, setDisplayScore] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (targetScore == null) return;

    setIsAnimating(true);
    const start = performance.now();
    const startValue = 0;
    const endValue = targetScore;

    function easeOutCubic(t: number): number {
      return 1 - Math.pow(1 - t, 3);
    }

    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const current = Math.round(startValue + (endValue - startValue) * eased);
      setDisplayScore(current);

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        setDisplayScore(endValue);
        setIsAnimating(false);
      }
    }

    requestAnimationFrame(tick);
  }, [targetScore, duration]);

  const gaugeProgress =
    targetScore != null ? Math.min(Math.max(targetScore / 100, 0), 1) : 0;

  return { displayScore, gaugeProgress, isAnimating };
}
