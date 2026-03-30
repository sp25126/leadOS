"use client";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useThemeStore } from "@/lib/themes/theme-store";

export default function HolographicOrb() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const themeId   = useThemeStore(s => s.theme.id);
  const isNord    = themeId === "nord";
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!canvasRef.current) return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    let animId: number;
    let t = 0;

    const resize = () => {
      if (!canvas) return;
      canvas.width  = canvas.offsetWidth  * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener("resize", resize);

    const ribbons = [
      { phase:0,     speed:0.006, amplitude:100, yFrac:0.35, width:2.5, hue:270 },
      { phase:1.05,  speed:0.008, amplitude:80,  yFrac:0.45, width:3.5, hue:200 },
      { phase:2.1,   speed:0.007, amplitude:120, yFrac:0.55, width:2.0, hue:320 },
      { phase:3.14,  speed:0.009, amplitude:70,  yFrac:0.40, width:4.0, hue:180 },
      { phase:4.19,  speed:0.006, amplitude:90,  yFrac:0.60, width:2.5, hue:240 },
      { phase:5.24,  speed:0.008, amplitude:110, yFrac:0.50, width:3.0, hue:290 },
    ];

    const draw = () => {
      const W = canvas.offsetWidth, H = canvas.offsetHeight;
      if (!W || !H) return;
      ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "screen";

      const drawCurve = (lineWidth: number, strokeColor: any, blur: number, points: [number,number][]) => {
          ctx.beginPath();
          ctx.moveTo(points[0][0], points[0][1]);
          for (let i = 1; i < points.length - 2; i++) {
              const xc = (points[i][0] + points[i + 1][0]) / 2;
              const yc = (points[i][1] + points[i + 1][1]) / 2;
              ctx.quadraticCurveTo(points[i][0], points[i][1], xc, yc);
          }
          ctx.strokeStyle = strokeColor;
          ctx.lineWidth = lineWidth;
          ctx.shadowColor = blur ? strokeColor : "transparent";
          ctx.shadowBlur = blur;
          ctx.stroke();
      };

      ribbons.forEach((r) => {
        const pts: [number,number][] = [];
        for (let x = -60; x <= W + 60; x += 10) {
          const p  = x / W;
          const w1 = Math.sin(p * Math.PI * 3 + t * r.speed + r.phase);
          const w2 = Math.sin(p * Math.PI * 5 + t * r.speed * 1.4 + r.phase * 1.3);
          const w3 = Math.cos(p * Math.PI * 2 + t * r.speed * 0.8 + r.phase * 0.7);
          pts.push([x, H * r.yFrac + w1 * r.amplitude + w2 * r.amplitude * 0.35 + w3 * r.amplitude * 0.15]);
        }

        const hShift = (r.hue + t * 0.4) % 360;

        const g1 = ctx.createLinearGradient(0, 0, W, 0);
        if (isNord) {
          g1.addColorStop(0,   `rgba(255,255,255,0)`);
          g1.addColorStop(0.2, `rgba(236,239,244,0.4)`); 
          g1.addColorStop(0.5, `rgba(208,135,112,0.85)`); 
          g1.addColorStop(0.8, `rgba(255,164,164,0.4)`); 
          g1.addColorStop(1,   `rgba(255,255,255,0)`);
          
          drawCurve(r.width, g1, 15, pts);
          drawCurve(r.width * 0.4, `rgba(255,255,255,0.6)`, 8, pts);
        } else {
          g1.addColorStop(0,   `hsla(${hShift},100%,65%,0)`);
          g1.addColorStop(0.2, `hsla(${hShift},100%,65%,0.55)`);
          g1.addColorStop(0.5, `hsla(${(hShift+60)%360},100%,70%,0.85)`);
          g1.addColorStop(0.8, `hsla(${(hShift+120)%360},100%,65%,0.55)`);
          g1.addColorStop(1,   `hsla(${(hShift+180)%360},100%,65%,0)`);
          
          drawCurve(r.width, g1, 22, pts);
          drawCurve(r.width * 0.25, `hsla(${(hShift+30)%360},100%,95%,0.35)`, 6, pts);
        }
      });

      t++;
      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => { 
        cancelAnimationFrame(animId); 
        window.removeEventListener("resize", resize); 
    };
  }, [isNord]);

  if (!mounted) return null;

  return (
    <motion.div
      className="absolute inset-0 w-full h-full pointer-events-none"
      initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ duration:2.5, ease:"easeOut" }}
    >
      <canvas ref={canvasRef} key={themeId} className="w-full h-full" style={{ mixBlendMode: isNord ? "normal" : "screen" }} />
      <div className="absolute inset-0" style={{
        background:`radial-gradient(ellipse 80% 65% at 50% 50%, transparent 25%, var(--c-bg, #000000) 100%)`
      }} />
    </motion.div>
  );
}
