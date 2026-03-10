"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface AnimatedNumberProps {
  value: number;
  duration?: number;
  formatter?: (v: number) => string;
  className?: string;
}

export function AnimatedNumber({
  value,
  duration = 900,
  formatter = (v) => Math.round(v).toString(),
  className,
}: AnimatedNumberProps) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const start = performance.now();
    const startVal = 0;

    function easeOut(t: number) {
      return 1 - Math.pow(1 - t, 3);
    }

    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const current = startVal + (value - startVal) * easeOut(progress);
      setDisplay(current);
      if (progress < 1) requestAnimationFrame(tick);
      else setDisplay(value);
    }

    requestAnimationFrame(tick);
  }, [value, duration]);

  return <span className={cn(className)}>{formatter(display)}</span>;
}
