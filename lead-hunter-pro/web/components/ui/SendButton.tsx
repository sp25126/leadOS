"use client";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, CheckCircle, Loader2 } from "lucide-react";
import { useThemeStore } from "@/lib/themes/theme-store";

interface Props {
  onClick: () => Promise<void>;
  label?: string;
  className?: string;
  disabled?: boolean;
}

export default function SendButton({
  onClick, label = "Send", className = "", disabled = false,
}: Props) {
  const [state, setState] = useState<"idle" | "launching" | "sending" | "done">("idle");
  const [particles, setParticles] = useState<{ id: number; x: number; y: number }[]>([]);
  const btnRef = useRef<HTMLButtonElement>(null);
  
  const isNord = useThemeStore(s => s.theme.id) === "nord";

  const handleClick = async () => {
    if (state !== "idle" || disabled) return;

    // Generate trail particles
    setParticles(
      Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: Math.random() * 80 - 40,
        y: Math.random() * 60 - 30,
      }))
    );

    setState("launching");
    
    // Simulate flight time
    await new Promise((r) => setTimeout(r, 600));
    setState("sending");

    try {
      await onClick();
      setState("done");
      // Hold success state
      await new Promise((r) => setTimeout(r, 2200));
    } catch {
      /* error handled by caller */
    } finally {
      setState("idle");
      setParticles([]);
    }
  };

  const isActive = state !== "idle";

  return (
    <div className="relative inline-flex items-center justify-center">
      {/* Trail particles on launch */}
      <AnimatePresence>
        {state === "launching" &&
          particles.map((p) => (
            <motion.div
              key={p.id}
              className="absolute rounded-full pointer-events-none"
              style={{
                width: 5,
                height: 5,
                background: p.id % 2 === 0 ? (isNord ? "#88C0D0" : "#7B2FFF") : (isNord ? "#B48EAD" : "#00E5FF"),
                boxShadow: `0 0 10px ${p.id % 2 === 0 ? (isNord ? "#88C0D0" : "#7B2FFF") : (isNord ? "#B48EAD" : "#00E5FF")}`,
              }}
              initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
              animate={{
                x: [0, p.x * 2, p.x * 6],
                y: [0, p.y * 1.5, p.y * 3 - 60],
                opacity: [1, 0.7, 0],
                scale: [1, 1.2, 0],
              }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          ))}
      </AnimatePresence>

      <button
        ref={btnRef}
        onClick={handleClick}
        disabled={disabled || isActive}
        className={`
          relative overflow-hidden flex items-center gap-3
          px-8 py-4 rounded-3xl text-sm font-black uppercase tracking-widest
          transition-all duration-300 select-none
          ${disabled ? "opacity-30 cursor-not-allowed grayscale" : (isNord ? "cursor-pointer active:scale-98 hover:scale-[1.01]" : "cursor-pointer active:scale-95 hover:scale-[1.02]")}
          ${className}
        `}
        style={{
          background:
            state === "done"
              ? "linear-gradient(135deg, #10b981, #059669)"
              : (isNord ? "linear-gradient(135deg, #88C0D0 0%, #81A1C1 60%, #B48EAD 100%)" : "linear-gradient(135deg, #7B2FFF 0%, #00E5FF 60%, #FF2D9B 100%)"),
          boxShadow:
            state === "done"
              ? "0 0 30px rgba(16,185,129,0.5), inset 0 0 15px rgba(255,255,255,0.2)"
              : (isNord ? "0 0 20px rgba(136,192,208,0.3), 0 0 40px rgba(129,161,193,0.1), inset 0 0 15px rgba(255,255,255,0.15)" : "0 0 30px rgba(123,47,255,0.5), 0 0 60px rgba(0,229,255,0.2), inset 0 0 15px rgba(255,255,255,0.1)"),
          color: "#fff",
        }}
      >
        {/* Success burst video */}
        <AnimatePresence>
          {state === "done" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-0 pointer-events-none"
            >
              <video
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover"
              >
                <source src="/videos/send-burst.mp4" type="video/mp4" />
              </video>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Prismatic Shimmer Sweep */}
        {!isActive && (
          <motion.div
            className="absolute inset-0 pointer-events-none opacity-40 z-20"
            style={{
              background:
                "linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.4) 50%, transparent 65%)",
            }}
            animate={{ x: ["-150%", "300%"] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "linear", repeatDelay: 1 }}
          />
        )}

        {/* Action Icon Transition */}
        <AnimatePresence mode="wait">
          {state === "idle" && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, scale: 0.4 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, x: 40, y: -20, rotate: 15, scale: 0.6 }}
              transition={{ duration: 0.15 }}
              className="z-10"
            >
              <Send className="w-5 h-5 fill-current" />
            </motion.div>
          )}
          {state === "launching" && (
            <motion.div
              key="launch"
              initial={{ opacity: 1, x: 0, y: 0 }}
              animate={{ opacity: 0, x: 80, y: -40, rotate: 30, scale: 0.5 }}
              transition={{ duration: 0.45, ease: "easeOut" }}
              className="z-10"
            >
              <Send className="w-5 h-5 fill-current" />
            </motion.div>
          )}
          {state === "sending" && (
            <motion.div
              key="sending"
              initial={{ opacity: 0, scale: 0.4 }}
              animate={{ opacity: 1, scale: 1 }}
              className="z-10"
            >
              <Loader2 className="w-5 h-5 animate-spin" />
            </motion.div>
          )}
          {state === "done" && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.2, rotate: -45 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 500, damping: 12 }}
              className="z-10"
            >
              <CheckCircle className="w-5 h-5" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Dynamic Label */}
        <motion.span
          className="relative z-10"
          animate={{
            opacity: state === "launching" ? 0 : 1,
            x: state === "launching" ? -10 : 0
          }}
          transition={{ duration: 0.15 }}
        >
          {state === "done" ? "Success" : state === "sending" ? "Transmitting" : label}
        </motion.span>

        {/* Border glow ring */}
        <div className="absolute inset-0 border border-white/20 rounded-3xl" />
      </button>
    </div>
  );
}
