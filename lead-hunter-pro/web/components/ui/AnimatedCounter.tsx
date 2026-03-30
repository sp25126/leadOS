"use client";
import { useEffect, useRef, useState } from "react";
import { useInView } from "react-intersection-observer";

interface Props { 
  end: number; 
  duration?: number; 
  prefix?: string; 
  suffix?: string; 
  decimals?: number;
}

export default function AnimatedCounter({ 
  end, duration = 2000, prefix = "", suffix = "", decimals = 0 
}: Props) {
  const [count, setCount] = useState(0);
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.1 });
  const t0 = useRef<number | null>(null);

  useEffect(() => {
    if (!inView) return;
    t0.current = null;
    
    // Ease Out Quintic
    const ease = (t: number) => 1 - Math.pow(1 - t, 5);
    
    const go = (ts: number) => {
      if (!t0.current) t0.current = ts;
      const p = Math.min((ts - t0.current) / duration, 1);
      const next = ease(p) * end;
      setCount(parseFloat(next.toFixed(decimals)));
      if (p < 1) requestAnimationFrame(go);
    };
    
    requestAnimationFrame(go);
  }, [inView, end, duration, decimals]);

  return (
    <span ref={ref} className="tabular-nums font-black tracking-tighter">
      {prefix}{count.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}{suffix}
    </span>
  );
}
