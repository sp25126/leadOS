"use client";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useRef } from "react";
import { useThemeStore } from "@/lib/themes/theme-store";

interface Props {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit";
  variant?: "violet" | "cyan" | "pink" | "white";
}

const GRADIENTS = {
  violet: { from: "#7B2FFF", to: "#00E5FF", glow: "rgba(123,47,255,0.6)" },
  cyan:   { from: "#00E5FF", to: "#7B2FFF", glow: "rgba(0,229,255,0.5)"  },
  pink:   { from: "#FF2D9B", to: "#7B2FFF", glow: "rgba(255,45,155,0.6)" },
  white:  { from: "rgba(255,255,255,0.3)", to: "rgba(255,255,255,0.1)", glow: "rgba(255,255,255,0.2)" },
};

const NORD_GRADIENTS = {
  violet: { from: "#88C0D0", to: "#81A1C1", glow: "rgba(136,192,208,0.3)" },
  cyan:   { from: "#81A1C1", to: "#B48EAD", glow: "rgba(129,161,193,0.3)" },
  pink:   { from: "#B48EAD", to: "#88C0D0", glow: "rgba(180,142,173,0.3)" },
  white:  { from: "rgba(236,239,244,0.3)", to: "rgba(236,239,244,0.1)", glow: "rgba(236,239,244,0.15)" },
};

export default function ActionButton({
  children, onClick, className = "", disabled = false, type = "button", variant = "violet",
}: Props) {
  const isNord = useThemeStore(s => s.theme.id) === "nord";
  const g = isNord ? NORD_GRADIENTS[variant] : GRADIENTS[variant];
  const ref = useRef<HTMLButtonElement>(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const springConfig = isNord ? { stiffness: 200, damping: 40 } : { stiffness: 400, damping: 40 };
  const springX = useSpring(mouseX, springConfig);
  const springY = useSpring(mouseY, springConfig);

  const handleMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    mouseX.set((e.clientX - rect.left - rect.width / 2) * 0.4);
    mouseY.set((e.clientY - rect.top - rect.height / 2) * 0.4);
  };

  return (
    <motion.button
      ref={ref}
      type={type}
      onClick={onClick}
      disabled={disabled}
      onMouseMove={handleMove}
      onMouseLeave={() => { mouseX.set(0); mouseY.set(0); }}
      style={{ x: springX, y: springY }}
      whileTap={{ scale: isNord ? 0.985 : 0.96 }}
      whileHover={{ scale: isNord ? 1.01 : 1.02 }}
      className={`
        relative inline-flex items-center justify-center gap-3
        px-6 py-3 rounded-2xl text-xs font-black uppercase tracking-widest
        overflow-hidden group select-none
        ${disabled ? "opacity-30 cursor-not-allowed grayscale pointer-events-none" : "cursor-pointer"}
        ${className}
      `}
    >
      {/* Dynamic Gradient Border */}
      <span
        className="absolute inset-0 rounded-2xl p-px z-0 pointer-events-none"
        style={{
          background: `linear-gradient(135deg, ${g.from}, ${g.to})`,
          WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
        }}
      />

      {/* Internal Matte Layer */}
      <span className="absolute inset-[1.5px] rounded-[14px] bg-zinc-950 z-0 group-hover:bg-zinc-900 transition-colors" />

      {/* Surface Scanning Glow */}
      <motion.span
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-10"
        style={{
          background: `linear-gradient(105deg, transparent 30%, ${g.from}33 50%, transparent 70%)`,
        }}
        animate={{ x: ["-150%", "300%"] }}
        transition={{ duration: 1.8, repeat: Infinity, ease: "linear", repeatDelay: 0.8 }}
      />

      {/* Radiant External Glow */}
      <motion.span
        className={`absolute inset-[-15px] rounded-[40px] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-[-1] ${isNord ? 'blur-md' : 'blur-2xl'}`}
        style={{
           background: `radial-gradient(circle, ${g.glow} 0%, transparent ${isNord ? '50%' : '65%'})`,
        }}
      />

      {/* Inner Bloom effect */}
      <motion.span
        className={`absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 pointer-events-none z-10 ${isNord ? 'group-hover:opacity-15 blur-md' : 'group-hover:opacity-30 blur-xl'}`}
        style={{
          boxShadow: `inset 0 0 ${isNord ? '12px' : '25px'} ${g.glow}`,
        }}
      />

      {/* Primary Label Content */}
      <span className="relative z-20 flex items-center gap-2.5 text-white/90 group-hover:text-white transition-colors">
         {children}
      </span>

      {/* Active Reflection */}
      <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-white/5 to-transparent pointer-events-none opacity-50 z-10" />
    </motion.button>
  );
}
