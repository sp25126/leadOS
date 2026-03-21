"use client";
import { useEffect, useRef } from "react";
import { useThemeStore } from "@/lib/themes/theme-store";

export default function CursorSpotlight() {
  const ref       = useRef<HTMLDivElement>(null);
  const themeId   = useThemeStore(s => s.themeId);
  const cursorClr = useThemeStore(s => s.theme.fx.cursorColor);

  // Cyber: larger, greener cursor glow
  const size    = themeId === "cyber" ? 500 : themeId === "nord" ? 600 : 700;

  useEffect(() => {
    let raf: number;
    let tx = 0, ty = 0, cx = 0, cy = 0;
    
    const onMove = (e: MouseEvent) => { 
      tx = e.clientX; 
      ty = e.clientY; 
    };
    
    window.addEventListener("mousemove", onMove);

    const tick = () => {
      // Smooth interpolation using a lerp factor of 0.08
      cx += (tx - cx) * 0.08;
      cy += (ty - cy) * 0.08;
      
      if (ref.current) {
        ref.current.style.transform = `translate3d(${cx - (size / 2)}px, ${cy - (size / 2)}px, 0)`;
      }
      raf = requestAnimationFrame(tick);
    };
    
    tick();

    return () => { 
      cancelAnimationFrame(raf); 
      window.removeEventListener("mousemove", onMove); 
    };
  }, [size]);

  return (
    <div
      ref={ref}
      className="pointer-events-none fixed top-0 left-0 z-[100] rounded-full overflow-hidden"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle, ${cursorClr} 0%, transparent 70%)`,
        willChange: "transform",
        mixBlendMode: themeId === "cyber" ? "screen" : "normal",
      }}
    />
  );
}
