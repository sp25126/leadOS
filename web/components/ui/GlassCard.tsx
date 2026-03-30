"use client";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useRef, useState, useMemo, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useThemeStore } from "@/lib/themes/theme-store";

type Variant = "default" | "elevated" | "bordered" | "ghost" | "glow";

interface Props {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  tilt?: boolean;
  glow?: boolean;
  onClick?: () => void;
  variant?: Variant;
  glowColor?: string;
  once?: boolean;
  videoSrc?: string;
}

const VARIANT_STYLES: Record<Variant, string> = {
  default:  "bg-[#0a0a0a] border border-white/[0.06]",
  elevated: "bg-[#0d0d0d] border border-white/[0.08] shadow-2xl",
  bordered: "bg-transparent border border-white/[0.1]",
  ghost:    "bg-white/[0.02] border border-white/[0.04]",
  glow:     "bg-[#0a0a0a] border border-violet-500/[0.15]",
};

export default function GlassCard({
  children,
  className = "",
  delay = 0,
  tilt = false,
  glow = false,
  onClick,
  variant = "default",
  glowColor = "#7B2FFF",
  once = true,
  videoSrc,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const themeId = useThemeStore(s => s.theme.id);
  const isNord = themeId === "nord";

  const mouseX = useMotionValue(0.5);
  const mouseY = useMotionValue(0.5);
  // Nord has a calmer spring for movement
  const springConfig = isNord ? { stiffness: 150, damping: 40 } : { stiffness: 200, damping: 30 };
  const smoothX = useSpring(mouseX, springConfig);
  const smoothY = useSpring(mouseY, springConfig);

  // Nord has significantly reduced 3D tilt
  const tiltMax = isNord ? 1.5 : 3.5;
  const rotateX = useTransform(smoothY, [0, 1], [tiltMax, -tiltMax]);
  const rotateY = useTransform(smoothX, [0, 1], [-tiltMax, tiltMax]);

  const glowX = useTransform(smoothX, [0, 1], [0, 100]);
  const glowY = useTransform(smoothY, [0, 1], [0, 100]);

  const handleMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    mouseX.set((e.clientX - rect.left) / rect.width);
    mouseY.set((e.clientY - rect.top) / rect.height);
    setIsHovered(true);
  };

  const handleLeave = () => {
    mouseX.set(0.5);
    mouseY.set(0.5);
    setIsHovered(false);
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once, margin: "-30px" }}
      transition={{ duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] }}
      style={tilt && mounted
        ? { rotateX, rotateY, transformStyle: "preserve-3d", perspective: "1200px" }
        : undefined}
      onMouseMove={tilt || glow ? handleMove : undefined}
      onMouseLeave={tilt || glow ? handleLeave : undefined}
      onClick={onClick}
      whileTap={onClick ? { scale: isNord ? 0.995 : 0.99 } : undefined}
      className={cn(
        "relative rounded-2xl overflow-hidden transition-all duration-300 group",
        VARIANT_STYLES[variant],
        onClick && "cursor-pointer",
        className
      )}
    >
      {/* Cursor-tracked glow */}
      {glow && (
        <motion.div
          className="absolute inset-0 pointer-events-none rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background: `radial-gradient(circle at ${glowX.get()}% ${glowY.get()}%, ${glowColor}12 0%, transparent 50%)`,
          }}
        />
      )}

      {/* Glow variant outer ring */}
      {variant === "glow" && !isNord && (
        <div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{ boxShadow: `0 0 40px ${glowColor}08, inset 0 0 40px ${glowColor}04` }}
        />
      )}

      {/* Inner shimmer / frost border on hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none opacity-0 transition-opacity duration-400 group-hover:opacity-100"
        style={{
          background: isNord 
            ? "linear-gradient(135deg, rgba(136,192,208,0.15) 0%, transparent 40%, transparent 60%, rgba(129,161,193,0.15) 100%)" // Nord Frost shimmer
            : "linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 50%, rgba(255,255,255,0.02) 100%)", // Cosmic shimmer
        }}
      />

      {/* Optional video background — Only on hover to save memory/cpu */}
      {isHovered && (
        <video
          autoPlay
          loop
          muted
          playsInline
          key={isNord ? "nord-video" : videoSrc}
          preload="none"
          className="absolute inset-0 w-full h-full object-cover opacity-[0.14] pointer-events-none z-0 transition-opacity duration-700"
        >
          <source 
            src={isNord ? "/videos/hero-orb.mp4" : videoSrc} 
            type="video/mp4" 
          />
        </video>
      )}

      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </motion.div>
  );
}
